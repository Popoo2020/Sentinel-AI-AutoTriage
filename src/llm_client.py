"""
llm_client.py
-------------

This module provides an abstraction over different large‑language model providers.
By default it integrates with the OpenAI API. You can extend or replace this
implementation to use LangChain or other providers. API keys are read from
environment variables; no secrets are stored in code.
"""
from __future__ import annotations

import logging
import os
from typing import Dict, Optional

try:
    import openai  # type: ignore
except ImportError:
    openai = None  # openai is optional

logger = logging.getLogger(__name__)


class LLMClient:
    """Simple wrapper for interacting with an LLM service (OpenAI by default)."""

    def __init__(self, model_name: str = "gpt-4", temperature: float = 0.2) -> None:
        self.model_name = model_name
        self.temperature = temperature
        api_key = os.getenv("OPENAI_API_KEY")
        if openai is None:
            raise ImportError(
                "openai package is not installed. Install openai or implement a different provider."
            )
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable is not set")
        openai.api_key = api_key

    def analyse_incident(self, incident_title: str, incident_description: str) -> Dict[str, str]:
        """Send incident data to the LLM and return structured recommendations.

        The model is prompted to decide whether an incident is benign, false
        positive or malicious and suggest whether to close it.

        Returns a dictionary with keys: `recommended_status`, `classification`,
        and `comment`.
        """
        prompt = (
            "You are a cybersecurity analyst. A SIEM incident has the following title"
            f" and description:\nTitle: {incident_title}\nDescription: {incident_description}\n"
            "Provide a recommended incident status (New, Active or Closed), a brief classification (True Positive, False Positive"
            ", or Benign) and a one‑sentence comment explaining your decision."
        )
        try:
            response = openai.ChatCompletion.create(
                model=self.model_name,
                messages=[{"role": "user", "content": prompt}],
                temperature=self.temperature,
                max_tokens=200,
            )
            content = response.choices[0].message["content"]  # type: ignore
            # Parse simple structured output expected as comma‑separated values
            recommended_status = "Active"
            classification = ""
            comment = content.strip()
            # Naïve parsing – you can implement JSON output parsing for reliability
            return {
                "recommended_status": recommended_status,
                "classification": classification,
                "comment": comment,
            }
        except Exception as exc:
            logger.error("Error invoking LLM: %s", exc)
            # Default to leaving the incident active
            return {
                "recommended_status": "Active",
                "classification": "Unspecified",
                "comment": "LLM analysis failed; leaving incident open.",
            }
