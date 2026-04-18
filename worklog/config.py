"""Configuration loader and defaults."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

import yaml


DEFAULT_CONFIG_DIR = Path.home() / ".worklog"
DEFAULT_CONFIG_PATH = DEFAULT_CONFIG_DIR / "config.yaml"
DEFAULT_DB_PATH = DEFAULT_CONFIG_DIR / "worklog.db"
DEFAULT_EXPORT_DIR = DEFAULT_CONFIG_DIR / "exports"


@dataclass
class Config:
    """Application configuration."""

    repos: list[str] = field(default_factory=list)
    author_email: str = ""
    week_start: str = "monday"
    export_dir: str = str(DEFAULT_EXPORT_DIR)
    db_path: str = str(DEFAULT_DB_PATH)

    @classmethod
    def load(cls, path: Path | None = None) -> Config:
        """Load configuration from YAML file."""
        config_path = path or DEFAULT_CONFIG_PATH
        if not config_path.exists():
            return cls()
        with open(config_path) as f:
            data = yaml.safe_load(f) or {}
        return cls(
            repos=data.get("repos", []),
            author_email=data.get("author", {}).get("email", ""),
            week_start=data.get("week_start", "monday"),
            export_dir=data.get("export_dir", str(DEFAULT_EXPORT_DIR)),
            db_path=str(
                Path(config_path).parent / "worklog.db"
            ),
        )

    def resolved_repo_paths(self) -> list[Path]:
        """Expand ~ in repo paths and return resolved Path objects."""
        return [
            Path(os.path.expanduser(r if isinstance(r, str) else r.get("path", "")))
            for r in self.repos
            if (isinstance(r, str) and r) or (isinstance(r, dict) and r.get("path"))
        ]

    def save(self, path: Path | None = None) -> None:
        """Save configuration to YAML file."""
        config_path = path or DEFAULT_CONFIG_PATH
        config_path.parent.mkdir(parents=True, exist_ok=True)
        data = {
            "repos": self.repos,
            "author": {"email": self.author_email} if self.author_email else {},
            "week_start": self.week_start,
            "export_dir": self.export_dir,
        }
        with open(config_path, "w") as f:
            yaml.dump(data, f, default_flow_style=False, sort_keys=False)
