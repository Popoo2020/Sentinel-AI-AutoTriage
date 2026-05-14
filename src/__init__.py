"""Public package surface for Sentinel-AI-AutoTriage."""
from .llm_client import LLMClient
from .models import IncidentSummary
from .redaction import RedactionResult, redact_text
from .sentinel_client import (
    SentinelConfig,
    get_sentinel_client,
    list_active_incidents,
    update_incident_status,
)

__all__ = [
    "IncidentSummary",
    "LLMClient",
    "RedactionResult",
    "SentinelConfig",
    "get_sentinel_client",
    "list_active_incidents",
    "redact_text",
    "update_incident_status",
]
