"""Local persistence for lookup results, so the web UI can restore a
previous search's graph after the app is closed and reopened.

Stored in a SQLite file under the user's home directory rather than the
project folder, so it survives regardless of where the tool is invoked from.
"""

import json
import sqlite3
from pathlib import Path

from .models import Finding, LookupResult

DB_PATH = Path.home() / ".osint_lookup" / "history.db"


def _connect() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS lookups (
            query TEXT PRIMARY KEY,
            query_type TEXT NOT NULL,
            findings_json TEXT NOT NULL,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    return conn


def save_lookup(result: LookupResult) -> None:
    findings_json = json.dumps([vars(f) for f in result.findings])
    with _connect() as conn:
        conn.execute(
            """
            INSERT INTO lookups (query, query_type, findings_json, updated_at)
            VALUES (?, ?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(query) DO UPDATE SET
                query_type = excluded.query_type,
                findings_json = excluded.findings_json,
                updated_at = CURRENT_TIMESTAMP
            """,
            (result.query, result.query_type, findings_json),
        )


def get_lookup(query: str) -> LookupResult | None:
    with _connect() as conn:
        row = conn.execute(
            "SELECT query, query_type, findings_json FROM lookups WHERE query = ?",
            (query,),
        ).fetchone()

    if row is None:
        return None

    query_value, query_type, findings_json = row
    findings = [Finding(**f) for f in json.loads(findings_json)]
    return LookupResult(query=query_value, query_type=query_type, findings=findings)


def list_recent(limit: int = 20) -> list[dict]:
    with _connect() as conn:
        rows = conn.execute(
            """
            SELECT query, query_type, updated_at FROM lookups
            ORDER BY updated_at DESC LIMIT ?
            """,
            (limit,),
        ).fetchall()

    return [
        {"query": q, "query_type": qt, "updated_at": ts} for q, qt, ts in rows
    ]
