.PHONY: lint lint-check format format-check

lint:
	pipenv run ruff check --fix icecap

lint-check:
	pipenv run ruff check icecap

format:
	pipenv run ruff format icecap

format-check:
	pipenv run ruff format --check icecap
