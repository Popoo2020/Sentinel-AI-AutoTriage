# Deployment and Least-Privilege Guide

This guide explains how to think about deploying Sentinel-AI-AutoTriage in a controlled environment.  It is intentionally conservative and keeps the repository positioned as a **security-focused prototype**, not as an unattended production closure engine.

## 1. Recommended deployment posture

Use the project in this order:

1. **Local dry-run** with test or synthetic data.
2. **Controlled workspace validation** with `AUTO_APPLY_CHANGES=false`.
3. **Explicitly approved write-path demonstrations** only after the recommendation-policy and approval controls are understood.
4. **Production design review** before any real operational use.

## 2. Identity and permissions

The Sentinel SDK wrapper uses Azure identity mechanisms through the runtime environment.  In any deployment design, prefer:

- a dedicated workload identity or managed identity,
- a narrowly scoped identity dedicated to this workflow,
- no reuse of broad administrator identities,
- least privilege aligned to the exact operations being demonstrated.

The project currently needs only the access required to:

- read the relevant incident information,
- and, only when intentionally enabled, exercise the update path.

Exact role assignments should be reviewed against the current Azure/Sentinel permissions model in the target environment before use.

## 3. Dry-run remains the default

The default configuration should remain:

```bash
AUTO_APPLY_CHANGES=false
```

This allows the workflow to:

- retrieve incidents,
- redact common sensitive-looking values,
- obtain and validate a model recommendation,
- evaluate deterministic recommendation policy,
- evaluate whether approval is required,
- append metadata-only decision records,
- without writing back to Sentinel.

## 4. Closure recommendations require separate approval state

Sensitive closure paths are deliberately separated from the model recommendation.

For controlled demonstrations only, the current prototype can model local approval metadata through:

```bash
TRIAGE_APPROVAL_TOKEN=
TRIAGE_APPROVER=
```

When blank, closure recommendations remain pending and do not reach the update path.  A production-grade design should replace the local demonstration indicator with a durable workflow such as:

- an analyst queue,
- a ticket approval state,
- a signed approval record,
- or a case-management integration.

## 5. Audit logging and retention

The repository supports a metadata-only local JSONL decision log:

```bash
TRIAGE_AUDIT_LOG_PATH=logs/triage_audit.jsonl
```

The log intentionally avoids storing:

- raw incident titles,
- raw incident descriptions,
- model prompt content,
- redacted secret values.

A production design should define:

- retention period,
- access controls,
- integrity checks,
- centralised export destination,
- and deletion procedures where applicable.

## 6. Model-provider boundary

The repository exposes an injectable completion-provider boundary so benchmark runs and tests can remain deterministic.  An enterprise deployment could attach a managed provider adapter without changing the redaction, parsing, recommendation-policy or approval layers.

See:

```text
docs/provider-extension.md
```

## 7. Deployment checklist

Before any write-capable experiment:

- confirm the target workspace is authorised for testing,
- confirm dry-run behaviour and audit output first,
- confirm sensitive incident data handling is acceptable for the configured model provider,
- confirm recommendation-policy checks behave as expected,
- confirm approval gating remains active for closure paths,
- confirm logs and local audit files are handled securely,
- confirm the identity used by the workflow is appropriately scoped.

## 8. What still belongs in a production implementation

The repository is intentionally transparent about what remains outside the current prototype:

- durable approval workflow,
- centralised audit export and retention controls,
- environment-specific role validation,
- monitoring and alerting for the automation itself,
- labelled evaluation datasets for live model quality,
- retry, backoff and richer failure-mode observability.
