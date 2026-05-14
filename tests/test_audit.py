from __future__ import annotations

import json

from src.audit import append_audit_record, build_audit_record


def test_build_audit_record_contains_metadata_only() -> None:
    record = build_audit_record(
        incident_id="incident-001",
        current_status="new",
        recommended_status="Active",
        classification="Undetermined",
        write_mode=False,
        policy_allowed=True,
        policy_reason="Non-closure status recommendation passed deterministic write policy.",
        applied_update=False,
    )

    assert record.incident_id == "incident-001"
    assert record.current_status == "new"
    assert record.recommended_status == "Active"
    assert record.classification == "Undetermined"
    assert record.write_mode is False
    assert record.policy_allowed is True
    assert record.applied_update is False
    assert record.timestamp


def test_append_audit_record_writes_jsonl_payload(tmp_path) -> None:
    record = build_audit_record(
        incident_id="incident-002",
        current_status="active",
        recommended_status="Closed",
        classification="True Positive",
        write_mode=True,
        policy_allowed=True,
        policy_reason="Closure recommendation passed deterministic classification and comment checks.",
        applied_update=True,
    )
    path = tmp_path / "triage_audit.jsonl"

    append_audit_record(path, record)

    payload = json.loads(path.read_text(encoding="utf-8").strip())
    assert payload["incident_id"] == "incident-002"
    assert payload["current_status"] == "active"
    assert payload["recommended_status"] == "Closed"
    assert payload["classification"] == "True Positive"
    assert payload["write_mode"] is True
    assert payload["policy_allowed"] is True
    assert payload["applied_update"] is True
    assert "title" not in payload
    assert "description" not in payload
    assert "prompt" not in payload
