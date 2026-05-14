# Sentinel-AI-AutoTriage

[![CI](https://github.com/Popoo2020/Sentinel-AI-AutoTriage/actions/workflows/ci.yml/badge.svg)](https://github.com/Popoo2020/Sentinel-AI-AutoTriage/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

**Sentinel-AI-AutoTriage** is a security-focused Microsoft Sentinel triage prototype that combines **LLM-assisted incident analysis** with explicit **safety gates**, **data minimisation before model invocation**, **deterministic write-policy checks**, and a **metadata-only decision audit trail**.

It retrieves active incidents, prepares a compact incident summary, redacts common sensitive-looking values before they are sent to an LLM, validates the model response against a strict schema, applies an independent policy gate before any write action, and either logs a recommendation or updates Sentinel only when explicit write mode is enabled.

> **Status:** working security-focused prototype / active hardening.  
> Suitable for portfolio review, architecture discussion, controlled demos and further engineering — **not** for unattended production incident closure.

![Sentinel-AI-AutoTriage architecture](assets/sentinel-auto-triage-architecture.svg)

## What is implemented

| Capability | Status |
|---|---|
| Azure Sentinel incident retrieval | ✅ Implemented |
| Environment-based configuration | ✅ Implemented |
| LLM client abstraction | ✅ Implemented |
| Structured JSON-first model response parsing | ✅ Implemented |
| Safe fallbacks for malformed or unsafe model output | ✅ Implemented |
| Pre-LLM redaction of common sensitive-looking values | ✅ Implemented |
| Incident status recommendation handling | ✅ Implemented |
| Explicit write-action gate via `AUTO_APPLY_CHANGES` | ✅ Implemented |
| Dry-run-first execution model | ✅ Implemented |
| Deterministic write-policy gate before Sentinel updates | ✅ Implemented |
| Metadata-only JSONL decision audit trail | ✅ Implemented |
| Non-blocking audit-file failure handling | ✅ Implemented |
| Console + file logging | ✅ Implemented |
| Unit tests for redaction, parsing, policy, audit, status handling, configuration and update logic | ✅ Implemented |
| CI linting, tests and coverage reporting | ✅ Implemented |
| Technical walkthrough, dry-run transcript and audit-record examples | ✅ Implemented |
| Production-grade human approvals and operational benchmarking | 🟡 Future hardening |

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
LLM analysis layer
        │
        ▼
Validated recommendation
        │
        ▼
Deterministic write-policy gate
        │
        ├── Dry-run logging (default)
        ├── Controlled Sentinel update (explicit write mode only)
        └── Metadata-only JSONL decision audit trail
```

## Security posture

The project is intentionally **non-destructive by default**:

- `AUTO_APPLY_CHANGES=false` keeps the tool in dry-run mode.
- Incidents are only updated when write mode is explicitly enabled.
- LLM output is parsed and validated before it can influence status handling.
- Invalid, malformed or out-of-policy model output falls back to `Active / Unspecified`.
- Common sensitive-looking values are redacted before incident text is sent to the model.
- Status comparison logic handles enum-style and string-style Sentinel responses consistently.
- A deterministic policy layer can block a recommendation even when the model suggests closure.
- Every processing decision can be recorded in a metadata-only JSONL audit trail.

## Pre-LLM redaction layer

Before analysis, the project redacts representative values such as:

- secret-like API key / token / secret assignments,
- password-like values,
- bearer-token strings,
- email addresses,
- IPv4 addresses.

This layer is intentionally deterministic and transparent. It demonstrates **data minimisation** before LLM invocation, but it is **not** positioned as a full enterprise DLP product.

## Deterministic write-policy gate

Before any recommendation can be written to Sentinel, `src/recommendation_policy.py` evaluates whether the recommendation is specific enough to act on.

The current policy:

- allows non-closure status recommendations after the external write gate is enabled,
- blocks closure when the classification is missing, ambiguous or unsupported,
- blocks closure when the analyst-facing justification is too short,
- allows closure only when the deterministic conditions pass.

This design intentionally separates **model recommendation** from **state-changing authority**.

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
- **Deterministic write policy** — closure decisions require more than a model response.
- **Write-action gate** — updates are only applied when explicit write mode is enabled.
- **Metadata-only audit** — operational decision trail without raw prompt or incident-text storage.
- **Testable workflow units** — incident processing is broken into smaller functions that can be asserted without Azure network calls.
- **Structured logging** — console and local file logging for controlled triage runs.

## Repository structure

```text
src/
  audit.py                # Metadata-only JSONL audit records
  auto_triage.py          # Main workflow, dry-run gate, policy gate and incident processing
  llm_client.py           # LLM invocation, strict response parsing and safe fallback logic
  models.py               # Shared incident data model
  recommendation_policy.py # Deterministic write-policy checks
  redaction.py            # Pre-LLM deterministic redaction layer
  sentinel_client.py      # Microsoft Sentinel SDK wrapper

tests/
  test_audit.py
  test_auto_triage.py
  test_config_and_models.py
  test_llm_client.py
  test_recommendation_policy.py
  test_redaction.py
  test_sentinel_client.py

samples/
  sample_incident.json

docs/
  decision-audit-example.md
  sample-dry-run-output.md
  technical-walkthrough.md

.github/workflows/
  ci.yml

.env.example
.gitignore
CHANGELOG.md
LICENSE
requirements-dev.txt
requirements.txt
SECURITY.md
```

## Configuration

Start from `.env.example`:

```bash
SUBSCRIPTION_ID=
RESOURCE_GROUP=
WORKSPACE_NAME=
OPENAI_API_KEY=
LLM_MODEL=gpt-4o-mini
AUTO_APPLY_CHANGES=false
TRIAGE_AUDIT_LOG_PATH=logs/triage_audit.jsonl
```

The dry-run-safe default is:

```bash
AUTO_APPLY_CHANGES=false
```

## Quickstart

```bash
git clone https://github.com/Popoo2020/Sentinel-AI-AutoTriage.git
cd Sentinel-AI-AutoTriage

python -m venv .venv
source .venv/bin/activate

pip install -r requirements-dev.txt
cp .env.example .env
python -m src.auto_triage
```

## Testing and quality checks

```bash
ruff check src tests
pytest -q --cov=src --cov-report=term-missing
```

The CI workflow runs:

1. dependency installation via `requirements-dev.txt`,
2. linting of `src` and `tests`,
3. the full pytest suite,
4. coverage reporting.

## Example LLM response contract

The analysis layer expects a JSON object shaped like:

```json
{
  "recommended_status": "Active",
  "classification": "True Positive",
  "comment": "Suspicious repeated authentication failures against a privileged account require analyst review."
}
```

## Example redaction-aware incident input

A sample incident is included in:

```text
samples/sample_incident.json
```

It contains an example email, IPv4 address and token-like value so the redaction behaviour is easy to explain during portfolio review or technical discussion.

## Supporting documentation

- [`docs/technical-walkthrough.md`](docs/technical-walkthrough.md) — a detailed explanation of the architecture, redaction, policy gate, audit trail and test philosophy.
- [`docs/sample-dry-run-output.md`](docs/sample-dry-run-output.md) — an illustrative dry-run transcript showing recommendations without write actions.
- [`docs/decision-audit-example.md`](docs/decision-audit-example.md) — a metadata-only JSONL audit-record example.
- [`SECURITY.md`](SECURITY.md) — responsible-use guidance and the intended non-destructive operating model.

## Current hardening achieved

- Strict model response validation
- Deterministic safe fallbacks
- Explicit dry-run/write separation
- Redaction before LLM invocation
- Deterministic policy checks before write actions
- Metadata-only JSONL audit trail
- Non-blocking audit I/O failure handling
- Unit coverage across high-risk decision points
- Defensive Sentinel status handling
- Configuration and model tests
- CI enforcement for linting, tests and coverage reporting
- Documented responsible-use posture in `SECURITY.md`

## Next sensible extensions

1. Add human approval objects for sensitive write paths.
2. Introduce benchmark datasets for triage-quality evaluation.
3. Add provider adapters for model-agnostic inference backends.
4. Add centralised audit export and retention policy.
5. Add deployment guidance for managed identity and least-privilege Azure roles.

## Release readiness

This repository is now positioned as a strong **`v0.1.x` security-focused prototype**. A tagged release is appropriate once GitHub Actions confirms a green run for the current hardened baseline.

## Known limitations

- This is not a production SOC platform.
- It does not yet include an operational approval queue or analyst workflow UI.
- It does not yet benchmark recommendation quality against labelled incident datasets.
- The redaction layer is intentionally scoped and does not replace enterprise DLP, privacy engineering or secret-scanning controls.
- Automated incident updates should remain disabled unless tested in a controlled, authorised environment.
