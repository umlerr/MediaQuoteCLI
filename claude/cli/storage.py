"""Локальное SQLite хранилище"""
import sqlite3
import json
import uuid
from pathlib import Path
from typing import Optional, List, Dict, Any

DB_PATH = Path.home() / ".mediaquote" / "quotes.db"


def _conn() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    return con


def init_db():
    with _conn() as con:
        con.executescript("""
            CREATE TABLE IF NOT EXISTS quotes (
                id TEXT PRIMARY KEY,
                content TEXT NOT NULL,
                author TEXT,
                source TEXT,
                source_type TEXT,
                tags TEXT DEFAULT '[]',
                api TEXT DEFAULT 'local',
                created_at TEXT DEFAULT (datetime('now'))
            );
            CREATE TABLE IF NOT EXISTS favorites (
                quote_id TEXT PRIMARY KEY,
                added_at TEXT DEFAULT (datetime('now'))
            );
            CREATE TABLE IF NOT EXISTS ratings (
                quote_id TEXT PRIMARY KEY,
                score INTEGER NOT NULL,
                rated_at TEXT DEFAULT (datetime('now'))
            );
        """)


def _row(row) -> Dict:
    d = dict(row)
    d["tags"] = json.loads(d.get("tags") or "[]")
    return d


def save_quote(q: Dict) -> Dict:
    init_db()
    qid = q.get("id") or f"local_{uuid.uuid4().hex[:8]}"
    with _conn() as con:
        con.execute(
            "INSERT OR REPLACE INTO quotes (id,content,author,source,source_type,tags,api) VALUES (?,?,?,?,?,?,?)",
            (qid, q.get("content",""), q.get("author","Unknown"),
             q.get("source",""), q.get("source_type","person"),
             json.dumps(q.get("tags",[])), q.get("api","local"))
        )
    q["id"] = qid
    return q


def get_quote(qid: str) -> Optional[Dict]:
    init_db()
    with _conn() as con:
        row = con.execute("SELECT * FROM quotes WHERE id=?", (qid,)).fetchone()
    return _row(row) if row else None


def delete_quote(qid: str) -> bool:
    init_db()
    with _conn() as con:
        cur = con.execute("DELETE FROM quotes WHERE id=?", (qid,))
    return cur.rowcount > 0


def list_quotes(author=None, source_type=None, source=None, limit=50) -> List[Dict]:
    init_db()
    sql = "SELECT * FROM quotes WHERE 1=1"
    params = []
    if author:
        sql += " AND lower(author) LIKE ?"
        params.append(f"%{author.lower()}%")
    if source_type:
        sql += " AND source_type=?"
        params.append(source_type)
    if source:
        sql += " AND lower(source) LIKE ?"
        params.append(f"%{source.lower()}%")
    sql += " ORDER BY created_at DESC LIMIT ?"
    params.append(limit)
    with _conn() as con:
        rows = con.execute(sql, params).fetchall()
    return [_row(r) for r in rows]


def search_quotes(keyword: str, limit=50) -> List[Dict]:
    init_db()
    kw = f"%{keyword.lower()}%"
    with _conn() as con:
        rows = con.execute(
            "SELECT * FROM quotes WHERE lower(content) LIKE ? OR lower(author) LIKE ? OR lower(source) LIKE ? LIMIT ?",
            (kw, kw, kw, limit)
        ).fetchall()
    return [_row(r) for r in rows]


def add_favorite(qid: str) -> bool:
    init_db()
    with _conn() as con:
        con.execute("INSERT OR IGNORE INTO favorites (quote_id) VALUES (?)", (qid,))
    return True


def list_favorites() -> List[Dict]:
    init_db()
    with _conn() as con:
        rows = con.execute(
            "SELECT q.* FROM quotes q JOIN favorites f ON q.id=f.quote_id ORDER BY f.added_at DESC"
        ).fetchall()
    return [_row(r) for r in rows]


def is_favorite(qid: str) -> bool:
    init_db()
    with _conn() as con:
        row = con.execute("SELECT 1 FROM favorites WHERE quote_id=?", (qid,)).fetchone()
    return row is not None


def rate_quote(qid: str, score: int) -> bool:
    init_db()
    with _conn() as con:
        con.execute("INSERT OR REPLACE INTO ratings (quote_id,score) VALUES (?,?)", (qid, score))
    return True


def get_rating(qid: str) -> Optional[int]:
    init_db()
    with _conn() as con:
        row = con.execute("SELECT score FROM ratings WHERE quote_id=?", (qid,)).fetchone()
    return row["score"] if row else None


def get_stats() -> Dict[str, Any]:
    init_db()
    with _conn() as con:
        total = con.execute("SELECT COUNT(*) FROM quotes").fetchone()[0]
        by_type = con.execute("SELECT source_type, COUNT(*) as cnt FROM quotes GROUP BY source_type").fetchall()
        by_api = con.execute("SELECT api, COUNT(*) as cnt FROM quotes GROUP BY api").fetchall()
        fav_count = con.execute("SELECT COUNT(*) FROM favorites").fetchone()[0]
        avg_rating = con.execute("SELECT AVG(score) FROM ratings").fetchone()[0]
    return {
        "total": total,
        "favorites": fav_count,
        "avg_rating": round(avg_rating, 2) if avg_rating else None,
        "by_type": {r["source_type"]: r["cnt"] for r in by_type},
        "by_api": {r["api"]: r["cnt"] for r in by_api},
    }