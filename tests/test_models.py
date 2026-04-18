"""Tests for data models."""

from datetime import datetime, timezone

from worklog.models import Activity, Annotation, DaySummary


def test_activity_defaults():
    act = Activity(source="git", timestamp=datetime.now(timezone.utc), summary="test commit")
    assert act.source == "git"
    assert act.repo == ""
    assert act.tag == ""
    assert act.metadata == {}


def test_annotation_creation():
    ann = Annotation(id=1, date="2026-04-18", note="deployed v2.0", tag="release")
    assert ann.id == 1
    assert ann.date == "2026-04-18"
    assert ann.tag == "release"


def test_day_summary_counts():
    activities = [
        Activity(source="git", timestamp=datetime(2026, 4, 18, 9, 0), summary="commit 1", repo="proj"),
        Activity(source="git", timestamp=datetime(2026, 4, 18, 10, 0), summary="commit 2", repo="proj"),
        Activity(source="note", timestamp=datetime(2026, 4, 18, 11, 0), summary="a note"),
    ]
    annotations = [
        Annotation(id=1, date="2026-04-18", note="note 1"),
        Annotation(id=2, date="2026-04-18", note="note 2"),
    ]
    day = DaySummary(date="2026-04-18", activities=activities, annotations=annotations)

    assert day.total_count == 5
    assert day.commit_count == 2
    assert day.note_count == 2
    assert day.repos_used == {"proj"}


def test_day_summary_all_items_sorted():
    activities = [
        Activity(source="git", timestamp=datetime(2026, 4, 18, 14, 0), summary="afternoon commit"),
        Activity(source="git", timestamp=datetime(2026, 4, 18, 9, 0), summary="morning commit"),
    ]
    annotations = [
        Annotation(id=1, date="2026-04-18", note="noon note", created_at="2026-04-18T12:00:00+00:00"),
    ]
    day = DaySummary(date="2026-04-18", activities=activities, annotations=annotations)
    items = day.all_items_sorted()

    assert len(items) == 3
    assert isinstance(items[0], Activity)
    assert items[0].summary == "morning commit"
