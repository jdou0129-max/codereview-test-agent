from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Settings:
    api_key: str
    base_url: str
    model: str
    temperature: float = 0.2
    timeout_seconds: int = 120
    max_context_chars: int = 60_000


def load_dotenv(path: str | Path = ".env") -> None:
    """Tiny .env loader to avoid external dependencies."""
    p = Path(path)
    if not p.exists():
        return
    for raw in p.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        os.environ.setdefault(key, value)


def get_settings(max_context_chars: int | None = None) -> Settings:
    load_dotenv()
    api_key = os.getenv("LLM_API_KEY", "")
    base_url = os.getenv("LLM_BASE_URL", "https://api.openai.com/v1/chat/completions")
    model = os.getenv("LLM_MODEL", "gpt-4.1-mini")
    temperature = float(os.getenv("LLM_TEMPERATURE", "0.2"))
    timeout_seconds = int(os.getenv("LLM_TIMEOUT_SECONDS", "120"))
    context_chars = max_context_chars or int(os.getenv("MAX_CONTEXT_CHARS", "60000"))
    return Settings(
        api_key=api_key,
        base_url=base_url,
        model=model,
        temperature=temperature,
        timeout_seconds=timeout_seconds,
        max_context_chars=context_chars,
    )
