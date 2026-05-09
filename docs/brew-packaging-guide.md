# Homebrew Packaging Guide

## How Homebrew Formulae Work

A Homebrew formula is a Ruby class that describes how to download, build, and install a piece of software. When you run `brew install foo`, Homebrew:

1. Downloads the source tarball from the URL in the formula
2. Verifies the sha256 checksum
3. Runs the `install` method in a sandboxed temp directory
4. Links the resulting binaries into `$(brew --prefix)/bin`

Formulae live in **tap repositories** — standard git repos with a `Formula/` directory.

---

## Tap Repositories

A tap is just a git repo named `homebrew-<tapname>` on GitHub. Homebrew discovers it via:

```bash
brew tap sdaas/tap
# looks for https://github.com/sdaas/homebrew-tap
```

Once tapped, formulae in it are available by name:

```bash
brew install sdaas/tap/brew-demo
# or just "brew-demo" once tapped
```

The local working clone of the tap is at `~/dev/homebrew-tap`. The `release.sh` script commits formula changes there and pushes to GitHub.

---

## The `brew-demo` Formula

The formula (`~/dev/homebrew-tap/Formula/brew-demo.rb`) installs all three apps from a single formula. Key design decisions:

- **Single formula**: Users run `brew install brew-demo` to get all three binaries.
- **Shared virtualenv**: Both Python apps are installed into one virtualenv in the Homebrew cellar. This avoids duplicating `requests`, `starlette`, etc.
- **Shell client**: Copied directly to `bin/` — no virtualenv needed.
- **`python@3.12`**: Pinned Python version for reproducibility.
- **`rust => :build`**: Required at build time to compile `pydantic-core`.

### Formula structure

```ruby
class BrewDemo < Formula
  include Language::Python::Virtualenv

  url "..."         # GitHub tarball URL — updated by release.sh
  sha256 "..."      # Updated by release.yml GitHub Action

  depends_on "python@3.12"
  depends_on "rust" => :build
  depends_on "jq"

  resource "fastapi" do ... end
  resource "uvicorn" do ... end
  # ... all transitive deps as resource blocks

  def install
    venv = virtualenv_create(libexec, "python3.12")
    venv.pip_install resources
    venv.pip_install_and_link buildpath/"apps/server"
    venv.pip_install_and_link buildpath/"apps/python-client"
    bin.install "apps/shell-client/bin/demo-shell-client"
    inreplace bin/"demo-shell-client", "__VERSION__", version
  end

  service do ... end  # for brew services
  test do ... end     # for brew test
end
```

---

## Brew Services

The `service do` block lets Homebrew manage the server process as a launchd service on macOS:

```bash
brew services start brew-demo   # starts demo-server on boot
brew services stop brew-demo
brew services restart brew-demo
brew services info brew-demo    # shows status, PID, log path
```

Logs go to `$(brew --prefix)/var/log/demo-server.log`.

The service block in the formula:

```ruby
service do
  run [opt_bin/"demo-server", "--port", "8100"]
  keep_alive true
  log_path var/"log/demo-server.log"
  error_log_path var/"log/demo-server.log"
end
```

---

## Formula Testing

Every formula should have a `test do` block — a minimal smoke test that Homebrew runs via `brew test`:

```bash
brew test brew-demo
```

Our test block runs `--version` on all three binaries and verifies the version string matches:

```ruby
test do
  assert_match version.to_s, shell_output("#{bin}/demo-server --version")
  assert_match version.to_s, shell_output("#{bin}/demo-python-client --version")
  assert_match version.to_s, shell_output("#{bin}/demo-shell-client --version")
end
```

The `brew-test.yml` GitHub Action in the tap repo runs this automatically on every push to `main`.

---

## Updating Resource Blocks

When a Python dependency version changes, you need to update the `resource` block in the formula with the new PyPI URL and sha256. The standard Homebrew tool for this is:

```bash
brew update-python-resources brew-demo
```

This auto-fetches the latest PyPI metadata and rewrites all resource blocks. Run it after bumping a dependency version in a release.

---

## Adding a New Python Dependency

1. Add the package to the app's `pyproject.toml`
2. Run `pip install -e "apps/<name>"` locally
3. Get the PyPI sdist URL and sha256:
   ```bash
   pip download "package==version" --no-deps --no-binary :all: -d /tmp/pkgs
   shasum -a 256 /tmp/pkgs/package-version.tar.gz
   ```
4. Add a `resource` block to `brew-demo.rb`
5. Also add any transitive deps that aren't already present
