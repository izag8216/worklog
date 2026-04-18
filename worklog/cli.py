"""CLI entry point for worklog."""

from __future__ import annotations

from datetime import datetime, timedelta
from pathlib import Path

import click
from rich.console import Console

from worklog import __version__
from worklog.collectors.git import collect_all_repos
from worklog.config import Config, DEFAULT_CONFIG_PATH
from worklog.formatters import terminal as term_fmt
from worklog.formatters import markdown as md_fmt
from worklog.formatters.json_fmt import format_timeline as json_format
from worklog.formatters.csv_fmt import format_timeline as csv_format
from worklog.store import Store
from worklog.timeline import build_timeline, filter_timeline


console = Console()


def _load_config() -> Config:
    return Config.load()


def _get_store(cfg: Config) -> Store:
    return Store(cfg.db_path)


def _today_str() -> str:
    return datetime.now().strftime("%Y-%m-%d")


def _week_range(cfg: Config) -> tuple[str, str]:
    """Return (start, end) for current week as YYYY-MM-DD strings."""
    today = datetime.now()
    weekday = today.weekday()
    if cfg.week_start == "sunday":
        start = today - timedelta(days=(weekday + 1) % 7)
    else:
        start = today - timedelta(days=weekday)
    end = start + timedelta(days=6)
    return start.strftime("%Y-%m-%d"), end.strftime("%Y-%m-%d")


def _month_range() -> tuple[str, str]:
    """Return (start, end) for current month."""
    today = datetime.now()
    start = today.replace(day=1)
    if today.month == 12:
        end = today.replace(year=today.year + 1, month=1, day=1) - timedelta(days=1)
    else:
        end = today.replace(month=today.month + 1, day=1) - timedelta(days=1)
    return start.strftime("%Y-%m-%d"), end.strftime("%Y-%m-%d")


def _collect_and_build(cfg: Config, start: str | None = None, end: str | None = None) -> list:
    """Collect git activities + annotations and build timeline."""
    since = datetime.fromisoformat(start) if start else None
    until = datetime.fromisoformat(end) + timedelta(days=1) if end else None

    repo_paths = cfg.resolved_repo_paths()
    activities = collect_all_repos(repo_paths, cfg.author_email, since, until)

    store = _get_store(cfg)
    store.cache_activities(activities)

    cached = store.get_cached_activities(start, end)
    if start and end:
        annotations = store.get_annotations_range(start, end)
    elif start:
        annotations = store.get_annotations_range(start, _today_str())
    else:
        annotations = store.get_annotations()

    store.close()
    return build_timeline(cached, annotations)


@click.group()
@click.version_option(version=__version__, prog_name="worklog")
def cli() -> None:
    """worklog -- Daily activity aggregator for solopreneurs."""
    pass


@cli.command()
def init() -> None:
    """Create configuration file interactively."""
    if DEFAULT_CONFIG_PATH.exists():
        console.print(f"[yellow]Config already exists at {DEFAULT_CONFIG_PATH}[/]")
        if not click.confirm("Overwrite?"):
            return

    console.print("[bold]worklog init[/] -- Configure your worklog\n")

    repos: list[str] = []
    console.print("Enter git repository paths (one per line, empty to finish):")
    while True:
        path = click.prompt("  Repo path", default="", show_default=False)
        if not path:
            break
        expanded = str(Path(path).expanduser().resolve())
        if Path(expanded).exists():
            repos.append(expanded)
            console.print(f"    [green]Added: {expanded}[/]")
        else:
            console.print(f"    [red]Path not found: {expanded}[/]")

    email = click.prompt("  Author email (empty = all authors)", default="")
    week = click.choice(["monday", "sunday"], default="monday")

    cfg = Config(
        repos=[{"path": r} for r in repos],
        author_email=email,
        week_start=week,
    )
    cfg.save()
    console.print(f"\n[green]Config saved to {DEFAULT_CONFIG_PATH}[/]")


@cli.command()
@click.option("--date", default=None, help="Date (YYYY-MM-DD), default: today")
def today(date: str | None) -> None:
    """Show today's activity summary."""
    cfg = _load_config()
    target = date or _today_str()
    timeline = _collect_and_build(cfg, start=target, end=target)
    if timeline:
        term_fmt.format_day(timeline[0], console)
    else:
        console.print(f"[dim]No activities found for {target}.[/]")


