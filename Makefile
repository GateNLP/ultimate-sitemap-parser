.PHONY: test
test:
	uv run pytest

.PHONY: integ
integ:
	uv run pytest --integration tests/integration --durations 0

.PHONY: mem
mem:
	uv run pytest --memray --memray-bin-path memray --integration tests/integration

.PHONY: prof
prof:
	uv run pyinstrument -m pytest --integration tests/integration

.PHONY: lint
lint:
	uv run ruff check --fix

.PHONY: format
format:
	uv run ruff format