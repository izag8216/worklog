"""SQLite storage for annotations and activity cache."""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from worklog.models import Activity, Annotation


class Store:
    """SQLite-backed storage for annotations."""

    def __init__(self, db_path: str | Path) -> None:
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._conn: sqlite3.Connection | None = None

    @property
    def conn(self) -> sqlite3.Connection:
        if self._conn is None:
            self._conn = sqlite3.connect(str(self.db_path))
            self._conn.row_factory = sqlite3.Row
            self._conn.execute("PRAGMA journal_mode=WAL")
            self._create_tables()
        return self._conn

    def _create_tables(self) -> None:
        assert self._conn is not None
        self._conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS annotations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                note TEXT NOT NULL,
                tag TEXT DEFAULT '',
                created_at TEXT NOT NULL
            );
            CREATE INDEX IF NOT EXISTS idx_annotations_date
                ON annotations(date);

            CREATE TABLE IF NOT EXISTS activities_cache (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source TEXT NOT NULL,
                source_id TEXT DEFAULT '',
                repo TEXT DEFAULT '',
                timestamp TEXT NOT NULL,
                summary TEXT NOT NULL,
                tag TEXT DEFAULT '',
                metadata TEXT DEFAULT '{}'
            );
            CREATE INDEX IF NOT EXISTS idx_activities_timestamp
                ON activities_cache(timestamp);
            """
        )
        self._conn.commit()

    # -- Annotations --

    def add_annotation(self, date: str, note: str, tag: str = "") -> Annotation:
        """Insert a new annotation and return it."""
        now = datetime.now(timezone.utc).isoformat()
        cursor = self.conn.execute(
            "INSERT INTO annotations (date, note, tag, created_at) VALUES (?, ?, ?, ?)",
            (date, note, tag, now),
        )
        self.conn.commit()
        return Annotation(
            id=cursor.lastrowid,
            date=date,
            note=note,
            tag=tag,
            created_at=now,
        )

    def get_annotations(self, date: str | None = None) -> list[Annotation]:
        """Get annotations, optionally filtered by date."""
        if date:
            rows = self.conn.execute(
                "SELECT * FROM annotations WHERE date = ? ORDER BY created_at",
                (date,),
            ).fetchall()
        else:
            rows = self.conn.execute(
                "SELECT * FROM annotations ORDER BY date DESC, created_at"
            ).fetchall()
        return [
            Annotation(
                id=r["id"],
                date=r["date"],
                note=r["note"],
                tag=r["tag"],
                created_at=r["created_at"],
            )
            for r in rows
        ]

    def get_annotations_range(self, start: str, end: str) -> list[Annotation]:
        """Get annotations within a date range (inclusive)."""
        rows = self.conn.execute(
            "SELECT * FROM annotations WHERE date >= ? AND date <= ? ORDER BY date, created_at",
            (start, end),
        ).fetchall()
        return [
            Annotation(
                id=r["id"],
                date=r["date"],
                note=r["note"],
                tag=r["tag"],
                created_at=r["created_at"],
            )
            for r in rows
        ]

    def delete_annotation(self, annotation_id: int) -> bool:
        """Delete an annotation by ID. Returns True if deleted."""
        cursor = self.conn.execute(
            "DELETE FROM annotations WHERE id = ?", (annotation_id,)
        )
        self.conn.commit()
        return cursor.rowcount > 0

    # -- Activity Cache --

    def cache_activities(self, activities: list[Activity]) -> int:
        """Cache activities to avoid re-scanning. Returns count inserted."""
        inserted = 0
        for act in activities:
            dedup_key = f"{act.source}:{act.source_id}"
            existing = self.conn.execute(
                "SELECT id FROM activities_cache WHERE source = ? AND source_id = ?",
                (act.source, act.source_id),
            ).fetchone()
            if existing is None:
                self.conn.execute(
                    "INSERT INTO activities_cache (source, source_id, repo, timestamp, summary, tag, metadata) "
                    "VALUES (?, ?, ?, ?, ?, ?, ?)",
                    (
                        act.source,
                        act.source_id,
                        act.repo,
                        act.timestamp.isoformat(),
                        act.summary,
                        act.tag,
                        json.dumps(act.metadata),
                    ),
                )
                inserted += 1
        self.conn.commit()
        return inserted

    def get_cached_activities(
        self, start: str | None = None, end: str | None = None
    ) -> list[Activity]:
        """Retrieve cached activities, optionally filtered by date range."""
        query = "SELECT * FROM activities_cache"
        params: list[Any] = []
        conditions: list[str] = []

        if start:
            conditions.append("timestamp >= ?")
            params.append(f"{start}T00:00:00")
        if end:
            conditions.append("timestamp < ?")
            params.append(f"{end}T23:59:59" if len(end) == 10 else end)

        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        query += " ORDER BY timestamp"

        rows = self.conn.execute(query, params).fetchall()
        return [
            Activity(
                source=r["source"],
                timestamp=datetime.fromisoformat(r["timestamp"]),
                summary=r["summary"],
                repo=r["repo"],
                source_id=r["source_id"],
                tag=r["tag"],
                metadata=json.loads(r["metadata"]) if r["metadata"] else {},
            )
            for r in rows
        ]

    def close(self) -> None:
        if self._conn is not None:
            self._conn.close()
            self._conn = None
