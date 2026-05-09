import os
import subprocess
import sys
import time

import pytest
import requests

SERVER_PORT = 18100
BASE_URL = f"http://localhost:{SERVER_PORT}"


@pytest.fixture(scope="session")
def running_server(tmp_path_factory):
    log_dir = str(tmp_path_factory.mktemp("logs"))
    proc = subprocess.Popen(
        [sys.executable, "-m", "demo_server.cli", "--port", str(SERVER_PORT)],
        env={**os.environ, "DEMO_LOG_DIR": log_dir},
    )
    for _ in range(20):
        try:
            requests.get(f"{BASE_URL}/health", timeout=1)
            break
        except Exception:
            time.sleep(0.3)
    else:
        proc.terminate()
        pytest.fail(f"Server failed to start on port {SERVER_PORT} within 6 seconds")
    yield proc
    proc.terminate()
    try:
        proc.wait(timeout=5)
    except subprocess.TimeoutExpired:
        proc.kill()
