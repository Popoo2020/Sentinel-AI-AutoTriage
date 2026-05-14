"""
auto_triage.py
---------------

Entry point for the Sentinel-AI-AutoTriage framework. This script loads
configuration from environment variables, initialises the Sentinel client and
LLM client, fetches incidents and applies LLM-assisted triage to each. Logging
is configured to output to both the console and a file in the `logs/` directory.

Safety model:
- `AUTO_APPLY_CHANGES=false` by default
- recommendations are logged in dry-run mode
- incident updates are only written when explicitly enabled
"""
from __future__ import annotations

import logging
import os
from pathlib import Path

from azure.mgmt.securityinsight.models import IncidentStatus
from dotenv import load_dotenv

from .llm_client import LLMClient
from .models import IncidentSummary
from .sentinel_client import (
    SentinelConfig,
    get_sentinel_client,
    list_active_incidents,
    update_incident_status,
)


def configure_logging() -> None:
    """Configure logging for console and file outputs."""
    logs_dir = Path(__file__).resolve().parent.parent / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)
    log_file = logs_dir / "auto_triage.log"

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(log_file),
        ],
    )


def load_config() -> SentinelConfig:
    """Load Sentinel configuration from environment variables."""
    subscription_id = os.environ.get("SUBSCRIPTION_ID")
    resource_group = os.environ.get("RESOURCE_GROUP")
    workspace_name = os.environ.get("WORKSPACE_NAME")
    if not (subscription_id and resource_group and workspace_name):
        raise EnvironmentError(
            "SUBSCRIPTION_ID, RESOURCE_GROUP and WORKSPACE_NAME environment variables must be set"
        )
    return SentinelConfig(subscription_id, resource_group, workspace_name)


def auto_apply_changes_enabled() -> bool:
    """Return True only when explicit write mode has been enabled."""
    return os.getenv("AUTO_APPLY_CHANGES", "false").strip().lower() in {
        "1",
        "true",
        "yes",
        "on",
    }


def map_status(recommended_status: str) -> IncidentStatus:
    """Map validated status text to the Sentinel IncidentStatus enum."""
    normalized = recommended_status.strip().lower()
    if normalized == "closed":
        return IncidentStatus.CLOSED
    if normalized == "new":
        return IncidentStatus.NEW
    return IncidentStatus.ACTIVE


def _status_text(status: object) -> str:
    """Normalise enum/string status values into lower-case text."""
    name = getattr(status, "name", None)
    if name:
        return str(name).lower()
    value = getattr(status, "value", status)
    return str(value).split(".")[-1].lower()


def build_summary(incident: object) -> IncidentSummary:
    """Convert a Sentinel SDK incident into the compact LLM-facing summary."""
    properties = getattr(incident, "properties", None)
    severity = getattr(properties, "severity", None)
    status = getattr(properties, "status", None)
    severity_label = getattr(severity, "name", None) or str(severity or "Unknown")
    status_label = getattr(status, "name", None) or str(status or "Unknown")

    return IncidentSummary(
        id=str(getattr(incident, "name", "unknown-incident")),
        title=getattr(properties, "title", None) or "(no title)",
        description=getattr(properties, "description", None) or "(no description)",
        severity=severity_label,
        status=status_label,
    )


def process_incident(
    *,
    incident: object,
    llm_client: LLMClient,
    sentinel_client: object,
    config: SentinelConfig,
    write_mode: bool,
    logger: logging.Logger,
) -> bool:
    """Process one incident and return True when an update is applied.

    Returning a boolean makes the safety behaviour testable: dry-run processing
    can be asserted without contacting Azure, while explicit write mode can be
    verified through mocked update calls.
    """
    summary = build_summary(incident)
    logger.info("Processing incident %s", summary.id)

    properties = getattr(incident, "properties", None)
    current_status = getattr(properties, "status", None)

    result = llm_client.analyse_incident(summary.title, summary.description)
    recommended_status = result.get("recommended_status", "Active")
    classification = result.get("classification") or None
    comment = result.get("comment") or None
    status_enum = map_status(recommended_status)

    logger.info(
        "Recommendation for incident %s: status=%s classification=%s comment=%s",
        summary.id,
        recommended_status,
        classification,
        comment,
    )

    if _status_text(current_status) == _status_text(status_enum):
        logger.info("No status change recommended for incident %s", summary.id)
        return False

    if not write_mode:
        logger.info(
            "Dry-run mode: would update incident %s to status %s with classification %s",
            summary.id,
            recommended_status,
            classification,
        )
        return False

    update_incident_status(
        sentinel_client,
        config,
        incident,
        status=status_enum,
        classification=classification,
        comment=comment,
    )
    return True


def run_triage() -> None:
    """Main function to perform LLM-assisted triage on Sentinel incidents."""
    configure_logging()
    load_dotenv()
    logger = logging.getLogger(__name__)
    config = load_config()
    write_mode = auto_apply_changes_enabled()

    logger.info(
        "Starting Sentinel-AI-AutoTriage in %s mode",
        "write" if write_mode else "dry-run",
    )

    sentinel_client = get_sentinel_client(config)
    try:
        llm_client = LLMClient(model_name=os.getenv("LLM_MODEL", "gpt-4o-mini"))
    except Exception as exc:
        logger.error("LLM client could not be initialised: %s", exc)
        return

    incidents = list_active_incidents(sentinel_client, config)
    logger.info("Processing %d active/new incidents", len(incidents))

    updates_applied = 0
    for incident in incidents:
        if process_incident(
            incident=incident,
            llm_client=llm_client,
            sentinel_client=sentinel_client,
            config=config,
            write_mode=write_mode,
            logger=logger,
        ):
            updates_applied += 1

    logger.info("Triage run completed; applied_updates=%d", updates_applied)


if __name__ == "__main__":
    try:
        run_triage()
    except Exception as general_exc:
        logging.getLogger(__name__).exception(
            "Unhandled exception in triage script: %s", general_exc
        )
