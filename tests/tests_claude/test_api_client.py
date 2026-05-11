"""Тесты для api_client.py"""
import pytest
import httpx
import respx

from cli.api_client import (
    _make,
    zen_random, zen_list, zen_search,
    movie_random, movie_list, game_random, game_list,
    get_random_quote, search_all,
    _ZEN_FALLBACK,
)

API_URL = "http://localhost:8000"
ZEN_URL = "https://zenquotes.io/api"


# ── _make ──────────────────────────────────────────────────────────────────────

def test_make_structure():
    q = _make("id1", "Content", "Author", "Source", "person", ["tag"], "zenquotes")
    assert q["id"] == "id1"
    assert q["content"] == "Content"
    assert q["source_type"] == "person"
    assert q["tags"] == ["tag"]

def test_make_defaults():
    q = _make("x", "text", "auth")
    assert q["source"] == ""
    assert q["tags"] == []
    assert q["api"] == "unknown"


# ── ZenQuotes ──────────────────────────────────────────────────────────────────

@respx.mock
def test_zen_random_success():
    respx.get(f"{ZEN_URL}/random").mock(
        return_value=httpx.Response(200, json=[{"q": "Test", "a": "Tester"}])
    )
    q = zen_random()
    assert q is not None
    assert q["content"] == "Test"
    assert q["author"] == "Tester"
    assert q["source_type"] == "person"
    assert q["api"] == "zenquotes"

@respx.mock
def test_zen_random_fallback_on_error():
    respx.get(f"{ZEN_URL}/random").mock(return_value=httpx.Response(500))
    q = zen_random()
    assert q is not None
    assert q["content"] in [f["q"] for f in _ZEN_FALLBACK]

@respx.mock
def test_zen_list_success():
    mock_data = [{"q": f"Quote {i}", "a": f"Author {i}"} for i in range(5)]
    respx.get(f"{ZEN_URL}/quotes").mock(return_value=httpx.Response(200, json=mock_data))
    result = zen_list(limit=5)
    assert len(result) == 5
    assert all(q["source_type"] == "person" for q in result)
    assert all(q["api"] == "zenquotes" for q in result)

@respx.mock
def test_zen_list_fallback():
    respx.get(f"{ZEN_URL}/quotes").mock(return_value=httpx.Response(503))
    result = zen_list(limit=5)
    assert len(result) > 0

def test_zen_search_filters():
    with respx.mock:
        mock_data = [
            {"q": "Life is short", "a": "Einstein"},
            {"q": "War never changes", "a": "Narrator"},
        ]
        respx.get(f"{ZEN_URL}/quotes").mock(return_value=httpx.Response(200, json=mock_data))
        result = zen_search("life")
        assert all("life" in q["content"].lower() or "life" in q["author"].lower() for q in result)

def test_zen_fallback_not_empty():
    assert len(_ZEN_FALLBACK) >= 5


# ── Local API ─────────────────────────────────────────────────────────────────

@respx.mock
def test_movie_random_success():
    respx.get(f"{API_URL}/movies/quotes/random").mock(
        return_value=httpx.Response(200, json={
            "id": 1, "quote": "I'll be back.",
            "movie": "Terminator", "character": "T-800"
        })
    )
    q = movie_random()
    assert q is not None
    assert q["source_type"] == "movie"
    assert q["content"] == "I'll be back."

@respx.mock
def test_movie_random_api_down():
    respx.get(f"{API_URL}/movies/quotes/random").mock(
        side_effect=httpx.ConnectError("down")
    )
    q = movie_random()
    assert q is None

@respx.mock
def test_movie_list_success():
    mock_data = [
        {"id": i, "quote": f"Q{i}", "movie": "Film", "character": "Char"}
        for i in range(3)
    ]
    respx.get(f"{API_URL}/movies/quotes").mock(
        return_value=httpx.Response(200, json=mock_data)
    )
    result = movie_list(limit=3)
    assert len(result) == 3
    assert all(q["source_type"] == "movie" for q in result)

@respx.mock
def test_movie_list_empty_on_error():
    respx.get(f"{API_URL}/movies/quotes").mock(return_value=httpx.Response(500))
    result = movie_list()
    assert result == []

@respx.mock
def test_game_random_success():
    respx.get(f"{API_URL}/games/quotes/random").mock(
        return_value=httpx.Response(200, json={
            "id": 1, "quote": "War never changes.",
            "game": "Fallout", "character": "Narrator"
        })
    )
    q = game_random()
    assert q is not None
    assert q["source_type"] == "game"

@respx.mock
def test_game_list_success():
    mock_data = [
        {"id": i, "quote": f"Q{i}", "game": "Portal", "character": "GLaDOS"}
        for i in range(2)
    ]
    respx.get(f"{API_URL}/games/quotes").mock(
        return_value=httpx.Response(200, json=mock_data)
    )
    result = game_list(limit=2)
    assert len(result) == 2
    assert all(q["source_type"] == "game" for q in result)


# ── Aggregated ────────────────────────────────────────────────────────────────

@respx.mock
def test_get_random_quote_returns_something():
    respx.get(f"{ZEN_URL}/random").mock(
        return_value=httpx.Response(200, json=[{"q": "Random!", "a": "Someone"}])
    )
    respx.get(f"{API_URL}/movies/quotes/random").mock(return_value=httpx.Response(500))
    respx.get(f"{API_URL}/games/quotes/random").mock(return_value=httpx.Response(500))
    q = get_random_quote()
    assert q is not None
    assert q["content"]

@respx.mock
def test_search_all_returns_list():
    respx.get(f"{ZEN_URL}/quotes").mock(return_value=httpx.Response(503))
    respx.get(f"{API_URL}/movies/quotes").mock(
        return_value=httpx.Response(200, json=[
            {"id": 1, "quote": "war quote", "movie": "Film", "character": "X"}
        ])
    )
    respx.get(f"{API_URL}/games/quotes").mock(
        return_value=httpx.Response(200, json=[
            {"id": 1, "quote": "war game", "game": "Game", "character": "Y"}
        ])
    )
    result = search_all("war")
    assert isinstance(result, list)
    assert len(result) >= 1