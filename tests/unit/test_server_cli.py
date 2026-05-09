import pytest
from demo_server.cli import build_parser
from demo_server.config import DEFAULT_PORT


def test_defaults():
    args = build_parser(DEFAULT_PORT).parse_args([])
    assert args.port == DEFAULT_PORT
    assert args.verbose is False


def test_port_override():
    args = build_parser(DEFAULT_PORT).parse_args(["--port", "9000"])
    assert args.port == 9000


def test_config_file_default_port_used():
    # Simulates what main() does: passes load_port() result as default_port
    args = build_parser(7777).parse_args([])
    assert args.port == 7777


def test_cli_port_overrides_config_default():
    args = build_parser(7777).parse_args(["--port", "9999"])
    assert args.port == 9999


def test_verbose_flag():
    args = build_parser(DEFAULT_PORT).parse_args(["--verbose"])
    assert args.verbose is True


def test_version_exits(capsys):
    with pytest.raises(SystemExit) as exc:
        build_parser(DEFAULT_PORT).parse_args(["--version"])
    assert exc.value.code == 0
