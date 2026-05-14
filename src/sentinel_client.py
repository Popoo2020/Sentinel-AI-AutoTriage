"""
sentinel_client.py
------------------

Microsoft Sentinel SDK wrapper used by Sentinel-AI-AutoTriage.

The module intentionally keeps the Azure integration small and inspectable:
- authenticate with DefaultAzureCredential
- list active/new incidents
- update an incident only when the higher-level workflow explicitly allows it

No secrets are hard-coded in this module. Runtime configuration is provided via
environment variables and Azure identity mechanisms.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass

from azure.identity import DefaultAzureCredential
from azure.mgmt.securityinsight import SecurityInsights
from azure.mgmt.securityinsight.models import Incident, IncidentStatus

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class SentinelConfig:
    """Azure identifiers required to access a Sentinel workspace."""

    subscription_id: str
    resource_group: str
    workspace_name: str


def get_credential() -> DefaultAzureCredential:
    """Return a validated DefaultAzureCredential instance."""
    try:
        credential = DefaultAzureCredential()
        credential.get_token("https://management.azure.com/.default")
        logger.debug("Validated Azure credentials using DefaultAzureCredential")
        return credential
    except Exception as exc:
        logger.error("Failed to obtain Azure credentials: %s", exc)
        raise


def get_sentinel_client(config: SentinelConfig) -> SecurityInsights:
    """Initialise a SecurityInsights client for Microsoft Sentinel."""
    credential = get_credential()
    return SecurityInsights(credential, config.subscription_id)


def list_active_incidents(client: SecurityInsights, config: SentinelConfig) -> list[Incident]:
    """Fetch incidents whose Sentinel status is New or Active."""
    incidents: list[Incident] = []
    try:
        pager = client.incidents.list(
            resource_group_name=config.resource_group,
            workspace_name=config.workspace_name,
        )
        for incident in pager:
            properties = getattr(incident, "properties", None)
            status = getattr(properties, "status", None)
            if status in {IncidentStatus.NEW, IncidentStatus.ACTIVE}:
                incidents.append(incident)
        logger.info("Fetched %d active/new incidents", len(incidents))
        return incidents
    except Exception as exc:
        logger.error("Error listing incidents: %s", exc)
        return []


def update_incident_status(
    client: SecurityInsights,
    config: SentinelConfig,
    incident: Incident,
    status: IncidentStatus,
    classification: str | None = None,
    comment: str | None = None,
) -> None:
    """Update incident status and optional closure metadata.

    This function is deliberately narrow.  It is intended to be called only by
    the explicit write path in ``auto_triage.py`` after the dry-run/write gate has
    already been evaluated.
    """
    try:
        current = client.incidents.get(
            resource_group_name=config.resource_group,
            workspace_name=config.workspace_name,
            incident_id=incident.name,
        )
        if not current:
            logger.warning("Incident %s not found", incident.name)
            return

        properties = getattr(current, "properties", None)
        if properties is None:
            logger.warning("Incident %s has no properties and cannot be updated", incident.name)
            return

        properties.status = status
        if classification:
            properties.classification = classification
        if comment:
            properties.classification_comment = comment

        client.incidents.create_or_update(
            resource_group_name=config.resource_group,
            workspace_name=config.workspace_name,
            incident_id=current.name,
            incident=current,
        )
        logger.info(
            "Updated incident %s to status %s with classification %s",
            incident.name,
            status,
            classification,
        )
    except Exception as exc:
        logger.error("Error updating incident %s: %s", incident.name, exc)
