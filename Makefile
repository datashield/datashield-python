install:
	uv sync --extra dev

test:
	uv run pytest

lint:
	uv run ruff check .

fix:
	uv run ruff check . --fix

build:
	uv build

publish:
	uv publish

clean:
	rm -rf dist

local-install:
	pip install ./dist/datashield-*.tar.gz
