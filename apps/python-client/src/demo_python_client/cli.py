import argparse
import logging
import sys

from demo_python_client import __version__
from demo_python_client.client import DEFAULT_HOST, DEFAULT_PORT, print_health


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="demo-python-client",
        description="Python client for demo-server",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    parser.add_argument("--host", default=DEFAULT_HOST, help="Server host (default: localhost)")
    parser.add_argument(
        "--port", type=int, default=DEFAULT_PORT, help="Server port (default: 8100)"
    )
    parser.add_argument("--verbose", action="store_true", help="Enable debug logging")
    return parser


def main(argv: list[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.WARNING,
        format="%(asctime)s  %(levelname)-8s  %(message)s",
    )

    try:
        print_health(host=args.host, port=args.port)
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main(sys.argv[1:])
