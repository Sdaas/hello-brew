PYTHON := python
VENV   := .venv
BIN    := $(VENV)/bin

.PHONY: install fmt lint typecheck test-unit test-integration test clean

install:
	$(PYTHON) -m venv $(VENV)
	$(BIN)/pip install --upgrade pip
	$(BIN)/pip install -e ".[dev]"
	$(BIN)/pip install -e "apps/server[dev]"
	$(BIN)/pip install -e "apps/python-client[dev]"

fmt:
	$(BIN)/black apps/ tests/
	$(BIN)/ruff check --fix apps/ tests/

lint:
	$(BIN)/black --check apps/ tests/
	$(BIN)/ruff check apps/ tests/

typecheck:
	$(BIN)/mypy apps/server/src apps/python-client/src

test-unit:
	$(BIN)/pytest tests/unit/ -v

test-integration:
	$(BIN)/pytest tests/integration/ -v

test: test-unit test-integration

clean:
	rm -rf $(VENV) dist/ build/ logs/
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name "*.egg-info" -exec rm -rf {} +
