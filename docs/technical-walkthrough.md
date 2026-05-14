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

## 5. Deterministic write-policy gate

Model output is not treated as final authority.  After parsing, the recommendation
passes through `src/recommendation_policy.py` before any write can occur.

The current write policy:

- allows non-closure recommendations after the external write gate is enabled,
- blocks closure if the classification is missing, ambiguous or unsupported,
- blocks closure if the analyst-facing explanation is too short,
- allows closure only when the deterministic conditions pass.

This adds an important second layer of control between **model recommendation** and
**state-changing action**.

## 6. Dry-run/write gate

The project runs in dry-run mode unless:

```bash
AUTO_APPLY_CHANGES=true
```

Even when the model recommends a different status, the tool:

- logs the recommendation in dry-run mode,
- does **not** call the Sentinel update path,
- applies changes only when explicit write mode is enabled,
- still obeys the deterministic write-policy gate.

## 7. Defensive status comparison

The workflow compares the current Sentinel status and the recommended status
through a normalisation helper so equivalent enum/string values are treated as
identical. This prevents unnecessary write attempts when the status is already
correct.

## 8. Metadata-only audit trail

Every triage decision can be appended to a local JSONL decision log through:

```bash
TRIAGE_AUDIT_LOG_PATH=logs/triage_audit.jsonl
```

`src/audit.py` deliberately records **metadata only**:

- incident ID,
- current status,
- recommended status,
- classification,
- whether write mode was enabled,
- whether deterministic policy allowed the action,
- whether an update was actually applied.

It does **not** store raw incident titles, descriptions or prompt text.  Audit-log
I/O failures are handled as warnings so they do not crash the triage process.

## 9. Test coverage philosophy

The test suite deliberately targets the parts of the workflow that could affect
safe operation:

- parsing malformed or wrapped LLM output,
- redaction of sensitive-looking values,
- dry-run behaviour,
- explicit write-gate behaviour,
- deterministic write-policy allow/block logic,
- unchanged-status no-op behaviour,
- Azure status normalisation,
- update-path handling,
- metadata-only audit record construction,
- audit-log write behaviour,
- non-blocking audit I/O failures,
- required environment configuration.

## 10. What would make it production-grade?

The current project is intentionally a **security-focused prototype**, not an
unattended production closure engine. Production hardening would require:

1. organisation-specific policy thresholds,
2. approved classification mappings to Sentinel SDK expectations,
3. analyst approval workflows,
4. centralised audit export and retention policy,
5. labelled datasets for triage-quality evaluation,
6. privacy/security review for incident data sent to external model providers,
7. monitoring, rate limits and failure-mode observability,
8. deployment guidance for managed identity and least-privilege Azure roles.
