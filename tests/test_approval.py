from __future__ import annotations

from src.approval import (
    approval_required_for_recommendation,
    build_approval_decision,
)


def test_non_closure_recommendation_does_not_require_approval() -> None:
    assert approval_required_for_recommendation("Active") is False
    decision = build_approval_decision(recommended_status="Active")

    assert decision.required is False
    assert decision.status == "not_required"
    assert decision.approved_by is None


def test_closure_recommendation_requires_approval_by_default() -> None:
    assert approval_required_for_recommendation("Closed") is True
    decision = build_approval_decision(recommended_status="Closed")

    assert decision.required is True
    assert decision.status == "pending"
    assert "requires explicit human approval" in decision.reason


def test_closure_recommendation_can_be_explicitly_approved() -> None:
    decision = build_approval_decision(
        recommended_status="Closed",
        approval_token="1",
        approver="security-manager",
    )

    assert decision.required is True
    assert decision.status == "approved"
    assert decision.approved_by == "security-manager"
    assert decision.approved_at
