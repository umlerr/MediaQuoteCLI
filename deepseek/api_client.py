"""Клиент для работы с API"""
import httpx
from typing import List, Dict, Optional
from config import LOCAL_API_URL, ZENQUOTES_API_URL, REQUEST_TIMEOUT


class APIClient:
    def __init__(self):
        self.local_api = LOCAL_API_URL
        self.zen_api = ZENQUOTES_API_URL

    def _normalize(self, raw: Dict, content_type: str) -> Dict:
        if content_type == "movie":
            return {
                "id": f"movie_{raw.get('id', 0)}",
                "quote": raw.get("quote", ""),
                "author": raw.get("character", "Unknown"),
                "source": raw.get("movie", ""),
                "content_type": "movie"
            }
        elif content_type == "game":
            return {
                "id": f"game_{raw.get('id', 0)}",
                "quote": raw.get("quote", ""),
                "author": raw.get("character", "Unknown"),
                "source": raw.get("game", ""),
                "content_type": "game"
            }
        else:
            return raw

    def get_random_quote(self, content_type: Optional[str] = None) -> Optional[Dict]:
        try:
            if content_type == "movie":
                url = f"{self.local_api}/movies/quotes/random"
            elif content_type == "game":
                url = f"{self.local_api}/games/quotes/random"
            else:
                url = f"{self.local_api}/quotes/random"
            with httpx.Client(timeout=REQUEST_TIMEOUT) as client:
                r = client.get(url)
                r.raise_for_status()
                data = r.json()
                ct = data.get("source_type", content_type or "movie")
                return self._normalize(data, ct)
        except Exception:
            return None

    def get_movie_quotes(self, movie_title: str) -> List[Dict]:
        try:
            with httpx.Client(timeout=REQUEST_TIMEOUT) as client:
                r = client.get(f"{self.local_api}/movies/quotes?movie={movie_title}&limit=20")
                r.raise_for_status()
                return [self._normalize(q, "movie") for q in r.json()]
        except Exception:
            return []

    def get_game_quotes(self, game_title: str) -> List[Dict]:
        try:
            with httpx.Client(timeout=REQUEST_TIMEOUT) as client:
                r = client.get(f"{self.local_api}/games/quotes?game={game_title}&limit=20")
                r.raise_for_status()
                return [self._normalize(q, "game") for q in r.json()]
        except Exception:
            return []

    def search_quotes(self, keyword: str, content_type: Optional[str] = None, limit: int = 20) -> List[Dict]:
        try:
            url = f"{self.local_api}/quotes/search?q={keyword}&limit={limit}"
            with httpx.Client(timeout=REQUEST_TIMEOUT) as client:
                r = client.get(url)
                r.raise_for_status()
                return [self._normalize(q, q.get("source_type", "movie")) for q in r.json()]
        except Exception:
            return []

    def get_random_movie(self) -> Optional[Dict]:
        return self.get_random_quote("movie")

    def get_random_game(self) -> Optional[Dict]:
        return self.get_random_quote("game")

    def get_movies_list(self) -> List[str]:
        try:
            with httpx.Client(timeout=REQUEST_TIMEOUT) as client:
                r = client.get(f"{self.local_api}/movies/quotes?limit=60")
                r.raise_for_status()
                data = r.json()
                return list(set(q["movie"] for q in data))
        except Exception:
            return []

    def get_games_list(self) -> List[str]:
        try:
            with httpx.Client(timeout=REQUEST_TIMEOUT) as client:
                r = client.get(f"{self.local_api}/games/quotes?limit=20")
                r.raise_for_status()
                data = r.json()
                return list(set(q["game"] for q in data))
        except Exception:
            return []

    def get_movie_quotes(self, movie_title: str) -> List[Dict]:
        try:
            with httpx.Client(timeout=REQUEST_TIMEOUT) as client:
                r = client.get(f"{self.local_api}/movies/quotes?movie={movie_title}&limit=20")
                r.raise_for_status()
                return r.json()
        except Exception:
            return []

    def get_game_quotes(self, game_title: str) -> List[Dict]:
        try:
            with httpx.Client(timeout=REQUEST_TIMEOUT) as client:
                r = client.get(f"{self.local_api}/games/quotes?game={game_title}&limit=20")
                r.raise_for_status()
                return r.json()
        except Exception:
            return []

    def get_sources(self) -> Dict:
        try:
            with httpx.Client(timeout=REQUEST_TIMEOUT) as client:
                r = client.get(f"{self.local_api}/quotes/stats")
                r.raise_for_status()
                stats = r.json()
                movies_r = client.get(f"{self.local_api}/movies/quotes?limit=60")
                games_r = client.get(f"{self.local_api}/games/quotes?limit=20")
                movies = list(set(q["movie"] for q in movies_r.json()))
                games = list(set(q["game"] for q in games_r.json()))
                return {"movies": movies, "games": games}
        except Exception:
            return {"movies": [], "games": []}