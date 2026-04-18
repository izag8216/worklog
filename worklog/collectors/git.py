"""Git activity collector using gitpython."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

import git

from worklog.models import Activity


def collect_git_commits(
    repo_path: Path,
    author_email: str = "",
    since: datetime | None = None,
    until: datetime | None = None,
) -> list[Activity]:
    """Collect git commits from a single repository.

    Args:
        repo_path: Path to the git repository.
        author_email: Filter commits by author email. Empty = all authors.
        since: Start datetime (inclusive).
        until: End datetime (exclusive).

    Returns:
        List of Activity objects from git commits.
    """
    if not (repo_path / ".git").exists() and not _is_bare_repo(repo_path):
        return []

    try:
        repo = git.Repo(str(repo_path))
    except (git.InvalidGitRepositoryError, git.NoSuchPathError):
        return []

    kwargs: dict = {}
    if author_email:
        kwargs["author"] = author_email
    if since:
        kwargs["after"] = since.isoformat()
    if until:
        kwargs["before"] = until.isoformat()

    try:
        commits = list(repo.iter_commits(**kwargs))
    except (git.GitCommandError, ValueError):
        return []

    activities: list[Activity] = []
    for commit in commits:
        ts = commit.committed_datetime
        if ts.tzinfo is None:
            ts = ts.replace(tzinfo=timezone.utc)
        activities.append(
            Activity(
                source="git",
                timestamp=ts,
                summary=commit.message.strip().split("\n")[0],
                repo=repo_path.name,
                source_id=commit.hexsha[:7],
                metadata={"hexsha": commit.hexsha, "author": str(commit.author)},
            )
        )

    activities.sort(key=lambda a: a.timestamp)
    return activities


def collect_all_repos(
    repo_paths: list[Path],
    author_email: str = "",
    since: datetime | None = None,
    until: datetime | None = None,
) -> list[Activity]:
    """Collect git commits from multiple repositories.

    Returns deduplicated activities sorted by timestamp.
    """
    all_activities: list[Activity] = []
    seen_ids: set[str] = set()

    for path in repo_paths:
        acts = collect_git_commits(path, author_email, since, until)
        for act in acts:
            dedup_key = f"{act.repo}:{act.source_id}"
            if dedup_key not in seen_ids:
                seen_ids.add(dedup_key)
                all_activities.append(act)

    all_activities.sort(key=lambda a: a.timestamp)
    return all_activities


def _is_bare_repo(path: Path) -> bool:
    """Check if path is a bare git repository."""
    try:
        repo = git.Repo(str(path))
        return repo.bare
    except (git.InvalidGitRepositoryError, git.NoSuchPathError):
        return False
