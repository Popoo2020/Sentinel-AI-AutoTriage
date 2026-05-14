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
- deterministic write policy checks can still block an update in write mode
- closure recommendations require explicit human approval before update
- metadata-only JSONL audit records are appended for each processed decision
"""
from __future__ import annotations

import logging
import os
from pathlib import Path

from azure.mgmt.securityinsight.models import IncidentStatus
from dotenv import load_dotenv

from .approval import build_approval_decision
from .audit import append_audit_record, build_audit_record
from .llm_client import LLMClient
from .models import IncidentSummary
from .recommendation_policy import evaluate_write_recommendation
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


def approval_token() -> str | None:
    """Return the optional local approval token for controlled write demos."""
    raw = os.getenv("TRIAGE_APPROVAL_TOKEN")
    return raw.strip() if raw and raw.strip() else None


def approver_identity() -> str | None:
    """Return the optional approver identity label for audit metadata."""
    raw = os.getenv("TRIAGE_APPROVER")
    return raw.strip() if raw and raw.strip() else None


def audit_log_path() -> Path:
    """Return the metadata-only JSONL audit log path."""
    raw = os.getenv("TRIAGE_AUDIT_LOG_PATH", "logs/triage_audit.jsonl").strip()
    return Path(raw or "logs/triage_audit.jsonl")


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


def _append_decision_audit(
    *,
    summary: IncidentSummary,
    current_status: object,
    recommended_status: str,
    classification: str | None,
    write_mode: bool,
    policy_allowed: bool,
    policy_reason: str,
    approval_required: bool,
    approval_status: str,
    approved_by: str | None,
    applied_update: bool,
) -> None:
    """Append a metadata-only audit record without breaking triage on I/O failure."""
    record = build_audit_record(
        incident_id=summary.id,
        current_status=_status_text(current_status),
        recommended_status=recommended_status,
        classification=classification,
        write_mode=write_mode,
        policy_allowed=policy_allowed,
        policy_reason=policy_reason,
        approval_required=approval_required,
        approval_status=approval_status,
        approved_by=approved_by,
        applied_update=applied_update,
    )
    try:
        append_audit_record(audit_log_path(), record)
    except OSError as exc:
        logging.getLogger(__name__).warning(
            "Could not append triage audit record for incident %s: %s",
            summary.id,
            exc,
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
    verified through mocked update calls. Even with write mode enabled, a
    deterministic policy gate and an explicit approval state may still block a
    recommendation.
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

    approval = build_approval_decision(
        recommended_status=recommended_status,
        approval_token=approval_token(),
        approver=approver_identity(),
    )

    logger.info(
        "Recommendation for incident %s: status=%s classification=%s comment=%s",
        summary.id,
        recommended_status,
        classification,
        comment,
    )

    if _status_text(current_status) == _status_text(status_enum):
        reason = "No update required because the current status already matches the recommendation."
        logger.info("No status change recommended for incident %s", summary.id)
        _append_decision_audit(
            summary=summary,
            current_status=current_status,
            recommended_status=recommended_status,
            classification=classification,
            write_mode=write_mode,
            policy_allowed=True,
            policy_reason=reason,
            approval_required=approval.required,
            approval_status=approval.status,
            approved_by=approval.approved_by,
            applied_update=False,
        )
        return False

    write_policy = evaluate_write_recommendation(
        recommended_status=recommended_status,
        classification=classification,
        comment=comment,
    )
    if not write_policy.allowed:
        logger.info(
            "Deterministic write policy blocked incident %s recommendation: %s",
            summary.id,
            write_policy.reason,
        )
        _append_decision_audit(
            summary=summary,
            current_status=current_status,
            recommended_status=recommended_status,
            classification=classification,
            write_mode=write_mode,
            policy_allowed=False,
            policy_reason=write_policy.reason,
            approval_required=approval.required,
            approval_status=approval.status,
            approved_by=approval.approved_by,
            applied_update=False,
        )
        return False

    if approval.required and approval.status != "approved":
        logger.info(
            "Human approval blocked incident %s recommendation: %s",
            summary.id,
            approval.reason,
        )
        _append_decision_audit(
            summary=summary,
            current_status=current_status,
            recommended_status=recommended_status,
            classification=classification,
            write_mode=write_mode,
            policy_allowed=True,
            policy_reason=write_policy.reason,
            approval_required=True,
            approval_status=approval.status,
            approved_by=approval.approved_by,
            applied_update=False,
        )
        return False

    if not write_mode:
        logger.info(
            "Dry-run mode: would update incident %s to status %s with classification %s",
            summary.id,
            recommended_status,
            classification,
        )
        _append_decision_audit(
            summary=summary,
            current_status=current_status,
            recommended_status=recommended_status,
            classification=classification,
            write_mode=False,
            policy_allowed=True,
            policy_reason=write_policy.reason,
            approval_required=approval.required,
            approval_status=approval.status,
            approved_by=approval.approved_by,
            applied_update=False,
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
    _append_decision_audit(
        summary=summary,
        current_status=current_status,
        recommended_status=recommended_status,
        classification=classification,
        write_mode=True,
        policy_allowed=True,
        policy_reason=write_policy.reason,
        approval_required=approval.required,
        approval_status=approval.status,
        approved_by=approval.approved_by,
        applied_update=True,
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
