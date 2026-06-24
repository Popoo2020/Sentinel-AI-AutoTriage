# Changelog

All notable changes to **Sentinel-AI-AutoTriage** are documented in this file.

## [Unreleased] - 2026-06-24

### Added
- Release checklist for creating a GitHub `v0.1.0` release.
- Version notes and portfolio release guidance.
- QA, security and operations documentation for employer/client review.

## [Portfolio Hardening] - 2026-05-14

### Added
- Deterministic pre-LLM redaction layer for common secret-like, email and IPv4 values.
- Recommendation-policy checks that prevent weak or ambiguous closure recommendations from being acted on.
- Explicit human-approval state for closure recommendations through `src/approval.py`.
- Metadata-only JSONL decision log with configurable local path via `TRIAGE_AUDIT_LOG_PATH`.
- Approval metadata fields in decision audit records, including whether approval was required, the approval state and approver label when present.
- Non-blocking handling for decision-log file errors so local logging issues do not interrupt triage processing.
- Injectable completion-provider boundary through `src/providers.py`.
- `StaticMockProvider` for deterministic tests and benchmark execution without external model calls.
- Enterprise-provider extension boundary scaffold in `src/azure_provider.py`.
- Deterministic benchmark dataset in `benchmarks/triage_cases.json`.
- Benchmark runner and Markdown-summary generation in `src/benchmark.py`.
- Expanded test suite covering LLM parsing, redaction, provider injection, dry-run logic, policy checks, approval handling, audit records, benchmark behaviour and Sentinel status handling.
- `requirements-dev.txt` for CI and local development tooling.
- `.env.example` with dry-run-safe configuration defaults, optional decision-log path and controlled approval metadata fields.
- `.gitignore` for local secrets, virtual environments, logs, JSONL audit files, coverage and caches.
- Complete MIT `LICENSE` file.
- `samples/sample_incident.json` showing redaction-aware triage input.
- Technical walkthrough, demo output, decision-audit example, benchmark overview, deployment guide and provider-extension notes.
- Architecture documentation, threat model, quality/security checklist, version notes and Makefile validation target.

### Changed
- Refactored incident handling into smaller, testable workflow functions.
- Hardened status comparison logic so SDK enum and string responses are handled consistently.
- Simplified runtime dependencies to direct project requirements only.
- Modernised CI to enforce linting, tests, coverage reporting, static review, dependency review and deterministic benchmark generation.
- Cleaned the Sentinel SDK wrapper and improved defensive handling around missing incident properties.
- Updated the package exports to expose approval, audit, provider, redaction and recommendation-policy helpers.
- Refreshed the README to reflect redaction, recommendation checks, explicit approval, provider abstraction, deterministic benchmarking and the hardened workflow.
- Updated `SECURITY.md` to document responsible use, recommendation-policy checks, approval state, provider boundary and metadata-only audit safeguards.

## [0.1.0] - 2026-03-01

### Added
- Initial public Microsoft Sentinel triage prototype.
- LLM-assisted recommendation flow with structured JSON parsing and safe fallbacks.
- Dry-run-first operating mode with explicit change gating.
- Basic project documentation, architecture overview and CI foundation.
