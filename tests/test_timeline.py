"""Tests for timeline assembly."""

from datetime import datetime, timezone

from worklog.models import Activity, Annotation
from worklog.timeline import build_timeline, filter_timeline


def test_build_timeline_empty():
    result = build_timeline([], [])
    assert result == []


def test_build_timeline_activities_only():
    activities = [
        Activity(source="git", timestamp=datetime(2026, 4, 18, 9, 0, tzinfo=timezone.utc), summary="commit 1", repo="proj"),
        Activity(source="git", timestamp=datetime(2026, 4, 17, 14, 0, tzinfo=timezone.utc), summary="commit 2", repo="proj"),
    ]
    result = build_timeline(activities, [])
    assert len(result) == 2
    assert result[0].date == "2026-04-18"
    assert result[1].date == "2026-04-17"


def test_build_timeline_merged():
    activities = [
        Activity(source="git", timestamp=datetime(2026, 4, 18, 9, 0, tzinfo=timezone.utc), summary="commit", repo="proj"),
    ]
    annotations = [
        Annotation(id=1, date="2026-04-18", note="deployed", tag="release"),
    ]
    result = build_timeline(activities, annotations)
    assert len(result) == 1
    assert result[0].total_count == 2


def test_build_timeline_multi_day():
    activities = [
        Activity(source="git", timestamp=datetime(2026, 4, 16, 9, 0, tzinfo=timezone.utc), summary="c1"),
        Activity(source="git", timestamp=datetime(2026, 4, 17, 9, 0, tzinfo=timezone.utc), summary="c2"),
        Activity(source="git", timestamp=datetime(2026, 4, 18, 9, 0, tzinfo=timezone.utc), summary="c3"),
    ]
    result = build_timeline(activities, [])
    assert len(result) == 3
    assert result[0].date == "2026-04-18"
    assert result[2].date == "2026-04-16"


def test_filter_timeline():
    activities = [
        Activity(source="git", timestamp=datetime(2026, 4, 16, 9, 0, tzinfo=timezone.utc), summary="c1"),
        Activity(source="git", timestamp=datetime(2026, 4, 17, 9, 0, tzinfo=timezone.utc), summary="c2"),
        Activity(source="git", timestamp=datetime(2026, 4, 18, 9, 0, tzinfo=timezone.utc), summary="c3"),
    ]
    timeline = build_timeline(activities, [])
    filtered = filter_timeline(timeline, start="2026-04-17", end="2026-04-17")
    assert len(filtered) == 1
    assert filtered[0].date == "2026-04-17"


def test_filter_timeline_start_only():
    activities = [
        Activity(source="git", timestamp=datetime(2026, 4, 16, 9, 0, tzinfo=timezone.utc), summary="c1"),
        Activity(source="git", timestamp=datetime(2026, 4, 18, 9, 0, tzinfo=timezone.utc), summary="c2"),
    ]
    timeline = build_timeline(activities, [])
    filtered = filter_timeline(timeline, start="2026-04-17")
    assert len(filtered) == 1
    assert filtered[0].date == "2026-04-18"
