from __future__ import annotations

import pytest

from src.auto_triage import load_config
from src.models import IncidentSummary


def test_load_config_reads_required_environment(monkeypatch) -> None:
    monkeypatch.setenv("SUBSCRIPTION_ID", "sub-123")
    monkeypatch.setenv("RESOURCE_GROUP", "rg-security")
    monkeypatch.setenv("WORKSPACE_NAME", "sentinel-workspace")

    config = load_config()

    assert config.subscription_id == "sub-123"
    assert config.resource_group == "rg-security"
    assert config.workspace_name == "sentinel-workspace"


def test_load_config_rejects_missing_required_environment(monkeypatch) -> None:
    monkeypatch.delenv("SUBSCRIPTION_ID", raising=False)
    monkeypatch.delenv("RESOURCE_GROUP", raising=False)
    monkeypatch.delenv("WORKSPACE_NAME", raising=False)

    with pytest.raises(EnvironmentError):
        load_config()


def test_incident_summary_renders_compact_prompt_fragment() -> None:
    summary = IncidentSummary(
        id="incident-123",
        title="Impossible travel sign-in",
        description="Risky authentication pattern detected.",
        severity="High",
        status="New",
    )

    assert summary.as_prompt() == (
        "[High] Impossible travel sign-in: Risky authentication pattern detected."
    )
