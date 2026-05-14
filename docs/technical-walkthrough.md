# Technical Walkthrough — Sentinel-AI-AutoTriage

This document explains the core flow of the project in a way that is useful for
technical portfolio review, architecture discussion and future engineering work.

## 1. Incident retrieval

`src/sentinel_client.py` connects to Microsoft Sentinel through the Azure SDK and
collects incidents whose status is interpreted as **New** or **Active**.

The wrapper normalises both enum-style and string-style status values so that the
project behaves consistently even when SDK responses differ in representation.

## 2. Compact incident summary

`src/auto_triage.py` converts the SDK object into a compact `IncidentSummary`:

- incident ID
- title
- description
- severity
- status

This keeps the LLM-facing context intentionally narrow and easier to reason about.

## 3. Data minimisation before LLM invocation

Before incident text is sent to a model, `src/redaction.py` masks representative:

- key/token/secret assignments,
- password-style values,
- bearer tokens,
- email addresses,
- IPv4 addresses.

The module returns both the redacted text and a count/type summary so the workflow
can log **what kind of minimisation happened** without logging the original value.

## 4. Strict model response contract

`src/llm_client.py` asks for JSON only:

```json
{
  "recommended_status": "Active",
  "classification": "Undetermined",
  "comment": "Analyst review required."
}
```

The parser:

1. accepts valid JSON,
2. attempts to recover JSON wrapped in accidental surrounding text,
3. rejects invalid status/classification values,
4. fails safely to `Active / Unspecified` when parsing or validation fails.

## 5. Dry-run/write gate

The project runs in dry-run mode unless:

```bash
AUTO_APPLY_CHANGES=true
```

Even when the model recommends a different status, the tool:

- logs the recommendation in dry-run mode,
- does **not** call the Sentinel update path,
- applies changes only when explicit write mode is enabled.

## 6. Defensive status comparison

The workflow compares the current Sentinel status and the recommended status
through a normalisation helper so equivalent enum/string values are treated as
identical. This prevents unnecessary write attempts when the status is already
correct.

## 7. Test coverage philosophy

The test suite deliberately targets the parts of the workflow that could affect
safe operation:

- parsing malformed or wrapped LLM output,
- redaction of sensitive-looking values,
- dry-run behaviour,
- explicit write-gate behaviour,
- unchanged-status no-op behaviour,
- Azure status normalisation,
- update-path handling,
- required environment configuration.

## 8. What would make it production-grade?

The current project is intentionally a **security-focused prototype**, not an
unattended production closure engine. Production hardening would require:

1. organisation-specific policy thresholds,
2. approved classification mappings to Sentinel SDK expectations,
3. analyst approval workflows,
4. richer audit exports,
5. labelled datasets for triage-quality evaluation,
6. privacy/security review for incident data sent to external model providers,
7. monitoring, rate limits and failure-mode observability.
