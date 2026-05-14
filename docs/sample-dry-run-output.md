# Sample Dry-Run Output

The default operating mode of Sentinel-AI-AutoTriage is **dry-run**.  The tool
can analyse incidents and log recommendations without writing updates back to
Microsoft Sentinel.

Example output from a controlled demonstration run:

```text
2026-05-13 09:14:02 [INFO] src.auto_triage: Starting Sentinel-AI-AutoTriage in dry-run mode
2026-05-13 09:14:03 [INFO] src.sentinel_client: Fetched 1 active/new incidents
2026-05-13 09:14:03 [INFO] src.auto_triage: Processing 1 active/new incidents
2026-05-13 09:14:03 [INFO] src.auto_triage: Processing incident incident-demo-001
2026-05-13 09:14:03 [INFO] src.llm_client: Redacted 3 sensitive-looking value(s) before LLM analysis; types=api_key,email,ipv4
2026-05-13 09:14:04 [INFO] src.auto_triage: Recommendation for incident incident-demo-001: status=Active classification=Undetermined comment=Analyst review required.
2026-05-13 09:14:04 [INFO] src.auto_triage: Dry-run mode: would update incident incident-demo-001 to status Active with classification Undetermined
2026-05-13 09:14:04 [INFO] src.auto_triage: Triage run completed; applied_updates=0
```

## Why this matters

A dry-run transcript demonstrates three important safety properties:

1. the system can produce useful recommendations without changing Sentinel,
2. sensitive-looking values are redacted before LLM processing,
3. applied updates remain at zero unless the write gate is explicitly enabled.
