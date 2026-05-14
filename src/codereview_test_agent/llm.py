from __future__ import annotations

import json
import urllib.error
import urllib.request
from dataclasses import dataclass

from .config import Settings
from .mock_llm import MockLLM


@dataclass(frozen=True)
class ChatMessage:
    role: str
    content: str


class LLMError(RuntimeError):
    pass


class LLMClient:
    """OpenAI-compatible chat completion client.

    Supports providers exposing a /chat/completions-compatible endpoint,
    such as OpenAI and DeepSeek. For demos, pass mock=True.
    """

    def __init__(self, settings: Settings, mock: bool = False):
        self.settings = settings
        self.mock = mock
        self._mock_client = MockLLM() if mock else None

    def chat(self, messages: list[ChatMessage]) -> str:
        payload_messages = [{"role": m.role, "content": m.content} for m in messages]
        if self.mock:
            return self._mock_client.chat(payload_messages)  # type: ignore[union-attr]

        if not self.settings.api_key or self.settings.api_key == "replace-with-your-api-key":
            raise LLMError(
                "LLM_API_KEY is missing. Set it in .env or run with --mock for demo mode."
            )

        payload = {
            "model": self.settings.model,
            "messages": payload_messages,
            "temperature": self.settings.temperature,
        }
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            self.settings.base_url,
            data=data,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.settings.api_key}",
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=self.settings.timeout_seconds) as resp:
                raw = resp.read().decode("utf-8")
        except urllib.error.HTTPError as exc:
            body = exc.read().decode("utf-8", errors="replace")
            raise LLMError(f"LLM HTTP error {exc.code}: {body}") from exc
        except urllib.error.URLError as exc:
            raise LLMError(f"LLM network error: {exc}") from exc

        try:
            obj = json.loads(raw)
            return obj["choices"][0]["message"]["content"]
        except Exception as exc:  # noqa: BLE001
            raise LLMError(f"Unexpected LLM response: {raw[:1000]}") from exc
