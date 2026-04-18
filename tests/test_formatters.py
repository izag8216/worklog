"""Tests for formatters."""

import json
from datetime import datetime, timezone

from worklog.models import Activity, Annotation, DaySummary
from worklog.formatters.markdown import format_timeline as md_format
from worklog.formatters.json_fmt import format_timeline as json_format
from worklog.formatters.csv_fmt import format_timeline as csv_format


def _sample_day():
    return DaySummary(
        date="2026-04-18",
        activities=[
            Activity(
                source="git",
                timestamp=datetime(2026, 4, 18, 9, 15, tzinfo=timezone.utc),
                summary="Refactor auth module (#42)",
                repo="my-project",
                source_id="abc1234",
            ),
        ],
        annotations=[
            Annotation(
                id=1,
                date="2026-04-18",
                note="Deployed v2.0",
                tag="release",
                created_at="2026-04-18T15:30:00+00:00",
            ),
        ],
    )


def test_markdown_format():
    days = [_sample_day()]
    output = md_format(days, title="Test Log")
    assert "# Test Log" in output
    assert "2026-04-18" in output
    assert "Refactor auth module" in output
    assert "Deployed v2.0" in output


def test_json_format():
    days = [_sample_day()]
    output = json_format(days)
    data = json.loads(output)
    assert len(data["days"]) == 1
    assert data["days"][0]["date"] == "2026-04-18"
    assert data["days"][0]["summary"]["total"] == 2


def test_csv_format():
    days = [_sample_day()]
    output = csv_format(days)
    lines = output.strip().replace("\r\n", "\n").split("\n")
    assert lines[0] == "date,time,source,repo,summary,tag,type"
    assert len(lines) == 3  # header + 2 data rows


def test_empty_timeline():
    assert md_format([]) == "# Work Log\n\nNo activities found for the specified period."
    json_data = json.loads(json_format([]))
    assert json_data["days"] == []
    assert csv_format([]).strip() == "date,time,source,repo,summary,tag,type"
