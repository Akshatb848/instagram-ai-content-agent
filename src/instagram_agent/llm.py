import json
from abc import ABC, abstractmethod
from typing import Any

import httpx
from pydantic import ValidationError

from instagram_agent.schemas import ReelPackage


class ProviderError(RuntimeError):
    pass


class QuotaExhaustedError(ProviderError):
    pass


class LLMProvider(ABC):
    @abstractmethod
    def generate(self, prompt: str) -> dict[str, Any]: ...


class MockProvider(LLMProvider):
    def __init__(self, response: dict[str, Any]) -> None:
        self.response = response

    def generate(self, prompt: str) -> dict[str, Any]:
        del prompt
        return self.response


class GeminiProvider(LLMProvider):
    def __init__(self, api_key: str, model: str, timeout: float = 30) -> None:
        self.api_key, self.model, self.timeout = api_key, model, timeout

    def generate(self, prompt: str) -> dict[str, Any]:
        url = (
            f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent"
        )
        response = httpx.post(
            url,
            params={"key": self.api_key},
            json={
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {"responseMimeType": "application/json"},
            },
            timeout=self.timeout,
        )
        if response.status_code == 429:
            raise QuotaExhaustedError("Gemini free-tier quota exhausted")
        response.raise_for_status()
        text = response.json()["candidates"][0]["content"]["parts"][0]["text"]
        return parse_json_once(text)


class OllamaProvider(LLMProvider):
    def __init__(self, base_url: str, model: str, timeout: float = 60) -> None:
        self.base_url, self.model, self.timeout = base_url.rstrip("/"), model, timeout

    def generate(self, prompt: str) -> dict[str, Any]:
        response = httpx.post(
            f"{self.base_url}/api/generate",
            json={"model": self.model, "prompt": prompt, "format": "json", "stream": False},
            timeout=self.timeout,
        )
        response.raise_for_status()
        return parse_json_once(response.json()["response"])


def parse_json_once(text: str) -> dict[str, Any]:
    try:
        value = json.loads(text)
    except json.JSONDecodeError:
        start, end = text.find("{"), text.rfind("}")
        if start < 0 or end <= start:
            raise ProviderError("Provider returned invalid JSON") from None
        try:
            value = json.loads(text[start : end + 1])
        except json.JSONDecodeError as exc:
            raise ProviderError("JSON repair failed") from exc
    if not isinstance(value, dict):
        raise ProviderError("Provider response must be an object")
    return value


def generate_package(provider: LLMProvider, prompt: str) -> ReelPackage:
    try:
        return ReelPackage.model_validate(provider.generate(prompt))
    except ValidationError as exc:
        raise ProviderError("Provider response violated the content contract") from exc
