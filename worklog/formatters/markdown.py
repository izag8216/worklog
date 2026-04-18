"""Markdown export formatter."""

from __future__ import annotations

from worklog.models import Activity, Annotation, DaySummary


def format_day(day: DaySummary) -> str:
    """Format a single day summary as markdown."""
    lines: list[str] = []
    lines.append(f"## {day.date}")
    lines.append("")
    lines.append("| Time | Source | Activity |")
    lines.append("|------|--------|----------|")

    items = day.all_items_sorted()
    for item in items:
        if isinstance(item, Activity):
            time_str = item.timestamp.strftime("%H:%M")
            source = f"git ({item.repo})" if item.repo else item.source
            lines.append(f"| {time_str} | {source} | {item.summary} |")
        elif isinstance(item, Annotation):
            time_str = item.created_at[11:16] if len(item.created_at) > 16 else "--:--"
            tag = f" [{item.tag}]" if item.tag else ""
            lines.append(f"| {time_str} | note | {item.note}{tag} |")

    lines.append("")
    lines.append(f"> {day.total_count} activities | {day.commit_count} commits | {day.note_count} notes")
    lines.append("")
    return "\n".join(lines)


def format_timeline(days: list[DaySummary], title: str = "Work Log") -> str:
    """Format full timeline as markdown document."""
    lines: list[str] = []
    lines.append(f"# {title}")
    lines.append("")

    if not days:
        lines.append("No activities found for the specified period.")
        return "\n".join(lines)

    for day in days:
        lines.append(format_day(day))

    total_activities = sum(d.total_count for d in days)
    total_commits = sum(d.commit_count for d in days)
    lines.append("---")
    lines.append("")
    lines.append(f"Total: {len(days)} days | {total_activities} activities | {total_commits} commits")
    return "\n".join(lines)
