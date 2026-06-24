# Quality and Security Checklist

## CI quality gates

Before merge or external presentation, confirm:

- [ ] Ruff linting passes.
- [ ] Pytest passes.
- [ ] Coverage step completes.
- [ ] Bandit review passes.
- [ ] Dependency review passes.
- [ ] Benchmark summary is generated.
- [ ] CodeQL completes successfully.

## Security gates

- [ ] No real tokens or private configuration values are committed.
- [ ] Dry-run mode remains the default.
- [ ] Write mode requires explicit configuration.
- [ ] Sensitive status changes require approval.
- [ ] Audit records avoid raw incident text and raw prompts.
- [ ] Redaction layer is tested.
- [ ] Safe fallback behaviour is tested.

## Operational readiness gates

- [ ] Architecture documentation is present.
- [ ] Threat model is present.
- [ ] Demo output is documented.
- [ ] Recruiter summary is present.
- [ ] Security policy is present.
- [ ] README clearly states this is not unattended production automation.

## Future readiness gates

- [ ] Configuration schema validation.
- [ ] Provider timeout and retry handling.
- [ ] Durable approval queue.
- [ ] Centralised audit retention.
- [ ] Environment-specific access review.
- [ ] Labelled evaluation dataset.
