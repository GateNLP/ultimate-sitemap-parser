.PHONY: test
test:
	poetry run pytest

.PHONY: lint
lint:
	poetry run ruff check --fix

.PHONY: format
format:
	poetry run ruff format