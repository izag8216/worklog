"""Tests for configuration module."""

import os
from pathlib import Path

import pytest
import yaml

from worklog.config import Config


@pytest.fixture
def tmp_config_path(tmp_path):
    return tmp_path / "config.yaml"


def test_default_config():
    cfg = Config()
    assert cfg.repos == []
    assert cfg.author_email == ""
    assert cfg.week_start == "monday"


def test_load_missing_config(tmp_path):
    cfg = Config.load(tmp_path / "nonexistent.yaml")
    assert cfg.repos == []


def test_save_and_load(tmp_config_path):
    cfg = Config(
        repos=[{"path": "~/projects/repo1"}],
        author_email="test@example.com",
        week_start="sunday",
        export_dir="/tmp/exports",
    )
    cfg.save(tmp_config_path)

    loaded = Config.load(tmp_config_path)
    assert len(loaded.repos) == 1
    assert loaded.author_email == "test@example.com"
    assert loaded.week_start == "sunday"
    assert loaded.export_dir == "/tmp/exports"


def test_resolved_repo_paths(tmp_path):
    cfg = Config(repos=[{"path": "~/projects/test"}, {"path": str(tmp_path)}])
    paths = cfg.resolved_repo_paths()
    assert len(paths) == 2
    assert paths[0] == Path.home() / "projects" / "test"
    assert paths[1] == tmp_path


def test_resolved_repo_paths_ignores_empty(tmp_path):
    cfg = Config(repos=[{"path": "~/valid"}, {"path": ""}, ""])
    paths = cfg.resolved_repo_paths()
    assert len(paths) == 1
