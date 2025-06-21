.PHONY: lint lint-check format format-check docs

lint:
	pipenv run ruff check --fix icecap

lint-check:
	pipenv run ruff check icecap
	pipenv run mypy icecap

format:
	pipenv run ruff format icecap

format-check:
	pipenv run ruff format --check icecap

docs:
	pipenv run mkdocs serve