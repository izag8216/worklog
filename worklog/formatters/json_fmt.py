"""JSON export formatter."""

from __future__ import annotations

import json
from dataclasses import asdict
from datetime import datetime

from worklog.models import Activity, Annotation, DaySummary


class _Encoder(json.JSONEncoder):
    """Custom encoder for dataclass and datetime objects."""

    def default(self, o: object) -> object:
        if isinstance(o, datetime):
            return o.isoformat()
        if hasattr(o, "__dataclass_fields__"):
            return asdict(o)
        return super().default(o)


def format_day(day: DaySummary) -> dict:
    """Format a single day as a JSON-serializable dict."""
    items = []
    for item in day.all_items_sorted():
        if isinstance(item, Activity):
            items.append({
                "time": item.timestamp.strftime("%H:%M"),
                "source": "git" if item.source == "git" else item.source,
                "repo": item.repo,
                "summary": item.summary,
                "type": "commit",
            })
        elif isinstance(item, Annotation):
            items.append({
                "time": item.created_at[11:16] if len(item.created_at) > 16 else "--:--",
                "source": "note",
                "summary": item.note,
                "tag": item.tag,
                "type": "annotation",
            })
    return {
        "date": day.date,
        "items": items,
        "summary": {
            "total": day.total_count,
            "commits": day.commit_count,
            "notes": day.note_count,
            "repos": sorted(day.repos_used),
        },
    }


def format_timeline(days: list[DaySummary]) -> str:
    """Format full timeline as JSON string."""
    data = {
        "days": [format_day(d) for d in days],
        "totals": {
            "days": len(days),
            "total_activities": sum(d.total_count for d in days),
            "total_commits": sum(d.commit_count for d in days),
        },
    }
    return json.dumps(data, indent=2, cls=_Encoder)
