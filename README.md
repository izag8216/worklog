<p align="center">
  <img src="https://capsule-render.vercel.app/api?type=wave&color=2D5A27&fontColor=FDF6E3&height=180&text=worklog&fontSize=45&fontAlignY=42&desc=Daily%20Activity%20Aggregator%20for%20Solopreneurs&descSize=18&descAlignY=62&descAlign=center&animation=fadeIn" alt="worklog header" />
</p>

<p align="center">
  <img src="https://img.shields.io/badge/python-3.9+-blue?style=flat-square" alt="Python 3.9+" />
  <img src="https://img.shields.io/badge/license-MIT-green?style=flat-square" alt="MIT License" />
  <img src="https://img.shields.io/badge/tests-47%20passing-brightgreen?style=flat-square" alt="Tests" />
  <img src="https://img.shields.io/badge/coverage-91%25-brightgreen?style=flat-square" alt="Coverage" />
</p>

**worklog** is a CLI tool that auto-aggregates your daily activities from git commits, manual annotations, and other local sources into a unified timeline. No cloud services, no APIs -- just your local data.

## Features

- **Git Activity Collection** -- Scan multiple local git repos, extract commits by author and date
- **Manual Annotations** -- Add free-text notes with tags to any date
- **Unified Timeline** -- Merge all sources into a chronological daily summary
- **Multiple Outputs** -- Terminal (rich), Markdown, JSON, CSV
- **Export** -- Save reports to files for archival or sharing
- **Zero Dependencies on Cloud** -- Everything runs locally with SQLite + git

## Installation

```bash
pip install worklog
```

Or install from source:

```bash
git clone https://github.com/izag8216/worklog.git
cd worklog
pip install -e .
```

## Quick Start

```bash
# Initialize configuration (interactive)
worklog init

# Today's activity summary
worklog today

# This week's summary
worklog week

# This month's summary
worklog month

# Custom date range
worklog log --from 2026-04-01 --to 2026-04-18

# Add a manual note
worklog annotate --note "Deployed v2.0 to production" --tag release

# Export to file
worklog export --from 2026-04-01 --to 2026-04-30 --format markdown --output april-log.md
worklog export --from 2026-04-01 --to 2026-04-30 --format json --output april-log.json
worklog export --from 2026-04-01 --to 2026-04-30 --format csv --output april-log.csv
```

## Configuration

Configuration is stored at `~/.worklog/config.yaml`:

```yaml
repos:
  - path: ~/projects/my-project
  - path: ~/projects/other-repo

author:
  email: user@example.com

week_start: monday    # monday or sunday
export_dir: ~/.worklog/exports
```

## Commands

| Command | Description |
|---------|-------------|
| `worklog init` | Create configuration file interactively |
| `worklog today` | Show today's activity summary |
| `worklog week` | Show this week's summary |
| `worklog month` | Show this month's summary |
| `worklog log --from DATE --to DATE` | Custom date range |
| `worklog annotate --note TEXT` | Add a manual note |
| `worklog notes` | List annotations |
| `worklog export --from DATE --to DATE --format FMT` | Export to file |
| `worklog repos` | List configured repos and status |
| `worklog config` | Show current configuration |

## Output Example

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

## Development

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest tests/ -v

# Run with coverage
pytest tests/ -v --cov=worklog --cov-report=term-missing
```

## License

MIT License -- see [LICENSE](LICENSE) for details.
