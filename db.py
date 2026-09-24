import sqlite3
from contextlib import contextmanager
from datetime import datetime
from typing import Any, Iterable

from config import DB_PATH


def _connect() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


@contextmanager
def cursor():
    conn = _connect()
    try:
        yield conn.cursor()
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_db() -> None:
    with cursor() as cur:
        cur.executescript("""
        CREATE TABLE IF NOT EXISTS event_types (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE
        );
        CREATE TABLE IF NOT EXISTS responsibles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE
        );
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            start_at TEXT NOT NULL,          -- ISO: YYYY-MM-DD HH:MM
            reg_url TEXT,
            type_id INTEGER NOT NULL REFERENCES event_types(id),
            responsible_id INTEGER NOT NULL REFERENCES responsibles(id)
        );
        CREATE INDEX IF NOT EXISTS idx_events_start ON events(start_at);
        """)

        # Начальные типы/ответственные — опционально
        cur.execute("SELECT COUNT(*) FROM event_types")
        if cur.fetchone()[0] == 0:
            cur.executemany(
                "INSERT INTO event_types(name) VALUES (?)",
                [("Встреча",), ("Конференция",), ("Вебинар",)],
            )


# ---------- Типы ----------

def list_types() -> list[sqlite3.Row]:
    with cursor() as cur:
        cur.execute("SELECT id, name FROM event_types ORDER BY name")
        return cur.fetchall()


def get_type(type_id: int) -> sqlite3.Row | None:
    with cursor() as cur:
        cur.execute("SELECT id, name FROM event_types WHERE id = ?", (type_id,))
        return cur.fetchone()


def add_type(name: str) -> bool:
    try:
        with cursor() as cur:
            cur.execute("INSERT INTO event_types(name) VALUES (?)", (name,))
        return True
    except sqlite3.IntegrityError:
        return False


def delete_type(name: str) -> str:
    """Возвращает 'ok', 'not_found' или 'in_use'."""
    with cursor() as cur:
        cur.execute("SELECT id FROM event_types WHERE name = ?", (name,))
        row = cur.fetchone()
        if not row:
            return "not_found"
        type_id = row["id"]
        cur.execute("SELECT COUNT(*) FROM events WHERE type_id = ?", (type_id,))
        if cur.fetchone()[0] > 0:
            return "in_use"
        cur.execute("DELETE FROM event_types WHERE id = ?", (type_id,))
        return "ok"


# ---------- Ответственные ----------

def list_responsibles() -> list[sqlite3.Row]:
    with cursor() as cur:
        cur.execute("SELECT id, name FROM responsibles ORDER BY name")
        return cur.fetchall()


def add_responsible(name: str) -> bool:
    try:
        with cursor() as cur:
            cur.execute("INSERT INTO responsibles(name) VALUES (?)", (name,))
        return True
    except sqlite3.IntegrityError:
        return False


# ---------- Мероприятия ----------

def add_event(
    title: str,
    description: str | None,
    start_at: datetime,
    reg_url: str | None,
    type_id: int,
    responsible_id: int,
) -> int:
    with cursor() as cur:
        cur.execute(
            """INSERT INTO events(title, description, start_at, reg_url, type_id, responsible_id)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (title, description, start_at.strftime("%Y-%m-%d %H:%M"),
             reg_url, type_id, responsible_id),
        )
        return cur.lastrowid


def get_event(event_id: int) -> sqlite3.Row | None:
    with cursor() as cur:
        cur.execute("""
            SELECT e.*, t.name AS type_name, r.name AS resp_name
            FROM events e
            JOIN event_types t ON t.id = e.type_id
            JOIN responsibles r ON r.id = e.responsible_id
            WHERE e.id = ?
        """, (event_id,))
        return cur.fetchone()


def list_all_events() -> list[sqlite3.Row]:
    with cursor() as cur:
        cur.execute("""
            SELECT e.*, t.name AS type_name, r.name AS resp_name
            FROM events e
            JOIN event_types t ON t.id = e.type_id
            JOIN responsibles r ON r.id = e.responsible_id
            ORDER BY e.start_at
        """)
        return cur.fetchall()


def list_events_for_day(date_str: str) -> list[sqlite3.Row]:
    """date_str = 'YYYY-MM-DD'"""
    with cursor() as cur:
        cur.execute("""
            SELECT e.*, t.name AS type_name, r.name AS resp_name
            FROM events e
            JOIN event_types t ON t.id = e.type_id
            JOIN responsibles r ON r.id = e.responsible_id
            WHERE e.start_at >= ? AND e.start_at < ?
            ORDER BY e.start_at
        """, (f"{date_str} 00:00", f"{date_str} 23:59"))
        return cur.fetchall()


def count_events_by_day(start_date: str, end_date: str) -> dict[str, int]:
    """{'2025-01-15': 3, ...}"""
    with cursor() as cur:
        cur.execute("""
            SELECT substr(start_at, 1, 10) AS d, COUNT(*) AS c
            FROM events
            WHERE start_at >= ? AND start_at < ?
            GROUP BY d
        """, (f"{start_date} 00:00", f"{end_date} 23:59"))
        return {row["d"]: row["c"] for row in cur.fetchall()}


def delete_event(event_id: int) -> bool:
    with cursor() as cur:
        cur.execute("DELETE FROM events WHERE id = ?", (event_id,))
        return cur.rowcount > 0