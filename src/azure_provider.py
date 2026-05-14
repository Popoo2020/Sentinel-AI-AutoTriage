"""Optional adapter skeleton for enterprise-hosted chat completions.

This module deliberately keeps the interface vendor-neutral.  It exists to show
where a managed enterprise provider can be attached without changing the triage
workflow or its safety controls.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class EnterpriseProviderConfig:
    """Configuration metadata for a future enterprise model-provider adapter."""

    endpoint: str
    deployment: str
    api_version: str


def provider_extension_note() -> str:
    """Explain the intended role of this adapter boundary."""
    return (
        "Attach an enterprise-hosted provider here while keeping the existing "
        "redaction, parsing, policy and audit layers unchanged."
    )
