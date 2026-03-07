COMPOSE_DIR = docker_files
COMPOSE      = docker compose -f $(COMPOSE_DIR)/docker-compose.yml
COMPOSE_PG   = docker compose -f $(COMPOSE_DIR)/docker-compose.postgres.yml

# ── Docker ────────────────────────────────────────────────────────────────────

.PHONY: up
up:
	$(COMPOSE) up -d

.PHONY: down
down:
	$(COMPOSE) down

.PHONY: up-pg
up-pg:
	$(COMPOSE_PG) up -d

.PHONY: down-pg
down-pg:
	$(COMPOSE_PG) down

.PHONY: logs
logs:
	$(COMPOSE) logs -f

# ── Django ────────────────────────────────────────────────────────────────────

.PHONY: migrate
migrate:
	python manage.py migrate

.PHONY: migrations
migrations:
	python manage.py makemigrations

.PHONY: run
run:
	python manage.py runserver

# ── Code quality ──────────────────────────────────────────────────────────────

.PHONY: ruff
ruff:
	ruff check . --fix --config=code_quality/.ruff.toml --exclude core --exclude tests --exclude manage.py

.PHONY: ty
ty:
	mypy --config-file=code_quality/mypy.ini apps/

.PHONY: lint
lint:
	pylint --rcfile=code_quality/pylint.toml apps

.PHONY: tests
tests:
	python -m pytest tests/

.PHONY: hooks
hooks:
	pre-commit run --all-files

.PHONY: check
check: hooks ruff ty lint tests
