.PHONY: help install install-dev format lint type-check test coverage clean pre-commit update-deps

# Colors for terminal output
BLUE=\033[0;34m
NC=\033[0m # No Color

help:
	@echo "$(BLUE)Pokemon Showdown AI Development Commands:$(NC)"
	@echo "make install         - Install production dependencies"
	@echo "make install-dev     - Install development dependencies"
	@echo "make format         - Format code with black and ruff"
	@echo "make lint           - Run all linting (ruff, pylint)"
	@echo "make type-check     - Run static type checking"
	@echo "make test           - Run tests"
	@echo "make coverage       - Run tests with coverage report"
	@echo "make check-all      - Run all checks (format, lint, type-check, test)"
	@echo "make clean          - Remove generated files"
	@echo "make pre-commit     - Run pre-commit hooks"
	@echo "make update-deps    - Update dependencies to latest versions"

install:
	poetry install --only main

install-dev:
	poetry install --with dev
	poetry run pre-commit install

format:
	poetry run black .
	poetry run ruff . --fix

lint:
	poetry run ruff .
	poetry run pylint src tests

type-check:
	poetry run mypy

test:
	poetry run pytest

coverage:
	poetry run pytest --cov-report=html:coverage_html --cov-report=xml:coverage.xml

check-all: format lint type-check test

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".ruff_cache" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type d -name ".coverage" -delete
	find . -type d -name "coverage_html" -exec rm -rf {} +
	find . -type f -name "coverage.xml" -delete
	find . -type f -name ".coverage" -delete
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.pyd" -delete
	find . -type f -name ".DS_Store" -delete

pre-commit:
	poetry run pre-commit run --all-files

update-deps:
	poetry update
	poetry run pre-commit autoupdate
