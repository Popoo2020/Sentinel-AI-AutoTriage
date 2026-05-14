"""Structured, metadata-only audit records for triage decisions.

The audit trail intentionally avoids incident titles, descriptions and raw prompt
content.  It captures only the decision metadata needed to understand what the
workflow recommended, whether deterministic policy allowed it, and whether an
update was actually applied.
"""
from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path


@dataclass(frozen=True)
class TriageAuditRecord:
    """Metadata-only audit record for one incident-processing decision."""

    timestamp: str
    incident_id: str
    current_status: str
    recommended_status: str
    classification: str | None
    write_mode: bool
    policy_allowed: bool
    policy_reason: str
    applied_update: bool


def build_audit_record(
    *,
    incident_id: str,
    current_status: str,
    recommended_status: str,
    classification: str | None,
    write_mode: bool,
    policy_allowed: bool,
    policy_reason: str,
    applied_update: bool,
) -> TriageAuditRecord:
    """Create a timestamped metadata-only audit record."""
    return TriageAuditRecord(
        timestamp=datetime.now(UTC).isoformat(),
        incident_id=incident_id,
        current_status=current_status,
        recommended_status=recommended_status,
        classification=classification,
        write_mode=write_mode,
        policy_allowed=policy_allowed,
        policy_reason=policy_reason,
        applied_update=applied_update,
    )


def append_audit_record(path: Path, record: TriageAuditRecord) -> None:
    """Append one JSONL audit record to ``path``."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(asdict(record), sort_keys=True) + "\n")
