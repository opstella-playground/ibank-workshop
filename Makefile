.PHONY: help install dev lint format typecheck test run clean docker-dev docker-prod

# Default target
help:
	@echo "FastAPI Todo Starter - Available Commands"
	@echo "=========================================="
	@echo ""
	@echo "Development:"
	@echo "  make install     - Install dependencies with uv"
	@echo "  make dev         - Run development server with hot-reload"
	@echo "  make run         - Run production server"
	@echo ""
	@echo "Code Quality:"
	@echo "  make lint        - Run ruff linter"
	@echo "  make format      - Format code with ruff"
	@echo "  make typecheck   - Run ty type checker"
	@echo "  make check       - Run all checks (lint + typecheck)"
	@echo ""
	@echo "Testing:"
	@echo "  make test        - Run all tests"
	@echo "  make test-cov    - Run tests with coverage"
	@echo ""
	@echo "Docker:"
	@echo "  make docker-base - Build base Docker image"
	@echo "  make docker-dev  - Run with Docker (development)"
	@echo "  make docker-prod - Run with Docker (production)"
	@echo ""
	@echo "Utilities:"
	@echo "  make clean       - Remove cache files and build artifacts"
	@echo "  make lock        - Update uv.lock file"

# ============================================================================
# Development
# ============================================================================

install:
	uv sync --all-groups

dev:
	uv run fastapi dev app/main.py

run:
	uv run fastapi run app/main.py

# ============================================================================
# Code Quality
# ============================================================================

lint:
	uv run ruff check app tests

lint-fix:
	uv run ruff check app tests --fix

format:
	uv run ruff format app tests

format-check:
	uv run ruff format app tests --check

typecheck:
	uv run ty check app

check: lint-fix format typecheck
	@echo "✅ All checks passed!"

# ============================================================================
# Testing
# ============================================================================

test:
	uv run pytest

test-cov:
	uv run pytest --cov=app --cov-report=term-missing --cov-report=html

# ============================================================================
# Docker
# ============================================================================

docker-dev:
	docker compose -f docker-compose.dev.yml up --build

docker-prod:
	docker compose up --build -d

docker-down:
	docker compose down
	docker compose -f docker-compose.dev.yml down

# ============================================================================
# Utilities
# ============================================================================

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "htmlcov" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type f -name ".coverage" -delete 2>/dev/null || true
	rm -rf dist/ build/ *.egg-info/ 2>/dev/null || true
	@echo "🧹 Cleaned up cache and build files"

lock:
	uv lock
