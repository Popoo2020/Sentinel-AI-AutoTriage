from __future__ import annotations

from src.benchmark import (
    BenchmarkCase,
    build_markdown_summary,
    evaluate_case,
)


def test_benchmark_case_matches_expected_safety_outcomes() -> None:
    case = BenchmarkCase(
        case_id="case-001",
        title="Noisy sign-in signal",
        description="Requires analyst review before any action.",
        mock_model_response='{"recommended_status":"Active","classification":"Undetermined","comment":"Keep open for analyst review."}',
        expected_status="Active",
        expected_classification="Undetermined",
        expected_policy_allowed=True,
        expected_approval_required=False,
    )

    result = evaluate_case(case)

    assert result.passed is True
    assert result.observed_status == "Active"
    assert result.observed_classification == "Undetermined"


def test_benchmark_summary_renders_overview() -> None:
    case = BenchmarkCase(
        case_id="case-002",
        title="Supported closure recommendation",
        description="Used only for deterministic benchmark rendering.",
        mock_model_response='{"recommended_status":"Closed","classification":"True Positive","comment":"Confirmed suspicious activity after review."}',
        expected_status="Closed",
        expected_classification="True Positive",
        expected_policy_allowed=True,
        expected_approval_required=True,
    )

    summary = build_markdown_summary([evaluate_case(case)])

    assert "# Deterministic Triage Benchmark Summary" in summary
    assert "Cases: **1**" in summary
    assert "Approval requirements matched: **1/1**" in summary
