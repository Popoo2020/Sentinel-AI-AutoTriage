# Recruiter Summary

**Sentinel-AI-AutoTriage** is a Python safety-workflow prototype for AI-assisted incident triage.

## One-sentence summary

A Microsoft Sentinel triage prototype that uses LLM-assisted analysis only inside a controlled workflow with data minimisation, strict parsing, deterministic policy gates, human approval for sensitive closure paths and metadata-only audit logging.

## What you can inspect

- [Workflow](../src/auto_triage.py): default dry-run behavior, policy checks and a separate local approval signal before closure writes.
- [Provider boundary](../src/llm_client.py): deterministic redaction before model invocation and safe parsing fallbacks.
- [Azure adapter](../src/sentinel_client.py): SDK incident fields, supported classification values and explicit update outcomes.
- [SDK regression tests](../tests/test_sdk_integration.py): actual `Incident` objects with mocked SDK operations; failed writes remain `applied_update=false` in the audit record.
- [Deterministic benchmark](../src/benchmark.py): four authored mock-response cases covering parsing, policy and approval expectations.

Local verification on **19 October 2026**: **48 tests passed**, Python 3.12.14, Azure Security Insights SDK 1.0.0. These are offline tests; no live Azure or model requests were made. See the [README reproduction commands](../README.md#inspect-the-implementation).

## Best-fit roles

- AI Security Engineer
- SOC Automation Engineer
- Cybersecurity GRC Analyst / Consultant
- Responsible AI / AI Governance Analyst
- Security Automation Developer
- Microsoft Sentinel / SIEM Analyst

## Interview talking points

1. Why LLM output should be treated as a recommendation, not authority.
2. Why dry-run defaults matter in SOC automation.
3. How redaction supports data minimisation before LLM invocation.
4. How deterministic policy gates reduce unsafe automation risk.
5. Why closure recommendations require stronger human oversight.
6. Why metadata-only audit logs are useful for governance and privacy.

## Current maturity

This prototype supports code review and controlled demonstrations. Live tenant integration and model quality have not been established by these tests. Approval is currently a nonempty local token, not a durable authenticated approval workflow. SDK timeouts can leave remote state uncertain and require reconciliation. The deterministic benchmark is not a SOC accuracy claim.
