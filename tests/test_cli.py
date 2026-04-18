"""Tests for CLI commands."""

from click.testing import CliRunner

from worklog.cli import cli


runner = CliRunner()


def test_version():
    result = runner.invoke(cli, ["--version"])
    assert result.exit_code == 0
    assert "1.0.0" in result.output


def test_help():
    result = runner.invoke(cli, ["--help"])
    assert result.exit_code == 0
    assert "worklog" in result.output
    assert "today" in result.output
    assert "week" in result.output
    assert "annotate" in result.output


def test_annotate(tmp_path, monkeypatch):
    from worklog.config import DEFAULT_CONFIG_PATH, Config
    import worklog.cli as cli_mod

    config_path = tmp_path / "config.yaml"
    db_path = tmp_path / "test.db"
    cfg = Config(db_path=str(db_path))
    cfg.save(config_path)
    monkeypatch.setattr(cli_mod, "_load_config", lambda: cfg)

    result = runner.invoke(cli, ["annotate", "--note", "test note", "--tag", "test"])
    assert result.exit_code == 0
    assert "Annotation added" in result.output


def test_notes_empty(tmp_path, monkeypatch):
    from worklog.config import Config
    import worklog.cli as cli_mod

    db_path = tmp_path / "test.db"
    cfg = Config(db_path=str(db_path))
    monkeypatch.setattr(cli_mod, "_load_config", lambda: cfg)

    result = runner.invoke(cli, ["notes"])
    assert result.exit_code == 0
    assert "No annotations found" in result.output


def test_repos_empty(tmp_path, monkeypatch):
    from worklog.config import Config
    import worklog.cli as cli_mod

    cfg = Config()
    monkeypatch.setattr(cli_mod, "_load_config", lambda: cfg)

    result = runner.invoke(cli, ["repos"])
    assert result.exit_code == 0
    assert "No repositories configured" in result.output


def test_config_command(tmp_path, monkeypatch):
    from worklog.config import Config
    import worklog.cli as cli_mod

    cfg = Config(
        repos=[{"path": "~/projects/test"}],
        author_email="test@example.com",
        week_start="monday",
    )
    monkeypatch.setattr(cli_mod, "_load_config", lambda: cfg)

    result = runner.invoke(cli, ["config"])
    assert result.exit_code == 0
    assert "test@example.com" in result.output
    assert "monday" in result.output
