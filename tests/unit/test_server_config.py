from pathlib import Path

from demo_server.config import DEFAULT_PORT, load_port


def _write_config(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content)


def test_default_port_when_no_config(monkeypatch):
    monkeypatch.setenv("DEMO_SERVER_CONFIG", "/tmp/nonexistent-demo-server-config-xyz")
    monkeypatch.setenv("HOME", "/tmp/nonexistent-home-xyz")
    assert load_port() == DEFAULT_PORT


def test_reads_port_from_env_config(tmp_path, monkeypatch):
    config = tmp_path / "config"
    _write_config(config, "PORT=9000\n")
    monkeypatch.setenv("DEMO_SERVER_CONFIG", str(config))
    assert load_port() == 9000


def test_ignores_comments(tmp_path, monkeypatch):
    config = tmp_path / "config"
    _write_config(config, "# This is a comment\nPORT=7777\n")
    monkeypatch.setenv("DEMO_SERVER_CONFIG", str(config))
    assert load_port() == 7777


def test_case_insensitive_key(tmp_path, monkeypatch):
    config = tmp_path / "config"
    _write_config(config, "port=6666\n")
    monkeypatch.setenv("DEMO_SERVER_CONFIG", str(config))
    assert load_port() == 6666


def test_invalid_port_value_falls_back(tmp_path, monkeypatch):
    config = tmp_path / "config"
    _write_config(config, "PORT=notanumber\n")
    monkeypatch.setenv("DEMO_SERVER_CONFIG", str(config))
    # falls through to next candidate (none) → default
    monkeypatch.setenv("HOME", "/tmp/nonexistent-home-xyz")
    assert load_port() == DEFAULT_PORT
