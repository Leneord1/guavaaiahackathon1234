"""SQLite persistence for reports and user settings."""

from __future__ import annotations

import json
import sqlite3
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from .paths import DATABASE_PATH, ensure_data_dirs


@dataclass(frozen=True)
class Report:
    id: int
    call_id: str
    mode: str
    payload: dict[str, Any]
    sources: list[str]
    created_at: str


class Storage:
    """Persist application state."""

    def __init__(self, path: Path = DATABASE_PATH) -> None:
        self.path = path
        if path == DATABASE_PATH:
            ensure_data_dirs()
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        """Open configured database."""
        connection = sqlite3.connect(self.path)
        connection.row_factory = sqlite3.Row
        return connection

    def _initialize(self) -> None:
        """Create required tables."""
        with self._connect() as connection:
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS reports (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    call_id TEXT NOT NULL,
                    mode TEXT NOT NULL,
                    payload_json TEXT NOT NULL,
                    sources_json TEXT NOT NULL,
                    created_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS profile_field (
                    singleton INTEGER PRIMARY KEY CHECK (singleton = 1),
                    label TEXT NOT NULL,
                    field_type TEXT NOT NULL,
                    value TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS provider_accounts (
                    provider_id TEXT PRIMARY KEY,
                    username TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );
                """
            )

    def save_report(
        self,
        call_id: str,
        mode: str,
        payload: dict[str, Any],
        sources: list[str] | None = None,
    ) -> int:
        """Save one completed call report."""
        with self._connect() as connection:
            cursor = connection.execute(
                """
                INSERT INTO reports(call_id, mode, payload_json, sources_json, created_at)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    call_id,
                    mode,
                    json.dumps(payload, ensure_ascii=False),
                    json.dumps(sources or []),
                    datetime.now(UTC).isoformat(),
                ),
            )
            if cursor.lastrowid is None:
                raise RuntimeError("Report insert did not return an identifier.")
            return cursor.lastrowid

    def list_reports(self, limit: int = 50) -> list[Report]:
        """Return newest reports."""
        with self._connect() as connection:
            rows = connection.execute(
                "SELECT * FROM reports ORDER BY id DESC LIMIT ?", (limit,)
            ).fetchall()
        return [
            Report(
                id=int(row["id"]),
                call_id=str(row["call_id"]),
                mode=str(row["mode"]),
                payload=json.loads(row["payload_json"]),
                sources=json.loads(row["sources_json"]),
                created_at=str(row["created_at"]),
            )
            for row in rows
        ]

    def save_profile_field(self, label: str, field_type: str, value: str) -> None:
        """Upsert single runtime profile field."""
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO profile_field(singleton, label, field_type, value)
                VALUES (1, ?, ?, ?)
                ON CONFLICT(singleton) DO UPDATE SET
                    label = excluded.label,
                    field_type = excluded.field_type,
                    value = excluded.value
                """,
                (label, field_type, value),
            )

    def get_profile_field(self) -> dict[str, str] | None:
        """Load runtime profile field."""
        with self._connect() as connection:
            row = connection.execute(
                "SELECT label, field_type, value FROM profile_field WHERE singleton = 1"
            ).fetchone()
        return dict(row) if row else None

    def save_provider_username(self, provider_id: str, username: str) -> None:
        """Store non-secret provider metadata."""
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO provider_accounts(provider_id, username, updated_at)
                VALUES (?, ?, ?)
                ON CONFLICT(provider_id) DO UPDATE SET
                    username = excluded.username,
                    updated_at = excluded.updated_at
                """,
                (provider_id, username, datetime.now(UTC).isoformat()),
            )

    def list_provider_usernames(self) -> dict[str, str]:
        """Return configured provider usernames."""
        with self._connect() as connection:
            rows = connection.execute(
                "SELECT provider_id, username FROM provider_accounts"
            ).fetchall()
        return {str(row["provider_id"]): str(row["username"]) for row in rows}

    def delete_provider_username(self, provider_id: str) -> None:
        """Delete provider metadata."""
        with self._connect() as connection:
            connection.execute(
                "DELETE FROM provider_accounts WHERE provider_id = ?", (provider_id,)
            )
