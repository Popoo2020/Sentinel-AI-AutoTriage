# Metadata-Only Decision Audit Example

Sentinel-AI-AutoTriage can append one JSONL record per processed triage decision.
The record is intentionally **metadata-only** and does not store raw incident text,
raw prompts, descriptions or titles.

Example JSONL record:

```json
{
  "applied_update": false,
  "classification": "Undetermined",
  "current_status": "new",
  "incident_id": "incident-demo-001",
  "policy_allowed": false,
  "policy_reason": "Closure blocked: classification is missing, ambiguous or unsupported.",
  "recommended_status": "Closed",
  "timestamp": "2026-05-13T09:14:04+00:00",
  "write_mode": true
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
| `policy_allowed` | Whether deterministic policy allowed the action |
| `policy_reason` | Human-readable policy explanation |
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
