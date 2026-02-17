"""
sentinel_client.py
-------------------

Wrapper around the Azure Security Insights (Microsoft Sentinel) SDK. Handles
authentication via DefaultAzureCredential and exposes helper methods for
listing and updating incidents. Environment variables are used for
configuration; no secrets are hard‑coded. This module embraces the
principle of least privilege by using token‑based authentication【987667603810256†L350-L394】.

"""
from __future__ import annotations

import logging
import os
from dataclasses import dataclass
from typing import Iterable, List

from azure.identity import DefaultAzureCredential, ClientSecretCredential
from azure.mgmt.securityinsight import SecurityInsights
from azure.mgmt.securityinsight.models import Incident, IncidentSeverity, IncidentStatus


logger = logging.getLogger(__name__)


@dataclass
class SentinelConfig:
    subscription_id: str
    resource_group: str
    workspace_name: str


def get_credential() -> DefaultAzureCredential:
    """Return a credential for authenticating to Azure.

    Uses DefaultAzureCredential, which automatically chooses between environment
    variables, managed identity, or developer credentials【987667603810256†L350-L365】. Service principal
    variables (AZURE_CLIENT_ID, AZURE_TENANT_ID, AZURE_CLIENT_SECRET) should be
    defined in the environment【987667603810256†L428-L433】.
    """
    try:
        credential = DefaultAzureCredential()
        # Attempt to get a token to validate credentials early
        credential.get_token("https://management.azure.com/.default")
        logger.debug("Obtained token using DefaultAzureCredential")
        return credential
    except Exception as exc:
        logger.error("Failed to obtain Azure credentials: %s", exc)
        raise


def get_sentinel_client(config: SentinelConfig) -> SecurityInsights:
    """Initialise a SecurityInsights client for Microsoft Sentinel."""
    credential = get_credential()
    client = SecurityInsights(credential, config.subscription_id)
    return client


def list_active_incidents(client: SecurityInsights, config: SentinelConfig) -> List[Incident]:
    """Fetch a list of active (New or Active) incidents from Microsoft Sentinel."""
    incidents: List[Incident] = []
    try:
        pager = client.incidents.list(
            resource_group_name=config.resource_group,
            workspace_name=config.workspace_name,
        )
        for incident in pager:
            if incident.properties and incident.properties.status in [IncidentStatus.NEW, IncidentStatus.ACTIVE]:
                incidents.append(incident)
        logger.info("Fetched %d active incidents", len(incidents))
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
    """Update the status of an incident and optionally add classification/comment.

    Microsoft Sentinel allows closing or updating incidents via the API. The
    underlying SDK uses the `Incident` model. This function retrieves the
    existing incident, modifies its status, adds classification data and
    submits the update.
    """
    try:
        # Retrieve the latest incident record
        current = client.incidents.get(
            resource_group_name=config.resource_group,
            workspace_name=config.workspace_name,
            incident_id=incident.name,
        )
        if not current:
            logger.warning("Incident %s not found", incident.name)
            return

        # Modify status and classification
        current.properties.status = status
        if classification:
            current.properties.classification = classification
        if comment:
            current.properties.classification_comment = comment

        # Update incident
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
