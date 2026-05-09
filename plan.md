# Implementation Plan: hello-brew

## Phase 1 — Repo Foundation ✅
- [x] `.python-version` (3.12)
- [x] Root `pyproject.toml` — dev tooling only (black, ruff, mypy, pytest, pytest-httpserver)
- [x] `Makefile` — targets: `install`, `fmt`, `lint`, `typecheck`, `test-unit`, `test-integration`, `clean`
- [x] `logs/` directory (git-ignored)
- [x] `.gitignore`

## Phase 2 — Server (`apps/server/`) ✅
- [x] `apps/server/pyproject.toml` — FastAPI + uvicorn, entry point `demo-server`
- [x] `apps/server/src/demo_server/__init__.py`
- [x] `apps/server/src/demo_server/main.py` — FastAPI app, `GET /health`
- [x] `apps/server/src/demo_server/cli.py` — argparse: `--port 8100`, `--verbose`, `--version`, `--help`
- [x] `apps/server/src/demo_server/logging_config.py` — text logging to `logs/demo-server.log`
- [x] `tests/unit/test_server_routes.py`
- [x] `tests/unit/test_server_cli.py`
- [x] `tests/unit/test_server_logging.py`
- [x] `tests/integration/test_server.py` — subprocess startup + real HTTP on port 18100

## Phase 3 — Python Client (`apps/python-client/`) ✅
- [x] `apps/python-client/pyproject.toml` — requests, entry point `demo-python-client`
- [x] `apps/python-client/src/demo_python_client/__init__.py`
- [x] `apps/python-client/src/demo_python_client/client.py` — calls GET /health, prints formatted JSON
- [x] `apps/python-client/src/demo_python_client/cli.py` — argparse: `--host`, `--port`, `--verbose`, `--version`, `--help`
- [x] `tests/unit/test_python_client_cli.py`
- [x] `tests/unit/test_python_client.py` — mock server (pytest-httpserver)
- [x] `tests/integration/test_python_client.py` — real server on port 18100

## Phase 4 — Shell Client (`apps/shell-client/`) ✅
- [x] `apps/shell-client/bin/demo-shell-client` — bash, curl + jq
- [x] Supports: `--help`, `--version`, `--verbose`, `--host localhost`, `--port 8100`
- [x] Version placeholder `VERSION="__VERSION__"` for release.sh substitution
- [x] `tests/unit/test_shell_client.py` — arg parsing via subprocess
- [x] `tests/integration/test_shell_client.py` — real server on port 18100

## Phase 5 — Homebrew Formula ✅
- [x] `~/dev/homebrew-tap/Formula/brew-demo.rb`
- [x] Depends on `python@3.12`
- [x] Single virtualenv: installs both Python apps
- [x] Copies `demo-shell-client` to `bin/`
- [x] `service do` block for `demo-server`
- [x] `test do` block: `--version` on all three binaries

## Phase 6 — Release Script ✅
- [x] `release.sh` — interactive: detect latest tag, recommend next patch, confirm, then run all steps
- [x] Steps: clean git check, fmt/lint/typecheck, tests, version bump, build, checksum, update formula, commit+tag+push source, commit+push tap

## Phase 7 — CI/CD ✅
- [x] `.github/workflows/ci.yml` — lint, typecheck, unit + integration tests (triggers: push + PR to main)
- [x] `.github/workflows/release.yml` — build, checksum, update tap, push tap (trigger: v* tag push)
- [x] `~/dev/homebrew-tap/.github/workflows/brew-test.yml` — brew install + brew test (trigger: push to main)

## Phase 8 — Documentation ✅
- [x] `README.md` — overview, architecture, install, brew services, dev quickstart, troubleshooting
- [x] `docs/developer-guide.md`
- [x] `docs/brew-packaging-guide.md`
- [x] `docs/python-packaging-guide.md`
