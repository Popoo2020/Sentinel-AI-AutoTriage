"""Human-approval primitives for sensitive triage actions.

The project remains dry-run-first, but it can now model a separate human approval
state before a sensitive recommendation is allowed to reach the Sentinel update
path.  The approval object is intentionally small and metadata-only.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Literal

ApprovalStatus = Literal["not_required", "pending", "approved", "rejected"]


@dataclass(frozen=True)
class ApprovalDecision:
    """Approval state for a proposed state-changing action."""

    required: bool
    status: ApprovalStatus
    reason: str
    approved_by: str | None = None
    approved_at: str | None = None


def approval_required_for_recommendation(recommended_status: str) -> bool:
    """Require human approval for closure recommendations."""
    return recommended_status.strip().title() == "Closed"


def build_approval_decision(
    *,
    recommended_status: str,
    approval_token: str | None = None,
    approver: str | None = None,
) -> ApprovalDecision:
    """Return a metadata-only approval decision.

    The current prototype treats a non-empty approval token as an explicit local
    approval signal.  A production implementation would replace this with a
    durable ticket, analyst queue or signed workflow approval.
    """
    if not approval_required_for_recommendation(recommended_status):
        return ApprovalDecision(
            required=False,
            status="not_required",
            reason="Human approval is not required for non-closure recommendations.",
        )

    if approval_token and approval_token.strip():
        return ApprovalDecision(
            required=True,
            status="approved",
            reason="Explicit approval token supplied for a closure recommendation.",
            approved_by=(approver or "local-approver").strip() or "local-approver",
            approved_at=datetime.now(UTC).isoformat(),
        )

    return ApprovalDecision(
        required=True,
        status="pending",
        reason="Closure recommendation requires explicit human approval.",
    )
