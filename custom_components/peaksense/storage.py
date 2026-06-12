import sqlite3
import os

DB_PATH = "/config/peaksense.db"

class Storage:
    def __init__(self):
        self._init_db()

    def _init_db(self):
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()

        c.execute("""
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            start TEXT,
            end TEXT,
            peak REAL,
            avg REAL,
            duration INTEGER,
            label TEXT
        )
        """)

        conn.commit()
        conn.close()

    def save_event(self, event, label="unknown"):
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()

        c.execute("""
        INSERT INTO events (start, end, peak, avg, duration, label)
        VALUES (?, ?, ?, ?, ?, ?)
        """, (
            event.get("start"),
            event.get("end"),
            event.get("peak"),
            event.get("avg"),
            event.get("duration"),
            label
        ))

        conn.commit()
        conn.close()
