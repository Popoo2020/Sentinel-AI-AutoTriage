"""
auto_triage.py
---------------

Entry point for the Sentinel‑AI‑AutoTriage framework. This script loads
configuration from environment variables, initialises the Sentinel client and
LLM client, fetches incidents and applies AI‑based triage to each. Logging
is configured to output to both the console and a file in the `logs/` directory.

Before running, ensure that environment variables for Azure and OpenAI are set
either via a `.env` file or your shell environment. For more details see
README.md.
"""
from __future__ import annotations

import logging
import os
from pathlib import Path

from dotenv import load_dotenv

from .sentinel_client import SentinelConfig, get_sentinel_client, list_active_incidents, update_incident_status
from .llm_client import LLMClient
from .models import IncidentSummary
from azure.mgmt.securityinsight.models import IncidentStatus


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
    """Load configuration from environment variables."""
    subscription_id = os.environ.get("SUBSCRIPTION_ID")
    resource_group = os.environ.get("RESOURCE_GROUP")
    workspace_name = os.environ.get("WORKSPACE_NAME")
    if not (subscription_id and resource_group and workspace_name):
        raise EnvironmentError(
            "SUBSCRIPTION_ID, RESOURCE_GROUP and WORKSPACE_NAME environment variables must be set"
        )
    return SentinelConfig(subscription_id, resource_group, workspace_name)


def run_triage() -> None:
    """Main function to perform AI‑based triage on Sentinel incidents."""
    configure_logging()
    load_dotenv()  # optionally load variables from a .env file
    logger = logging.getLogger(__name__)
    config = load_config()

    # Initialise clients
    sentinel_client = get_sentinel_client(config)
    llm_client = None
    try:
        llm_client = LLMClient(model_name=os.getenv("LLM_MODEL", "gpt-4"))
    except Exception as exc:
        logger.error("LLM client could not be initialised: %s", exc)
        return

    incidents = list_active_incidents(sentinel_client, config)
    for inc in incidents:
        # Prepare summary for AI
        props = inc.properties
        summary = IncidentSummary(
            id=inc.name,
            title=props.title or "(no title)",
            description=props.description or "(no description)",
            severity=props.severity.name if props.severity else "Unknown",
            status=props.status.name if props.status else "Unknown",
        )
        logger.info("Processing incident %s", summary.id)
        result = llm_client.analyse_incident(summary.title, summary.description)
        recommended_status = result.get("recommended_status", "Active")
        classification = result.get("classification") or None
        comment = result.get("comment") or None

        # Map recommended status string to IncidentStatus enum
        status_enum = IncidentStatus.ACTIVE
        if recommended_status.lower().startswith("clos"):
            status_enum = IncidentStatus.CLOSED
        elif recommended_status.lower().startswith("new"):
            status_enum = IncidentStatus.NEW

        if status_enum != props.status:
            update_incident_status(
                sentinel_client,
                config,
                inc,
                status=status_enum,
                classification=classification,
                comment=comment,
            )
        else:
            logger.info("No status change for incident %s", summary.id)


if __name__ == "__main__":
    try:
        run_triage()
    except Exception as general_exc:
        logging.getLogger(__name__).exception("Unhandled exception in triage script: %s", general_exc)
