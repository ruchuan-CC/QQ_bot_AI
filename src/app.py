from __future__ import annotations

import json
from contextlib import asynccontextmanager

from fastapi import FastAPI, Header, Request
from fastapi.responses import JSONResponse
from loguru import logger

from src.ai.openai_compatible_client import OpenAICompatibleProvider
from src.config import Settings
from src.db import create_engine, create_sessionmaker
from src.models import Base
from src.prompts.chat_prompt import ChatPromptBuilder
from src.qq.auth import AccessTokenManager
from src.qq.client import QQOfficialClient
from src.qq.events import parse_event
from src.qq.webhook import WebhookSignatureVerifier, build_callback_validation_response
from src.services.chat_service import ChatService, DuplicateMessageError
from src.services.emotion_service import EmotionService, SQLEmotionRepository
from src.services.memory_service import MemoryService, SQLMemoryRepository
from src.services.message_service import SQLMessageRepository
from src.services.persona_service import PersonaService
from src.services.user_service import SQLUserRepository, UserService


def create_app(settings: Settings | None = None, ai_provider=None, qq_client=None) -> FastAPI:
    settings = settings or Settings()
    engine = create_engine(settings.database_url)
    session_factory = create_sessionmaker(engine)

    @asynccontextmanager
    async def lifespan(_: FastAPI):
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        yield
        await engine.dispose()

    app = FastAPI(title="QQ Private AI Companion Bot", lifespan=lifespan)

    persona_service = PersonaService(settings.bot_persona_file)
    user_service = UserService(SQLUserRepository(session_factory))
    message_repository = SQLMessageRepository(session_factory)
    memory_service = MemoryService(SQLMemoryRepository(session_factory))
    emotion_service = EmotionService(SQLEmotionRepository(session_factory))
    prompt_builder = ChatPromptBuilder()

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

    chat_service = ChatService(
        ai_provider=ai_provider,
        user_service=user_service,
        message_repository=message_repository,
        memory_service=memory_service,
        emotion_service=emotion_service,
        prompt_builder=prompt_builder,
        persona=persona_service.load(),
        max_history_messages=settings.max_history_messages,
        max_memory_items=settings.max_memory_items,
        max_reply_chars=settings.max_reply_chars,
        memory_enabled=settings.memory_enabled,
        memory_extract_enabled=settings.memory_extract_enabled,
        memory_min_importance=settings.memory_min_importance,
        emotion_enabled=settings.emotion_enabled,
    )

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
            try:
                reply = await chat_service.prepare_reply(event)
            except DuplicateMessageError:
                return JSONResponse({"status": "duplicate"})

            try:
                send_result = await qq_client.send_text_message(
                    openid=event.openid,
                    content=reply.content,
                    msg_seq=reply.msg_seq,
                    msg_id=event.msg_id,
                    event_id=None,
                )
            except Exception:
                logger.exception("Failed to send QQ C2C reply")
                return JSONResponse({"status": "send_failed"}, status_code=502)

            await chat_service.record_assistant_reply(
                qq_openid=event.openid,
                content=reply.content,
                msg_seq=reply.msg_seq,
                qq_message_id_sent=send_result.get("id") or send_result.get("message_id"),
            )
            return JSONResponse({"status": "replied", "event_type": event.raw_type})

        return JSONResponse({"status": "accepted", "event_type": event.raw_type})

    return app
