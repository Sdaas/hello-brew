import subprocess
from pathlib import Path

SCRIPT = str(Path(__file__).parents[2] / "apps" / "shell-client" / "bin" / "demo-shell-client")


def run(*args: str) -> subprocess.CompletedProcess:  # type: ignore[type-arg]
    return subprocess.run([SCRIPT, *args], capture_output=True, text=True)


def test_help_exits_zero():
    result = run("--help")
    assert result.returncode == 0


def test_help_contains_usage():
    result = run("--help")
    assert "Usage:" in result.stdout


def test_version_exits_zero():
    result = run("--version")
    assert result.returncode == 0


def test_version_contains_version_string():
    result = run("--version")
    # VERSION placeholder not yet substituted in dev; just check the binary name is present
    assert "demo-shell-client" in result.stdout


def test_unknown_option_exits_nonzero():
    result = run("--not-a-flag")
    assert result.returncode != 0


def test_verbose_flag_accepted():
    # --verbose alone will fail trying to reach server, but flag parsing itself is fine
    result = run("--verbose", "--host", "localhost", "--port", "19999")
    # Should print the URL to stderr before failing on connection
    assert "GET http://localhost:19999/health" in result.stderr
