# Changelog

## [Unreleased]

### Added
- Added GitHub Actions CI workflow
- Minimal smoke tests to improve CI stability
- Unit test for IncidentSummary.as_prompt



### Changed
- Normalized Unicode dashes in documentation
- CI now fails on test errors
-  CI now installs pytest for unit tests
-  
- Hardened CI workflow to avoid false failures: upgrade pip, conditionally install requirements, ensure pytest is installed, and skip tests when pytest or test directory is missing
