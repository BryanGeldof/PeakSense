import sqlite3, os
DB_PATH = "/config/peaksense.db"

class Storage:
    def __init__(self):
        self._init_db()

    def _init_db(self):
        os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("CREATE TABLE IF NOT EXISTS events (id INTEGER PRIMARY KEY AUTOINCREMENT, start TEXT, end TEXT, peak REAL, avg REAL, duration INTEGER, variance REAL, label TEXT, device_id INTEGER, confidence REAL, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, FOREIGN KEY(device_id) REFERENCES devices(id))")
        c.execute("CREATE TABLE IF NOT EXISTS devices (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL UNIQUE, standby_power REAL DEFAULT 0, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)")
        c.execute("CREATE TABLE IF NOT EXISTS signatures (id INTEGER PRIMARY KEY AUTOINCREMENT, device_id INTEGER NOT NULL, peak REAL, avg REAL, duration INTEGER, variance REAL, count INTEGER DEFAULT 1, FOREIGN KEY(device_id) REFERENCES devices(id) ON DELETE CASCADE)")
        conn.commit()
        conn.close()

    def save_event(self, event):
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("INSERT INTO events (start, end, peak, avg, duration, variance, label) VALUES (?, ?, ?, ?, ?, ?, ?)", (event.get("start"), event.get("end"), event.get("peak"), event.get("avg"), event.get("duration"), event.get("variance", 0), event.get("label", "unknown")))
        conn.commit()
        eid = c.lastrowid
        conn.close()
        return eid

    def get_recent_events(self, limit=100):
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute("SELECT * FROM events ORDER BY id DESC LIMIT ?", (limit,))
        rows = [dict(row) for row in c.fetchall()]
        conn.close()
        return rows

    def create_device(self, name, standby_power=0):
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("INSERT INTO devices (name, standby_power) VALUES (?, ?)", (name, standby_power))
        conn.commit()
        did = c.lastrowid
        conn.close()
        return did

    def get_all_devices(self):
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute("SELECT * FROM devices ORDER BY name")
        rows = [dict(row) for row in c.fetchall()]
        conn.close()
        return rows

    def get_device(self, device_id):
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute("SELECT * FROM devices WHERE id = ?", (device_id,))
        row = c.fetchone()
        conn.close()
        return dict(row) if row else None

    def delete_device(self, device_id):
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("DELETE FROM devices WHERE id = ?", (device_id,))
        conn.commit()
        conn.close()

    def record_signature(self, device_id, event):
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT id FROM signatures WHERE device_id = ? AND ABS(peak - ?) < 50 LIMIT 1", (device_id, event['peak']))
        existing = c.fetchone()
        if existing:
            c.execute("UPDATE signatures SET count = count + 1 WHERE id = ?", (existing[0],))
        else:
            c.execute("INSERT INTO signatures (device_id, peak, avg, duration, variance) VALUES (?, ?, ?, ?, ?)", (device_id, event.get('peak'), event.get('avg'), event.get('duration'), event.get('variance', 0)))
        conn.commit()
        conn.close()

    def get_device_signatures(self, device_id):
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute("SELECT * FROM signatures WHERE device_id = ? ORDER BY count DESC", (device_id,))
        rows = [dict(row) for row in c.fetchall()]
        conn.close()
        return rows

    def update_event_device(self, event_id, device_id, confidence=1.0):
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("UPDATE events SET device_id = ?, confidence = ? WHERE id = ?", (device_id, confidence, event_id))
        conn.commit()
        conn.close()
