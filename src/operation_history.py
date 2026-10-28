import os
import sqlite3
from pathlib import Path
from datetime import datetime
from .logger import logger

class HistoryManager:
    def __init__(self):
        # Use the PyInstaller-safe path
        base_dir = Path(os.environ.get("CTC_DATA_DIR", Path(__file__).parent.parent))
        db_path = base_dir / "data" / "history.db"
        
        # CRITICAL FIX: Ensure the 'data' directory exists before SQLite connects
        db_path.parent.mkdir(parents=True, exist_ok=True)
        
        self.conn = sqlite3.connect(str(db_path), check_same_thread=False)
        self._init_db()

    def _init_db(self):
        with self.conn:
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS operations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    batch_id TEXT,
                    original_path TEXT,
                    new_path TEXT,
                    timestamp DATETIME,
                    status TEXT
                )
            """)

    def record_move(self, batch_id: str, original: str, new_path: str, status: str = "MOVED"):
        with self.conn:
            self.conn.execute(
                "INSERT INTO operations (batch_id, original_path, new_path, timestamp, status) VALUES (?, ?, ?, ?, ?)",
                (batch_id, original, new_path, datetime.now(), status)
            )

    def get_latest_batch_id(self) -> str:
        cursor = self.conn.cursor()
        cursor.execute("SELECT batch_id FROM operations ORDER BY id DESC LIMIT 1")
        row = cursor.fetchone()
        return row[0] if row else None

    def get_operations_by_batch(self, batch_id: str):
        cursor = self.conn.cursor()
        cursor.execute("SELECT id, original_path, new_path FROM operations WHERE batch_id = ? AND status = 'MOVED' ORDER BY id DESC", (batch_id,))
        return cursor.fetchall()
        
    def mark_undone(self, op_id: int):
        with self.conn:
            self.conn.execute("UPDATE operations SET status = 'UNDONE' WHERE id = ?", (op_id,))