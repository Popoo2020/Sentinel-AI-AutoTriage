"""
llm_client.py
-------------

LLM provider wrapper for the Sentinel-AI-AutoTriage prototype.

The module asks the model for a strict JSON response and validates the result
before the triage layer consumes it. If the model returns malformed content,
the client degrades safely to a non-destructive recommendation that leaves the
incident active for analyst review.
"""
from __future__ import annotations

import json
import logging
import os
import re
from typing import Any, Dict

try:
    from openai import OpenAI  # type: ignore
except ImportError:
    OpenAI = None  # type: ignore[assignment]

logger = logging.getLogger(__name__)

_ALLOWED_STATUSES = {"New", "Active", "Closed"}
_ALLOWED_CLASSIFICATIONS = {
    "True Positive",
    "False Positive",
    "Benign Positive",
    "Undetermined",
    "Unspecified",
}


class LLMClient:
    """Small abstraction for LLM-assisted incident triage recommendations."""

    def __init__(self, model_name: str = "gpt-4o-mini", temperature: float = 0.2) -> None:
        self.model_name = model_name
        self.temperature = temperature
        api_key = os.getenv("OPENAI_API_KEY")
        if OpenAI is None:
            raise ImportError(
                "openai package is not installed. Install openai or implement another provider."
            )
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable is not set")
        self.client = OpenAI(api_key=api_key)

    def analyse_incident(self, incident_title: str, incident_description: str) -> Dict[str, str]:
        """Return a validated incident triage recommendation.

        Expected output schema:
        {
          "recommended_status": "New" | "Active" | "Closed",
          "classification": "True Positive" | "False Positive" | "Benign Positive" | "Undetermined" | "Unspecified",
          "comment": "short analyst-facing explanation"
        }
        """
        prompt = (
            "You are assisting a cybersecurity analyst with Microsoft Sentinel incident triage. "
            "Return ONLY valid JSON, without markdown fences or additional prose. "
            "Use this exact schema: "
            '{"recommended_status":"New|Active|Closed",'
            '"classification":"True Positive|False Positive|Benign Positive|Undetermined|Unspecified",'
            '"comment":"one concise analyst-facing sentence"}. '
            "Do not recommend closing an incident unless the available context strongly supports it.\n\n"
            f"Title: {incident_title}\n"
            f"Description: {incident_description}"
        )

        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[{"role": "user", "content": prompt}],
                temperature=self.temperature,
                max_tokens=220,
            )
            content = response.choices[0].message.content or ""
            return self._parse_response(content)
        except Exception as exc:
            logger.error("Error invoking LLM: %s", exc)
            return self._safe_fallback("LLM analysis failed; leaving incident open for analyst review.")

    def _parse_response(self, content: str) -> Dict[str, str]:
        """Parse and validate the model response, with safe fallbacks."""
        if not content or not content.strip():
            logger.warning("LLM returned empty content")
            return self._safe_fallback("LLM returned no usable analysis; leaving incident open.")

        parsed: Dict[str, Any] | None = None
        try:
            parsed = json.loads(content)
        except json.JSONDecodeError:
            match = re.search(r"\{.*\}", content, flags=re.DOTALL)
            if match:
                try:
                    parsed = json.loads(match.group(0))
                except json.JSONDecodeError:
                    parsed = None

        if not isinstance(parsed, dict):
            logger.warning("LLM returned non-JSON or invalid JSON content")
            return self._safe_fallback("LLM response could not be parsed safely; leaving incident open.")

        recommended_status = str(parsed.get("recommended_status", "Active")).strip().title()
        classification = str(parsed.get("classification", "Unspecified")).strip()
        comment = str(parsed.get("comment", "")).strip()

        if recommended_status not in _ALLOWED_STATUSES:
            logger.warning("Invalid recommended_status from LLM: %s", recommended_status)
            recommended_status = "Active"

        if classification not in _ALLOWED_CLASSIFICATIONS:
            logger.warning("Invalid classification from LLM: %s", classification)
            classification = "Unspecified"

        if not comment:
            comment = "No analyst-facing explanation was provided by the LLM."

        return {
            "recommended_status": recommended_status,
            "classification": classification,
            "comment": comment,
        }

    @staticmethod
    def _safe_fallback(comment: str) -> Dict[str, str]:
        return {
            "recommended_status": "Active",
            "classification": "Unspecified",
            "comment": comment,
        }
