.PHONY: help setup run test check clean docs compose-up compose-down build-lib

PYTHON ?= python

help:
	@echo "setup  - install project dependencies"
	@echo "run    - start desktop application"
	@echo "test   - run automated tests"
	@echo "check  - run all local checks"
	@echo "docs   - validate documentation sources"
	@echo "build-lib - validate reusable core package"
	@echo "compose-up - build and run container checks"
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

check: test build-lib docs

docs:
	$(PYTHON) -c "from pathlib import Path; required=['docs/specification.md','docs/architecture.md','docs/domain.md','docs/diagrams/context.mmd','docs/diagrams/order-sequence.mmd']; missing=[p for p in required if not Path(p).exists()]; assert not missing, missing"

compose-up:
	docker compose -f infra/compose.yaml up --build

compose-down:
	docker compose -f infra/compose.yaml down

clean:
	$(PYTHON) -c "import shutil; [shutil.rmtree(p, ignore_errors=True) for p in ['.pytest_cache','__pycache__','app/__pycache__','packages/__pycache__','packages/core/__pycache__','tests/__pycache__','tests/unit/__pycache__','tests/integration/__pycache__','db']]"
