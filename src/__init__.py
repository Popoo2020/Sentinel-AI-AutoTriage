"""Public package surface for Sentinel-AI-AutoTriage."""
from .approval import (
    ApprovalDecision,
    approval_required_for_recommendation,
    build_approval_decision,
)
from .audit import TriageAuditRecord, append_audit_record, build_audit_record
from .llm_client import LLMClient
from .models import IncidentSummary
from .providers import CompletionProvider, StaticMockProvider
from .recommendation_policy import WritePolicyDecision, evaluate_write_recommendation
from .redaction import RedactionResult, redact_text
from .sentinel_client import (
    SentinelConfig,
    get_sentinel_client,
    list_active_incidents,
    update_incident_status,
)

__all__ = [
    "ApprovalDecision",
    "CompletionProvider",
    "IncidentSummary",
    "LLMClient",
    "RedactionResult",
    "SentinelConfig",
    "StaticMockProvider",
    "TriageAuditRecord",
    "WritePolicyDecision",
    "append_audit_record",
    "approval_required_for_recommendation",
    "build_approval_decision",
    "build_audit_record",
    "evaluate_write_recommendation",
    "get_sentinel_client",
    "list_active_incidents",
    "redact_text",
    "update_incident_status",
]
