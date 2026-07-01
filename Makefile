.PHONY: check clean install upgrade

check:
	uv run yamllint .
	uv run ruff check
	uv run ruff format --check
	uv run vulture
	uv run ty check
	uv run pyright
	uv run mypy
	uv run coverage run -m pytest
	uv run coverage report

clean:
	rm -rf .coverage .mypy_cache .pytest_cache .ruff_cache
	find . -type d -name __pycache__ -exec rm -rf {} +

install:
	uv sync --locked

upgrade:
	uv sync --upgrade