@cli.command()
def week() -> None:
    """Show this week's activity summary."""
    cfg = _load_config()
    start, end = _week_range(cfg)
    timeline = _collect_and_build(cfg, start=start, end=end)
    term_fmt.format_timeline(timeline, console)


@cli.command()
def month() -> None:
    """Show this month's activity summary."""
    cfg = _load_config()
    start, end = _month_range()
    timeline = _collect_and_build(cfg, start=start, end=end)
    term_fmt.format_timeline(timeline, console)


@cli.command()
@click.option("--from", "from_date", required=True, help="Start date (YYYY-MM-DD)")
@click.option("--to", "to_date", required=True, help="End date (YYYY-MM-DD)")
def log(from_date: str, to_date: str) -> None:
    """Show activities for a custom date range."""
    cfg = _load_config()
    timeline = _collect_and_build(cfg, start=from_date, end=to_date)
    term_fmt.format_timeline(timeline, console)


@cli.command()
@click.option("--note", required=True, help="Note text")
@click.option("--date", "date_str", default=None, help="Date (YYYY-MM-DD), default: today")
@click.option("--tag", default="", help="Optional tag (e.g., release, meeting)")
def annotate(note: str, date_str: str | None, tag: str) -> None:
    """Add a manual annotation to a date."""
    cfg = _load_config()
    store = _get_store(cfg)
    target = date_str or _today_str()
    ann = store.add_annotation(target, note, tag)
    store.close()
    console.print(f"[green]Annotation added to {target}[/]: {ann.note}")
    if tag:
        console.print(f"  Tag: [yellow]{tag}[/]")


@cli.command()
@click.option("--date", "date_str", default=None, help="Filter by date (YYYY-MM-DD)")
def notes(date_str: str | None) -> None:
    """List annotations."""
    cfg = _load_config()
    store = _get_store(cfg)
    anns = store.get_annotations(date_str)
    store.close()

    if not anns:
        console.print("[dim]No annotations found.[/]")
        return

    for ann in anns:
        tag_str = f" [[yellow]{ann.tag}[/]]" if ann.tag else ""
        console.print(f"  [cyan]{ann.date}[/] {ann.note}{tag_str}")


@cli.command()
@click.option("--from", "from_date", required=True, help="Start date (YYYY-MM-DD)")
@click.option("--to", "to_date", required=True, help="End date (YYYY-MM-DD)")
@click.option(
    "--format", "fmt",
    type=click.Choice(["markdown", "json", "csv"]),
    default="markdown",
    help="Output format",
)
@click.option("--output", "-o", default=None, help="Output file path (default: stdout)")
def export(from_date: str, to_date: str, fmt: str, output: str | None) -> None:
    """Export activities to file."""
    cfg = _load_config()
    timeline = _collect_and_build(cfg, start=from_date, end=to_date)

    if fmt == "markdown":
        content = md_fmt.format_timeline(timeline, title=f"Work Log: {from_date} to {to_date}")
    elif fmt == "json":
        content = json_format(timeline)
    else:
        content = csv_format(timeline)

    if output:
        out_path = Path(output)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(content)
        console.print(f"[green]Exported to {out_path}[/]")
    else:
        console.print(content)


@cli.command()
def repos() -> None:
    """List configured repositories and their status."""
    cfg = _load_config()
    if not cfg.repos:
        console.print("[dim]No repositories configured. Run 'worklog init' first.[/]")
        return

    for repo_entry in cfg.repos:
        if isinstance(repo_entry, str):
            path = Path(repo_entry).expanduser()
        else:
            path = Path(repo_entry.get("path", "")).expanduser()
        is_git = (path / ".git").exists()
        status = "[green]OK[/]" if is_git else "[red]not a git repo[/]"
        console.print(f"  {status}  {path}")


@cli.command()
def config() -> None:
    """Show current configuration."""
    cfg = _load_config()
    console.print(f"[bold]Config:[/] {DEFAULT_CONFIG_PATH}")
    console.print(f"  Repos: {len(cfg.repos)}")
    for r in cfg.repos:
        p = r if isinstance(r, str) else r.get("path", "")
        console.print(f"    - {p}")
    console.print(f"  Author: {cfg.author_email or '(all)'}")
    console.print(f"  Week start: {cfg.week_start}")
    console.print(f"  Export dir: {cfg.export_dir}")
