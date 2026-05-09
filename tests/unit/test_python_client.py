import json

import pytest
from demo_python_client.client import fetch_health
from pytest_httpserver import HTTPServer


@pytest.fixture()
def health_server(httpserver: HTTPServer):
    payload = {"status": "ok", "timestamp": "2026-05-09T12:00:00Z", "version": "0.1.0"}
    httpserver.expect_request("/health").respond_with_data(
        json.dumps(payload), content_type="application/json"
    )
    return httpserver


def test_fetch_health_returns_dict(health_server):
    data = fetch_health(host="localhost", port=health_server.port)
    assert isinstance(data, dict)


def test_fetch_health_status(health_server):
    data = fetch_health(host="localhost", port=health_server.port)
    assert data["status"] == "ok"


def test_fetch_health_version(health_server):
    data = fetch_health(host="localhost", port=health_server.port)
    assert data["version"] == "0.1.0"


def test_fetch_health_connection_error():
    with pytest.raises(Exception):
        fetch_health(host="localhost", port=19999, timeout=1)
