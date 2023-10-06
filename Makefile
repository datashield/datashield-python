install:
	poetry install

test:
	poetry run pytest

build:
	poetry build

publish:
	poetry publish --build

clean:
	rm -rf dist

local-install:
	pip install ./dist/datashield-*.tar.gz 
