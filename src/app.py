from __future__ import annotations

import json

from fastapi import FastAPI, Header, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from loguru import logger

from src.ai.openai_compatible_client import OpenAICompatibleProvider
from src.config import Settings
from src.prompts.chat_prompt import ChatPromptBuilder
from src.qq.auth import AccessTokenManager
from src.qq.client import QQOfficialClient
from src.qq.events import parse_event
from src.qq.webhook import WebhookSignatureVerifier, build_callback_validation_response
from src.services.command_service import CommandService
from src.services.memory_service import InMemoryMemoryRepository, MemoryService
from src.services.message_service import MessageDeduplicator, MessageSequence
from src.services.persona_service import PersonaService
from src.services.user_service import InMemoryUserRepository, UserService


def create_app(settings: Settings | None = None, ai_provider=None, qq_client=None) -> FastAPI:
    settings = settings or Settings()
    app = FastAPI(title="QQ Private AI Companion Bot")
    persona_service = PersonaService(settings.bot_persona_file)
    user_service = UserService(InMemoryUserRepository())
    memory_service = MemoryService(InMemoryMemoryRepository())
    command_service = CommandService(
        user_service=user_service,
        memory_service=memory_service,
        persona_summary=persona_service.summary(),
    )
    prompt_builder = ChatPromptBuilder()
    deduplicator = MessageDeduplicator()
    sequences = MessageSequence()
    ai_provider = ai_provider or OpenAICompatibleProvider(
        api_key=settings.ai_api_key,
        base_url=settings.ai_base_url,
        model=settings.ai_model,
        temperature=settings.ai_temperature,
        max_tokens=settings.ai_max_tokens,
        timeout=settings.ai_timeout_seconds,
    )
    if qq_client is None:
        token_manager = AccessTokenManager(
            app_id=settings.qq_app_id,
            client_secret=settings.qq_client_secret,
            token_url=settings.qq_token_url,
        )
        qq_client = QQOfficialClient(api_base_url=settings.qq_api_base_url, token_manager=token_manager)

    if settings.assets_enabled:
        app.mount("/assets", StaticFiles(directory=str(settings.assets_dir), check_dir=False), name="assets")

    @app.get("/health")
    async def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.post(settings.qq_webhook_path)
    async def qq_callback(
        request: Request,
        x_signature_ed25519: str | None = Header(default=None),
        x_signature_timestamp: str | None = Header(default=None),
    ) -> JSONResponse:
        body = await request.body()
        if settings.qq_bot_secret and x_signature_ed25519 and x_signature_timestamp:
            verifier = WebhookSignatureVerifier(settings.qq_bot_secret)
            if not verifier.verify(
                timestamp=x_signature_timestamp,
                body=body,
                signature=x_signature_ed25519,
            ):
                return JSONResponse({"error": "invalid signature"}, status_code=401)

        try:
            payload = json.loads(body.decode("utf-8") or "{}")
        except json.JSONDecodeError:
            return JSONResponse({"error": "invalid json"}, status_code=400)

        if payload.get("op") == 13 and payload.get("d", {}).get("plain_token"):
            event_ts = str(payload["d"].get("event_ts") or payload.get("id") or "")
            return JSONResponse(
                build_callback_validation_response(
                    plain_token=payload["d"]["plain_token"],
                    event_ts=event_ts,
                    bot_secret=settings.qq_bot_secret,
                )
            )

        event = parse_event(payload)
        if event.out_of_scope:
            logger.debug("Ignoring out-of-scope QQ event: {}", event.raw_type)
            return JSONResponse({"status": "ignored"})
        if event.raw_type == "C2C_MESSAGE_CREATE":
            if not event.openid:
                return JSONResponse({"status": "ignored", "reason": "missing openid"})
            if not deduplicator.remember(event.msg_id):
                return JSONResponse({"status": "duplicate"})

            command_reply = await command_service.handle(event.openid, event.content)
            if command_reply is not None:
                reply_text = command_reply
            else:
                memories = [item.content for item in await memory_service.list(event.openid)]
                style = await user_service.get_setting(event.openid, "style")
                prompt = prompt_builder.build(
                    persona=persona_service.load(),
                    memories=memories,
                    emotion={},
                    style=style,
                    history=[],
                    current_message=event.content,
                )
                try:
                    reply_text = await ai_provider.complete(prompt)
                except Exception:
                    logger.exception("AI provider failed")
                    reply_text = "我现在暂时无法生成回复。"

            msg_seq = sequences.next(event.openid)
            try:
                await qq_client.send_text_message(
                    openid=event.openid,
                    content=reply_text,
                    msg_seq=msg_seq,
                    msg_id=event.msg_id,
                    event_id=None,
                )
            except Exception:
                logger.exception("Failed to send QQ C2C reply")
                return JSONResponse({"status": "send_failed"}, status_code=502)
            return JSONResponse({"status": "replied", "event_type": event.raw_type})

        return JSONResponse({"status": "accepted", "event_type": event.raw_type})

    return app
