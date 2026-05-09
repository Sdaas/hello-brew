import logging
import os
from pathlib import Path


def setup_logging(verbose: bool = False, log_dir: str | None = None) -> None:
    level = logging.DEBUG if verbose else logging.INFO

    if log_dir is None:
        # Locate logs/ relative to repo root (two levels up from this file's package)
        here = Path(__file__).resolve().parent
        candidate = here.parents[3] / "logs"
        if candidate.exists():
            log_dir = str(candidate)
        else:
            # Homebrew install: use /usr/local/var/log or HOMEBREW_PREFIX equivalent
            prefix = os.environ.get("HOMEBREW_PREFIX", "/usr/local")
            log_dir = os.path.join(prefix, "var", "log")

    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, "demo-server.log")

    logging.basicConfig(
        level=level,
        format="%(asctime)s  %(levelname)-8s  %(name)s  %(message)s",
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler(),
        ],
        force=True,
    )
