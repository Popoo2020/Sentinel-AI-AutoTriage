from src.recommendation_policy import evaluate_write_recommendation


def test_non_closure_recommendation_passes_policy() -> None:
    decision = evaluate_write_recommendation(
        recommended_status="Active",
        classification="Undetermined",
        comment="Keep the incident open for analyst review.",
    )

    assert decision.allowed is True
    assert "Non-closure" in decision.reason


def test_closure_is_blocked_without_supported_classification() -> None:
    decision = evaluate_write_recommendation(
        recommended_status="Closed",
        classification="Undetermined",
        comment="The incident looks low-risk, but the classification is not closure-ready.",
    )

    assert decision.allowed is False
    assert "classification" in decision.reason.lower()


def test_closure_is_blocked_when_comment_is_too_short() -> None:
    decision = evaluate_write_recommendation(
        recommended_status="Closed",
        classification="True Positive",
        comment="Confirmed.",
    )

    assert decision.allowed is False
    assert "too short" in decision.reason.lower()


def test_closure_passes_with_supported_classification_and_comment() -> None:
    decision = evaluate_write_recommendation(
        recommended_status="Closed",
        classification="True Positive",
        comment="Confirmed malicious activity after correlation with additional telemetry.",
    )

    assert decision.allowed is True
    assert "passed" in decision.reason.lower()
