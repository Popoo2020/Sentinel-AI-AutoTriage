# Sentinel-AI-AutoTriage

[![CI](https://github.com/Popoo2020/Sentinel-AI-AutoTriage/actions/workflows/ci.yml/badge.svg)](https://github.com/Popoo2020/Sentinel-AI-AutoTriage/actions/workflows/ci.yml)
[![CodeQL](https://github.com/Popoo2020/Sentinel-AI-AutoTriage/actions/workflows/codeql.yml/badge.svg)](https://github.com/Popoo2020/Sentinel-AI-AutoTriage/actions/workflows/codeql.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

**Sentinel-AI-AutoTriage** is a security-focused Microsoft Sentinel triage prototype that combines **LLM-assisted incident analysis** with explicit **safety gates**, **data minimisation before model invocation**, **deterministic recommendation-policy checks**, **human approval for sensitive closure paths**, and a **metadata-only decision audit trail**.

It retrieves active incidents, prepares a compact incident summary, redacts common sensitive-looking values before they are sent to an LLM, validates the model response against a strict schema, evaluates an independent recommendation-policy layer, applies an explicit approval requirement for closure recommendations, and either logs a recommendation or updates Sentinel only when every gate is satisfied.

> **Status:** working security-focused prototype / active hardening.  
> Suitable for portfolio review, architecture discussion, controlled demos and further engineering — **not** for unattended production incident closure.

![Sentinel-AI-AutoTriage architecture](assets/sentinel-auto-triage-architecture.svg)

## Hiring-manager view

See [`docs/recruiter_summary.md`](docs/recruiter_summary.md) for a short role-oriented summary.

This project is especially relevant for:

- AI Security Engineer,
- SOC Automation Engineer,
- Cybersecurity GRC / Security Governance roles,
- Responsible AI / AI Governance roles,
- Microsoft Sentinel / SIEM automation roles.

## What is implemented

| Capability | Status |
|---|---|
| Azure Sentinel incident retrieval | ✅ Implemented |
| Environment-based configuration | ✅ Implemented |
| LLM client abstraction | ✅ Implemented |
| Injectable completion-provider boundary | ✅ Implemented |
| Deterministic mock provider for tests / benchmark runs | ✅ Implemented |
| Structured JSON-first model response parsing | ✅ Implemented |
| Safe fallbacks for malformed or unsafe model output | ✅ Implemented |
| Pre-LLM redaction of common sensitive-looking values | ✅ Implemented |
| Incident status recommendation handling | ✅ Implemented |
| Explicit write-action gate via `AUTO_APPLY_CHANGES` | ✅ Implemented |
| Dry-run-first execution model | ✅ Implemented |
| Deterministic recommendation-policy gate before Sentinel updates | ✅ Implemented |
| Human approval state for sensitive closure recommendations | ✅ Implemented |
| Metadata-only JSONL decision audit trail | ✅ Implemented |
| Non-blocking audit-file failure handling | ✅ Implemented |
| Deterministic triage benchmark dataset and runner | ✅ Implemented |
| Console + file logging | ✅ Implemented |
| Unit tests for redaction, parsing, providers, policy, approval, audit, status handling, benchmark logic and update flow | ✅ Implemented |
| CI linting, tests, coverage reporting, SAST, dependency audit and benchmark generation | ✅ Implemented |
| CodeQL and Dependabot configuration | ✅ Implemented |
| Technical walkthrough, deployment guide, provider-extension notes, dry-run transcript and audit-record examples | ✅ Implemented |
| Durable production approval workflow / centralised audit retention | 🟡 Future hardening |

## Hardened architecture

```text
Microsoft Sentinel
        │
        ▼
Incident retrieval
        │
        ▼
Compact incident summary
        │
        ▼
Pre-LLM redaction layer
        │
        ▼
LLM analysis layer / injectable provider boundary
        │
        ▼
Validated recommendation
        │
        ▼
Deterministic recommendation-policy gate
        │
        ▼
Human approval state for closure paths
        │
        ├── Dry-run logging (default)
        ├── Controlled Sentinel update (all gates satisfied only)
        └── Metadata-only JSONL decision audit trail
```

## Security posture

The project is intentionally **non-destructive by default**:

- `AUTO_APPLY_CHANGES=false` keeps the tool in dry-run mode.
- Incidents are only updated when explicit write mode is enabled.
- LLM output is parsed and validated before it can influence status handling.
- Invalid, malformed or out-of-policy model output falls back to `Active / Unspecified`.
- Common sensitive-looking values are redacted before incident text is sent to the model.
- Status comparison logic handles enum-style and string-style Sentinel responses consistently.
- A deterministic recommendation-policy layer can block a model suggestion even when write mode is enabled.
- Closure recommendations require a separate human-approval state before the update path can run.
- Every processing decision can be recorded in a metadata-only JSONL audit trail.

## Pre-LLM redaction layer

Before analysis, the project redacts representative values such as:

- secret-like API key / token / secret assignments,
- password-like values,
- bearer-token strings,
- email addresses,
- IPv4 addresses.

This layer is intentionally deterministic and transparent. It demonstrates **data minimisation** before LLM invocation, but it is **not** positioned as a full enterprise DLP product.

## Deterministic recommendation-policy gate

Before any recommendation can be written to Sentinel, `src/recommendation_policy.py` evaluates whether the recommendation is specific enough to act on.

The current policy:

- allows non-closure status recommendations after the external write gate is enabled,
- blocks closure when the classification is missing, ambiguous or unsupported,
- blocks closure when the analyst-facing justification is too short,
- allows closure only when the deterministic conditions pass.

This design intentionally separates **model recommendation** from **state-changing authority**.

## Human approval state for closure paths

`src/approval.py` adds an explicit approval object for sensitive closure recommendations.

The current prototype behaviour:

- non-closure recommendations do not require approval,
- closure recommendations default to `pending`,
- an explicit local approval indicator is required before a closure write can proceed,
- approval metadata can be recorded in the decision log without storing raw incident content.

Configuration values used for controlled demonstrations:

```bash
TRIAGE_APPROVAL_TOKEN=
TRIAGE_APPROVER=
```

A production implementation should replace the local demonstration indicator with a durable analyst queue, ticket approval state, signed approval record or equivalent enterprise workflow.

## Provider abstraction and deterministic benchmark

The LLM client supports an injectable provider boundary:

- `CompletionProvider` — minimal provider protocol,
- `StaticMockProvider` — deterministic provider for tests and benchmark execution,
- `src/azure_provider.py` — documented enterprise-provider extension boundary scaffold.

The benchmark runner evaluates a small deterministic dataset through the same parsing, recommendation-policy and approval-requirement logic used by the repository:

```bash
python -m src.benchmark
```

Input data:

```text
benchmarks/triage_cases.json
```

Generated output:

```text
reports/triage_benchmark_summary.md
```

This benchmark validates the **safety pipeline around model output**. It is not a claim of live SOC accuracy or a substitute for labelled incident-quality evaluation.

## Metadata-only decision audit trail

Each triage decision can be appended to a local JSONL file configured by:

```bash
TRIAGE_AUDIT_LOG_PATH=logs/triage_audit.jsonl
```

The audit record intentionally avoids raw incident text, raw prompts, titles and descriptions. It records only operational metadata such as:

- incident ID,
- current and recommended status,
- classification,
- whether write mode was enabled,
- whether deterministic policy allowed the action,
- whether approval was required,
- approval status / approver metadata when present,
- whether an update was applied.

Audit-write failures are logged as warnings and do **not** crash the triage flow.

## Features

- **Sentinel incident triage flow** — fetches active/new incidents and converts them into a compact summary.
- **LLM-assisted analysis** — requests a strict JSON recommendation with:
  - `recommended_status`
  - `classification`
  - `comment`
- **Safe parsing layer** — accepts valid JSON, attempts recovery from wrapped JSON, and fails safely when parsing is impossible.
- **Redaction-aware prompting** — sensitive-looking values are masked before the prompt is constructed.
- **Injectable completion provider** — enables deterministic tests and benchmark runs without changing triage logic.
- **Deterministic recommendation policy** — closure decisions require more than a model response.
- **Human approval state** — sensitive closure paths remain blocked by default.
- **Write-action gate** — updates are only applied when explicit write mode is enabled and all controls pass.
- **Metadata-only audit** — operational decision trail without raw prompt or incident-text storage.
- **Benchmark harness** — repeatable safety-pipeline checks over representative triage cases.
- **Testable workflow units** — incident processing is broken into smaller functions that can be asserted without Azure network calls.
- **Structured logging** — console and local file logging for controlled triage runs.
- **Security automation checks** — CI includes linting, coverage, SAST and dependency audit.

## Repository structure

```text
src/
  approval.py               # Human-approval state for sensitive closure recommendations
  audit.py                  # Metadata-only JSONL audit records
  auto_triage.py            # Main workflow, dry-run gate, policy gate, approval gate and incident processing
  azure_provider.py         # Enterprise-provider extension boundary scaffold
  benchmark.py              # Deterministic benchmark runner and report generation
  llm_client.py             # LLM invocation, provider boundary, strict parsing and safe fallbacks
  models.py                 # Shared incident data model
  providers.py              # CompletionProvider protocol and StaticMockProvider
  recommendation_policy.py # Deterministic recommendation-policy checks
  redaction.py              # Pre-LLM deterministic redaction layer
  sentinel_client.py        # Microsoft Sentinel SDK wrapper

benchmarks/
  triage_cases.json

tests/
  test_approval.py
  test_audit.py
  test_auto_triage.py
  test_benchmark.py
  test_config_and_models.py
  test_llm_client.py
  test_providers.py
  test_recommendation_policy.py
  test_redaction.py
  test_sentinel_client.py

samples/
  sample_incident.json

docs/
  recruiter_summary.md
```
