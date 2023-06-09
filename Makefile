install:
	poetry install

test:
	poetry run pytest

build:
	poetry build

clean:
	rm -rf dist

local-install:
	pip install ./dist/datashield-*.tar.gz 
