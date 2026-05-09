import json
import logging

import requests

logger = logging.getLogger(__name__)

DEFAULT_HOST = "localhost"
DEFAULT_PORT = 8100


def fetch_health(host: str = DEFAULT_HOST, port: int = DEFAULT_PORT, timeout: int = 5) -> dict:  # type: ignore[type-arg]
    url = f"http://{host}:{port}/health"
    logger.debug("GET %s", url)
    response = requests.get(url, timeout=timeout)
    response.raise_for_status()
    return response.json()  # type: ignore[no-any-return]


def print_health(host: str = DEFAULT_HOST, port: int = DEFAULT_PORT) -> None:
    data = fetch_health(host=host, port=port)
    print(json.dumps(data, indent=2))
