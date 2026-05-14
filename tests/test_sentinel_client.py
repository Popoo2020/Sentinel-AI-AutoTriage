from __future__ import annotations

from types import SimpleNamespace

from azure.mgmt.securityinsight.models import IncidentStatus

from src.sentinel_client import (
    SentinelConfig,
    list_active_incidents,
    update_incident_status,
)


def _incident(name: str, status: object) -> SimpleNamespace:
    return SimpleNamespace(
        name=name,
        properties=SimpleNamespace(
            status=status,
            classification=None,
            classification_comment=None,
        ),
    )


def test_list_active_incidents_filters_new_and_active_only() -> None:
    config = SentinelConfig("sub", "rg", "workspace")
    client = SimpleNamespace(
        incidents=SimpleNamespace(
            list=lambda **_kwargs: [
                _incident("incident-new", IncidentStatus.NEW),
                _incident("incident-active", IncidentStatus.ACTIVE),
                _incident("incident-closed", IncidentStatus.CLOSED),
            ]
        )
    )

    incidents = list_active_incidents(client, config)

    assert [incident.name for incident in incidents] == [
        "incident-new",
        "incident-active",
    ]


def test_list_active_incidents_accepts_string_status_values() -> None:
    config = SentinelConfig("sub", "rg", "workspace")
    client = SimpleNamespace(
        incidents=SimpleNamespace(
            list=lambda **_kwargs: [
                _incident("incident-new", "New"),
                _incident("incident-active", "Active"),
                _incident("incident-closed", "Closed"),
            ]
        )
    )

    incidents = list_active_incidents(client, config)

    assert [incident.name for incident in incidents] == [
        "incident-new",
        "incident-active",
    ]


def test_update_incident_status_mutates_and_submits_existing_incident() -> None:
    config = SentinelConfig("sub", "rg", "workspace")
    source_incident = _incident("incident-123", IncidentStatus.ACTIVE)
    current = _incident("incident-123", IncidentStatus.ACTIVE)
    captured: dict[str, object] = {}

    def fake_get(**_kwargs):
        return current

    def fake_create_or_update(**kwargs):
        captured.update(kwargs)

    client = SimpleNamespace(
        incidents=SimpleNamespace(
            get=fake_get,
            create_or_update=fake_create_or_update,
        )
    )

    update_incident_status(
        client,
        config,
        source_incident,
        status=IncidentStatus.CLOSED,
        classification="True Positive",
        comment="Confirmed malicious activity.",
    )

    assert current.properties.status == IncidentStatus.CLOSED
    assert current.properties.classification == "True Positive"
    assert current.properties.classification_comment == "Confirmed malicious activity."
    assert captured["incident_id"] == "incident-123"
    assert captured["incident"] is current


def test_update_incident_status_skips_missing_current_incident() -> None:
    config = SentinelConfig("sub", "rg", "workspace")
    source_incident = _incident("incident-404", IncidentStatus.ACTIVE)
    called = {"updated": False}

    def fake_create_or_update(**_kwargs):
        called["updated"] = True

    client = SimpleNamespace(
        incidents=SimpleNamespace(
            get=lambda **_kwargs: None,
            create_or_update=fake_create_or_update,
        )
    )

    update_incident_status(
        client,
        config,
        source_incident,
        status=IncidentStatus.CLOSED,
        classification="True Positive",
        comment="Should not be applied.",
    )

    assert called["updated"] is False
