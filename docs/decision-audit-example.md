# Metadata-Only Decision Audit Example

Sentinel-AI-AutoTriage can append one JSONL record per processed triage decision.
The record is intentionally **metadata-only** and does not store raw incident text,
raw prompts, descriptions or titles.

Example JSONL record for a closure recommendation that remains pending human approval:

```json
{
  "applied_update": false,
  "approval_required": true,
  "approval_status": "pending",
  "approved_by": null,
  "classification": "True Positive",
  "current_status": "new",
  "incident_id": "incident-demo-001",
  "policy_allowed": true,
  "policy_reason": "Closure recommendation passed deterministic classification and comment checks.",
  "recommended_status": "Closed",
  "timestamp": "2026-05-14T09:14:04+00:00",
  "write_mode": false
}
```

## Field meanings

| Field | Meaning |
|---|---|
| `incident_id` | Sentinel incident identifier only |
| `current_status` | Normalised current status before handling |
| `recommended_status` | Validated recommendation from the model path |
| `classification` | Parsed classification value, when present |
| `write_mode` | Whether explicit write mode was enabled |
| `policy_allowed` | Whether deterministic recommendation checks allowed the action |
| `policy_reason` | Human-readable policy explanation |
| `approval_required` | Whether a separate approval state is required |
| `approval_status` | `not_required`, `pending`, `approved`, or `rejected` |
| `approved_by` | Metadata label for the local approver when present |
| `applied_update` | Whether the Sentinel update path actually executed |

## What is deliberately excluded

The audit record does **not** include:

- raw incident title,
- raw incident description,
- model prompt content,
- raw secrets or values redacted before LLM invocation,
- model provider response bodies beyond the validated recommendation metadata.

This design keeps the audit trail useful for workflow review while reducing the
risk of accidentally persisting sensitive operational content.
