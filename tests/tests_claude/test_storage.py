"""Тесты для storage.py"""
import pytest
from unittest.mock import patch
from pathlib import Path


@pytest.fixture(autouse=True)
def tmp_db(tmp_path):
    with patch("cli.storage.DB_PATH", tmp_path / "test.db"):
        yield


from cli.storage import (
    save_quote, get_quote, delete_quote, list_quotes, search_quotes,
    add_favorite, list_favorites, is_favorite,
    rate_quote, get_rating, get_stats, init_db,
)

@pytest.fixture
def sample_quote():
    return {
        "content": "War. War never changes.",
        "author": "Narrator",
        "source": "Fallout",
        "source_type": "game",
        "tags": ["game"],
        "api": "local",
    }

@pytest.fixture
def saved_quote(sample_quote):
    return save_quote(sample_quote)


# ── save / get ─────────────────────────────────────────────────────────────────

def test_save_quote_returns_dict(sample_quote):
    result = save_quote(sample_quote)
    assert isinstance(result, dict)

def test_save_quote_has_id(sample_quote):
    result = save_quote(sample_quote)
    assert "id" in result

def test_save_quote_preserves_content(sample_quote):
    result = save_quote(sample_quote)
    assert result["content"] == sample_quote["content"]

def test_get_quote_existing(saved_quote):
    result = get_quote(saved_quote["id"])
    assert result is not None
    assert result["content"] == saved_quote["content"]

def test_get_quote_not_found():
    assert get_quote("nonexistent_999") is None

def test_get_quote_tags_as_list(saved_quote):
    result = get_quote(saved_quote["id"])
    assert isinstance(result["tags"], list)

def test_save_upsert():
    q = {"id": "dup_001", "content": "Original", "author": "A", "api": "local"}
    save_quote(q)
    q["content"] = "Updated"
    save_quote(q)
    assert get_quote("dup_001")["content"] == "Updated"


# ── delete ─────────────────────────────────────────────────────────────────────

def test_delete_existing(saved_quote):
    assert delete_quote(saved_quote["id"]) is True
    assert get_quote(saved_quote["id"]) is None

def test_delete_not_found():
    assert delete_quote("nonexistent_999") is False


# ── list / search ──────────────────────────────────────────────────────────────

def test_list_empty():
    assert list_quotes() == []

def test_list_returns_saved(saved_quote):
    assert len(list_quotes()) >= 1

def test_list_filter_by_source_type():
    save_quote({"content": "Q1", "author": "A", "source_type": "movie", "api": "local"})
    save_quote({"content": "Q2", "author": "B", "source_type": "game", "api": "local"})
    result = list_quotes(source_type="movie")
    assert all(q["source_type"] == "movie" for q in result)

def test_list_filter_by_author():
    save_quote({"content": "Q", "author": "Einstein", "source_type": "person", "api": "local"})
    result = list_quotes(author="Einstein")
    assert all("einstein" in q["author"].lower() for q in result)

def test_list_limit():
    for i in range(5):
        save_quote({"content": f"Q{i}", "author": "X", "api": "local"})
    assert len(list_quotes(limit=3)) <= 3

def test_search_by_content():
    save_quote({"content": "The cake is a lie", "author": "GLaDOS", "api": "local"})
    assert any("cake" in q["content"].lower() for q in search_quotes("cake"))

def test_search_no_results():
    assert search_quotes("xyzxyz_notfound") == []


# ── favorites ──────────────────────────────────────────────────────────────────

def test_add_favorite(saved_quote):
    assert add_favorite(saved_quote["id"]) is True

def test_is_favorite_true(saved_quote):
    add_favorite(saved_quote["id"])
    assert is_favorite(saved_quote["id"]) is True

def test_is_favorite_false():
    assert is_favorite("nonexistent_999") is False

def test_list_favorites_empty():
    assert list_favorites() == []

def test_list_favorites_returns_added(saved_quote):
    add_favorite(saved_quote["id"])
    assert any(q["id"] == saved_quote["id"] for q in list_favorites())

def test_add_favorite_no_duplicate(saved_quote):
    add_favorite(saved_quote["id"])
    add_favorite(saved_quote["id"])
    ids = [q["id"] for q in list_favorites()]
    assert ids.count(saved_quote["id"]) == 1


# ── ratings ────────────────────────────────────────────────────────────────────

def test_rate_quote(saved_quote):
    assert rate_quote(saved_quote["id"], 5) is True

def test_get_rating(saved_quote):
    rate_quote(saved_quote["id"], 4)
    assert get_rating(saved_quote["id"]) == 4

def test_get_rating_none():
    assert get_rating("nonexistent_999") is None

def test_rate_overwrites(saved_quote):
    rate_quote(saved_quote["id"], 3)
    rate_quote(saved_quote["id"], 5)
    assert get_rating(saved_quote["id"]) == 5


# ── stats ──────────────────────────────────────────────────────────────────────

def test_stats_empty():
    stats = get_stats()
    assert stats["total"] == 0
    assert stats["favorites"] == 0
    assert stats["avg_rating"] is None

def test_stats_after_saves():
    save_quote({"content": "Q1", "author": "A", "source_type": "movie", "api": "dataset"})
    save_quote({"content": "Q2", "author": "B", "source_type": "game", "api": "dataset"})
    stats = get_stats()
    assert stats["total"] == 2
    assert "movie" in stats["by_type"]

def test_stats_avg_rating(saved_quote):
    rate_quote(saved_quote["id"], 4)
    assert get_stats()["avg_rating"] == 4.0

def test_stats_favorites_count(saved_quote):
    add_favorite(saved_quote["id"])
    assert get_stats()["favorites"] == 1