# Case Study: Governed AI-Assisted Sentinel Triage

> Portfolio case study. This is not a claim of production deployment.

## Scenario

A security team wants to explore whether an AI assistant can help analysts summarise Microsoft Sentinel incidents and suggest next steps without creating unsafe automation or uncontrolled incident closure.

## Problem

Naive AI triage introduces several risks:

- raw incident data may be sent to a model without minimisation,
- model output may be malformed or overconfident,
- closure recommendations may be accepted too easily,
- write actions may occur without human approval,
- audit trails may store unnecessary incident detail.

## Design response

The prototype wraps the AI recommendation inside a governed workflow:

1. Retrieve incident summary.
2. Redact common sensitive-looking values before model invocation.
3. Ask for strict JSON output.
4. Parse and validate the model response.
5. Apply deterministic recommendation-policy checks.
6. Require human approval for closure paths.
7. Keep dry-run mode as the default.
8. Write metadata-only decision audit records.

## Control mapping

| Risk | Control |
|---|---|
| Model output is malformed | Strict parsing and safe fallback |
| Model recommends unsafe closure | Deterministic policy gate and approval requirement |
| Sensitive values enter the model prompt | Pre-LLM redaction layer |
| Automation changes incidents unexpectedly | Dry-run default and explicit write gate |
| No auditability | Metadata-only JSONL decision audit |

## Portfolio value

This case study demonstrates practical AI governance applied to SOC automation. It shows how AI adoption can be combined with defensive engineering, human accountability, and audit-ready control design.
