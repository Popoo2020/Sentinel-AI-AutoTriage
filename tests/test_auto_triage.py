from __future__ import annotations

import logging
from types import SimpleNamespace

from azure.mgmt.securityinsight.models import IncidentStatus

from src.auto_triage import (
    auto_apply_changes_enabled,
    build_summary,
    map_status,
    process_incident,
)
from src.sentinel_client import SentinelConfig


def _incident(*, status: object = IncidentStatus.NEW) -> SimpleNamespace:
    return SimpleNamespace(
        name="incident-001",
        properties=SimpleNamespace(
            title="Impossible travel sign-in",
            description="Sign-in anomaly requiring analyst review.",
            severity=SimpleNamespace(name="High"),
            status=status,
        ),
    )


class FakeLLMClient:
    def __init__(self, recommendation: dict[str, str]) -> None:
        self.recommendation = recommendation

    def analyse_incident(self, _title: str, _description: str) -> dict[str, str]:
        return self.recommendation


def test_auto_apply_changes_enabled_is_false_by_default(monkeypatch) -> None:
    monkeypatch.delenv("AUTO_APPLY_CHANGES", raising=False)
    assert auto_apply_changes_enabled() is False


def test_auto_apply_changes_enabled_accepts_explicit_true(monkeypatch) -> None:
    monkeypatch.setenv("AUTO_APPLY_CHANGES", "true")
    assert auto_apply_changes_enabled() is True


def test_map_status_handles_expected_values() -> None:
    assert map_status("Closed") == IncidentStatus.CLOSED
    assert map_status("New") == IncidentStatus.NEW
    assert map_status("Active") == IncidentStatus.ACTIVE
    assert map_status("unexpected") == IncidentStatus.ACTIVE


def test_build_summary_handles_sdk_like_incident() -> None:
    summary = build_summary(_incident())

    assert summary.id == "incident-001"
    assert summary.title == "Impossible travel sign-in"
    assert summary.description == "Sign-in anomaly requiring analyst review."
    assert summary.severity == "High"
    assert summary.status == IncidentStatus.NEW.name


def test_process_incident_dry_run_does_not_apply_update(monkeypatch) -> None:
    called = {"updated": False}

    def fake_update(*_args, **_kwargs) -> None:
        called["updated"] = True

    monkeypatch.setattr("src.auto_triage.update_incident_status", fake_update)

    applied = process_incident(
        incident=_incident(status=IncidentStatus.NEW),
        llm_client=FakeLLMClient(
            {
                "recommended_status": "Closed",
                "classification": "True Positive",
                "comment": "Verified malicious activity.",
            }
        ),
        sentinel_client=object(),
        config=SentinelConfig("sub", "rg", "workspace"),
        write_mode=False,
        logger=logging.getLogger("test.dry_run"),
    )

    assert applied is False
    assert called["updated"] is False


def test_process_incident_write_mode_applies_update(monkeypatch) -> None:
    captured: dict[str, object] = {}

    def fake_update(_client, _config, incident, *, status, classification, comment) -> None:
        captured["incident"] = incident.name
        captured["status"] = status
        captured["classification"] = classification
        captured["comment"] = comment

    monkeypatch.setattr("src.auto_triage.update_incident_status", fake_update)

    applied = process_incident(
        incident=_incident(status=IncidentStatus.NEW),
        llm_client=FakeLLMClient(
            {
                "recommended_status": "Closed",
                "classification": "True Positive",
                "comment": "Verified malicious activity.",
            }
        ),
        sentinel_client=object(),
        config=SentinelConfig("sub", "rg", "workspace"),
        write_mode=True,
        logger=logging.getLogger("test.write_mode"),
    )

    assert applied is True
    assert captured == {
        "incident": "incident-001",
        "status": IncidentStatus.CLOSED,
        "classification": "True Positive",
        "comment": "Verified malicious activity.",
    }


def test_process_incident_does_not_update_when_status_is_unchanged(monkeypatch) -> None:
    called = {"updated": False}

    def fake_update(*_args, **_kwargs) -> None:
        called["updated"] = True

    monkeypatch.setattr("src.auto_triage.update_incident_status", fake_update)

    applied = process_incident(
        incident=_incident(status=IncidentStatus.ACTIVE),
        llm_client=FakeLLMClient(
            {
                "recommended_status": "Active",
                "classification": "Undetermined",
                "comment": "Keep open for review.",
            }
        ),
        sentinel_client=object(),
        config=SentinelConfig("sub", "rg", "workspace"),
        write_mode=True,
        logger=logging.getLogger("test.no_change"),
    )

    assert applied is False
    assert called["updated"] is False


def test_process_incident_does_not_update_when_sdk_returns_string_status(monkeypatch) -> None:
    called = {"updated": False}

    def fake_update(*_args, **_kwargs) -> None:
        called["updated"] = True

    monkeypatch.setattr("src.auto_triage.update_incident_status", fake_update)

    applied = process_incident(
        incident=_incident(status="Active"),
        llm_client=FakeLLMClient(
            {
                "recommended_status": "Active",
                "classification": "Undetermined",
                "comment": "Keep open for review.",
            }
        ),
        sentinel_client=object(),
        config=SentinelConfig("sub", "rg", "workspace"),
        write_mode=True,
        logger=logging.getLogger("test.string_status"),
    )

    assert applied is False
    assert called["updated"] is False
