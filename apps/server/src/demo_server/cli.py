import argparse
import sys

import uvicorn

from demo_server import __version__
from demo_server.logging_config import setup_logging

DEFAULT_PORT = 8100


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="demo-server",
        description="Demo REST API server",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    parser.add_argument(
        "--port", type=int, default=DEFAULT_PORT, help="Port to listen on (default: 8100)"
    )
    parser.add_argument("--verbose", action="store_true", help="Enable debug logging")
    return parser


def main(argv: list[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)

    setup_logging(verbose=args.verbose)

    uvicorn.run(
        "demo_server.main:app",
        host="0.0.0.0",
        port=args.port,
        log_level="debug" if args.verbose else "info",
        access_log=False,  # we handle request logging via middleware
    )


if __name__ == "__main__":
    main(sys.argv[1:])
