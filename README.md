# start_templates

A **starter template** for Python backend projects. Clone it, rename it, and start building — all the boilerplate for code quality, testing, and logging is already configured.

## Branch structure

| Branch                | Stack                                                                        |
|-----------------------|------------------------------------------------------------------------------|
| `main`                | Base — linting, mypy, pylint, pytest, pre-commit, logging                    |
| `playwright`          | Base + Playwright E2E test setup                                             |
| `django`              | Base + Django, PostgreSQL, admin, basic app structure                        |
| `django-celery-redis` | Django + Celery + Redis + PostgreSQL + Docker                                |
| `drf-celery-redis`    | Django + DRF + SimpleJWT + Swagger + Celery + Redis + PostgreSQL + Sentry    |

```bash
# clone a specific branch
git clone -b drf-celery-redis <repo-url> my-project
```

### Start your own project from this template

```bash
# 1. clone the branch you need
git clone -b drf-celery-redis <repo-url> my-project
cd my-project

# 2. remove the template remote
git remote remove origin

# 3. add your own remote
git remote add origin <your-repo-url>

# 4. push
git push -u origin main
```

---

## `main` branch — what's included

- **Linting & formatting** — ruff, pylint
- **Type checking** — mypy
- **Testing** — pytest
- **Pre-commit hooks** — all tools run automatically before every commit
- **CI** — GitHub Actions on every pull request
- **Logging** — colorized console output + file handler (`logs/events.log`)

---

## Setup

```bash
pip install -r requirements/requirements_dev
pre-commit install
```

---

## Makefile

```bash
make ruff     # lint + autofix
make ty       # mypy type check
make lint     # pylint
make tests    # pytest
make hooks    # pre-commit --all-files
make check    # hooks + ruff + ty + lint + tests
```

---

## Code quality

Config files in `code_quality/`:

| Tool    | Config                     | Purpose                                |
|---------|----------------------------|----------------------------------------|
| ruff    | `code_quality/.ruff.toml`  | Linting + formatting (auto-fix)        |
| mypy    | `code_quality/mypy.ini`    | Static type checking                   |
| pylint  | `code_quality/pylint.toml` | Deep static analysis (fails below 8.0) |

### Run manually

```bash
ruff check --fix --config=code_quality/.ruff.toml
ruff format --config=code_quality/.ruff.toml
mypy --config-file=code_quality/mypy.ini .
pylint --rcfile=code_quality/pylint.toml .
```

---

## Pre-commit

Hooks run automatically before each commit in this order:

1. check-yaml, end-of-file-fixer, trailing-whitespace, debug-statements
2. **ruff** — lint + autofix
3. **ruff-format** — formatting
4. **mypy** — type check
5. **pylint** — static analysis
6. **pytest** — run tests

```bash
pre-commit run              # run on staged files
pre-commit run --all-files  # run on all files
pre-commit run ruff         # run specific hook
```

---

## Tests

```bash
make tests
# or
pytest tests/ -q
pytest tests/test_example.py::test_something  # specific test
pytest -s                                      # show output
```

---

## CI

Configured in `.github/workflows/ci.yml`. Runs on every pull request.

| Job     | Command                              |
|---------|--------------------------------------|
| ruff    | `ruff check` + `ruff format --check` |
| mypy    | `mypy .`                             |
| pylint  | `pylint .`                           |
| pytest  | `pytest tests/ -q`                   |

---

## Logging

Configured in `core/logger.py`.

- **Console** — colorized via `colorlog`, level `DEBUG`
- **File** — `logs/events.log`, level `INFO`

```python
from core.logger import logger

logger.info("Something happened")
logger.debug("Debug details")
```
