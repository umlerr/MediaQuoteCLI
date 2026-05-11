import sys
import pytest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "deepseek"))

from api_client import APIClient
from database import Database
from config import DB_PATH, LOCAL_API_URL, ZENQUOTES_API_URL


@pytest.fixture(autouse=True)
def tmp_db(tmp_path):
    with patch("database.DB_PATH", tmp_path / "test.db"):
        yield


@pytest.fixture
def test_db(tmp_path):
    with patch("database.DB_PATH", tmp_path / "test.db"):
        db = Database()
        yield db


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def sample_quote_movie():
    return {
        "id": "movie_test_001",
        "quote": "I'll be back.",
        "author": "Terminator",
        "source": "The Terminator",
        "content_type": "movie",
    }


@pytest.fixture
def sample_quote_game():
    return {
        "id": "game_test_001",
        "quote": "War never changes.",
        "author": "Narrator",
        "source": "Fallout",
        "content_type": "game",
    }


@pytest.fixture
def mock_zenquotes_response():
    return [{"q": "Life is short.", "a": "John Lennon"}]


@pytest.fixture
def mock_local_api_response():
    return {
        "success": True,
        "data": {
            "id": "movie_001",
            "quote": "May the Force be with you.",
            "author": "Han Solo",
            "source": "Star Wars",
            "content_type": "movie",
        }
    }


@pytest.fixture
def mock_local_search_response():
    return {
        "success": True,
        "data": [
            {"id": "movie_001", "quote": "May the Force be with you.",
             "author": "Han Solo", "source": "Star Wars", "content_type": "movie"},
        ],
        "count": 1
    }


@pytest.fixture
def mock_movies_list_response():
    return {"success": True, "movies": ["Star Wars", "The Terminator"]}


@pytest.fixture
def mock_games_list_response():
    return {"success": True, "games": ["Half-Life 2", "BioShock"]}


@pytest.fixture
def mock_sources_response():
    return {"movies": ["Star Wars"], "games": ["Half-Life 2"]}