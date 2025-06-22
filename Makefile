.PHONY: lint lint-check format format-check serve-docs build-docs build

lint:
	pipenv run ruff check --fix icecap

lint-check:
	pipenv run ruff check icecap
	pipenv run mypy icecap

format:
	pipenv run ruff format icecap

format-check:
	pipenv run ruff format --check icecap

serve-docs:
	pipenv run mkdocs serve

build-docs:
	pipenv run mkdocs build

build:
	pipenv run python -m build