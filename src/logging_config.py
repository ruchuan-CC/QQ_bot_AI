from __future__ import annotations

from loguru import logger


def configure_logging(level: str = "INFO") -> None:
    logger.remove()
    logger.add(lambda message: print(message, end=""), level=level)
