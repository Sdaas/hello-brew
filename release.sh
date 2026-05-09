#!/usr/bin/env bash
# release.sh — interactive release script for hello-brew
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TAP_DIR="${HOME}/dev/homebrew-tap"
FORMULA="${TAP_DIR}/Formula/brew-demo.rb"
GITHUB_SOURCE="https://github.com/Sdaas/hello-brew"

# Derive Python minor version (e.g. "3.12") from .python-version
PYTHON_MINOR="$(cut -d. -f1,2 < "${REPO_ROOT}/.python-version")"

# ── helpers ───────────────────────────────────────────────────────────────

info()  { echo "  [info]  $*"; }
ok()    { echo "  [ ok ]  $*"; }
die()   { echo "  [FAIL]  $*" >&2; exit 1; }
step()  { echo; echo "══ $* ══"; }

cleanup() {
    if [[ $? -ne 0 ]]; then
        echo "  [FAIL]  Release failed. Resetting modified files..." >&2
        git -C "${REPO_ROOT}" checkout -- \
            apps/server/pyproject.toml \
            apps/python-client/pyproject.toml \
            apps/shell-client/bin/demo-shell-client
    fi
}
trap cleanup EXIT

# ── detect current version from git tags ─────────────────────────────────

latest_tag=$(git -C "${REPO_ROOT}" describe --tags --abbrev=0 2>/dev/null || echo "v0.0.0")
current="${latest_tag#v}"  # strip leading v

IFS='.' read -r major minor patch <<< "${current}"
recommended="${major}.${minor}.$((patch + 1))"

# ── ask for version ───────────────────────────────────────────────────────

echo
echo "Current version : ${current}"
echo "Recommended     : ${recommended}"
echo
read -rp "Release version [${recommended}]: " input_version
VERSION="${input_version:-${recommended}}"

# Validate semver format
if ! [[ "${VERSION}" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
    die "Version must be in X.Y.Z format, got: ${VERSION}"
fi

TAG="v${VERSION}"

echo
echo "Release plan:"
echo "  version   : ${VERSION}"
echo "  git tag   : ${TAG}"
echo "  source    : ${GITHUB_SOURCE}"
echo "  tap       : ${TAP_DIR}"
echo
read -rp "Proceed? [y/N]: " confirm
if [[ "${confirm}" != "y" && "${confirm}" != "Y" ]]; then
    echo "Aborted."
    exit 0
fi

# ── preflight checks ──────────────────────────────────────────────────────

step "Checking git state"
if [[ -n "$(git -C "${REPO_ROOT}" status --porcelain)" ]]; then
    die "Working tree is not clean. Commit or stash your changes first."
fi
ok "Working tree is clean"

if git -C "${REPO_ROOT}" tag | grep -qx "${TAG}"; then
    die "Tag ${TAG} already exists"
fi
ok "Tag ${TAG} is available"

# ── activate venv ─────────────────────────────────────────────────────────

VENV="${REPO_ROOT}/.venv"
if [[ ! -f "${VENV}/bin/python" ]]; then
    die ".venv not found — run 'make install' first"
fi
# shellcheck disable=SC1091
source "${VENV}/bin/activate"

# ── formatting + linting + type checking ─────────────────────────────────

step "Format check"
black --check apps/ tests/
ruff check apps/ tests/
ok "Formatting OK"

step "Type checking"
mypy apps/server/src apps/python-client/src
ok "Type checking OK"

# ── tests ─────────────────────────────────────────────────────────────────

step "Unit tests"
pytest tests/unit/ -v
ok "Unit tests passed"

step "Integration tests"
pytest tests/integration/ -v
ok "Integration tests passed"

# ── bump version in source files ─────────────────────────────────────────

step "Bumping version to ${VERSION}"

bump_pyproject() {
    local file="$1"
    sed -i '' "s/^version = \"[^\"]*\"/version = \"${VERSION}\"/" "${file}"
}

bump_pyproject "${REPO_ROOT}/apps/server/pyproject.toml"
bump_pyproject "${REPO_ROOT}/apps/python-client/pyproject.toml"

# Stamp version into shell client
sed -i '' "s/VERSION=\"__VERSION__\"/VERSION=\"${VERSION}\"/" \
    "${REPO_ROOT}/apps/shell-client/bin/demo-shell-client"

ok "Version bumped in all source files"

# ── build distributions ───────────────────────────────────────────────────

step "Building distributions"
rm -rf "${REPO_ROOT}/dist"
mkdir -p "${REPO_ROOT}/dist"

python -m build "${REPO_ROOT}/apps/server" --outdir "${REPO_ROOT}/dist"
python -m build "${REPO_ROOT}/apps/python-client" --outdir "${REPO_ROOT}/dist"
ok "Distributions built"

ls "${REPO_ROOT}/dist/"

# ── compute tarball sha256 for the GitHub release archive ─────────────────
# The brew formula references the GitHub source tarball, not the wheel.
# We compute its sha256 after tagging & pushing (chicken-and-egg).
# Instead we record a placeholder and update after the push.
# The actual checksum update happens via the release.yml GitHub Action.
# For now, update the formula with the version and a placeholder sha256.

step "Updating Homebrew formula"

# Update version URL
sed -i '' \
    "s|/tags/v[^/]*.tar.gz|/tags/${TAG}.tar.gz|g" \
    "${FORMULA}"

# Update version placeholder if present
sed -i '' \
    "s/__VERSION__/${VERSION}/g" \
    "${FORMULA}"

# Sync python version from .python-version
sed -i '' \
    "s/depends_on \"python@[0-9.]*\"/depends_on \"python@${PYTHON_MINOR}\"/" \
    "${FORMULA}"
sed -i '' \
    "s/virtualenv_create(libexec, \"python[0-9.]*\")/virtualenv_create(libexec, \"python${PYTHON_MINOR}\")/" \
    "${FORMULA}"

ok "Formula updated to ${TAG} (python@${PYTHON_MINOR})"

# ── commit version bumps in source repo ───────────────────────────────────

step "Committing version bump in source repo"
git -C "${REPO_ROOT}" add \
    apps/server/pyproject.toml \
    apps/python-client/pyproject.toml \
    apps/shell-client/bin/demo-shell-client

git -C "${REPO_ROOT}" commit -m "chore: release ${TAG}"
git -C "${REPO_ROOT}" tag "${TAG}"
ok "Committed and tagged ${TAG}"

step "Pushing source repo"
git -C "${REPO_ROOT}" push origin main
git -C "${REPO_ROOT}" push origin "${TAG}"
ok "Source repo pushed"

# ── commit formula update in tap repo ────────────────────────────────────

step "Committing formula update in tap repo"
git -C "${TAP_DIR}" add Formula/brew-demo.rb
git -C "${TAP_DIR}" commit -m "brew-demo ${TAG}"

step "Pushing tap repo"
git -C "${TAP_DIR}" push origin main
ok "Tap repo pushed"

# ── reset shell client placeholder for local dev ──────────────────────────

sed -i '' \
    "s/VERSION=\"${VERSION}\"/VERSION=\"__VERSION__\"/" \
    "${REPO_ROOT}/apps/shell-client/bin/demo-shell-client"

echo
echo "╔══════════════════════════════════════════════════╗"
echo "║  Release ${TAG} complete!                        "
echo "║                                                   "
echo "║  NOTE: The GitHub Actions release.yml workflow    "
echo "║  will compute the tarball sha256 and update the   "
echo "║  formula automatically once the tag is pushed.    "
echo "╚══════════════════════════════════════════════════╝"
echo
echo "  brew update && brew upgrade brew-demo"
echo
