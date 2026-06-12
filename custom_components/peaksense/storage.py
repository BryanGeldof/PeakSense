import sqlite3

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
            label TEXT DEFAULT 'unknown'
        )
        """)
        conn.commit()
        conn.close()

    def save_event(self, event):
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
            event.get("label", "unknown"),
        ))
        conn.commit()
        conn.close()

    def label_event(self, event_id: int, label: str):
        """Update the label of an existing event."""
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("UPDATE events SET label = ? WHERE id = ?", (label, event_id))
        conn.commit()
        conn.close()

    def get_recent_events(self, limit: int = 50):
        """Return the most recent events as a list of dicts."""
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute(
            "SELECT * FROM events ORDER BY id DESC LIMIT ?", (limit,)
        )
        rows = [dict(row) for row in c.fetchall()]
        conn.close()
        return rows
