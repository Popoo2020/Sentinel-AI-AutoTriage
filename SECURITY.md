# Security Notes

Sentinel-AI-AutoTriage is a security-focused prototype for **authorised** Microsoft Sentinel triage experiments. It is not intended for unattended production incident closure without additional governance, validation and operational review.

## Safe operating model

- The default operating mode is **dry-run**.
- `AUTO_APPLY_CHANGES=false` should remain the default unless testing in a controlled environment.
- Any write action to Sentinel should be reviewed within the organisation's incident-response and change-management procedures.
- Model output is treated as a **recommendation**, not as an independent authority.
- A deterministic write-policy gate can still block a model recommendation even when write mode is enabled.

## Data minimisation before LLM invocation

The project includes a deterministic redaction layer that masks representative:

- secret-like key/token values,
- password-like values,
- bearer tokens,
- email addresses,
- IPv4 addresses.

This is a transparent portfolio-grade example of data minimisation. It is **not** a complete DLP system and should not be treated as a substitute for enterprise data classification, secret scanning or privacy controls.

## Deterministic write-policy gate

Before an update can be sent to Sentinel, `src/recommendation_policy.py` evaluates whether the recommendation is specific enough to write.

The current policy:

- allows non-closure status recommendations after the external write gate is enabled,
- blocks closure when the classification is missing, ambiguous or unsupported,
- blocks closure when the analyst-facing justification is too short,
- allows closure only when the deterministic checks pass.

This prevents the system from treating model output alone as sufficient authority for a sensitive state change.

## Metadata-only decision audit trail

The project can append local JSONL decision records to:

```bash
TRIAGE_AUDIT_LOG_PATH=logs/triage_audit.jsonl
```

These records are intentionally **metadata-only**. They capture:

- incident ID,
- current and recommended status,
- classification,
- whether write mode was enabled,
- whether deterministic policy allowed the action,
- whether an update was applied.

They intentionally do **not** store raw incident titles, descriptions or prompt content. Audit-log file I/O failures are logged as warnings and do not crash the triage flow.

## Responsible use

Use the project only with:

- workspaces and incidents you are authorised to access,
- test data or operational environments approved for such automation,
- appropriate Azure permissions based on least privilege,
- approved internal rules for sending security event context to external model providers.

## Reporting issues

Security-relevant defects should be handled responsibly. When reporting an issue, include:

- the affected file or workflow,
- the observed behaviour,
- why it could affect safe operation,
- a minimal reproducible example when possible.
