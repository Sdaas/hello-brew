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
1. Installs git hooks from `scripts/hooks/` into `.git/hooks/`
2. `python -m venv .venv`
3. `pip install -e ".[dev]"` — installs dev tools
4. `pip install -e "apps/server[dev]"` — editable server install
5. `pip install -e "apps/python-client"` — editable client install

All binaries resolve to repo-local code. Running `demo-server` (if activated) uses the editable install, not any globally installed version.

### Git Hooks

Hooks are stored in `scripts/hooks/` (tracked in git) and installed automatically by `make install`. To reinstall them without a full setup:

```bash
make hooks
```

| Hook | When it runs | What it checks |
|---|---|---|
| `pre-commit` | Before every commit | Unit tests |
| `pre-push` | Before every push | shellcheck → format → type check → integration tests |

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

## Quality Gates

Quality is enforced at three stages of the development workflow. Each stage adds checks appropriate to that point in the process.

### Stage 1 — pre-commit (before every commit)

Runs automatically on `git commit`. Must be fast.

| Check | Tool | Command |
|---|---|---|
| Unit tests | pytest | `make test-unit` |

If this fails, the commit is blocked. Fix the failing tests before committing.

### Stage 2 — pre-push (before every push)

Runs automatically on `git push`. Ordered cheapest-first so failures surface quickly.

| Check | Tool | Command | Why here and not pre-commit |
|---|---|---|---|
| Shell script lint | shellcheck | `make shellcheck` | Fast, but rarely breaks on small commits |
| Format + imports | black, ruff | `make lint` | Formatting drift is a push-time concern |
| Type checking | mypy | `make typecheck` | Slower than unit tests |
| Integration tests | pytest | `make test-integration` | Require a real server; too slow for every commit |

Unit tests are intentionally excluded here — pre-commit already ran them.

To run any of these manually:

```bash
make shellcheck
make lint
make typecheck
make test-integration
```

### Stage 3 — release.sh (before tagging a release)

These checks run after the formula is updated locally but before anything is pushed. They catch formula-level problems that only surface when Homebrew actually processes the file.

| Check | Command | What it catches |
|---|---|---|
| Formula lint | `brew audit --strict` | DSL errors, policy violations, dependency ordering |
| Formula style | `brew style` | RuboCop formatting issues |
| Full install | `brew install --build-from-source` | Virtualenv build, missing resources, broken installs |
| Formula tests | `brew test` | `test do` block — verifies installed binaries run and report the correct version |
| Linkage check | `brew linkage` | Broken dynamic library references |

If any of these fail, the release is aborted before any commits or tags are created.

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
8. Runs Homebrew formula quality gates: `brew audit --strict`, `brew style`, `brew install --build-from-source`, `brew test`, `brew linkage`
9. Commits + tags + pushes source repo
10. Commits + pushes tap repo
11. The `release.yml` GitHub Action computes the tarball sha256 and updates the formula automatically

### Prerequisites: GitHub Secrets

The `release.yml` Action checks out and pushes to the `Sdaas/homebrew-tap` repo. It authenticates using a personal access token stored as a repository secret. This must be configured once before the first release:

1. **Create a personal access token** at https://github.com/settings/tokens
   - Click "Generate new token" → "Generate new token (classic)"
   - Name: e.g. `homebrew-tap access`
   - Scopes: check `repo` (full control of private repositories)
   - Click "Generate token" and copy the value

2. **Add it as a repository secret** in `Sdaas/hello-brew`:
   - Go to Settings → Secrets and variables → Actions → **Secrets** tab
   - Click "New repository secret"
   - Name: `TAP_GITHUB_TOKEN`
   - Value: paste the token
   - Click "Add secret"

Without this secret the Action will fail and the formula sha256 will not be updated, causing `brew install` to fail.

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
