import subprocess
import sys
import time

import pytest
import requests
from demo_python_client.client import fetch_health

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


def test_fetch_health_against_real_server(running_server):
    data = fetch_health(host="localhost", port=SERVER_PORT)
    assert data["status"] == "ok"
    assert "version" in data
    assert "timestamp" in data
