# Python Packaging Guide

## `pyproject.toml`

This project uses the modern PEP 621 standard for Python packaging. Every Python app has its own `pyproject.toml`. There is no `setup.py` or `setup.cfg`.

Minimal structure:

```toml
[build-system]
requires = ["setuptools>=68"]
build-backend = "setuptools.build_meta"

[project]
name = "demo-server"
version = "0.1.0"
requires-python = ">=3.12"
dependencies = [
    "fastapi>=0.111",
    "uvicorn>=0.30",
]

[project.scripts]
demo-server = "demo_server.cli:main"

[tool.setuptools.packages.find]
where = ["src"]
```

Key sections:
- `[build-system]` — declares setuptools as the build backend
- `[project]` — PEP 621 metadata (name, version, deps)
- `[project.scripts]` — declares CLI entrypoints; pip creates wrapper scripts in `bin/`
- `[tool.setuptools.packages.find]` — tells setuptools where source packages live

---

## Editable Installs

During development, apps are installed in **editable mode**:

```bash
pip install -e "apps/server[dev]"
```

This means Python resolves imports directly from `apps/server/src/` on disk. Changes to source code take effect immediately — no reinstall needed. The `[dev]` extra installs test-only deps (`httpx` for the server).

This is what `make install` does for both Python apps.

---

## Entry Points

The `[project.scripts]` table maps a CLI name to a Python callable:

```toml
[project.scripts]
demo-server = "demo_server.cli:main"
```

When installed, pip generates a wrapper script at `.venv/bin/demo-server` that calls `demo_server.cli.main()`. This is how you get a `demo-server` command without any shell wrappers.

The callable (`main`) must be importable and accept no arguments (or use `sys.argv` internally). Our `main()` functions accept an optional `argv` list for testability.

---

## Dependency Management

Runtime deps go in `[project] dependencies`. Dev-only deps (httpx, pytest, etc.) go in `[project.optional-dependencies]`:

```toml
[project.optional-dependencies]
dev = [
    "httpx>=0.27",
]
```

Install with: `pip install -e "apps/server[dev]"`

The root `pyproject.toml` holds shared dev tooling (black, ruff, mypy, pytest, pytest-httpserver) that applies across the whole repo.

---

## Version Management

The version string lives in two places per app, kept in sync:

1. `pyproject.toml` → `[project] version = "0.1.0"`
2. `src/<package>/__init__.py` → `__version__ = "0.1.0"`

The `__init__.py` version is what the CLI exposes via `--version` and what the `/health` endpoint returns.

`release.sh` updates both files using `sed` at release time.

The shell client's version is a `VERSION="__VERSION__"` placeholder in the script, also replaced by `release.sh`.

---

## Building Distributions

To build a wheel and sdist:

```bash
pip install build
python -m build apps/server --outdir dist/
python -m build apps/python-client --outdir dist/
```

This produces `.tar.gz` (sdist) and `.whl` (wheel) files in `dist/`. The Homebrew formula references the GitHub source tarball (not PyPI), so the `dist/` output is mainly used to verify the build is clean.

---

## `src/` Layout

Both Python apps use the `src/` layout:

```
apps/server/
├── pyproject.toml
└── src/
    └── demo_server/
        ├── __init__.py
        ├── cli.py
        ├── main.py
        └── logging_config.py
```

The `src/` layout prevents accidentally importing the package from the repo root without installing it first. This catches import path bugs early and keeps the editable install honest.

---

## Testing Isolation

Tests use `sys.executable` to start subprocesses, ensuring the venv Python is always used:

```python
subprocess.Popen([sys.executable, "-m", "demo_server.cli", "--port", "18100"])
```

This guarantees tests never accidentally pick up a globally installed `demo-server` binary.
