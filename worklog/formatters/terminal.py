"""Rich terminal output formatter."""

from __future__ import annotations

from datetime import datetime

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from worklog.models import Activity, Annotation, DaySummary


def _format_time(dt: datetime) -> str:
    return dt.strftime("%H:%M")


def format_day(day: DaySummary, console: Console | None = None) -> None:
    """Print a single day summary to terminal."""
    c = console or Console()

    today = datetime.now().strftime("%Y-%m-%d")
    label = "(Today)" if day.date == today else ""
    c.print(f"\n[bold cyan]{day.date}[/] {label}")
    c.rule(style="dim")

    items = day.all_items_sorted()
    for item in items:
        if isinstance(item, Activity):
            time_str = _format_time(item.timestamp)
            source = f"[dim][git][/] [magenta]{item.repo}[/]: " if item.source == "git" else f"[dim][{item.source}][/]"
            c.print(f"  {time_str}  {source}{item.summary}")
        elif isinstance(item, Annotation):
            time_str = item.created_at[11:16] if len(item.created_at) > 16 else "--:--"
            tag_str = f"  [[yellow]{item.tag}[/]]" if item.tag else ""
            c.print(f"  {time_str}  [dim][note/][/]{item.note}{tag_str}")

    c.print(
        f"\n  [dim]{day.total_count} activities | "
        f"{day.commit_count} commits | "
        f"{day.note_count} notes[/]"
    )


def format_timeline(days: list[DaySummary], console: Console | None = None) -> None:
    """Print full timeline to terminal."""
    c = console or Console()

    if not days:
        c.print("[dim]No activities found for the specified period.[/]")
        return

    for day in days:
        format_day(day, c)

    total_activities = sum(d.total_count for d in days)
    total_commits = sum(d.commit_count for d in days)
    c.print(f"\n[bold]Total: {len(days)} days | {total_activities} activities | {total_commits} commits[/]")
