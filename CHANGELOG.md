# Changelog

All notable changes to **Sentinel-AI-AutoTriage** are documented in this file.

## [Unreleased] - 2026-05-13

### Added
- Deterministic pre-LLM redaction layer for common secret-like, email and IPv4 values.
- Expanded test suite covering:
  - LLM JSON parsing and safe fallbacks
  - redaction behaviour
  - dry-run and write-gate logic
  - Sentinel incident filtering and update handling
  - enum and string-form status handling
- `requirements-dev.txt` for CI and local development tooling.
- `.env.example` with explicit dry-run-safe configuration defaults.
- `.gitignore` for local secrets, virtual environments, logs, coverage and caches.
- Complete MIT `LICENSE` file.
- `samples/sample_incident.json` showing redaction-aware triage input.

### Changed
- Refactored incident handling into smaller, testable workflow functions.
- Hardened status comparison logic so SDK enum and string responses are handled consistently.
- Simplified runtime dependencies to direct project requirements only.
- Modernised CI to enforce linting, full tests and coverage reporting.
- Cleaned the Sentinel SDK wrapper and improved defensive handling around missing incident properties.
- Updated the package exports to expose a valid public API surface.

## [0.1.0] - 2026-03-01

### Added
- Initial public Microsoft Sentinel triage prototype.
- LLM-assisted recommendation flow with structured JSON parsing and safe fallbacks.
- Dry-run-first operating mode with explicit write-action gating.
- Basic project documentation, architecture overview and CI foundation.
