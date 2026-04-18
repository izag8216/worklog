"""Timeline assembly -- merge activities and annotations into daily summaries."""

from __future__ import annotations

from collections import defaultdict
from datetime import datetime

from worklog.models import Activity, Annotation, DaySummary


def build_timeline(
    activities: list[Activity],
    annotations: list[Annotation],
) -> list[DaySummary]:
    """Merge activities and annotations into chronological DaySummary list.

    Args:
        activities: Collected activities (git commits, etc.).
        annotations: Manual annotations.

    Returns:
        List of DaySummary objects sorted by date (newest first).
    """
    days: dict[str, DaySummary] = defaultdict(lambda: DaySummary(date=""))

    for act in activities:
        date_key = act.timestamp.strftime("%Y-%m-%d")
        days[date_key].date = date_key
        days[date_key].activities.append(act)

    for ann in annotations:
        date_key = ann.date
        days[date_key].date = date_key
        days[date_key].annotations.append(ann)

    return sorted(days.values(), key=lambda d: d.date, reverse=True)


def filter_timeline(
    timeline: list[DaySummary],
    start: str | None = None,
    end: str | None = None,
) -> list[DaySummary]:
    """Filter timeline by date range.

    Args:
        timeline: Full timeline.
        start: Start date (YYYY-MM-DD), inclusive.
        end: End date (YYYY-MM-DD), inclusive.

    Returns:
        Filtered timeline.
    """
    result = timeline
    if start:
        result = [d for d in result if d.date >= start]
    if end:
        result = [d for d in result if d.date <= end]
    return result
