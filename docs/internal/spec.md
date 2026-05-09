# Project Specification: Homebrew-Packaged Python + Shell Applications Demo

## Objective

Create a reference-quality repository that demonstrates modern best practices for:

- Python application development
- Shell script development
- Packaging applications as Homebrew formulae
- Managing dependencies and versions
- Automated testing
- Automated releases
- Homebrew service management

The repository should function as both:

1. A working production-quality example
2. A teaching/reference project

The implementation should prioritize:

- simplicity
- maintainability
- reproducibility
- developer ergonomics
- automation
- minimal manual release steps

---

# High-Level Requirements

The repository must contain three independently installable command-line applications:

- demo-server : Python  REST API server 
- demo-python-client : Python Client for the server ( uses request )
- demo-shell-client : curl-based shell client

All applications must be installable through Homebrew.

---

# Functional Requirements

# 1. Python Server (`demo-server`)

Implement a Python REST server.

## Requirements

### API

Implement:

```http
GET /health
```

Response:

- HTTP 200
- JSON payload containing:
  - status
  - timestamp
  - version

Example:

```json
{
  "status": "ok",
  "timestamp": "2026-05-09T12:00:00Z",
  "version": "1.0.0"
}
```

---

## CLI Requirements

The server CLI must support:

```bash
demo-server --help
demo-server --version
demo-server --verbose
demo-server --port 8100
```

Default port:

```text
8100
```

---

## Logging

All incoming HTTP requests must be logged.

Requirements:

- structured logging preferred
- logs written to a file
- log location configurable
- logs stored inside the repo during development
- logs stored in an OS-appropriate location when installed via brew

---

## Execution Modes

The server must support:

### Direct execution

Example:

```bash
demo-server
```

### Homebrew service management

Example:

```bash
brew services start demo-server
brew services stop demo-server
brew services restart demo-server
```

The Homebrew formula must define a proper `service do` block.

---

## Suggested Implementation

Preferred stack:

- FastAPI
- uvicorn

Alternative lightweight frameworks acceptable if simpler.

---

# 2. Python Client (`demo-python-client`)

Implement a Python CLI client that calls:

```http
GET /health
```

using the Python `requests` library.

---

## CLI Requirements

Support:

```bash
demo-python-client --help
demo-python-client --version
demo-python-client --verbose
demo-python-client --port 8100
demo-python-client --host localhost
```

Defaults:

- host: `localhost`
- port: `8100`

---

## Output

Print formatted JSON response to stdout.

Example:

```json
{
  "status": "ok",
  "timestamp": "...",
  "version": "1.0.0"
}
```

---

# 3. Shell Client (`demo-shell-client`)

Implement a shell script CLI that calls:

```http
GET /health
```

using `curl`.

---

## CLI Requirements

Support:

```bash
demo-shell-client --help
demo-shell-client --version
demo-shell-client --verbose
demo-shell-client --port 8100
demo-shell-client --host localhost
```

---

# Repository Structure

The repository should use a clean monorepo layout.

Recommended structure:

```text
.
├── apps/
│   ├── server/
│   ├── python-client/
│   └── shell-client/
├── tests/
│   ├── unit/
│   └── integration/
├── scripts/
├── Formula/
├── docs/
├── pyproject.toml
├── Makefile
├── release.sh
└── README.md
```

---

# Packaging Requirements

# Homebrew Packaging

Create Homebrew formulae for:

- demo-server
- demo-python-client
- demo-shell-client

Use best practices for:

- Python virtualenv packaging
- shell script installation
- dependency declaration
- version pinning
- formula testing

---

## Tap Repository

Formulae must be deployable to:

GitHub:

```text
https://github.com/Sdaas/homebrew-tap
```

Local clone:

```text
~/dev/homebrew-tap
```

---

# Dependency Management

# Python Packaging

Use modern Python standards:

- `pyproject.toml`
- PEP 621
- setuptools or hatchling
- editable installs for development

Preferred:

```bash
pip install -e ".[dev]"
```

---

## Tooling

Use:

| Purpose | Tool |
|---|---|
| formatting | black |
| linting | ruff |
| type checking | mypy |
| testing | pytest |
| mock server testing | pytest-httpserver |
| packaging | build |
| automation | Makefile |

---

# Testing Requirements

# Unit Tests

Implement unit tests for:

- CLI parsing
- server routes
- logging
- error handling

---

# Integration Tests

Implement integration tests for:

- real server startup
- client-to-server communication
- shell client execution
- brew-installed binaries

---

# Mock Server Testing

## Python Client

Must support testing against a mock HTTP server.

Requirements:

- use pytest fixtures
- avoid real network dependencies

---

## Shell Client

Must support testing against:

- mock HTTP server
- subprocess execution

---

# Critical Development Requirement

Developers may already have previous brew-installed versions.

The repository must ensure:

- local development always uses repo-local code
- tests never accidentally execute globally installed binaries

Preferred techniques:

- editable installs
- `python -m ...`
- explicit PATH isolation in tests

---

# Release Automation

# Fully Automated Release Process

Implement a single script:

```bash
./release.sh <version>
```

No manual release steps allowed.

---

## Responsibilities of release.sh

The script must:

1. validate clean git state
2. run formatting checks
3. run linting
4. run type checking
5. run unit tests
6. run integration tests
7. build distributions
8. generate/update checksums
9. update Homebrew formulae
10. commit version updates
11. create git tag
12. push source repo
13. push tap repo

---

# CI/CD Requirements

Create GitHub Actions workflows.

Minimum workflows:

| Workflow | Purpose |
|---|---|
| ci.yml | lint + tests |
| release.yml | automated release |
| brew-test.yml | formula validation |

---

# Documentation Requirements

# README.md

Must include:

- project overview
- architecture diagram
- installation instructions
- Homebrew usage
- brew services usage
- update instructions
- troubleshooting
- development quickstart

---

# docs/developer-guide.md

Must include:

- repo architecture
- local development
- testing strategy
- dependency management
- release process
- debugging tips

---

# docs/brew-packaging-guide.md

Must explain:

- how Homebrew formulae work
- tap repositories
- brew services
- formula testing
- packaging strategy

---

# docs/python-packaging-guide.md

Must explain:

- pyproject.toml
- editable installs
- dependency management
- version management
- entry points
- packaging workflow

---

# Quality Expectations

The repository should resemble a production-quality open source project.

Prioritize:

- clarity
- maintainability
- automation
- reproducibility
- good developer UX

Avoid:

- unnecessary complexity
- excessive abstraction
- hidden magic

Important: 

- Brew service management should be used wheere applicable
- Developers may already have a brew-installed version - Tests and local runs MUST always use repo-local code.
- Never rely on globally installed binaries during development.
---

# Deliverables

The final repository must include:

- working applications
- tests
- formulae
- CI/CD
- release automation
- complete documentation

Everything should work end-to-end on a clean macOS machine with Homebrew installed.




