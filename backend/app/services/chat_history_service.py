import os
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from urllib.parse import urlparse

from app.config import settings
from app.models.chat import ChatMessage


def _resolve_sqlite_path(database_url: str) -> str:
    parsed = urlparse(database_url)
    if parsed.scheme != "sqlite":
        raise ValueError("database_url must use the sqlite scheme")

    if parsed.netloc and parsed.path:
        return f"//{parsed.netloc}{parsed.path}"
    if parsed.path:
        return parsed.path.lstrip("/") or ":memory:"
    return ":memory:"


_DATABASE_PATH = _resolve_sqlite_path(settings.database_url)


def _connect() -> sqlite3.Connection:
    if _DATABASE_PATH == ":memory:":
        return sqlite3.connect(":memory:")
    os.makedirs(os.path.dirname(_DATABASE_PATH) or ".", exist_ok=True)
    return sqlite3.connect(_DATABASE_PATH)


@contextmanager
def _db():
    connection = _connect()
    connection.row_factory = sqlite3.Row
    try:
        yield connection
        connection.commit()
    finally:
        connection.close()


def initialize_chat_history() -> None:
    with _db() as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS chat_sessions (
                session_id TEXT PRIMARY KEY,
                document_id TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS chat_messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                FOREIGN KEY(session_id) REFERENCES chat_sessions(session_id)
            )
            """
        )


def ensure_session(session_id: str, document_id: str) -> None:
    initialize_chat_history()
    now = datetime.now(timezone.utc).isoformat()
    with _db() as connection:
        row = connection.execute(
            "SELECT document_id FROM chat_sessions WHERE session_id = ?",
            (session_id,),
        ).fetchone()
        if row is None:
            connection.execute(
                """
                INSERT INTO chat_sessions (session_id, document_id, created_at, updated_at)
                VALUES (?, ?, ?, ?)
                """,
                (session_id, document_id, now, now),
            )
            return

        if row["document_id"] != document_id:
            raise ValueError("Session belongs to a different document")

        connection.execute(
            "UPDATE chat_sessions SET updated_at = ? WHERE session_id = ?",
            (now, session_id),
        )


def add_message(session_id: str, role: str, content: str) -> None:
    initialize_chat_history()
    timestamp = datetime.now(timezone.utc).isoformat()
    with _db() as connection:
        connection.execute(
            """
            INSERT INTO chat_messages (session_id, role, content, timestamp)
            VALUES (?, ?, ?, ?)
            """,
            (session_id, role, content, timestamp),
        )
        connection.execute(
            "UPDATE chat_sessions SET updated_at = ? WHERE session_id = ?",
            (timestamp, session_id),
        )


def get_messages(session_id: str) -> list[ChatMessage]:
    initialize_chat_history()
    with _db() as connection:
        rows = connection.execute(
            """
            SELECT role, content, timestamp
            FROM chat_messages
            WHERE session_id = ?
            ORDER BY id ASC
            """,
            (session_id,),
        ).fetchall()

    return [
        ChatMessage(role=row["role"], content=row["content"], timestamp=row["timestamp"])
        for row in rows
    ]


def clear_chat_history() -> None:
    initialize_chat_history()
    with _db() as connection:
        connection.execute("DELETE FROM chat_messages")
        connection.execute("DELETE FROM chat_sessions")
