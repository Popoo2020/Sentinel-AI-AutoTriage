"""Redaction helpers for data minimisation before LLM invocation.

The goal is not to provide a complete DLP engine.  Instead, this module offers
transparent, deterministic examples of how obvious secret-like and identifier-
like values can be removed from incident text before it is sent to an LLM.
"""
from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass(frozen=True)
class RedactionResult:
    """Result object returned by the redaction layer."""

    text: str
    redaction_count: int
    redaction_types: tuple[str, ...]


_REDACTION_PATTERNS: tuple[tuple[str, re.Pattern[str], str], ...] = (
    (
        "api_key",
        re.compile(r"(?i)\b(api[_ -]?key|token|secret)\s*[:=]\s*[^\s,;]+"),
        "[REDACTED_SECRET]",
    ),
    (
        "password",
        re.compile(r"(?i)\bpassword\s*[:=]\s*[^\s,;]+"),
        "[REDACTED_PASSWORD]",
    ),
    (
        "bearer_token",
        re.compile(r"(?i)\bbearer\s+[A-Za-z0-9._\-]+"),
        "Bearer [REDACTED_TOKEN]",
    ),
    (
        "email",
        re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"),
        "[REDACTED_EMAIL]",
    ),
    (
        "ipv4",
        re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b"),
        "[REDACTED_IP]",
    ),
)


def redact_text(text: str) -> RedactionResult:
    """Redact common sensitive-looking values from free text.

    The function is deterministic and intentionally conservative.  It reports
    only redaction *types* and counts, never the original values.
    """
    if not isinstance(text, str):
        raise TypeError("text must be a string")

    redacted = text
    total = 0
    types: list[str] = []

    for redaction_type, pattern, replacement in _REDACTION_PATTERNS:
        redacted, count = pattern.subn(replacement, redacted)
        if count:
            total += count
            types.append(redaction_type)

    return RedactionResult(
        text=redacted,
        redaction_count=total,
        redaction_types=tuple(types),
    )
