"""Тесты для api_client.py"""
import pytest
import respx
import httpx
from api_client import APIClient

API_URL = "http://127.0.0.1:8000"
ZEN_URL = "https://zenquotes.io/api/random"


class TestAPIClient:

    @respx.mock
    def test_get_random_quote_success(self, api_client):
        respx.get(f"{API_URL}/quotes/random").mock(
            return_value=httpx.Response(200, json={
                "id": 1, "quote": "Test", "movie": "Film",
                "character": "Char", "source_type": "movie"
            })
        )
        quote = api_client.get_random_quote()
        assert quote is not None

    @respx.mock
    def test_get_random_quote_with_type(self, api_client):
        respx.get(f"{API_URL}/movies/quotes/random").mock(
            return_value=httpx.Response(200, json={
                "id": 1, "quote": "Test", "movie": "Film",
                "character": "Char", "source_type": "movie"
            })
        )
        quote = api_client.get_random_quote("movie")
        assert quote is not None
        assert quote["content_type"] == "movie"

    @respx.mock
    def test_get_random_quote_failure(self, api_client):
        respx.get(f"{API_URL}/quotes/random").mock(return_value=httpx.Response(500))
        quote = api_client.get_random_quote()
        assert quote is None

    @respx.mock
    def test_get_random_movie(self, api_client):
        respx.get(f"{API_URL}/movies/quotes/random").mock(
            return_value=httpx.Response(200, json={
                "id": 1, "quote": "Bond.", "movie": "Dr. No",
                "character": "James Bond", "source_type": "movie"
            })
        )
        quote = api_client.get_random_movie()
        assert quote is not None
        assert quote["content_type"] == "movie"

    @respx.mock
    def test_get_random_game(self, api_client):
        respx.get(f"{API_URL}/games/quotes/random").mock(
            return_value=httpx.Response(200, json={
                "id": 1, "quote": "War.", "game": "Fallout",
                "character": "Narrator", "source_type": "game"
            })
        )
        quote = api_client.get_random_game()
        assert quote is not None
        assert quote["content_type"] == "game"

    @respx.mock
    def test_search_quotes_success(self, api_client):
        respx.get(f"{API_URL}/quotes/search").mock(
            return_value=httpx.Response(200, json=[
                {"id": 1, "quote": "force quote", "movie": "Star Wars",
                 "character": "Yoda", "source_type": "movie"},
            ])
        )
        results = api_client.search_quotes("force")
        assert isinstance(results, list)

    @respx.mock
    def test_search_quotes_empty(self, api_client):
        respx.get(f"{API_URL}/quotes/search").mock(
            return_value=httpx.Response(200, json=[])
        )
        results = api_client.search_quotes("xyzxyz")
        assert results == []

    @respx.mock
    def test_get_movies_list(self, api_client):
        respx.get(f"{API_URL}/movies/quotes").mock(
            return_value=httpx.Response(200, json=[
                {"id": 1, "quote": "Q", "movie": "Star Wars", "character": "X"},
                {"id": 2, "quote": "Q2", "movie": "Terminator", "character": "Y"},
            ])
        )
        movies = api_client.get_movies_list()
        assert len(movies) >= 1

    @respx.mock
    def test_get_movies_list_failure(self, api_client):
        respx.get(f"{API_URL}/movies/quotes").mock(return_value=httpx.Response(500))
        movies = api_client.get_movies_list()
        assert movies == []

    @respx.mock
    def test_get_games_list(self, api_client):
        respx.get(f"{API_URL}/games/quotes").mock(
            return_value=httpx.Response(200, json=[
                {"id": 1, "quote": "Q", "game": "Fallout", "character": "X"},
                {"id": 2, "quote": "Q2", "game": "Portal", "character": "Y"},
            ])
        )
        games = api_client.get_games_list()
        assert len(games) >= 1

    @respx.mock
    def test_get_movie_quotes(self, api_client):
        respx.get(f"{API_URL}/movies/quotes").mock(
            return_value=httpx.Response(200, json=[
                {"id": 1, "quote": "May the Force be with you.",
                 "movie": "Star Wars", "character": "Han Solo"}
            ])
        )
        quotes = api_client.get_movie_quotes("Star Wars")
        assert len(quotes) >= 1

    @respx.mock
    def test_get_game_quotes(self, api_client):
        respx.get(f"{API_URL}/games/quotes").mock(
            return_value=httpx.Response(200, json=[
                {"id": 1, "quote": "Would you kindly?",
                 "game": "BioShock", "character": "Atlas"}
            ])
        )
        quotes = api_client.get_game_quotes("BioShock")
        assert len(quotes) >= 1

    @respx.mock
    def test_get_sources(self, api_client):
        respx.get(f"{API_URL}/quotes/stats").mock(
            return_value=httpx.Response(200, json={"total": 30})
        )
        respx.get(f"{API_URL}/movies/quotes").mock(
            return_value=httpx.Response(200, json=[
                {"id": 1, "quote": "Q", "movie": "Star Wars", "character": "X"}
            ])
        )
        respx.get(f"{API_URL}/games/quotes").mock(
            return_value=httpx.Response(200, json=[
                {"id": 1, "quote": "Q", "game": "Fallout", "character": "X"}
            ])
        )
        sources = api_client.get_sources()
        assert "movies" in sources
        assert "games" in sources

    @respx.mock
    def test_request_timeout(self, api_client):
        respx.get(f"{API_URL}/quotes/random").mock(
            side_effect=httpx.TimeoutException("Timeout")
        )
        quote = api_client.get_random_quote()
        assert quote is None