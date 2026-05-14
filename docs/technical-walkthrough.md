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

## 5. Provider abstraction for repeatability

`src/providers.py` adds a minimal completion-provider boundary. The production
client can keep its normal behaviour, while tests and benchmark runs inject a
`StaticMockProvider` to exercise the exact same parsing and safety logic without
external model calls.

This makes the project easier to:

- test deterministically,
- benchmark safely,
- extend toward enterprise-hosted provider adapters without rewriting the triage workflow.

The current repository also includes `src/azure_provider.py` as an explicit
enterprise-provider extension boundary scaffold.

## 6. Deterministic recommendation-policy gate

Model output is not treated as final authority. After parsing, the recommendation
passes through `src/recommendation_policy.py` before any write can occur.

The current recommendation policy:

- allows non-closure recommendations after the external write gate is enabled,
- blocks closure if the classification is missing, ambiguous or unsupported,
- blocks closure if the analyst-facing explanation is too short,
- allows closure only when the deterministic conditions pass.

This adds an important second layer of control between **model recommendation** and
**state-changing action**.

## 7. Human approval state for closure paths

`src/approval.py` introduces a separate human-approval object for closure recommendations.

The current prototype behaviour is:

- non-closure recommendations do not require approval,
- closure recommendations become `pending` by default,
- a local explicit approval indicator is required before a closure write can proceed,
- approval metadata can be recorded in the decision log without storing raw incident content.

A production implementation should replace the local indicator with a durable
analyst workflow, ticket state or signed approval system.

## 8. Dry-run/write gate

The project runs in dry-run mode unless:

```bash
AUTO_APPLY_CHANGES=true
```

Even when the model recommends a different status, the tool:

- evaluates redaction, parsing, policy and approval logic,
- logs the resulting recommendation in dry-run mode,
- does **not** call the Sentinel update path unless write mode is enabled,
- still obeys both the deterministic recommendation-policy gate and the approval state.

## 9. Defensive status comparison

The workflow compares the current Sentinel status and the recommended status
through a normalisation helper so equivalent enum/string values are treated as
identical. This prevents unnecessary write attempts when the status is already
correct.

## 10. Metadata-only audit trail

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
- whether approval was required,
- approval status / approver label when present,
- whether an update was actually applied.

It does **not** store raw incident titles, descriptions or prompt text. Audit-log
I/O failures are handled as warnings so they do not crash the triage process.

## 11. Deterministic benchmark

`src/benchmark.py` evaluates a small benchmark dataset in `benchmarks/triage_cases.json`.
Each case contains:

- input title and description,
- a deterministic mock model response,
- expected parsed status/classification,
- expected recommendation-policy result,
- expected approval requirement.

The benchmark generates:

```text
reports/triage_benchmark_summary.md
```

This benchmark validates the safety pipeline around model output. It is not a
live-model quality benchmark against labelled SOC data.

## 12. Test coverage philosophy

The test suite deliberately targets the parts of the workflow that could affect
safe operation:

- parsing malformed or wrapped LLM output,
- redaction of sensitive-looking values,
- provider injection and deterministic mock completions,
- dry-run behaviour,
- explicit write-gate behaviour,
- deterministic recommendation-policy allow/block logic,
- approval-state allow/block logic,
- unchanged-status no-op behaviour,
- Azure status normalisation,
- update-path handling,
- metadata-only audit record construction,
- audit-log write behaviour,
- non-blocking audit I/O failures,
- deterministic benchmark summary generation,
- required environment configuration.

## 13. What would make it production-grade?

The current project is intentionally a **security-focused prototype**, not an
unattended production closure engine. Production hardening would require:

1. organisation-specific policy thresholds,
2. approved classification mappings to Sentinel SDK expectations,
3. a durable analyst approval workflow,
4. centralised audit export and retention policy,
5. labelled datasets for live-model triage-quality evaluation,
6. privacy/security review for incident data sent to external model providers,
7. monitoring, rate limits and failure-mode observability,
8. deployment guidance for managed identity and least-privilege Azure roles.
