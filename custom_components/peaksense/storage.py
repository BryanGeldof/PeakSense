"""SQLite database for PeakSense."""

import sqlite3
import os

DB_PATH = "/config/peaksense.db"


class Storage:
    """Database management."""

    def __init__(self):
        self._init_db()

    def _init_db(self):
        """Initialize database."""
        os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
        
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
            variance REAL DEFAULT 0,
            label TEXT DEFAULT 'unknown',
            device_id INTEGER,
            confidence REAL DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(device_id) REFERENCES devices(id)
        )
        """)

        c.execute("""
        CREATE TABLE IF NOT EXISTS devices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            standby_power REAL DEFAULT 0,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)

        c.execute("""
        CREATE TABLE IF NOT EXISTS signatures (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            device_id INTEGER NOT NULL,
            peak REAL,
            avg REAL,
            duration INTEGER,
            variance REAL,
            count INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(device_id) REFERENCES devices(id) ON DELETE CASCADE
        )
        """)

        c.execute("""
        CREATE TABLE IF NOT EXISTS detections (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_id INTEGER,
            device_id INTEGER,
            confidence REAL,
            is_correct INTEGER DEFAULT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(event_id) REFERENCES events(id),
            FOREIGN KEY(device_id) REFERENCES devices(id)
        )
        """)

        conn.commit()
        conn.close()

    # Events
    def save_event(self, event):
        """Save event."""
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("""
        INSERT INTO events (start, end, peak, avg, duration, variance, label)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            event.get("start"),
            event.get("end"),
            event.get("peak"),
            event.get("avg"),
            event.get("duration"),
            event.get("variance", 0),
            event.get("label", "unknown"),
        ))
        conn.commit()
        event_id = c.lastrowid
        conn.close()
        return event_id

    def get_recent_events(self, limit=100):
        """Get recent events."""
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute("SELECT * FROM events ORDER BY id DESC LIMIT ?", (limit,))
        rows = [dict(row) for row in c.fetchall()]
        conn.close()
        return rows

    def update_event_device(self, event_id, device_id, confidence=1.0):
        """Update event with device."""
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute(
            "UPDATE events SET device_id = ?, confidence = ? WHERE id = ?",
            (device_id, confidence, event_id)
        )
        conn.commit()
        conn.close()

    def label_event(self, event_id, label):
        """Label event."""
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("UPDATE events SET label = ? WHERE id = ?", (label, event_id))
        conn.commit()
        conn.close()

    # Devices
    def create_device(self, name, standby_power=0, notes=""):
        """Create device."""
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute(
            "INSERT INTO devices (name, standby_power, notes) VALUES (?, ?, ?)",
            (name, standby_power, notes)
        )
        conn.commit()
        device_id = c.lastrowid
        conn.close()
        return device_id

    def get_all_devices(self):
        """Get all devices."""
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute("SELECT * FROM devices ORDER BY name")
        rows = [dict(row) for row in c.fetchall()]
        conn.close()
        return rows

    def get_device(self, device_id):
        """Get device."""
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute("SELECT * FROM devices WHERE id = ?", (device_id,))
        row = c.fetchone()
        conn.close()
        return dict(row) if row else None

    def update_device(self, device_id, name=None, standby_power=None, notes=None):
        """Update device."""
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        
        updates = ["updated_at = CURRENT_TIMESTAMP"]
        params = []
        
        if name is not None:
            updates.append("name = ?")
            params.append(name)
        if standby_power is not None:
            updates.append("standby_power = ?")
            params.append(standby_power)
        if notes is not None:
            updates.append("notes = ?")
            params.append(notes)
        
        params.append(device_id)
        c.execute(f"UPDATE devices SET {', '.join(updates)} WHERE id = ?", params)
        conn.commit()
        conn.close()

    def delete_device(self, device_id):
        """Delete device."""
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("DELETE FROM devices WHERE id = ?", (device_id,))
        conn.commit()
        conn.close()

    # Signatures
    def record_signature(self, device_id, event):
        """Record signature."""
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        
        c.execute(
            "SELECT id, count FROM signatures WHERE device_id = ? AND ABS(peak - ?) < 50 ORDER BY ABS(peak - ?) LIMIT 1",
            (device_id, event['peak'], event['peak'])
        )
        existing = c.fetchone()
        
        if existing:
            sig_id, count = existing
            c.execute("UPDATE signatures SET count = count + 1 WHERE id = ?", (sig_id,))
        else:
            c.execute("""
            INSERT INTO signatures (device_id, peak, avg, duration, variance)
            VALUES (?, ?, ?, ?, ?)
            """, (device_id, event.get('peak'), event.get('avg'), event.get('duration'), event.get('variance', 0)))
        
        conn.commit()
        conn.close()

    def get_device_signatures(self, device_id):
        """Get device signatures."""
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute("SELECT * FROM signatures WHERE device_id = ? ORDER BY count DESC", (device_id,))
        rows = [dict(row) for row in c.fetchall()]
        conn.close()
        return rows

    # Detections
    def record_detection(self, event_id, device_id, confidence):
        """Record detection."""
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("""
        INSERT INTO detections (event_id, device_id, confidence)
        VALUES (?, ?, ?)
        """, (event_id, device_id, confidence))
        conn.commit()
        conn.close()

    def get_detection(self, event_id):
        """Get detection."""
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute("SELECT * FROM detections WHERE event_id = ?", (event_id,))
        row = c.fetchone()
        conn.close()
        return dict(row) if row else None

    # Stats
    def get_device_statistics(self, device_id):
        """Get device stats."""
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        
        c.execute("SELECT COUNT(*) as total FROM events WHERE device_id = ?", (device_id,))
        total = c.fetchone()[0]
        
        c.execute(
            "SELECT AVG(peak) as avg_peak, MIN(peak) as min_peak, MAX(peak) as max_peak, AVG(duration) as avg_duration FROM events WHERE device_id = ?",
            (device_id,)
        )
        stats = c.fetchone()
        
        conn.close()
        
        return {
            'total_detections': total,
            'avg_peak': round(stats[0], 1) if stats[0] else 0,
            'min_peak': round(stats[1], 1) if stats[1] else 0,
            'max_peak': round(stats[2], 1) if stats[2] else 0,
            'avg_duration': int(stats[3]) if stats[3] else 0,
        }

    def get_accuracy_stats(self):
        """Get accuracy."""
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        
        c.execute("SELECT COUNT(*) FROM detections WHERE is_correct = 1")
        correct = c.fetchone()[0]
        
        c.execute("SELECT COUNT(*) FROM detections WHERE is_correct IS NOT NULL")
        total = c.fetchone()[0]
        
        conn.close()
        
        accuracy = (correct / total * 100) if total > 0 else 0
        return {
            'correct': correct,
            'total_feedback': total,
            'accuracy_percent': round(accuracy, 1)
        }
