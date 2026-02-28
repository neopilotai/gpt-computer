# GPT Computer Development Makefile
# Using uv for lightning-fast package management

SHELL := /bin/bash

# Color codes for terminal output
COLOR_RESET=\033[0m
COLOR_CYAN=\033[1;36m
COLOR_GREEN=\033[1;32m
COLOR_YELLOW=\033[1;33m
COLOR_RED=\033[1;31m

# Configuration
MODEL ?= gpt-4o
PROJECT_NAME := gpt-computer

.PHONY: help install update run test test-cov lint format fix type-check clean clean-all build cloc check \
	docker-build docker-runtime-build docker-run docker-test docker-push docker-compose-up

.DEFAULT_GOAL := help

# --- Docker ---
DOCKER_IMAGE ?= gpt-computer
DOCKER_TAG ?= latest
DOCKER_FULL_IMAGE := $(DOCKER_IMAGE):$(DOCKER_TAG)

docker-build: ## Build the minimal CLI docker image
	@echo -e "$(COLOR_CYAN)Building minimal CLI docker image...$(COLOR_RESET)"
	docker build --target cli -t $(DOCKER_FULL_IMAGE) -f docker/Dockerfile .

docker-runtime-build: ## Build the full runtime docker image (with SearXNG, VNC, etc.)
	@echo -e "$(COLOR_CYAN)Building full runtime docker image...$(COLOR_RESET)"
	docker build --target full-runtime -t $(DOCKER_IMAGE)-runtime:$(DOCKER_TAG) -f docker/Dockerfile .

docker-run: ## Run the CLI docker image (requires OPENAI_API_KEY and name=<project>)
	@if [ -z "$(name)" ]; then \
		echo -e "$(COLOR_RED)Error: Please specify a project name. Example: make docker-run name=calculator$(COLOR_RESET)"; \
		exit 1; \
	fi
	@echo -e "$(COLOR_CYAN)Running GPT Computer in Docker on project $(COLOR_GREEN)$(name)$(COLOR_CYAN)...$(COLOR_RESET)"
	docker run -it --rm \
		-e OPENAI_API_KEY=$(OPENAI_API_KEY) \
		-v $(PWD)/projects/$(name):/project \
		$(DOCKER_FULL_IMAGE)

docker-test: ## Test the docker image by checking the help command
	@echo -e "$(COLOR_CYAN)Testing docker image...$(COLOR_RESET)"
	docker run --rm $(DOCKER_FULL_IMAGE) --help

docker-push: ## Push the docker image to a registry
	@echo -e "$(COLOR_CYAN)Pushing docker image $(COLOR_FULL_IMAGE)...$(COLOR_RESET)"
	docker push $(DOCKER_FULL_IMAGE)

docker-compose-up: ## Start services using docker-compose
	@echo -e "$(COLOR_CYAN)Starting services with docker-compose...$(COLOR_RESET)"
	docker-compose up --build

# --- Help ---
help: ## Display this help message
	@echo -e "$(COLOR_CYAN)Usage:$(COLOR_RESET)"
	@echo -e "  make $(COLOR_GREEN)<target>$(COLOR_RESET)"
	@echo ""
	@echo -e "$(COLOR_CYAN)Targets:$(COLOR_RESET)"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[32m%-20s\033[0m %s\n", $$1, $$2}'

# --- Installation ---
install: ## Install dependencies (dev + docs) and setup pre-commit
	@echo -e "$(COLOR_CYAN)Installing $(PROJECT_NAME) dependencies with uv...$(COLOR_RESET)"
	uv sync --group dev --group docs
	@echo -e "$(COLOR_CYAN)Setting up pre-commit hooks...$(COLOR_RESET)"
	uv run pre-commit install
	@echo -e "$(COLOR_GREEN)Installation complete!$(COLOR_RESET)"

update: ## Update dependencies and lockfile
	@echo -e "$(COLOR_CYAN)Updating dependencies...$(COLOR_RESET)"
	uv lock --upgrade
	uv sync --group dev --group docs
	@echo -e "$(COLOR_GREEN)Update complete!$(COLOR_RESET)"

# --- Quality & Linting ---
check: lint type-check ## Run all quality checks (lint + type-check)

lint: ## Run linter (ruff)
	@echo -e "$(COLOR_CYAN)Running linter (ruff)...$(COLOR_RESET)"
	uv run ruff check .

format: ## Check formatting (ruff)
	@echo -e "$(COLOR_CYAN)Checking formatting (ruff)...$(COLOR_RESET)"
	uv run ruff format . --check

fix: ## Run auto-fixers (lint + format)
	@echo -e "$(COLOR_CYAN)Applying auto-fixes...$(COLOR_RESET)"
	uv run ruff check . --fix
	uv run ruff format .
	@echo -e "$(COLOR_GREEN)Fixes applied!$(COLOR_RESET)"

type-check: ## Run type checker (mypy)
	@echo -e "$(COLOR_CYAN)Running type checker (mypy)...$(COLOR_RESET)"
	uv run mypy gpt_computer

# --- Testing ---
test: ## Run unit tests
	@echo -e "$(COLOR_CYAN)Running tests...$(COLOR_RESET)"
	uv run pytest

test-cov: ## Run tests with coverage report
	@echo -e "$(COLOR_CYAN)Running tests with coverage...$(COLOR_RESET)"
	uv run pytest --cov=gpt_computer --cov-report=term-missing --cov-report=html
	@echo -e "$(COLOR_GREEN)Coverage report generated in htmlcov/index.html$(COLOR_RESET)"

# --- Execution ---
# Usage: make run name=calculator MODEL=gemini-1.5-pro
name ?= 
run: ## Run GPT Computer on a project (use name=<folder>)
	@if [ -z "$(name)" ]; then \
		echo -e "$(COLOR_RED)Error: Please specify a project name. Example: make run name=calculator$(COLOR_RESET)"; \
		exit 1; \
	fi
	@echo -e "$(COLOR_CYAN)Running GPT Computer on $(COLOR_GREEN)$(name)$(COLOR_CYAN) with model $(COLOR_GREEN)$(MODEL)$(COLOR_CYAN)...$(COLOR_RESET)"
	uv run gpt-computer main projects/$(name) --model $(MODEL)

run-auto: ## Run GPT Computer in autonomous mode
	@echo -e "$(COLOR_CYAN)Running GPT Computer in $(COLOR_YELLOW)AUTONOMOUS$(COLOR_CYAN) mode with model $(COLOR_GREEN)$(MODEL)$(COLOR_CYAN)...$(COLOR_RESET)"
	uv run gpt-computer main --autonomous --model $(MODEL)

bench: ## Run benchmarks
	@echo -e "$(COLOR_CYAN)Running benchmarks...$(COLOR_RESET)"
	uv run bench

# --- Cleanup ---
clean: ## Remove temporary python files
	@echo -e "$(COLOR_YELLOW)Cleaning up temporary files...$(COLOR_RESET)"
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache .ruff_cache .mypy_cache

clean-all: clean ## Remove all build artifacts and virtualenv
	@echo -e "$(COLOR_RED)Removing build artifacts and virtualenv...$(COLOR_RESET)"
	rm -rf .venv dist build *.egg-info htmlcov .coverage

# --- Utilities ---
build: ## Build the package
	@echo -e "$(COLOR_CYAN)Building package...$(COLOR_RESET)"
	uv build

cloc: ## Count lines of code
	@if command -v cloc > /dev/null; then \
		cloc . --exclude-dir=node_modules,dist,build,.mypy_cache,benchmark,.venv --exclude-list-file=.gitignore --fullpath --not-match-d='docs/_build' --by-file; \
	else \
		echo -e "$(COLOR_RED)Error: 'cloc' is not installed.$(COLOR_RESET)"; \
	fi

# Helper for debugging environment
env-info: ## Show information about the python environment
	@echo -e "$(COLOR_CYAN)Python path:$(COLOR_RESET) $$(uv run which python)"
	@echo -e "$(COLOR_CYAN)Python version:$(COLOR_RESET) $$(uv run python --version)"
	@echo -e "$(COLOR_CYAN)Installed packages:$(COLOR_RESET)"
	@uv pip list
