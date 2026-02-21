# start_templates

A **starter template** for Python backend projects. Clone it, rename it, and start building — all the boilerplate for code quality, testing, and logging is already configured.

## Branch structure

This repository uses a **branch-per-template** approach. Each branch is a ready-to-use starting point for a specific stack. The `main` branch is the base — it contains shared config (linting, CI, logging) that all other branches build on top of.

| Branch       | Description                        |
|--------------|------------------------------------|
| `main`       | Base template (this branch)        |
| `playwright` | Base + Playwright E2E test setup   |

To start a new project from a specific template:

```bash
git clone -b playwright <repo-url> my-project
```

## What's included

- **Linting & formatting** — ruff, pylint
- **Type checking** — mypy
- **Testing** — pytest with async support
- **Pre-commit hooks** — all tools run automatically before every commit
- **CI** — GitHub Actions on every pull request
- **Logging** — colorized console output + file handler

---

## Setup

```bash
pip install -r requirements/requirements_dev
pre-commit install
```

---

## Code Quality

Config files live in `code_quality/`.

| Tool         | Config                      | Purpose                                   |
|--------------|-----------------------------|-------------------------------------------|
| ruff         | `code_quality/.ruff.toml`   | Linting + import sorting (auto-fix)       |
| ruff format  | `code_quality/.ruff.toml`   | Code formatting                           |
| mypy         | `code_quality/mypy.ini`     | Static type checking                      |
| pylint       | `code_quality/pylint.toml`  | Deep static analysis (fails below 8.0)    |

### Run manually

```bash
ruff check --fix --config=code_quality/.ruff.toml
ruff format --config=code_quality/.ruff.toml
mypy --config-file=code_quality/mypy.ini apps/
pylint --rcfile=code_quality/pylint.toml apps/
```

---

## Pre-commit

Hooks run automatically before each commit in this order:

1. **ruff** — lint + autofix
2. **ruff-format** — formatting
3. **mypy** — type check
4. **pylint** — static analysis
5. **pytest** — run tests

### Run manually

```bash
# Run all hooks on changed files
pre-commit run

# Run all hooks on all files
pre-commit run --all-files

# Run a specific hook
pre-commit run ruff --all-files
pre-commit run pytest --all-files
```

### Skip hooks (not recommended)

```bash
git commit -m "message" --no-verify
```

---

## Tests

Config: `pytest.ini`

```ini
asyncio_mode = auto   # async test support
pythonpath = .        # project root in PYTHONPATH
testpaths = tests     # test directory
```

### Run

```bash
pytest                            # all tests
pytest tests/ -q                  # quiet mode
pytest tests/test_example.py      # specific file
pytest tests/test_example.py::test_something  # specific test
pytest -s                         # show print/log output
```

---

## CI

Configured in `.github/workflows/ci.yml`. Runs on every **pull request**.

Each job runs independently on `ubuntu-latest` with Python 3.13:

| Job     | Command                                      |
|---------|----------------------------------------------|
| ruff    | `ruff check` + `ruff format --check`         |
| mypy    | `mypy apps/`                                 |
| pylint  | `pylint apps/`                               |
| pytest  | `pytest tests/ -q`                           |

> Note: ruff in CI does **not** auto-fix — it only checks. Fixes happen locally via pre-commit.

---

## Logging

Configured in `core/logger.py`.

- **Console** — colorized via `colorlog`, level `DEBUG`
- **File** — `logs/events.log`, level `INFO`
- `event_logger` — named logger for application events, inherits both handlers

```python
from core.logger import logger

logger.info("Something happened")
logger.debug("Debug details")
```