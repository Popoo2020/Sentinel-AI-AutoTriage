# Changelog

All notable changes to **Sentinel-AI-AutoTriage** are documented in this file.

## [Unreleased] - 2026-05-13

### Added
- Deterministic pre-LLM redaction layer for common secret-like, email and IPv4 values.
- Recommendation-policy checks that prevent weak or ambiguous closure recommendations from being acted on.
- Metadata-only JSONL decision log with configurable local path via `TRIAGE_AUDIT_LOG_PATH`.
- Non-blocking handling for decision-log file errors so local logging issues do not interrupt triage processing.
- Expanded test suite covering:
  - LLM JSON parsing and safe fallbacks,
  - redaction behaviour,
  - dry-run and explicit mode logic,
  - recommendation-policy allow/block behaviour,
  - metadata-only audit record creation and JSONL writing,
  - non-blocking audit I/O failure handling,
  - Sentinel incident filtering and update handling,
  - enum and string-form status handling,
  - required environment configuration,
  - incident-summary rendering.
- `requirements-dev.txt` for CI and local development tooling.
- `.env.example` with dry-run-safe configuration defaults and optional decision-log path.
- `.gitignore` for local secrets, virtual environments, logs, JSONL audit files, coverage and caches.
- Complete MIT `LICENSE` file.
- `samples/sample_incident.json` showing redaction-aware triage input.
- `docs/technical-walkthrough.md` explaining the hardened architecture and test philosophy.
- `docs/sample-dry-run-output.md` showing a dry-run transcript with redaction, policy evaluation and zero applied updates.
- `docs/decision-audit-example.md` showing a metadata-only decision-log example.

### Changed
- Refactored incident handling into smaller, testable workflow functions.
- Hardened status comparison logic so SDK enum and string responses are handled consistently.
- Simplified runtime dependencies to direct project requirements only.
- Modernised CI to enforce linting, full tests and coverage reporting.
- Cleaned the Sentinel SDK wrapper and improved defensive handling around missing incident properties.
- Updated the package exports to expose a valid public API surface, including redaction and recommendation-policy helpers.
- Refreshed the architecture diagram and README to reflect redaction, policy gating, decision logging and the full hardened workflow.
- Updated `SECURITY.md` to document responsible use, policy checks and metadata-only audit safeguards.

## [0.1.0] - 2026-03-01

### Added
- Initial public Microsoft Sentinel triage prototype.
- LLM-assisted recommendation flow with structured JSON parsing and safe fallbacks.
- Dry-run-first operating mode with explicit change gating.
- Basic project documentation, architecture overview and CI foundation.
