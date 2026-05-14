"""Deterministic write-policy checks for Sentinel triage recommendations.

Model output is treated as input to policy, not as an authority by itself.  This
module blocks write actions that are insufficiently specific or that would close
an incident without a meaningful analyst-facing explanation.
"""
from __future__ import annotations

from dataclasses import dataclass

_ALLOWED_CLASSIFICATIONS_FOR_CLOSURE = {
    "True Positive",
    "False Positive",
    "Benign Positive",
}


@dataclass(frozen=True)
class WritePolicyDecision:
    """Decision returned before a recommendation is written to Sentinel."""

    allowed: bool
    reason: str


def evaluate_write_recommendation(
    *,
    recommended_status: str,
    classification: str | None,
    comment: str | None,
) -> WritePolicyDecision:
    """Return whether a model recommendation is safe enough to write.

    The policy is intentionally conservative:
    - non-closure status updates are allowed after the external write gate is enabled,
    - closure recommendations require a meaningful closure classification,
    - closure recommendations require an analyst-facing comment with sufficient detail.
    """
    status = recommended_status.strip().title()
    classification_value = (classification or "").strip()
    comment_value = (comment or "").strip()

    if status != "Closed":
        return WritePolicyDecision(
            allowed=True,
            reason="Non-closure status recommendation passed deterministic write policy.",
        )

    if classification_value not in _ALLOWED_CLASSIFICATIONS_FOR_CLOSURE:
        return WritePolicyDecision(
            allowed=False,
            reason="Closure blocked: classification is missing, ambiguous or unsupported.",
        )

    if len(comment_value) < 20:
        return WritePolicyDecision(
            allowed=False,
            reason="Closure blocked: analyst-facing justification is too short.",
        )

    return WritePolicyDecision(
        allowed=True,
        reason="Closure recommendation passed deterministic classification and comment checks.",
    )
