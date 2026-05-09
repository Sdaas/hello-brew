import re

from demo_server.main import app
from fastapi.testclient import TestClient

client = TestClient(app)


def test_health_status_code():
    response = client.get("/health")
    assert response.status_code == 200


def test_health_payload_keys():
    data = client.get("/health").json()
    assert set(data.keys()) == {"status", "timestamp", "version"}


def test_health_status_ok():
    data = client.get("/health").json()
    assert data["status"] == "ok"


def test_health_version_format():
    data = client.get("/health").json()
    assert re.match(r"\d+\.\d+\.\d+", data["version"])


def test_health_timestamp_format():
    data = client.get("/health").json()
    # e.g. 2026-05-09T12:00:00Z
    assert re.match(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z", data["timestamp"])
