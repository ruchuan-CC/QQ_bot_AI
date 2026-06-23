from __future__ import annotations


def split_reply(text: str, max_chars: int) -> list[str]:
    if max_chars <= 0:
        raise ValueError("max_chars must be positive")
    if not text:
        return []
    return [text[index : index + max_chars] for index in range(0, len(text), max_chars)]
