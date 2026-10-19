"""Offline adapter regressions using real Azure SDK models and mocked SDK operations."""
from __future__ import annotations

import json
import logging
from types import SimpleNamespace

import pytest
from azure.mgmt.securityinsight.models import Incident, IncidentSeverity, IncidentStatus

from src.auto_triage import build_summary, process_incident
from src.sentinel_client import SentinelConfig, list_active_incidents, update_incident_status


def sdk_incident(status: IncidentStatus = IncidentStatus.NEW) -> Incident:
    incident = Incident(
        title="Synthetic incident",
        description="Synthetic description for adapter verification.",
        severity=IncidentSeverity.HIGH,
        status=status,
    )
    # The service normally supplies this read-only response field.
    incident.name = "synthetic-001"
    return incident


def test_sdk_model_fields_survive_summary_and_active_filter() -> None:
    incident = sdk_incident()
    closed = sdk_incident(IncidentStatus.CLOSED)
    client = SimpleNamespace(incidents=SimpleNamespace(list=lambda **_: [incident, closed]))
    config = SentinelConfig("sub", "rg", "workspace")

    assert list_active_incidents(client, config) == [incident]
    summary = build_summary(incident)
    assert summary.id == "synthetic-001"
    assert summary.title == incident.title
    assert summary.description == incident.description
    assert summary.status == IncidentStatus.NEW.name
    assert summary.severity == IncidentSeverity.HIGH.name


def test_sdk_model_update_uses_supported_classification_values() -> None:
    incident = sdk_incident()
    captured: dict[str, object] = {}

    def write(**kwargs):
        captured.update(kwargs)
        return kwargs["incident"]

    client = SimpleNamespace(
        incidents=SimpleNamespace(get=lambda **_: incident, create_or_update=write)
    )
    result = update_incident_status(
        client, SentinelConfig("sub", "rg", "workspace"), incident,
        IncidentStatus.CLOSED, "True Positive", "Reviewed by an analyst.",
    )

    assert result is True
    assert captured["incident"] is incident
    assert incident.as_dict()["status"] == "Closed"
    assert incident.as_dict()["classification"] == "TruePositive"
    assert incident.classification_comment == "Reviewed by an analyst."


@pytest.mark.parametrize("write_succeeds", [False, True])
def test_sdk_write_outcome_matches_return_value_and_audit(
    monkeypatch, tmp_path, caplog, write_succeeds: bool,
) -> None:
    incident = sdk_incident()
    audit_path = tmp_path / "audit.jsonl"
    monkeypatch.setenv("TRIAGE_AUDIT_LOG_PATH", str(audit_path))
    monkeypatch.delenv("TRIAGE_APPROVAL_TOKEN", raising=False)
    monkeypatch.delenv("TRIAGE_APPROVER", raising=False)

    def write(**_):
        if not write_succeeds:
            raise RuntimeError("synthetic error containing token=do-not-log-this")
        return incident

    client = SimpleNamespace(
        incidents=SimpleNamespace(get=lambda **_: incident, create_or_update=write)
    )
    llm = SimpleNamespace(analyse_incident=lambda *_: {
        "recommended_status": "Active",
        "classification": "Undetermined",
        "comment": "Keep open; token=private-model-output analyst@example.com",
    })
    with caplog.at_level(logging.INFO):
        applied = process_incident(
            incident=incident, llm_client=llm, sentinel_client=client,
            config=SentinelConfig("sub", "rg", "workspace"), write_mode=True,
            logger=logging.getLogger("test.sdk_transport"),
        )

    assert applied is write_succeeds
    record = json.loads(audit_path.read_text())
    assert record["applied_update"] is write_succeeds
    assert record["current_status"] == "new"
    assert "private-model-output" not in caplog.text
    assert "analyst@example.com" not in caplog.text
    assert "do-not-log-this" not in caplog.text


def test_sdk_unchanged_status_does_not_write(monkeypatch, tmp_path) -> None:
    incident = sdk_incident(IncidentStatus.ACTIVE)
    monkeypatch.setenv("TRIAGE_AUDIT_LOG_PATH", str(tmp_path / "audit.jsonl"))
    llm = SimpleNamespace(analyse_incident=lambda *_: {
        "recommended_status": "Active", "classification": "Undetermined",
        "comment": "Continue the existing investigation.",
    })
    # No SDK operations are available: an unnecessary write would raise.
    applied = process_incident(
        incident=incident, llm_client=llm, sentinel_client=object(),
        config=SentinelConfig("sub", "rg", "workspace"), write_mode=True,
        logger=logging.getLogger("test.sdk_unchanged"),
    )
    assert applied is False
