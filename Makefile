.PHONY: setup test lint typecheck format check-templates check spec

setup:
	uv sync --locked

test:
	uv run --locked python scripts/tasks.py test

lint:
	uv run --locked python scripts/tasks.py lint

typecheck:
	uv run --locked python scripts/tasks.py typecheck

format:
	uv run --locked python scripts/tasks.py format

check-templates:
	uv run --locked python scripts/tasks.py check-templates

check:
	uv run --locked python scripts/tasks.py check

spec:
	uv run --locked python scripts/tasks.py spec
