"""Клиент для FastAPI сервера и ZenQuotes"""
import httpx
import random
from typing import Optional, List, Dict
from .config import Config

cfg = Config()
TIMEOUT = cfg.get("timeout", 10)
API_URL = cfg.get("api_url", "http://localhost:8000")
ZENQUOTES_BASE = "https://zenquotes.io/api"

_ZEN_FALLBACK = [
    {"q": "In the middle of every difficulty lies opportunity.", "a": "Albert Einstein"},
    {"q": "It does not matter how slowly you go as long as you do not stop.", "a": "Confucius"},
    {"q": "Life is what happens when you're busy making other plans.", "a": "John Lennon"},
    {"q": "The future belongs to those who believe in the beauty of their dreams.", "a": "Eleanor Roosevelt"},
    {"q": "It is during our darkest moments that we must focus to see the light.", "a": "Aristotle"},
    {"q": "In the end, it's not the years in your life that count. It's the life in your years.",
     "a": "Abraham Lincoln"},
    {"q": "Life is either a daring adventure or nothing at all.", "a": "Helen Keller"},
    {"q": "Many of life's failures are people who did not realize how close they were to success when they gave up.",
     "a": "Thomas Edison"},
]


def _make(qid, content, author, source="", source_type="person", tags=None, api="unknown") -> Dict:
    return {"id": qid, "content": content, "author": author,
            "source": source, "source_type": source_type,
            "tags": tags or [], "api": api}


# ── ZenQuotes ──────────────────────────────────────────────────────────────────

def zen_random() -> Optional[Dict]:
    try:
        r = httpx.get(f"{ZENQUOTES_BASE}/random", timeout=TIMEOUT)
        r.raise_for_status()
        item = r.json()[0]
        return _make(f"zen_{hash(item['q'])}", item["q"], item["a"],
                     source=item["a"], source_type="person", tags=["wisdom"], api="zenquotes")
    except Exception:
        item = random.choice(_ZEN_FALLBACK)
        return _make(f"zen_{hash(item['q'])}", item["q"], item["a"],
                     source=item["a"], source_type="person", tags=["wisdom"], api="zenquotes")


def zen_list(limit=20) -> List[Dict]:
    try:
        r = httpx.get(f"{ZENQUOTES_BASE}/quotes", timeout=TIMEOUT)
        r.raise_for_status()
        return [_make(f"zen_{i['q'][:8]}", i["q"], i["a"],
                      source=i["a"], source_type="person", api="zenquotes")
                for i in r.json()[:limit]]
    except Exception:
        return [_make(f"zen_{q['q'][:8]}", q["q"], q["a"],
                      source=q["a"], source_type="person", api="zenquotes")
                for q in _ZEN_FALLBACK[:limit]]


def zen_search(query: str, limit=20) -> List[Dict]:
    kw = query.lower()
    quotes = zen_list(limit=50)
    return [q for q in quotes if kw in q["content"].lower() or kw in q["author"].lower()][:limit]


# ── Local FastAPI ──────────────────────────────────────────────────────────────

def _from_movie(raw: Dict) -> Dict:
    return _make(
        qid=f"movie_{raw.get('movie', 'unknown').replace(' ', '_').lower()[:20]}_{raw.get('id', 0)}",
        content=raw.get("quote", ""),
        author=raw.get("character", "Unknown"),
        source=raw.get("movie", ""),
        source_type="movie",
        tags=["movie"],
        api="local-api"
    )


def _from_game(raw: Dict) -> Dict:
    return _make(
        qid=f"game_{raw.get('game', 'unknown').replace(' ', '_').lower()[:20]}_{raw.get('id', 0)}",
        content=raw.get("quote", ""),
        author=raw.get("character", "Unknown"),
        source=raw.get("game", ""),
        source_type="game",
        tags=["game"],
        api="local-api"
    )


def movie_random() -> Optional[Dict]:
    try:
        r = httpx.get(f"{API_URL}/movies/quotes/random", timeout=TIMEOUT)
        r.raise_for_status()
        return _from_movie(r.json())
    except Exception:
        return None


def movie_list(movie=None, character=None, search=None, limit=20) -> List[Dict]:
    try:
        params = {"limit": limit}
        if movie:
            params["movie"] = movie
        if character:
            params["character"] = character
        if search:
            params["search"] = search
        r = httpx.get(f"{API_URL}/movies/quotes", params=params, timeout=TIMEOUT)
        r.raise_for_status()
        return [_from_movie(q) for q in r.json()]
    except Exception:
        return []


def movie_get(quote_id: int) -> Optional[Dict]:
    try:
        r = httpx.get(f"{API_URL}/movies/quotes/{quote_id}", timeout=TIMEOUT)
        r.raise_for_status()
        return _from_movie(r.json())
    except Exception:
        return None


def game_random() -> Optional[Dict]:
    try:
        r = httpx.get(f"{API_URL}/games/quotes/random", timeout=TIMEOUT)
        r.raise_for_status()
        return _from_game(r.json())
    except Exception:
        return None


def game_list(game=None, character=None, search=None, limit=20) -> List[Dict]:
    try:
        params = {"limit": limit}
        if game:
            params["game"] = game
        if character:
            params["character"] = character
        if search:
            params["search"] = search
        r = httpx.get(f"{API_URL}/games/quotes", params=params, timeout=TIMEOUT)
        r.raise_for_status()
        return [_from_game(q) for q in r.json()]
    except Exception:
        return []


def game_get(quote_id: int) -> Optional[Dict]:
    try:
        r = httpx.get(f"{API_URL}/games/quotes/{quote_id}", timeout=TIMEOUT)
        r.raise_for_status()
        return _from_game(r.json())
    except Exception:
        return None


def get_random_quote() -> Dict:
    funcs = [zen_random, movie_random, game_random]
    random.shuffle(funcs)
    for fn in funcs:
        q = fn()
        if q:
            return q
    return _make("err_0", "No quote available", "Unknown")


def search_all(query: str, limit=20) -> List[Dict]:
    results = []
    results += zen_search(query, limit=limit // 3)
    results += movie_list(search=query, limit=limit // 3)
    results += game_list(search=query, limit=limit // 3)
    return results[:limit]
