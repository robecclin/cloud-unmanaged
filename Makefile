.PHONY: check clean format install upgrade

check:
	uv run yamllint .
	uv run ruff check
	uv run ruff format --check
	uv run vulture
	uv run ty check
	uv run mypy
	uv run coverage run -m pytest
	uv run coverage report

clean:
	rm -rf .coverage .mypy_cache .pytest_cache .ruff_cache
	find src tests -type d -name __pycache__ -prune -exec rm -rf {} +

format:
	uv run ruff check --fix
	uv run ruff format

install:
	uv sync --locked

upgrade:
	uv sync --upgrade
