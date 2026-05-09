from demo_python_client.client import fetch_health

from tests.conftest import SERVER_PORT


def test_fetch_health_against_real_server(running_server):
    data = fetch_health(host="localhost", port=SERVER_PORT)
    assert data["status"] == "ok"
    assert "version" in data
    assert "timestamp" in data
