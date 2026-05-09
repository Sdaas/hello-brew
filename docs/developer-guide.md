# Developer Guide

## Repo Architecture

```
hello-brew/
├── apps/
│   ├── server/                    FastAPI REST server
│   │   ├── pyproject.toml
│   │   └── src/demo_server/
│   │       ├── __init__.py        version string
│   │       ├── cli.py             argparse entrypoint
│   │       ├── main.py            FastAPI app + middleware
│   │       └── logging_config.py  logging setup
│   ├── python-client/             requests-based CLI client
│   │   ├── pyproject.toml
│   │   └── src/demo_python_client/
│   │       ├── __init__.py
│   │       ├── cli.py
│   │       └── client.py
│   └── shell-client/
│       └── bin/demo-shell-client  bash + curl + jq
├── tests/
│   ├── unit/                      fast, no real network
│   └── integration/               spins up real server on port 18100
├── .github/workflows/
│   ├── ci.yml                     lint + test on push/PR
│   └── release.yml                build + update tap on v* tag
├── pyproject.toml                 dev tooling (black, ruff, mypy, pytest)
├── Makefile
└── release.sh
```

Each Python app has its own `pyproject.toml` and is independently installable. The root `pyproject.toml` only carries dev tooling deps and pytest config.

---

## Local Development Setup

Requires: [pyenv](https://github.com/pyenv/pyenv), Python 3.12, `jq`

```bash
git clone https://github.com/Sdaas/hello-brew
cd hello-brew

# pyenv picks up .python-version automatically
pyenv install 3.12.10   # if not already installed

make install            # creates .venv and installs all packages in editable mode
```

`make install` runs:
1. `python -m venv .venv`
2. `pip install -e ".[dev]"` — installs dev tools
3. `pip install -e "apps/server[dev]"` — editable server install
4. `pip install -e "apps/python-client"` — editable client install

All binaries resolve to repo-local code. Running `demo-server` (if activated) uses the editable install, not any globally installed version.

---

## Running the Apps Locally

```bash
# Activate venv first
source .venv/bin/activate

demo-server --verbose
demo-python-client
demo-shell-client
```

Or without activation:

```bash
.venv/bin/demo-server
.venv/bin/demo-python-client
apps/shell-client/bin/demo-shell-client
```

---

## Testing Strategy

Tests never rely on globally installed binaries. Integration tests start the server via `sys.executable` (the venv Python), ensuring repo-local code is always used.

### Unit Tests

- Server: route responses, CLI parsing, logging config
- Python client: CLI parsing, mock server responses (pytest-httpserver)
- Shell client: argument parsing via subprocess

```bash
make test-unit
# or
.venv/bin/pytest tests/unit/ -v
```

### Integration Tests

All integration tests start `demo-server` on port **18100** (not 8100) to avoid conflict with a running dev server.

```bash
make test-integration
# or
.venv/bin/pytest tests/integration/ -v
```

### All Tests

```bash
make test
```

---

## Dependency Management

Each app declares its own runtime deps in `pyproject.toml`. Dev deps (black, ruff, mypy, pytest, pytest-httpserver) live in the root `pyproject.toml`.

To add a dependency to an app:
1. Add it to the app's `pyproject.toml` under `[project] dependencies`
2. Run `.venv/bin/pip install -e "apps/<name>"` to install it
3. Add the corresponding `resource` block to `~/dev/homebrewclau-tap/Formula/brew-demo.rb` with the PyPI URL and sha256

---

## Release Process

See [release.sh](../release.sh). Run:

```bash
./release.sh
```

The script:
1. Detects the latest git tag and recommends the next patch version
2. Asks you to confirm the version and proceed
3. Validates clean git state
4. Runs format check, lint, type check, unit tests, integration tests
5. Bumps version in all source files
6. Builds Python distributions
7. Updates the formula URL in `~/dev/homebrew-tap`
8. Commits + tags + pushes source repo
9. Commits + pushes tap repo
10. The `release.yml` GitHub Action computes the tarball sha256 and updates the formula automatically

---

## Debugging Tips

**Port already in use:**
```bash
lsof -i :18100 | grep LISTEN
kill -9 <PID>
```

**Stale `.pyc` / import errors:**
```bash
make clean && make install
```

**pytest can't find modules:**
Make sure you ran `make install` and the venv is active, or use `.venv/bin/pytest`.

**Formula syntax error:**
```bash
ruby -c ~/dev/homebrew-tap/Formula/brew-demo.rb
```
