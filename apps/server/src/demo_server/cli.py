import argparse
import sys

import uvicorn

from demo_server import __version__
from demo_server.config import load_port
from demo_server.logging_config import setup_logging


def build_parser(default_port: int) -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="demo-server",
        description="Demo REST API server",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    parser.add_argument(
        "--port",
        type=int,
        default=default_port,
        help=f"Port to listen on (default: {default_port}, from config file or 8100)",
    )
    parser.add_argument("--verbose", action="store_true", help="Enable debug logging")
    return parser


def main(argv: list[str] | None = None) -> None:
    default_port = load_port()
    parser = build_parser(default_port)
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
