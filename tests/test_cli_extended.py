"""Extended CLI tests for better coverage."""

import json
from pathlib import Path
from unittest.mock import patch

import git
from click.testing import CliRunner

from worklog.cli import cli
from worklog.config import Config


runner = CliRunner()


def _make_config(tmp_path, repos=None):
    return Config(
        repos=repos or [],
        db_path=str(tmp_path / "test.db"),
        export_dir=str(tmp_path / "exports"),
    )


def _make_git_repo(tmp_path, name="test-repo"):
    repo_path = tmp_path / name
    repo_path.mkdir(parents=True, exist_ok=True)
    repo = git.Repo.init(str(repo_path))
    (repo_path / "readme.md").write_text("# test")
    repo.index.add(["readme.md"])
    repo.index.commit(
        "Initial commit",
        author=git.Actor("T", "t@t.com"),
        committer=git.Actor("T", "t@t.com"),
    )
    return repo_path


def test_today_with_repo(tmp_path):
    repo_path = _make_git_repo(tmp_path)
    cfg = _make_config(tmp_path, repos=[{"path": str(repo_path)}])

    with patch("worklog.cli._load_config", return_value=cfg):
        result = runner.invoke(cli, ["today"])
    assert result.exit_code == 0


def test_export_markdown(tmp_path):
    repo_path = _make_git_repo(tmp_path)
    cfg = _make_config(tmp_path, repos=[{"path": str(repo_path)}])
    out_file = tmp_path / "exports" / "out.md"

    with patch("worklog.cli._load_config", return_value=cfg):
        result = runner.invoke(cli, [
            "export", "--from", "2020-01-01", "--to", "2030-12-31",
            "--format", "markdown", "--output", str(out_file),
        ])
    assert result.exit_code == 0
    assert out_file.exists()


def test_export_json(tmp_path):
    repo_path = _make_git_repo(tmp_path)
    cfg = _make_config(tmp_path, repos=[{"path": str(repo_path)}])

    with patch("worklog.cli._load_config", return_value=cfg):
        result = runner.invoke(cli, [
            "export", "--from", "2020-01-01", "--to", "2030-12-31",
            "--format", "json",
        ])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert "days" in data


def test_export_csv_file(tmp_path):
    repo_path = _make_git_repo(tmp_path)
    cfg = _make_config(tmp_path, repos=[{"path": str(repo_path)}])
    out_file = tmp_path / "exports" / "out.csv"

    with patch("worklog.cli._load_config", return_value=cfg):
        result = runner.invoke(cli, [
            "export", "--from", "2020-01-01", "--to", "2030-12-31",
            "--format", "csv", "--output", str(out_file),
        ])
    assert result.exit_code == 0
    assert out_file.exists()


def test_annotate_with_date(tmp_path):
    cfg = _make_config(tmp_path)

    with patch("worklog.cli._load_config", return_value=cfg):
        result = runner.invoke(cli, [
            "annotate", "--note", "retrospective note",
            "--date", "2026-04-17", "--tag", "review",
        ])
    assert result.exit_code == 0
    assert "Annotation added to 2026-04-17" in result.output


def test_notes_with_annotations(tmp_path):
    cfg = _make_config(tmp_path)

    with patch("worklog.cli._load_config", return_value=cfg):
        runner.invoke(cli, ["annotate", "--note", "first", "--date", "2026-04-18"])
        runner.invoke(cli, ["annotate", "--note", "second", "--date", "2026-04-18"])

        result = runner.invoke(cli, ["notes", "--date", "2026-04-18"])
    assert result.exit_code == 0
    assert "first" in result.output
    assert "second" in result.output


def test_repos_with_configured(tmp_path):
    repo_path = _make_git_repo(tmp_path)
    cfg = _make_config(tmp_path, repos=[{"path": str(repo_path)}])

    with patch("worklog.cli._load_config", return_value=cfg):
        result = runner.invoke(cli, ["repos"])
    assert result.exit_code == 0
    assert "OK" in result.output


def test_repos_nonexistent(tmp_path):
    fake_path = tmp_path / "not-a-repo"
    fake_path.mkdir()
    cfg = _make_config(tmp_path, repos=[{"path": str(fake_path)}])

    with patch("worklog.cli._load_config", return_value=cfg):
        result = runner.invoke(cli, ["repos"])
    assert result.exit_code == 0
    assert "not a git repo" in result.output


def test_log_command(tmp_path):
    repo_path = _make_git_repo(tmp_path)
    cfg = _make_config(tmp_path, repos=[{"path": str(repo_path)}])

    with patch("worklog.cli._load_config", return_value=cfg):
        result = runner.invoke(cli, [
            "log", "--from", "2020-01-01", "--to", "2030-12-31",
        ])
    assert result.exit_code == 0


def test_month_command(tmp_path):
    repo_path = _make_git_repo(tmp_path)
    cfg = _make_config(tmp_path, repos=[{"path": str(repo_path)}])

    with patch("worklog.cli._load_config", return_value=cfg):
        result = runner.invoke(cli, ["month"])
    assert result.exit_code == 0


def test_week_command(tmp_path):
    repo_path = _make_git_repo(tmp_path)
    cfg = _make_config(tmp_path, repos=[{"path": str(repo_path)}])

    with patch("worklog.cli._load_config", return_value=cfg):
        result = runner.invoke(cli, ["week"])
    assert result.exit_code == 0
