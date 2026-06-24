# Demo Output

This file documents expected local demo behaviour for portfolio review.

## Run deterministic benchmark

```bash
python -m src.benchmark
```

Expected output:

```text
Wrote reports/triage_benchmark_summary.md
```

## Expected benchmark summary sections

```text
# Sentinel AI AutoTriage Benchmark Summary
## Cases evaluated
## Recommendation outcomes
## Policy gate results
## Approval requirements
```

## Example analyst-facing interpretation

```text
Case ID: demo-case-001
Recommended status: Active
Classification: NeedsReview
Policy allowed: true
Approval required: false
Update applied: false
Reason: Dry-run mode is enabled by default.
```

## Expected safety behaviour

- Dry-run mode should not update Sentinel.
- Sensitive status changes should require approval.
- Malformed model output should fall back to safe review.
- Audit records should not include raw incident text or raw prompt content.
