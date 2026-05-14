from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Iterable


def timestamp() -> str:
    return datetime.now().strftime("%Y%m%d-%H%M%S")


def ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def truncate_text(text: str, limit: int, suffix: str = "\n...[truncated]...") -> str:
    if limit <= 0 or len(text) <= limit:
        return text
    keep = max(0, limit - len(suffix))
    return text[:keep] + suffix


def read_text_file(path: Path, max_chars: int | None = None) -> str:
    data = path.read_bytes()
    text = data.decode("utf-8", errors="replace")
    if max_chars is not None:
        return truncate_text(text, max_chars)
    return text


def bullet_list(items: Iterable[str]) -> str:
    return "\n".join(f"- {item}" for item in items)
