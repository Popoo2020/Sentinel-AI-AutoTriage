.PHONY: lint test security audit benchmark validate

lint:
	ruff check src tests

test:
	pytest -q --cov=src --cov-report=term-missing

security:
	bandit -r src -ll

audit:
	pip-audit -r requirements.txt

benchmark:
	python -m src.benchmark
	test -f reports/triage_benchmark_summary.md

validate: lint test security audit benchmark
