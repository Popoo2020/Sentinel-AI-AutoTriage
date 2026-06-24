# Release Notes: v0.1.0

## Sentinel-AI-AutoTriage

Initial portfolio release of the governed AI-assisted Microsoft Sentinel triage prototype.

## Highlights

- Sentinel incident retrieval workflow
- LLM-assisted incident analysis through a provider abstraction
- Deterministic mock provider for tests and benchmarks
- Pre-LLM sensitive-value redaction examples
- Strict JSON response parsing and safe fallbacks
- Dry-run-first execution model
- Explicit write-action gate
- Deterministic recommendation-policy checks
- Human approval state for sensitive closure paths
- Metadata-only JSONL decision audit trail
- Unit tests and coverage
- Benchmark dataset and summary report generation
- CI workflow with linting, tests, coverage, Bandit SAST, dependency audit and benchmark generation
- Dependabot and CodeQL configuration
- Hiring-manager summary
- Governed AI triage case study

## Positioning

This release is intended as a portfolio-grade prototype demonstrating safe AI-assisted SOC automation, AI security controls, governance-by-design and Microsoft Sentinel-oriented workflow thinking.

It is not intended for unattended production incident closure.
