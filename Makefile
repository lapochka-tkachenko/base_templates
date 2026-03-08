# ── Code quality ──────────────────────────────────────────────────────────────

.PHONY: ruff
ruff:
	ruff check . --fix --config=code_quality/.ruff.toml

.PHONY: ty
ty:
	mypy --config-file=code_quality/mypy.ini .

.PHONY: lint
lint:
	pylint --rcfile=code_quality/pylint.toml .

.PHONY: tests
tests:
	python -m pytest tests/

.PHONY: hooks
hooks:
	pre-commit run --all-files

.PHONY: check
check: hooks ruff ty lint tests
