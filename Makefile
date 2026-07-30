.DEFAULT_GOAL := help

COMPOSE_FILE ?=  -f docker/docker-compose.yml -f docker/docker-compose.dev.yml
COMPOSE := docker compose $(COMPOSE_FILE) --project-directory .
RUN := $(COMPOSE) run --rm app
EXEC := $(COMPOSE) exec app

.PHONY: help up down build logs shell format format-fix lint typecheck \
        test test-unit test-integration coverage migrate-up revision health clean \
		migrate-down revision-history

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-16s\033[0m %s\n", $$1, $$2}'

up: ## Start all services in the background
	$(COMPOSE) up -d

down: ## Stop and remove all services
	$(COMPOSE) down

clean: ## Stop and remove all services
	$(COMPOSE) down -v --remove-orphans

build: ## Build (or rebuild) the application image
	$(COMPOSE) build

logs: ## Tail logs from all services
	$(COMPOSE) logs -f

shell: ## Open a shell inside the running app container
	$(EXEC) /bin/bash

format: ## Check formatting without making changes
	$(RUN) black -l 120 --check .

format-fix: ## Reformat the codebase
	$(RUN) black -l 120 .

lint: ## Run ruff
	$(RUN) ruff check .

typecheck: ## Run mypy
	$(RUN) mypy app

test: ## Run the full test suite
	$(RUN) pytest

test-unit: ## Run unit tests only
	$(RUN) pytest tests/unit

test-integration: ## Run integration tests only (requires db/minio running)
	$(COMPOSE) up -d db minio
	$(RUN) pytest tests/integration

test-file: ## Run specific test file (usage: make test-file file=tests/unit/models)
	$(RUN) pytest $(file)

coverage: ## Run tests with coverage report
	$(RUN) pytest --cov=app --cov-report=term-missing

migrate-up: ## Apply database migrations
	$(COMPOSE) up -d db
	$(RUN) alembic upgrade head

revision: ## Generate a new Alembic revision (usage: make revision msg="message")
	$(COMPOSE) up -d db
	$(RUN) alembic revision --autogenerate -m "$(msg)"

migrate-down: ## Apply database migrations
	$(COMPOSE) up -d db
	$(RUN) alembic downgrade -1

revision-history: ## Show Alembic revision history
	$(COMPOSE) up -d db
	$(RUN) alembic history

health: ## Curl the running app's health endpoint
	curl -sf http://localhost:8000/health
