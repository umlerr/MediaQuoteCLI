"""Работа с SQLite базой данных"""
import sqlite3
from typing import List, Dict, Optional
from config import DB_PATH


class Database:
    def __init__(self):
        self.db_path = DB_PATH
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS favorites (
                    id TEXT PRIMARY KEY,
                    quote TEXT NOT NULL,
                    author TEXT NOT NULL,
                    source TEXT NOT NULL,
                    content_type TEXT NOT NULL,
                    rating INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS ratings (
                    quote_id TEXT PRIMARY KEY,
                    rating INTEGER NOT NULL,
                    rated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (quote_id) REFERENCES favorites(id) ON DELETE CASCADE
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS export_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    format TEXT NOT NULL,
                    file_path TEXT NOT NULL,
                    quotes_count INTEGER NOT NULL,
                    exported_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

    def add_favorite(self, quote: Dict) -> bool:
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    "INSERT OR IGNORE INTO favorites (id, quote, author, source, content_type) VALUES (?, ?, ?, ?, ?)",
                    (quote['id'], quote['quote'], quote['author'], quote['source'], quote['content_type'])
                )
                return conn.total_changes > 0
        except Exception:
            return False

    def get_favorites(self) -> List[Dict]:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(
                "SELECT id, quote, author, source, content_type, rating, "
                "created_at FROM favorites ORDER BY created_at DESC"
            )
            return [dict(row) for row in cursor.fetchall()]

    def remove_favorite(self, quote_id: str) -> bool:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("DELETE FROM favorites WHERE id = ?", (quote_id,))
            return cursor.rowcount > 0

    def is_favorite(self, quote_id: str) -> bool:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("SELECT 1 FROM favorites WHERE id = ?", (quote_id,))
            return cursor.fetchone() is not None

    def clear_favorites(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("DELETE FROM favorites")

    def rate_quote(self, quote_id: str, rating: int) -> bool:
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    "UPDATE favorites SET rating = ? WHERE id = ?",
                    (rating, quote_id)
                )
                conn.execute(
                    "INSERT OR REPLACE INTO ratings (quote_id, rating) VALUES (?, ?)",
                    (quote_id, rating)
                )
                return True
        except Exception:
            return False

    def get_rating(self, quote_id: str) -> Optional[int]:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("SELECT rating FROM ratings WHERE quote_id = ?", (quote_id,))
            row = cursor.fetchone()
            return row[0] if row else None

    def get_average_rating(self) -> float:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("SELECT AVG(rating) FROM ratings")
            avg = cursor.fetchone()[0]
            return round(avg, 2) if avg else 0.0

    def save_export_record(self, format: str, file_path: str, count: int):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT INTO export_history (format, file_path, quotes_count) VALUES (?, ?, ?)",
                (format, file_path, count)
            )

    def get_export_history(self, limit: int = 10) -> List[Dict]:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(
                "SELECT * FROM export_history ORDER BY exported_at DESC LIMIT ?",
                (limit,)
            )
            return [dict(row) for row in cursor.fetchall()]

    def get_stats(self) -> Dict:
        with sqlite3.connect(self.db_path) as conn:
            favorites_count = conn.execute("SELECT COUNT(*) FROM favorites").fetchone()[0]
            ratings_count = conn.execute("SELECT COUNT(*) FROM ratings").fetchone()[0]
            rating_dist = {}
            for r in range(1, 6):
                count = conn.execute(
                    "SELECT COUNT(*) FROM ratings WHERE rating = ?", (r,)
                ).fetchone()[0]
                if count > 0:
                    rating_dist[str(r)] = count
            return {
                "favorites_count": favorites_count,
                "rated_count": ratings_count,
                "average_rating": self.get_average_rating(),
                "rating_distribution": rating_dist,
                "export_count": conn.execute("SELECT COUNT(*) FROM export_history").fetchone()[0]
            }
