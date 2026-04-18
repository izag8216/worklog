"""CSV export formatter."""

from __future__ import annotations

import csv
import io

from worklog.models import Activity, Annotation, DaySummary


def format_timeline(days: list[DaySummary]) -> str:
    """Format full timeline as CSV string."""
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["date", "time", "source", "repo", "summary", "tag", "type"])

    for day in days:
        items = day.all_items_sorted()
        for item in items:
            if isinstance(item, Activity):
                writer.writerow([
                    day.date,
                    item.timestamp.strftime("%H:%M"),
                    item.source,
                    item.repo,
                    item.summary,
                    "",
                    "commit",
                ])
            elif isinstance(item, Annotation):
                writer.writerow([
                    day.date,
                    item.created_at[11:16] if len(item.created_at) > 16 else "--:--",
                    "note",
                    "",
                    item.note,
                    item.tag,
                    "annotation",
                ])

    return output.getvalue()
