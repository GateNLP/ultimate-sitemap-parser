.PHONY: test
test:
	poetry run pytest

.PHONY: integ
integ:
	poetry run pytest --integration tests/integration --durations 0

.PHONY: mem
mem:
	poetry run pytest --memray --memray-bin-path memray --integration tests/integration

.PHONY: prof
prof:
	poetry run pyinstrument -m pytest --integration tests/integration

.PHONY: lint
lint:
	poetry run ruff check --fix

.PHONY: format
format:
	poetry run ruff format