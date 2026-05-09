import pytest
from demo_python_client import __version__
from demo_python_client.cli import DEFAULT_HOST, DEFAULT_PORT, build_parser


def test_defaults():
    args = build_parser().parse_args([])
    assert args.host == DEFAULT_HOST
    assert args.port == DEFAULT_PORT
    assert args.verbose is False


def test_host_override():
    args = build_parser().parse_args(["--host", "example.com"])
    assert args.host == "example.com"


def test_port_override():
    args = build_parser().parse_args(["--port", "9000"])
    assert args.port == 9000


def test_verbose_flag():
    args = build_parser().parse_args(["--verbose"])
    assert args.verbose is True


def test_version_exits(capsys):
    with pytest.raises(SystemExit) as exc:
        build_parser().parse_args(["--version"])
    assert exc.value.code == 0
    captured = capsys.readouterr()
    assert __version__ in captured.out
