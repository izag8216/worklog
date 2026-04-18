# PRD: worklog -- Daily Activity Aggregator

## Metadata

| Field | Value |
|-------|-------|
| Version | 1.0.0 |
| Type | CLI Tool |
| License | MIT |
| Python | >=3.9 |
| Stack | click, gitpython, sqlite3 (stdlib), rich |
| GitHub | izag8216/worklog |

## Problem Statement

Solopreneurs maintain work logs for accountability and review. Current options are manual journaling (jrnl, 6k stars) or reconstructing from git commits (git-standup, 3k stars). No tool auto-aggregates from multiple local sources into a unified daily timeline.

## Target Users

- Solo developers / freelancers who work across multiple git repos
- One-person company (OPC) operators tracking daily output
- Anyone who wants automatic daily/weekly activity summaries from local data

## Core Features

### F1: Git Activity Collection
- Scan configurable list of local git repositories
- Extract commits (hash, message, author, timestamp, repo name)
- Filter by date range and author
- Deduplicate cross-repo activities

### F2: Manual Annotation
- Add free-text notes to any date
- Tag annotations (e.g., "release", "meeting", "milestone")
- Edit/delete existing annotations

### F3: Timeline Assembly
- Merge git commits + annotations into unified chronological timeline
- Group by date with configurable day boundary (default: midnight)
- Detect and merge adjacent activities from same repo

### F4: Reporting
- `today` -- Today's summary
- `week` -- This week's summary (configurable start day)
- `month` -- This month's summary
- Custom date range via `--from` / `--to`
- Output formats: terminal (rich), markdown, JSON, CSV

### F5: Export
- Markdown: Human-readable daily log (Obsidian-compatible)
- JSON: Machine-readable structured data
- CSV: Spreadsheet-importable tabular data

### F6: Configuration
- YAML config file (`~/.worklog/config.yaml`)
- Repo paths list
- Author email filter
- Week start day (Mon/Sun)
- Output directory for exports

## CLI Interface

```
worklog init                           # Create config file interactively
worklog today                          # Today's activity summary
worklog week                           # This week's summary
worklog month                          # This month's summary
worklog log [--from DATE] [--to DATE]  # Custom date range
worklog annotate --note "TEXT" [--date DATE] [--tag TAG]
worklog notes [--date DATE]            # List annotations
worklog export --from DATE --to DATE --format FORMAT  # Export to file
worklog repos                          # List configured repos + status
worklog config                         # Show current config
```

## Architecture

```
worklog/
  __init__.py
  cli.py              Click command group + all commands
  config.py           YAML config loader, defaults, validation
  collectors/
    __init__.py
    git.py            Git log collector (gitpython)
  models.py           Data classes: Activity, Annotation, DaySummary
  store.py            SQLite store (annotations, cached activities)
  timeline.py         Merge + group activities into timeline
  formatters/
    __init__.py
    terminal.py       Rich terminal output
    markdown.py       Markdown export
    json_fmt.py       JSON export
    csv_fmt.py        CSV export
```

## Database Schema (SQLite)

```sql
CREATE TABLE annotations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT NOT NULL,           -- YYYY-MM-DD
    note TEXT NOT NULL,
    tag TEXT,
    created_at TEXT NOT NULL      -- ISO timestamp
);

CREATE TABLE activities_cache (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source TEXT NOT NULL,         -- 'git', 'manual', etc.
    source_id TEXT,               -- commit hash, etc.
    repo TEXT,
    timestamp TEXT NOT NULL,
    summary TEXT NOT NULL,
    metadata TEXT                 -- JSON blob
);

CREATE INDEX idx_annotations_date ON annotations(date);
CREATE INDEX idx_activities_date ON activities_cache(timestamp);
```

## Configuration Schema (YAML)

```yaml
repos:
  - path: ~/projects/my-project
  - path: ~/projects/other-repo

author:
  email: user@example.com    # Filter git commits by author

week_start: monday           # monday or sunday

export_dir: ~/.worklog/exports
```

## Output Examples

### Terminal (rich)

```
2026-04-18 (Today)
─────────────────
09:15  [git] my-project: Refactor auth module (#42)
10:30  [note] Code review session with team
11:00  [git] other-repo: Fix pagination bug
14:00  [git] my-project: Add export feature (#43)
15:30  [note] Deployed v2.0 to production  [release]

5 activities | 3 commits | 2 notes
```

### Markdown Export

```markdown
# Daily Work Log -- 2026-04-18

## Timeline

| Time | Source | Activity |
|------|--------|----------|
| 09:15 | git (my-project) | Refactor auth module (#42) |
| 10:30 | note | Code review session with team |
| 11:00 | git (other-repo) | Fix pagination bug |
| 14:00 | git (my-project) | Add export feature (#43) |
| 15:30 | note | Deployed v2.0 to production [release] |

## Summary

- 5 activities
- 3 commits across 2 repos
- 2 manual notes
```

## Non-Goals

- No time tracking (that's `billable`)
- No billing/invoicing (that's `payup`)
- No expense tracking (that's `expensecap`)
- No cloud sync or remote API
- No GUI (CLI only)
- No git write operations (read-only)

## Testing Strategy

- Unit tests for each module (collectors, formatters, timeline, store)
- Integration tests with temporary git repos and database
- CLI tests via Click testing utilities
- Coverage target: 80%+

## Dependencies

| Package | Purpose | Version |
|---------|---------|---------|
| click | CLI framework | >=8.0 |
| gitpython | Git repo interaction | >=3.1 |
| rich | Terminal formatting | >=13.0 |
| pyyaml | Config file parsing | >=6.0 |

All other dependencies (sqlite3, json, csv, datetime, pathlib) are stdlib.

## Milestones

| # | Milestone | Deliverable |
|---|-----------|-------------|
| M1 | Project scaffold | pyproject.toml, package structure, config loader |
| M2 | Git collector + Store | Git activity extraction, SQLite store, models |
| M3 | Timeline + Formatters | Timeline assembly, terminal/markdown/JSON/CSV output |
| M4 | CLI commands | All click commands wired, init, today, week, month, log, annotate, export |
| M5 | Tests + Docs | 80%+ coverage, README (en+ja), LICENSE |
