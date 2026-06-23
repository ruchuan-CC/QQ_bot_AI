from __future__ import annotations

from typing import Any


class ChatPromptBuilder:
    def build(
        self,
        *,
        persona: str,
        memories: list[str],
        emotion: dict[str, Any],
        style: str | None,
        history: list[dict[str, str]],
        current_message: str,
    ) -> str:
        sections = [
            "# Persona",
            persona,
            "# Long-term Memory",
            "\n".join(f"- {memory}" for memory in memories) or "无",
            "# Emotion",
            ", ".join(f"{key}: {value}" for key, value in emotion.items()) or "unknown",
            "# User Style",
            style or "default",
            "# Recent History",
            "\n".join(f"{item['role']}: {item['content']}" for item in history) or "无",
            "# Current Message",
            current_message,
        ]
        return "\n\n".join(sections)
