"""Tests for git collector with real temp repos."""

import os

import git

from worklog.collectors.git import collect_git_commits, collect_all_repos


def _commit(repo, repo_path, filename, content, message, actor):
    """Helper: create a file, add, commit with Actor object."""
    (repo_path / filename).write_text(content)
    repo.index.add([filename])
    repo.index.commit(message, author=actor, committer=actor)


def test_collect_from_real_repo(tmp_path):
    """Create a real git repo with commits and collect them."""
    repo_path = tmp_path / "test-repo"
    repo_path.mkdir()
    repo = git.Repo.init(str(repo_path))
    actor = git.Actor("Test", "test@example.com")

    _commit(repo, repo_path, "hello.txt", "hello", "Initial commit", actor)
    _commit(repo, repo_path, "world.txt", "world", "Add world", actor)

    activities = collect_git_commits(repo_path)
    assert len(activities) == 2
    assert activities[0].source == "git"
    assert activities[0].repo == "test-repo"
    summaries = [a.summary for a in activities]
    assert "Initial commit" in summaries
    assert "Add world" in summaries


def test_collect_with_author_filter(tmp_path):
    """Filter commits by author email."""
    repo_path = tmp_path / "filtered-repo"
    repo_path.mkdir()
    repo = git.Repo.init(str(repo_path))
    alice = git.Actor("Alice", "alice@example.com")
    bob = git.Actor("Bob", "bob@example.com")

    _commit(repo, repo_path, "a.txt", "a", "Commit A", alice)
    _commit(repo, repo_path, "b.txt", "b", "Commit B", bob)

    alice_only = collect_git_commits(repo_path, author_email="alice@example.com")
    assert len(alice_only) == 1
    assert "Commit A" in alice_only[0].summary


def test_collect_non_git_dir(tmp_path):
    """Non-git directory returns empty list."""
    non_git = tmp_path / "not-a-repo"
    non_git.mkdir()
    result = collect_git_commits(non_git)
    assert result == []


def test_collect_all_repos_dedup(tmp_path):
    """Multiple repos with deduplication."""
    actor = git.Actor("T", "t@t.com")

    repo1_path = tmp_path / "repo1"
    repo1_path.mkdir()
    repo1 = git.Repo.init(str(repo1_path))
    _commit(repo1, repo1_path, "f.txt", "f", "Repo1 commit", actor)

    repo2_path = tmp_path / "repo2"
    repo2_path.mkdir()
    repo2 = git.Repo.init(str(repo2_path))
    _commit(repo2, repo2_path, "g.txt", "g", "Repo2 commit", actor)

    all_acts = collect_all_repos([repo1_path, repo2_path])
    assert len(all_acts) == 2
    repos = {a.repo for a in all_acts}
    assert repos == {"repo1", "repo2"}
