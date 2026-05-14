# Sample Dry-Run Output

The default operating mode of Sentinel-AI-AutoTriage is **dry-run**. The tool can analyse incidents, apply deterministic recommendation checks, evaluate whether human approval is required, and append a metadata-only decision audit record **without** writing updates back to Microsoft Sentinel.

Illustrative output from a controlled demonstration run with a closure recommendation but **no explicit approval token** configured:

```text
2026-05-14 09:14:02 [INFO] src.auto_triage: Starting Sentinel-AI-AutoTriage in dry-run mode
2026-05-14 09:14:03 [INFO] src.sentinel_client: Fetched 1 active/new incidents
2026-05-14 09:14:03 [INFO] src.auto_triage: Processing 1 active/new incidents
2026-05-14 09:14:03 [INFO] src.auto_triage: Processing incident incident-demo-001
2026-05-14 09:14:03 [INFO] src.llm_client: Redacted 3 sensitive-looking value(s) before LLM analysis; types=api_key,email,ipv4
2026-05-14 09:14:04 [INFO] src.auto_triage: Recommendation for incident incident-demo-001: status=Closed classification=True Positive comment=Confirmed suspicious activity after correlation with additional telemetry.
2026-05-14 09:14:04 [INFO] src.auto_triage: Human approval blocked incident incident-demo-001 recommendation: Closure recommendation requires explicit human approval.
2026-05-14 09:14:04 [INFO] src.auto_triage: Triage run completed; applied_updates=0
```

Because closure recommendations require explicit approval, the workflow would append an audit record with:

- `write_mode=false`
- `policy_allowed=true`
- `approval_required=true`
- `approval_status=pending`
- `applied_update=false`

The audit record is metadata-only and excludes raw incident text, redacted values and model prompt content. A full example is provided in [`decision-audit-example.md`](decision-audit-example.md).

## Why this matters

A dry-run transcript now demonstrates five safety properties:

1. the system can produce useful recommendations without changing Sentinel,
2. sensitive-looking values are redacted before LLM processing,
3. deterministic recommendation checks still evaluate the model result,
4. closure recommendations remain blocked until a separate approval state exists,
5. applied updates remain at zero unless both the write gate and the approval requirement are satisfied.
