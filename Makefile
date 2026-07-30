install:
	uv sync

run: install
	uv run python3 -m src

lint: install
	uv run flake8 src
	uv run mypy src --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs

lint-strict: install
	uv run flake8 src
	uv run mypy src --strict

clean:
	rm -rf */*__pycache__ */*/*__pycache__
	rm -rf .mypy_cache
	rm -rf .venv

.PHONY: venv install run debug lint lint-strict clean