# hello-brew

A reference-quality monorepo demonstrating how to build, test, package, and release Python and shell CLI applications via Homebrew.

---

## Contents

| App | Language | Description |
|---|---|---|
| `demo-server` | Python (FastAPI) | REST API server — `GET /health` |
| `demo-python-client` | Python (requests) | Client that calls the server |
| `demo-shell-client` | Bash (curl + jq) | Shell client that calls the server |

All three are installed by a single Homebrew formula: `sdaas/tap/brew-demo`.

> **Note:** `demo-server` is intended for local development use only. It does not support TLS and should not be exposed to external networks.

---

## Architecture

```
hello-brew/
├── apps/
│   ├── server/           FastAPI server (demo-server)
│   ├── python-client/    Python client (demo-python-client)
│   └── shell-client/     Bash client (demo-shell-client)
├── tests/
│   ├── unit/             Unit tests (pytest)
│   └── integration/      Integration tests (real server on port 18100)
├── .github/workflows/    CI/CD (ci.yml, release.yml)
├── pyproject.toml        Dev tooling deps
├── Makefile              Dev targets
└── release.sh            Interactive release script
```

---

## Installation via Homebrew

```bash
brew tap sdaas/tap
brew install brew-demo
```

This installs all three binaries: `demo-server`, `demo-python-client`, `demo-shell-client`.

---

## Usage

### Server

```bash
# Start directly
demo-server
demo-server --port 9000
demo-server --verbose

# Start as a Homebrew service
brew services start brew-demo

# Stop
brew services stop brew-demo

# Restart
brew services restart brew-demo

# Check status
brew services info brew-demo
```

The server listens on port `8100` by default and exposes:

```
GET /health  →  { "status": "ok", "timestamp": "...", "version": "..." }
```

### Python Client

```bash
demo-python-client
demo-python-client --host localhost --port 8100
demo-python-client --verbose
```

### Shell Client

```bash
demo-shell-client
demo-shell-client --host localhost --port 8100
demo-shell-client --verbose
```

---

## Updating

```bash
brew update && brew upgrade brew-demo
```

---

## Troubleshooting

**Server won't start:**
Check if port 8100 is already in use:
```bash
lsof -i :8100
```

**`brew services` doesn't show brew-demo:**
```bash
brew tap sdaas/tap
brew reinstall brew-demo
```

**Logs:**
- When installed via Homebrew: `$(brew --prefix)/var/log/demo-server.log`
- During local development: `logs/demo-server.log` inside the repo

---

## Development Quickstart

```bash
git clone https://github.com/Sdaas/hello-brew
cd hello-brew

# Requires pyenv with Python 3.12 installed
make install

# Run all tests
make test

# Format + lint + typecheck
make fmt lint typecheck
```

See [docs/developer-guide.md](docs/developer-guide.md) for full details.
