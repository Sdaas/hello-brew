PYTHON_VERSION := $(shell cat .python-version | tr -d '[:space:]')
PYTHON_MINOR   := $(shell cat .python-version | cut -d. -f1,2)
PYTHON         := python$(PYTHON_MINOR)
VENV           := .venv
BIN            := $(VENV)/bin

.PHONY: install hooks fmt lint shellcheck typecheck test-unit test-integration test clean

install: hooks
	$(PYTHON) -m venv $(VENV)
	$(BIN)/pip install --upgrade pip
	$(BIN)/pip install -e ".[dev]"
	$(BIN)/pip install -e "apps/server[dev]"
	$(BIN)/pip install -e "apps/python-client[dev]"

hooks:
	cp scripts/hooks/pre-commit .git/hooks/pre-commit
	cp scripts/hooks/pre-push .git/hooks/pre-push
	chmod +x .git/hooks/pre-commit .git/hooks/pre-push
	@echo "Git hooks installed"

fmt:
	$(BIN)/black apps/ tests/
	$(BIN)/ruff check --fix apps/ tests/

lint:
	$(BIN)/black --check apps/ tests/
	$(BIN)/ruff check apps/ tests/

shellcheck:
	shellcheck apps/shell-client/bin/demo-shell-client

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
