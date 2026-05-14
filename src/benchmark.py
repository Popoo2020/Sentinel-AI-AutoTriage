"""Deterministic triage benchmark for the Sentinel-AI-AutoTriage prototype.

The benchmark is intentionally provider-independent: each case includes a mock
model response that is parsed by the production LLM client, then checked against
policy and approval expectations.  This measures whether the safety workflow
behaves as designed, not whether a live model is objectively correct.
"""
from __future__ import annotations

import json
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

from .approval import approval_required_for_recommendation
from .llm_client import LLMClient
from .providers import StaticMockProvider
from .recommendation_policy import evaluate_write_recommendation


@dataclass(frozen=True)
class BenchmarkCase:
    """One deterministic benchmark case with expected safety outcomes."""

    case_id: str
    title: str
    description: str
    mock_model_response: str
    expected_status: str
    expected_classification: str
    expected_policy_allowed: bool
    expected_approval_required: bool


@dataclass(frozen=True)
class BenchmarkResult:
    """Observed benchmark result for one case."""

    case_id: str
    status_match: bool
    classification_match: bool
    policy_match: bool
    approval_match: bool
    observed_status: str
    observed_classification: str
    observed_policy_allowed: bool
    observed_approval_required: bool

    @property
    def passed(self) -> bool:
        """Return whether all benchmark expectations matched."""
        return all(
            (
                self.status_match,
                self.classification_match,
                self.policy_match,
                self.approval_match,
            )
        )


def repo_root() -> Path:
    """Return repository root when executed as ``python -m src.benchmark``."""
    return Path(__file__).resolve().parent.parent


def load_cases(path: Path) -> list[BenchmarkCase]:
    """Load deterministic benchmark cases from JSON."""
    payload = json.loads(path.read_text(encoding="utf-8"))
    return [BenchmarkCase(**item) for item in payload]


def evaluate_case(case: BenchmarkCase) -> BenchmarkResult:
    """Evaluate one benchmark case through the production parsing/policy path."""
    llm_client = LLMClient(
        model_name="benchmark-mock",
        provider=StaticMockProvider(case.mock_model_response),
    )
    parsed = llm_client.analyse_incident(case.title, case.description)
    policy = evaluate_write_recommendation(
        recommended_status=parsed["recommended_status"],
        classification=parsed["classification"],
        comment=parsed["comment"],
    )
    approval_required = approval_required_for_recommendation(
        parsed["recommended_status"]
    )

    return BenchmarkResult(
        case_id=case.case_id,
        status_match=parsed["recommended_status"] == case.expected_status,
        classification_match=(
            parsed["classification"] == case.expected_classification
        ),
        policy_match=policy.allowed is case.expected_policy_allowed,
        approval_match=(
            approval_required is case.expected_approval_required
        ),
        observed_status=parsed["recommended_status"],
        observed_classification=parsed["classification"],
        observed_policy_allowed=policy.allowed,
        observed_approval_required=approval_required,
    )


def evaluate_cases(cases: list[BenchmarkCase]) -> list[BenchmarkResult]:
    """Evaluate all benchmark cases."""
    return [evaluate_case(case) for case in cases]


def build_markdown_summary(results: list[BenchmarkResult]) -> str:
    """Build a portfolio-friendly benchmark summary report."""
    counts = Counter("passed" if result.passed else "failed" for result in results)
    total = len(results)
    passed = counts.get("passed", 0)
    failed = counts.get("failed", 0)

    status_matches = sum(result.status_match for result in results)
    classification_matches = sum(result.classification_match for result in results)
    policy_matches = sum(result.policy_match for result in results)
    approval_matches = sum(result.approval_match for result in results)

    lines = [
        "# Deterministic Triage Benchmark Summary",
        "",
        "## Overview",
        "",
        f"- Cases: **{total}**",
        f"- Fully matched: **{passed}**",
        f"- Mismatched: **{failed}**",
        "",
        "## Dimension checks",
        "",
        f"- Status expectations matched: **{status_matches}/{total}**",
        f"- Classification expectations matched: **{classification_matches}/{total}**",
        f"- Policy expectations matched: **{policy_matches}/{total}**",
        f"- Approval requirements matched: **{approval_matches}/{total}**",
        "",
        "## Case matrix",
        "",
        "| Case | Passed | Status | Classification | Policy allowed | Approval required |",
        "|---|---|---|---|---|---|",
    ]

    for result in results:
        lines.append(
            "| {case} | {passed} | {status} | {classification} | {policy} | {approval} |".format(
                case=result.case_id,
                passed="yes" if result.passed else "no",
                status=result.observed_status,
                classification=result.observed_classification,
                policy=str(result.observed_policy_allowed).lower(),
                approval=str(result.observed_approval_required).lower(),
            )
        )

    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "This benchmark validates the deterministic safety pipeline around model output: response parsing, policy checks and approval requirements. It is not a substitute for live-model quality evaluation against labelled SOC data.",
        ]
    )
    return "\n".join(lines) + "\n"


def write_summary(path: Path, results: list[BenchmarkResult]) -> None:
    """Write benchmark summary markdown to disk."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(build_markdown_summary(results), encoding="utf-8")


def main() -> None:
    """Run the deterministic benchmark and write the markdown report."""
    root = repo_root()
    cases = load_cases(root / "benchmarks" / "triage_cases.json")
    results = evaluate_cases(cases)
    write_summary(root / "reports" / "triage_benchmark_summary.md", results)


if __name__ == "__main__":
    main()
