# Release Checklist

Use this checklist before publishing a GitHub release such as `v0.1.0`.

## Release title

`v0.1.0 - Portfolio Hardening Release`

## Pre-release validation

- [ ] Pull request is merged into `main`.
- [ ] CI workflow passed.
- [ ] CodeQL workflow passed.
- [ ] `make validate` runs successfully.
- [ ] Benchmark summary is generated successfully.
- [ ] README links work.
- [ ] Architecture document is present.
- [ ] Threat model is present.
- [ ] Demo output document is present.
- [ ] Quality and security checklist is present.
- [ ] Changelog and version notes are present.

## Security review

- [ ] No real API keys, credentials or environment files are included.
- [ ] Dry-run remains the default documented mode.
- [ ] Write mode requires explicit configuration.
- [ ] Sensitive status changes require approval.
- [ ] Audit records avoid raw incident text and raw prompt content.
- [ ] Redaction and safe fallback behaviour are covered by tests.

## Suggested release description

```text
Initial portfolio hardening release of Sentinel-AI-AutoTriage.

This release demonstrates a governed, safety-first AI-assisted Microsoft Sentinel triage workflow with dry-run defaults, data minimisation, deterministic policy gates, explicit approval state, metadata-only audit records, benchmark generation and CI-based validation.

Included:
- AI-assisted triage workflow
- Redaction and safe fallback layer
- Recommendation policy gate
- Approval state for sensitive status changes
- Metadata-only audit records
- Benchmark runner
- Architecture documentation
- Threat model
- Demo output documentation
- Quality and security checklist
```

## Post-release actions

- [ ] Add release link to README or portfolio profile.
- [ ] Mention the release in LinkedIn/GitHub updates.
- [ ] Add screenshots or exported benchmark output for recruiter review.
