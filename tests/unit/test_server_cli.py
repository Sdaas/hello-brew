import pytest
from demo_server.cli import DEFAULT_PORT, build_parser


def test_defaults():
    args = build_parser().parse_args([])
    assert args.port == DEFAULT_PORT
    assert args.verbose is False


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
    assert "0.1.0" in captured.out
