"""MediaQuote API — независимый REST API сервер"""
import random
from typing import Optional
from fastapi import FastAPI, HTTPException, Query

from data import MOVIE_DATASET, GAME_DATASET

app = FastAPI(
    title="MediaQuote API",
    description="REST API для цитат из фильмов и видеоигр",
    version="1.0.0",
)


@app.get("/")
def root():
    return {
        "name": "MediaQuote API",
        "version": "1.0.0",
        "docs": "/docs",
        "endpoints": [
            "GET /movies/quotes",
            "GET /movies/quotes/random",
            "GET /movies/quotes/{id}",
            "GET /games/quotes",
            "GET /games/quotes/random",
            "GET /games/quotes/{id}",
            "GET /quotes/random",
            "GET /quotes/search",
            "GET /quotes/stats",
        ]
    }


# ── Movies ─────────────────────────────────────────────────────────────────────

@app.get("/movies/quotes")
def get_movie_quotes(
    movie: Optional[str] = Query(None, description="Название фильма"),
    character: Optional[str] = Query(None, description="Персонаж"),
    search: Optional[str] = Query(None, description="Поиск по тексту"),
    limit: int = Query(20, ge=1, le=60),
):
    result = MOVIE_DATASET
    if movie:
        result = [q for q in result if movie.lower() in q["movie"].lower()]
    if character:
        result = [q for q in result if character.lower() in q["character"].lower()]
    if search:
        kw = search.lower()
        result = [q for q in result if kw in q["quote"].lower() or kw in q["movie"].lower() or kw in q["character"].lower()]
    return result[:limit]


@app.get("/movies/quotes/random")
def get_random_movie_quote():
    return random.choice(MOVIE_DATASET)


@app.get("/movies/quotes/{quote_id}")
def get_movie_quote(quote_id: int):
    for q in MOVIE_DATASET:
        if q["id"] == quote_id:
            return q
    raise HTTPException(status_code=404, detail=f"Movie quote {quote_id} not found")


# ── Games ──────────────────────────────────────────────────────────────────────

@app.get("/games/quotes")
def get_game_quotes(
    game: Optional[str] = Query(None, description="Название игры"),
    character: Optional[str] = Query(None, description="Персонаж"),
    search: Optional[str] = Query(None, description="Поиск по тексту"),
    limit: int = Query(20, ge=1, le=20),
):
    result = GAME_DATASET
    if game:
        result = [q for q in result if game.lower() in q["game"].lower()]
    if character:
        result = [q for q in result if character.lower() in q["character"].lower()]
    if search:
        kw = search.lower()
        result = [q for q in result if kw in q["quote"].lower() or kw in q["game"].lower() or kw in q["character"].lower()]
    return result[:limit]


@app.get("/games/quotes/random")
def get_random_game_quote():
    return random.choice(GAME_DATASET)


@app.get("/games/quotes/{quote_id}")
def get_game_quote(quote_id: int):
    for q in GAME_DATASET:
        if q["id"] == quote_id:
            return q
    raise HTTPException(status_code=404, detail=f"Game quote {quote_id} not found")


# ── Combined ───────────────────────────────────────────────────────────────────

@app.get("/quotes/random")
def get_random_quote():
    source = random.choice(["movie", "game"])
    if source == "movie":
        q = random.choice(MOVIE_DATASET)
        return {**q, "source_type": "movie"}
    q = random.choice(GAME_DATASET)
    return {**q, "source_type": "game"}


@app.get("/quotes/search")
def search_quotes(
    q: str = Query(..., description="Ключевое слово"),
    limit: int = Query(20, ge=1, le=40),
):
    kw = q.lower()
    movies = [{**quote, "source_type": "movie"} for quote in MOVIE_DATASET
              if kw in quote["quote"].lower() or kw in quote["movie"].lower() or kw in quote["character"].lower()]
    games = [{**quote, "source_type": "game"} for quote in GAME_DATASET
             if kw in quote["quote"].lower() or kw in quote["game"].lower() or kw in quote["character"].lower()]
    return (movies + games)[:limit]


@app.get("/quotes/stats")
def get_stats():
    return {
        "total": len(MOVIE_DATASET) + len(GAME_DATASET),
        "movies": len(MOVIE_DATASET),
        "games": len(GAME_DATASET),
        "movie_titles": len(set(q["movie"] for q in MOVIE_DATASET)),
        "game_titles": len(set(q["game"] for q in GAME_DATASET)),
    }