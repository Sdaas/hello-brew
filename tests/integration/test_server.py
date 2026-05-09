import subprocess
import sys
import time

import pytest
import requests

SERVER_PORT = 18100
BASE_URL = f"http://localhost:{SERVER_PORT}"


@pytest.fixture(scope="module")
def running_server(tmp_path_factory):
    log_dir = str(tmp_path_factory.mktemp("logs"))
    proc = subprocess.Popen(
        [
            sys.executable,
            "-m",
            "demo_server.cli",
            "--port",
            str(SERVER_PORT),
        ],
        env={**__import__("os").environ, "DEMO_LOG_DIR": log_dir},
    )
    # Wait for server to be ready
    for _ in range(20):
        try:
            requests.get(f"{BASE_URL}/health", timeout=1)
            break
        except Exception:
            time.sleep(0.3)
    yield proc
    proc.terminate()
    proc.wait()


def test_health_endpoint(running_server):
    response = requests.get(f"{BASE_URL}/health", timeout=5)
    assert response.status_code == 200


def test_health_payload(running_server):
    data = requests.get(f"{BASE_URL}/health", timeout=5).json()
    assert data["status"] == "ok"
    assert "timestamp" in data
    assert "version" in data
