.PHONY: install dev lint typecheck test test-unit test-integration clean run-api run-cli

install:
	uv sync

dev:
	uv sync --group dev

lint:
	ruff check src/ tests/
	ruff format --check src/ tests/

typecheck:
	mypy src/

test:
	pytest -v

test-unit:
	pytest -v -m "not integration and not slow"

test-integration:
	pytest -v -m integration

clean:
	rm -rf .venv/
	rm -rf __pycache__/
	rm -rf .pytest_cache/
	rm -rf *.egg-info/
	rm -rf dist/
	rm -rf build/
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true

run-api:
	uv run python -m src.research_agent.main

run-cli:
	uv run python -m src.research_agent.cli

docker-build:
	docker compose build

docker-up:
	docker compose up -d

docker-down:
	docker compose down
