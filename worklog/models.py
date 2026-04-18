"""Data models for worklog activities and annotations."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class Activity:
    """A single activity entry from any source."""

    source: str          # 'git', 'note', etc.
    timestamp: datetime
    summary: str
    repo: str = ""
    source_id: str = ""  # commit hash, annotation id, etc.
    tag: str = ""
    metadata: dict = field(default_factory=dict)


@dataclass
class Annotation:
    """A manual annotation/note."""

    id: int | None
    date: str             # YYYY-MM-DD
    note: str
    tag: str = ""
    created_at: str = ""


@dataclass
class DaySummary:
    """Aggregated summary for a single day."""

    date: str             # YYYY-MM-DD
    activities: list[Activity] = field(default_factory=list)
    annotations: list[Annotation] = field(default_factory=list)

    @property
    def total_count(self) -> int:
        return len(self.activities) + len(self.annotations)

    @property
    def commit_count(self) -> int:
        return sum(1 for a in self.activities if a.source == "git")

    @property
    def note_count(self) -> int:
        return len(self.annotations)

    @property
    def repos_used(self) -> set[str]:
        return {a.repo for a in self.activities if a.repo}

    def all_items_sorted(self) -> list[Activity | Annotation]:
        """Return all items sorted by timestamp."""

        def _sort_key(item: Activity | Annotation) -> str:
            if isinstance(item, Activity):
                return item.timestamp.isoformat()
            return f"{item.date}T{item.created_at[11:] if item.created_at and len(item.created_at) > 11 else '00:00:00'}"

        items: list[Activity | Annotation] = []
        items.extend(self.activities)
        items.extend(self.annotations)
        items.sort(key=_sort_key)
        return items
