# Changelog

All notable changes to **Sentinel-AI-AutoTriage** are documented in this file.

## [Unreleased] - 2026-05-14

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
- Expanded test suite covering:
  - LLM JSON parsing and safe fallbacks,
  - redaction behaviour,
  - provider injection and deterministic mock completions,
  - dry-run and explicit mode logic,
  - recommendation-policy allow/block behaviour,
  - explicit approval allow/block behaviour,
  - metadata-only audit record creation and JSONL writing,
  - non-blocking audit I/O failure handling,
  - deterministic benchmark behaviour and summary rendering,
  - Sentinel incident filtering and update handling,
  - enum and string-form status handling,
  - required environment configuration,
  - incident-summary rendering.
- `requirements-dev.txt` for CI and local development tooling.
- `.env.example` with dry-run-safe configuration defaults, optional decision-log path and controlled approval metadata fields.
- `.gitignore` for local secrets, virtual environments, logs, JSONL audit files, coverage and caches.
- Complete MIT `LICENSE` file.
- `samples/sample_incident.json` showing redaction-aware triage input.
- `docs/technical-walkthrough.md` explaining the hardened architecture and test philosophy.
- `docs/sample-dry-run-output.md` showing a dry-run transcript with redaction, recommendation checks, approval blocking and zero applied updates.
- `docs/decision-audit-example.md` showing a metadata-only decision-log example with approval fields.
- `docs/benchmark-overview.md` explaining deterministic benchmark scope and limits.
- `docs/deployment-guide.md` describing conservative deployment posture and least-privilege design notes.
- `docs/provider-extension.md` describing the provider boundary and future enterprise-adapter path.

### Changed
- Refactored incident handling into smaller, testable workflow functions.
- Hardened status comparison logic so SDK enum and string responses are handled consistently.
- Simplified runtime dependencies to direct project requirements only.
- Modernised CI to enforce linting, full tests, coverage reporting and deterministic benchmark generation.
- Cleaned the Sentinel SDK wrapper and improved defensive handling around missing incident properties.
- Updated the package exports to expose approval, audit, provider, redaction and recommendation-policy helpers.
- Refreshed the architecture diagram and README to reflect redaction, recommendation checks, explicit approval, provider abstraction, deterministic benchmarking and the full hardened workflow.
- Updated `SECURITY.md` to document responsible use, recommendation-policy checks, approval state, provider boundary and metadata-only audit safeguards.

## [0.1.0] - 2026-03-01

### Added
- Initial public Microsoft Sentinel triage prototype.
- LLM-assisted recommendation flow with structured JSON parsing and safe fallbacks.
- Dry-run-first operating mode with explicit change gating.
- Basic project documentation, architecture overview and CI foundation.
