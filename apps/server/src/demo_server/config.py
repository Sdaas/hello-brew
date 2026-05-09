"""
Reads server config from a key=value file.

Search order (first file found wins):
  1. $DEMO_SERVER_CONFIG  (explicit override, useful in tests)
  2. ~/.config/demo-server/config  (user config, dev and brew-service use)
  3. $HOMEBREW_PREFIX/etc/demo-server.conf  (brew-managed system config)

Only PORT is supported today. Lines starting with '#' are ignored.
"""

import os
from pathlib import Path

DEFAULT_PORT = 8100


def _candidate_paths() -> list[Path]:
    paths: list[Path] = []

    env_override = os.environ.get("DEMO_SERVER_CONFIG")
    if env_override:
        paths.append(Path(env_override))

    paths.append(Path.home() / ".config" / "demo-server" / "config")

    prefix = os.environ.get("HOMEBREW_PREFIX", "/usr/local")
    paths.append(Path(prefix) / "etc" / "demo-server.conf")

    return paths


def load_port() -> int:
    for path in _candidate_paths():
        if not path.exists():
            continue
        for line in path.read_text().splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" in line:
                key, _, value = line.partition("=")
                if key.strip().upper() == "PORT":
                    try:
                        return int(value.strip())
                    except ValueError:
                        pass
    return DEFAULT_PORT
