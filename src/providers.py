"""Model-provider abstractions for Sentinel-AI-AutoTriage."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


class CompletionProvider(Protocol):
    """Minimal provider contract used by the LLM client."""

    def complete(
        self,
        *,
        prompt: str,
        model_name: str,
        temperature: float,
        max_tokens: int,
    ) -> str:
        """Return raw completion text for one prompt."""


@dataclass(frozen=True)
class StaticMockProvider:
    """Deterministic provider for tests, demos and benchmark scaffolding."""

    response_text: str

    def complete(
        self,
        *,
        prompt: str,
        model_name: str,
        temperature: float,
        max_tokens: int,
    ) -> str:
        del prompt, model_name, temperature, max_tokens
        return self.response_text
