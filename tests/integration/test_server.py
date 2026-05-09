import requests

from tests.conftest import BASE_URL


def test_health_endpoint(running_server):
    response = requests.get(f"{BASE_URL}/health", timeout=5)
    assert response.status_code == 200


def test_health_payload(running_server):
    data = requests.get(f"{BASE_URL}/health", timeout=5).json()
    assert data["status"] == "ok"
    assert "timestamp" in data
    assert "version" in data
