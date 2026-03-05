# Sentinel‑AI‑AutoTriage

[![CI](https://github.com/your-org/Sentinel-AI-AutoTriage/actions/workflows/ci.yml/badge.svg)](https://github.com/your-org/Sentinel-AI-AutoTriage/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

**Sentinel‑AI‑AutoTriage** is a proof‑of‑concept for automating security
incident triage in Microsoft Sentinel using large language models (LLMs).
The goal is to reduce analyst toil by parsing alerts, extracting key
context, applying scoring rubrics and recommending next actions.  This
repository contains Python scaffolding, a hardened CI pipeline and a
framework for adding parsers, scoring logic and integrations.

## Features

* **Flexible parsing:** The `src/` package (not yet included) is intended
  to house parsers that normalise diverse Sentinel alert formats into a
  consistent schema for analysis.
* **LLM integration:** Future modules will call a generative model to
  summarise incident context and recommend severity scores and confidence
  levels based on a rubric.
* **Scoring framework:** Plans include a scoring rubric that maps
  alert features to severity and confidence ratings, with configurable
  decision thresholds for auto‑closure or escalation.
* **Structured logging:** The project is designed to emit JSON‑formatted
  logs with correlation IDs (e.g. `incident_id`) to aid monitoring and
  troubleshooting.
* **Dry‑run mode:** Coming functionality will allow testing pipelines
  without writing back to Sentinel, printing intended updates instead.

## Quickstart

This project is a starting point and does not yet include a working
implementation.  To contribute or experiment:

1. Clone the repository and set up a virtual environment:

   ```bash
   git clone https://github.com/your‑org/Sentinel‑AI‑AutoTriage.git
   cd Sentinel‑AI‑AutoTriage
   python -m venv .venv && source .venv/bin/activate
   pip install -r requirements.txt
   ```

2. Add your parser and scoring logic under the `src/` directory.
3. Write unit tests under `tests/` to exercise your functions and ensure
   they handle malformed or incomplete data gracefully.  Example test cases
   are provided in `tests/test_parser.py` to get you started.
4. Run the CI workflow locally by executing the commands in
   `.github/workflows/ci.yml` or push your changes to trigger GitHub
   Actions.

## CI & Quality

The repository includes a hardened CI pipeline that:

* Installs dependencies while upgrading `pip` and tolerates optional
  installation failures (e.g. optional GPU packages).
* Runs `pytest` only when tests exist and skips gracefully otherwise.
* Provides a pre‑commit configuration (`.pre-commit-config.yaml`) that
  installs code formatters (`black`, `ruff`) and can be run via `pre‑commit
  run --all-files`.

See `CHANGELOG.md` for a detailed history of improvements.

## Roadmap

1. Implement threat modelling for the auto‑triage pipeline, including data
   flow, trust boundaries and abuse cases (e.g. prompt injection).
2. Develop the scoring rubric and integrate an LLM for summarisation.
3. Add retry logic and rate limiting to safely handle API calls.
4. Introduce a sanitisation layer that redacts sensitive data before
   sending it to the LLM.
5. Build a dry‑run mode and configuration validation.

Your contributions are welcome!  Refer to `CONTRIBUTING.md` for
instructions on opening issues and submitting pull requests.

## Known Limitations

At present, this repository contains scaffolding rather than a full
implementation.  There are no production‑ready parsers or scoring
algorithms, and LLM integration is not yet implemented.  The hardened CI
pipeline will skip tests if none are present, but you must write your own
tests to ensure quality.  Use this project as a foundation and do not
deploy it to handle live incidents without significant development and
validation.
