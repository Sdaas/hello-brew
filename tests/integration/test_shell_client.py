import subprocess
import sys
import time
from pathlib import Path

import pytest
import requests

SCRIPT = str(Path(__file__).parents[2] / "apps" / "shell-client" / "bin" / "demo-shell-client")
SERVER_PORT = 18100
BASE_URL = f"http://localhost:{SERVER_PORT}"


@pytest.fixture(scope="module")
def running_server(tmp_path_factory):
    log_dir = str(tmp_path_factory.mktemp("logs"))
    proc = subprocess.Popen(
        [sys.executable, "-m", "demo_server.cli", "--port", str(SERVER_PORT)],
        env={**__import__("os").environ, "DEMO_LOG_DIR": log_dir},
    )
    for _ in range(20):
        try:
            requests.get(f"{BASE_URL}/health", timeout=1)
            break
        except Exception:
            time.sleep(0.3)
    yield proc
    proc.terminate()
    proc.wait()


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
