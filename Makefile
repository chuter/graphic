.PHONY: help init test ci flake8 publish


.DEFAULT: help
help:
	@echo make init
	@echo        prepare development environment, use only once
	@echo make test
	@echo        run tests
	@echo make flake8
	@echo        run flake8
	@echo make coverage
	@echo        run test coverage report
	@echo make test-readme
	@echo        test whether the readme can be rendered by pypi
	@echo make doc
	@echo        build sphinx documentation
	@echo make publish
	@echo        upload to pypi


init:
	pip install pipenv --upgrade
	pipenv install --dev --skip-lock
test:
	# This runs all of the tests
	detox
ci:
	pipenv run py.test -n 8 --junitxml=report.xml

flake8:
	pipenv run flake8 --exclude=.tox,*.egg,build,data .

coverage:
	pipenv run py.test --cov-config .coveragerc --verbose --cov-report term --cov-report xml tests

test-readme:
	pip install --upgrade twine
	python setup.py sdist
	twine check dist/*

publish:
	twine upload dist/*
	rm -fr build dist .egg
