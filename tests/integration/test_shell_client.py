import subprocess
from pathlib import Path

from tests.conftest import SERVER_PORT

SCRIPT = str(Path(__file__).parents[2] / "apps" / "shell-client" / "bin" / "demo-shell-client")


def test_shell_client_health(running_server):
    result = subprocess.run(
        [SCRIPT, "--host", "localhost", "--port", str(SERVER_PORT)],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert '"status"' in result.stdout
    assert '"ok"' in result.stdout


def test_shell_client_verbose(running_server):
    result = subprocess.run(
        [SCRIPT, "--host", "localhost", "--port", str(SERVER_PORT), "--verbose"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "GET http://localhost" in result.stderr
