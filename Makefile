.PHONY: help setup run test check clean docs compose-up compose-down docker-gui-smoke build-lib install-lib-local publish-lib-testpypi

PYTHON ?= python

help:
	@echo "setup  - install project dependencies"
	@echo "run    - start desktop application"
	@echo "test   - run automated tests"
	@echo "check  - run all local checks"
	@echo "docs   - build Sphinx documentation"
	@echo "build-lib - validate reusable core package"
	@echo "install-lib-local - install reusable package locally"
	@echo "publish-lib-testpypi - build and publish package to TestPyPI"
	@echo "compose-up - build and run container checks"
	@echo "docker-gui-smoke - run Tkinter smoke test in Docker"
	@echo "compose-down - stop container checks"
	@echo "clean  - remove generated local files"

setup:
	$(PYTHON) -m pip install -r requirements.txt

run:
	$(PYTHON) main.py

test:
	$(PYTHON) -m unittest discover -s tests

build-lib:
	$(PYTHON) -m py_compile packages/core/order_logic.py
	$(PYTHON) -c "import packages.core as core; assert core.calculate_order_total([core.OrderLine(1, 1, 10)]) == 10"

install-lib-local:
	$(PYTHON) -m pip install -e .

publish-lib-testpypi:
	$(PYTHON) -m pip install build twine
	$(PYTHON) -m build
	$(PYTHON) -m twine upload --repository testpypi dist/*

check: test build-lib docs

docs:
	$(PYTHON) -m sphinx -b html docs docs/_build/html

compose-up:
	docker compose -f infra/compose.yaml up --build

docker-gui-smoke:
	docker compose -f infra/compose.yaml --profile gui run --rm gui-smoke

compose-down:
	docker compose -f infra/compose.yaml down

clean:
	$(PYTHON) -c "import shutil; [shutil.rmtree(p, ignore_errors=True) for p in ['.pytest_cache','__pycache__','app/__pycache__','packages/__pycache__','packages/core/__pycache__','tests/__pycache__','tests/unit/__pycache__','tests/integration/__pycache__','tests/smoke/__pycache__','db','build','dist','furniture_store_core.egg-info']]"
