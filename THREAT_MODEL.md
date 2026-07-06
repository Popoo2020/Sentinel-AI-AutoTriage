# Threat Model

## Scope

This threat model covers the portfolio prototype code paths that read Microsoft Sentinel incident metadata, call an LLM completion provider, evaluate deterministic write policy, and optionally update incident status when explicit write mode and approval gates allow it.

## Assets

- Microsoft Sentinel incident metadata and status.
- Azure subscription, resource group and workspace identifiers.
- Azure identity used by `DefaultAzureCredential`.
- LLM prompts, responses and derived recommendations.
- Metadata-only JSONL audit records.
- CI configuration and dependency manifests.

## Trust boundaries

1. Local runtime or CI environment to Azure authentication.
2. Sentinel incident data to the LLM-facing summary/redaction layer.
3. LLM provider response to deterministic recommendation policy.
4. Policy and approval state to Sentinel write operation.
5. Repository code to GitHub Actions workflows.

## Primary risks and controls

| Risk | Impact | Existing control | Additional note |
|---|---|---|---|
| Unauthorised incident updates | False closure or status changes | Dry-run by default, explicit `AUTO_APPLY_CHANGES`, deterministic policy and closure approval | Production use should add durable analyst approval records. |
| Sensitive data exposure to model provider | Disclosure of incident details | Compact incident summary and deterministic redaction layer | Treat redaction as defence-in-depth, not full DLP. |
| Prompt injection through incident text | Model manipulation | Model output is advisory and must pass deterministic policy | Avoid using model output as executable instructions. |
| Overbroad Azure permissions | Larger blast radius | Documentation recommends least privilege | Use a dedicated identity for testing. |
| Audit-log leakage | Local metadata exposure | Audit records avoid raw incident title/description/prompt content | Protect log directory permissions in real deployments. |
| Dependency compromise | CI/runtime compromise | `pip-audit`, Bandit, ruff and CodeQL workflows | Pinning and lock files should be considered before production. |

## Security invariants

- The default mode must not write to Sentinel.
- Model recommendations must never bypass deterministic policy checks.
- Closure recommendations must require explicit approval metadata.
- Audit records should remain metadata-only.
- Tests and security checks should run on pull requests and pushes to `main`.

## Out of scope

- Production-grade DLP.
- Full Azure RBAC design.
- Live incident-response workflow integration.
- Formal model evaluation across real customer data.
