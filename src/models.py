"""
models.py
---------

Shared data structures used across the Sentinel‑AI‑AutoTriage project.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass
class IncidentSummary:
    """Simplified representation of a Sentinel incident for LLM processing."""

    id: str
    title: str
    description: str
    severity: str
    status: str

    def as_prompt(self) -> str:
        return f"[{self.severity}] {self.title}: {self.description}"
