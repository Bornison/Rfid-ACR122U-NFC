import sqlite3
from datetime import datetime
from typing import List, Optional, Dict, Any


def get_connection(path: str = "cards.db") -> sqlite3.Connection:
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    return conn


def init_db(path: str = "cards.db") -> None:
    conn = get_connection(path)
    cur = conn.cursor()
    cur.execute("PRAGMA foreign_keys = ON;")
    cur.execute("""
    CREATE TABLE IF NOT EXISTS persons (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        rfid_uid TEXT UNIQUE,
        role TEXT NOT NULL CHECK(role IN ('student','faculty')),
        name TEXT NOT NULL,
        department TEXT,
        category TEXT,
        program TEXT,
        year TEXT,
        extra TEXT,
        created_at TEXT NOT NULL
    );
    """)
    conn.commit()
    conn.close()


def add_person(data: Dict[str, Any], path: str = "cards.db") -> int:
    conn = get_connection(path)
    cur = conn.cursor()
    now = datetime.utcnow().isoformat()
    cur.execute(
        """
        INSERT INTO persons (rfid_uid, role, name, department, category, program, year, extra, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            data.get("rfid_uid"),
            data.get("role", "student"),
            data.get("name"),
            data.get("department"),
            data.get("category"),
            data.get("program"),
            data.get("year"),
            data.get("extra"),
            now,
        ),
    )
    conn.commit()
    rowid = cur.lastrowid
    conn.close()
    return rowid


def update_person(person_id: int, data: Dict[str, Any], path: str = "cards.db") -> None:
    conn = get_connection(path)
    cur = conn.cursor()
    cur.execute(
        """
        UPDATE persons
        SET rfid_uid = ?, role = ?, name = ?, department = ?, category = ?, program = ?, year = ?, extra = ?
        WHERE id = ?
        """,
        (
            data.get("rfid_uid"),
            data.get("role"),
            data.get("name"),
            data.get("department"),
            data.get("category"),
            data.get("program"),
            data.get("year"),
            data.get("extra"),
            person_id,
        ),
    )
    conn.commit()
    conn.close()


def delete_person(person_id: int, path: str = "cards.db") -> None:
    conn = get_connection(path)
    cur = conn.cursor()
    cur.execute("DELETE FROM persons WHERE id = ?", (person_id,))
    conn.commit()
    conn.close()


def get_person_by_uid(uid: str, path: str = "cards.db") -> Optional[Dict[str, Any]]:
    conn = get_connection(path)
    cur = conn.cursor()
    cur.execute("SELECT * FROM persons WHERE rfid_uid = ?", (uid,))
    row = cur.fetchone()
    conn.close()
    if row:
        return dict(row)
    return None


def get_person(person_id: int, path: str = "cards.db") -> Optional[Dict[str, Any]]:
    conn = get_connection(path)
    cur = conn.cursor()
    cur.execute("SELECT * FROM persons WHERE id = ?", (person_id,))
    row = cur.fetchone()
    conn.close()
    if row:
        return dict(row)
    return None


def list_persons(path: str = "cards.db") -> List[Dict[str, Any]]:
    conn = get_connection(path)
    cur = conn.cursor()
    cur.execute("SELECT * FROM persons ORDER BY name COLLATE NOCASE")
    rows = cur.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def search_persons(q: str, path: str = "cards.db") -> List[Dict[str, Any]]:
    like = f"%{q}%"
    conn = get_connection(path)
    cur = conn.cursor()
    cur.execute(
        """
        SELECT * FROM persons
        WHERE name LIKE ? OR department LIKE ? OR rfid_uid LIKE ? OR program LIKE ?
        ORDER BY name COLLATE NOCASE
        """,
        (like, like, like, like),
    )
    rows = cur.fetchall()
    conn.close()
    return [dict(r) for r in rows]
