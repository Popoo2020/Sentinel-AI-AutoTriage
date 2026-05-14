# Sentinel-AI-AutoTriage

[![CI](https://github.com/Popoo2020/Sentinel-AI-AutoTriage/actions/workflows/ci.yml/badge.svg)](https://github.com/Popoo2020/Sentinel-AI-AutoTriage/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

**Sentinel-AI-AutoTriage** is a security-focused Microsoft Sentinel triage prototype that combines **LLM-assisted incident analysis** with explicit **safety gates**, **data minimisation before model invocation**, and a **testable dry-run-first workflow**.

It retrieves active incidents, prepares a compact incident summary, redacts common sensitive-looking values before they are sent to an LLM, validates the model response against a strict schema, and either logs a recommendation or applies an update only when explicit write mode is enabled.

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
| Console + file logging | ✅ Implemented |
| Unit tests for redaction, parsing, status handling and update logic | ✅ Implemented |
| CI linting, tests and coverage reporting | ✅ Implemented |
| Production-grade policy approvals and operational benchmarking | 🟡 Future hardening |

## Architecture

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
        ├── Dry-run logging (default)
        └── Optional incident update when explicitly enabled
```

## Security posture

The project is intentionally **non-destructive by default**:

- `AUTO_APPLY_CHANGES=false` keeps the tool in dry-run mode.
- Incidents are only updated when write mode is explicitly enabled.
- LLM output is parsed and validated before it can influence status handling.
- Invalid, malformed or out-of-policy model output falls back to `Active / Unspecified`.
- Common sensitive-looking values are redacted before incident text is sent to the model.
- Status comparison logic handles enum-style and string-style Sentinel responses consistently.

## Pre-LLM redaction layer

Before analysis, the project redacts representative values such as:

- secret-like API key / token / secret assignments,
- password-like values,
- bearer-token strings,
- email addresses,
- IPv4 addresses.

This layer is intentionally deterministic and transparent. It demonstrates **data minimisation** before LLM invocation, but it is **not** positioned as a full enterprise DLP product.

## Features

- **Sentinel incident triage flow** — fetches active/new incidents and converts them into a compact summary.
- **LLM-assisted analysis** — requests a strict JSON recommendation with:
  - `recommended_status`
  - `classification`
  - `comment`
- **Safe parsing layer** — accepts valid JSON, attempts recovery from wrapped JSON, and fails safely when parsing is impossible.
- **Redaction-aware prompting** — sensitive-looking values are masked before the prompt is constructed.
- **Write-action gate** — updates are only applied when explicit write mode is enabled.
- **Testable workflow units** — incident processing is broken into smaller functions that can be asserted without Azure network calls.
- **Structured logging** — console and local file logging for controlled triage runs.

## Repository structure

```text
src/
  auto_triage.py        # Main workflow, dry-run gate and testable incident processing
  llm_client.py         # LLM invocation, strict response parsing and safe fallback logic
  redaction.py          # Pre-LLM deterministic redaction layer
  sentinel_client.py    # Microsoft Sentinel SDK wrapper
  models.py             # Shared incident data model

tests/
  test_auto_triage.py
  test_llm_client.py
  test_redaction.py
  test_sentinel_client.py

samples/
  sample_incident.json

.github/workflows/
  ci.yml

.env.example
requirements.txt
requirements-dev.txt
SECURITY.md
CHANGELOG.md
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

## Current hardening achieved

- Strict model response validation
- Deterministic safe fallbacks
- Explicit dry-run/write separation
- Redaction before LLM invocation
- Unit coverage across high-risk decision points
- Defensive Sentinel status handling
- CI enforcement for linting and tests
- Documented responsible-use posture in `SECURITY.md`

## Next sensible extensions

1. Add configurable policy thresholds before any closure recommendation can be written.
2. Add human approval objects for sensitive write paths.
3. Introduce benchmark datasets for triage-quality evaluation.
4. Add provider adapters for model-agnostic inference backends.
5. Add structured JSONL audit export for each triage run.

## Release readiness

This repository is now positioned as a strong **`v0.1.x` security-focused prototype**.  A tagged release is appropriate once GitHub Actions confirms a green run for the current hardened baseline.

## Known limitations

- This is not a production SOC platform.
- It does not yet include an operational approval queue or analyst workflow UI.
- It does not yet benchmark recommendation quality against labelled incident datasets.
- The redaction layer is intentionally scoped and does not replace enterprise DLP, privacy engineering or secret-scanning controls.
- Automated incident updates should remain disabled unless tested in a controlled, authorised environment.
