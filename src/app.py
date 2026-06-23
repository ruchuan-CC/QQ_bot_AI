from __future__ import annotations

import json

from fastapi import FastAPI, Header, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from loguru import logger

from src.config import Settings
from src.qq.events import parse_event
from src.qq.webhook import WebhookSignatureVerifier, build_callback_validation_response


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or Settings()
    app = FastAPI(title="QQ Private AI Companion Bot")

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

        return JSONResponse({"status": "accepted", "event_type": event.raw_type})

    return app
