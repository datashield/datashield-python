install:
	uv sync

test:
	uv run pytest

build:
	uv build

publish:
	uv publish

clean:
	rm -rf dist

local-install:
	pip install ./dist/datashield-*.tar.gz
