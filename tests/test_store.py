"""Tests for SQLite store."""

from datetime import datetime, timezone

from worklog.models import Activity
from worklog.store import Store


def test_add_and_get_annotation(tmp_path):
    store = Store(tmp_path / "test.db")

    ann = store.add_annotation("2026-04-18", "deployed v2.0", "release")
    assert ann.id is not None
    assert ann.note == "deployed v2.0"
    assert ann.tag == "release"

    anns = store.get_annotations("2026-04-18")
    assert len(anns) == 1
    assert anns[0].note == "deployed v2.0"


def test_get_annotations_range(tmp_path):
    store = Store(tmp_path / "test.db")
    store.add_annotation("2026-04-17", "note A")
    store.add_annotation("2026-04-18", "note B")
    store.add_annotation("2026-04-19", "note C")

    anns = store.get_annotations_range("2026-04-17", "2026-04-18")
    assert len(anns) == 2


def test_delete_annotation(tmp_path):
    store = Store(tmp_path / "test.db")
    ann = store.add_annotation("2026-04-18", "to delete")

    assert store.delete_annotation(ann.id)
    assert len(store.get_annotations("2026-04-18")) == 0


def test_delete_nonexistent(tmp_path):
    store = Store(tmp_path / "test.db")
    assert not store.delete_annotation(9999)


def test_cache_and_get_activities(tmp_path):
    store = Store(tmp_path / "test.db")
    activities = [
        Activity(
            source="git",
            timestamp=datetime(2026, 4, 18, 9, 0, tzinfo=timezone.utc),
            summary="initial commit",
            repo="test-repo",
            source_id="abc1234",
        ),
        Activity(
            source="git",
            timestamp=datetime(2026, 4, 18, 10, 0, tzinfo=timezone.utc),
            summary="add feature",
            repo="test-repo",
            source_id="def5678",
        ),
    ]

    inserted = store.cache_activities(activities)
    assert inserted == 2

    cached = store.get_cached_activities()
    assert len(cached) == 2

    # Re-cache same activities should not duplicate
    inserted2 = store.cache_activities(activities)
    assert inserted2 == 0

    cached2 = store.get_cached_activities()
    assert len(cached2) == 2


def test_get_cached_activities_date_filter(tmp_path):
    store = Store(tmp_path / "test.db")
    activities = [
        Activity(
            source="git",
            timestamp=datetime(2026, 4, 17, 9, 0, tzinfo=timezone.utc),
            summary="yesterday",
            repo="test-repo",
            source_id="aaa1111",
        ),
        Activity(
            source="git",
            timestamp=datetime(2026, 4, 18, 9, 0, tzinfo=timezone.utc),
            summary="today",
            repo="test-repo",
            source_id="bbb2222",
        ),
    ]
    store.cache_activities(activities)

    filtered = store.get_cached_activities(start="2026-04-18", end="2026-04-18")
    assert len(filtered) == 1
    assert filtered[0].summary == "today"


def test_close_and_reopen(tmp_path):
    store = Store(tmp_path / "test.db")
    store.add_annotation("2026-04-18", "persistent note")
    store.close()

    store2 = Store(tmp_path / "test.db")
    anns = store2.get_annotations("2026-04-18")
    assert len(anns) == 1
    assert anns[0].note == "persistent note"
    store2.close()
