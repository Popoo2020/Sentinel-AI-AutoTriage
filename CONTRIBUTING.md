# Contributing

Thanks for your interest in improving **Sentinel-AI-AutoTriage**.

This repository is intentionally security-focused and conservative. Contributions should strengthen safe LLM-assisted triage, not turn the project into an unattended incident-closure engine.

## Good contribution areas

- safer parsing and fallback behaviour,
- redaction improvements,
- deterministic recommendation-policy tests,
- approval workflow modelling,
- metadata-only audit improvements,
- benchmark cases,
- deployment and least-privilege documentation.

## Contribution rules

Before opening a pull request:

1. keep `AUTO_APPLY_CHANGES=false` as the safe default,
2. do not include real incident data, credentials, tokens or private customer information,
3. add tests for behaviour changes,
4. keep audit records metadata-only,
5. document any change that can affect write-path safety,
6. keep README claims aligned with implemented behaviour.

## Local validation

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
ruff check src tests
pytest -q --cov=src --cov-report=term-missing
python -m src.benchmark
```

## Security expectations

Pull requests that change write gating, approval behaviour, policy decisions, provider handling or audit logging should clearly explain the safety impact and include targeted tests.
