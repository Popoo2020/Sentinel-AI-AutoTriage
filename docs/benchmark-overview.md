# Deterministic Benchmark Overview

Sentinel-AI-AutoTriage includes a deterministic benchmark flow for reviewing the **safety pipeline around model output**.

The benchmark is intentionally not a live-model quality study. Instead, it checks whether the repository's own controls behave as expected when given representative model-response patterns.

## Inputs

Benchmark cases are stored in:

```text
benchmarks/triage_cases.json
```

Each case includes:

- a case identifier,
- a title and description,
- a deterministic mock model response,
- the expected parsed status,
- the expected classification,
- the expected recommendation-policy outcome,
- the expected approval requirement.

## Execution

Run:

```bash
python -m src.benchmark
```

The script evaluates all benchmark cases through the same parsing, recommendation-policy and approval-requirement logic used by the repository.

It generates:

```text
reports/triage_benchmark_summary.md
```

## What the benchmark validates

The current deterministic benchmark checks whether:

- valid structured model output is parsed correctly,
- malformed model output falls back safely,
- strong closure recommendations can pass deterministic policy,
- weak or ambiguous closure recommendations are blocked,
- closure recommendations are correctly marked as requiring approval.

## What it does not validate

This benchmark does **not** claim to measure:

- real-world SOC precision or recall,
- model truthfulness,
- live Sentinel incident classification quality,
- operational alert fatigue reduction,
- production-ready closure accuracy.

Those questions require labelled incident datasets, environment-specific evaluation criteria and a much broader operational study.
