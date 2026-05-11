"""Тесты CLI команд через CliRunner"""
import pytest
from unittest.mock import patch
from typer.testing import CliRunner
from cli.main import app

runner = CliRunner()

@pytest.fixture(autouse=True)
def tmp_db(tmp_path):
    with patch("cli.storage.DB_PATH", tmp_path / "test.db"):
        yield

MOCK_QUOTE = {
    "id": "game_fallout_1",
    "content": "War. War never changes.",
    "author": "Narrator",
    "source": "Fallout",
    "source_type": "game",
    "tags": ["game"],
    "api": "local-api",
}


# ── version / config ───────────────────────────────────────────────────────────

def test_version():
    result = runner.invoke(app, ["version"])
    assert result.exit_code == 0
    assert "MediaQuote" in result.output

def test_config_show():
    result = runner.invoke(app, ["config", "--show"])
    assert result.exit_code == 0


# ── quotes random ──────────────────────────────────────────────────────────────

def test_quotes_random():
    with patch("cli.commands.quotes.get_random_quote", return_value=MOCK_QUOTE):
        result = runner.invoke(app, ["quotes", "random"], input="n\n")
    assert result.exit_code == 0
    assert "War" in result.output

def test_quotes_random_save():
    with patch("cli.commands.quotes.get_random_quote", return_value=MOCK_QUOTE):
        result = runner.invoke(app, ["quotes", "random"], input="y\nn\nn\n")
    assert result.exit_code == 0
    assert "Сохранено" in result.output


# ── quotes add / get / delete ─────────────────────────────────────────────────

def test_quotes_add():
    result = runner.invoke(app, ["quotes", "add", "Test quote", "--author", "Tester"])
    assert result.exit_code == 0
    assert "добавлена" in result.output.lower() or "Добавлено" in result.output

def test_quotes_get_not_found():
    result = runner.invoke(app, ["quotes", "get", "nonexistent_999"])
    assert result.exit_code != 0

def test_quotes_delete_yes(tmp_path):
    with patch("cli.storage.DB_PATH", tmp_path / "test.db"):
        runner.invoke(app, ["quotes", "add", "To delete", "--author", "X"])
        from cli.storage import list_quotes
        qid = list_quotes()[0]["id"]
        result = runner.invoke(app, ["quotes", "delete", qid, "--yes"])
        assert result.exit_code == 0


# ── quotes list / search ───────────────────────────────────────────────────────

def test_quotes_list_local_empty():
    result = runner.invoke(app, ["quotes", "list", "--local"])
    assert result.exit_code == 0

def test_quotes_search_local():
    runner.invoke(app, ["quotes", "add", "The cake is a lie", "--author", "GLaDOS"])
    result = runner.invoke(app, ["quotes", "search", "cake", "--local"])
    assert result.exit_code == 0
    assert "cake" in result.output.lower()


# ── movies ────────────────────────────────────────────────────────────────────

def test_movies_random_api_down():
    with patch("cli.commands.movies.movie_random", return_value=None):
        result = runner.invoke(app, ["movies", "random"])
    assert result.exit_code != 0

def test_movies_random_success():
    with patch("cli.commands.movies.movie_random", return_value=MOCK_QUOTE):
        result = runner.invoke(app, ["movies", "random"], input="n\n")
    assert result.exit_code == 0

def test_movies_list_not_found():
    with patch("cli.commands.movies.movie_list", return_value=[]):
        result = runner.invoke(app, ["movies", "list", "--movie", "NonExistent"])
    assert result.exit_code != 0


# ── games ─────────────────────────────────────────────────────────────────────

def test_games_random_success():
    with patch("cli.commands.games.game_random", return_value=MOCK_QUOTE):
        result = runner.invoke(app, ["games", "random"], input="n\n")
    assert result.exit_code == 0

def test_games_list_not_found():
    with patch("cli.commands.games.game_list", return_value=[]):
        result = runner.invoke(app, ["games", "list", "--game", "NonExistent"])
    assert result.exit_code != 0


# ── favorites ─────────────────────────────────────────────────────────────────

def test_favorites_list_empty():
    result = runner.invoke(app, ["favorites", "list"])
    assert result.exit_code == 0
    assert "пусто" in result.output.lower()

def test_favorites_add_not_saved():
    result = runner.invoke(app, ["favorites", "add", "nonexistent_999"])
    assert result.exit_code != 0

def test_favorites_add_and_list(tmp_path):
    with patch("cli.storage.DB_PATH", tmp_path / "test.db"):
        runner.invoke(app, ["quotes", "add", "Test fav", "--author", "X"])
        from cli.storage import list_quotes
        qid = list_quotes()[0]["id"]
        result = runner.invoke(app, ["favorites", "add", qid])
        assert result.exit_code == 0
        assert "избранное" in result.output.lower()


# ── rate ──────────────────────────────────────────────────────────────────────

def test_rate_invalid():
    runner.invoke(app, ["quotes", "add", "Test", "--author", "X"])
    from cli.storage import list_quotes
    qid = list_quotes()[0]["id"] if list_quotes() else "x"
    result = runner.invoke(app, ["rate", "set", qid, "6"])
    assert result.exit_code != 0

def test_rate_valid(tmp_path):
    with patch("cli.storage.DB_PATH", tmp_path / "test.db"):
        runner.invoke(app, ["quotes", "add", "Rateable", "--author", "X"])
        from cli.storage import list_quotes
        qid = list_quotes()[0]["id"]
        result = runner.invoke(app, ["rate", "set", qid, "5"])
        assert result.exit_code == 0
        assert "5/5" in result.output


# ── export ────────────────────────────────────────────────────────────────────

def test_export_empty():
    result = runner.invoke(app, ["export", "quotes"])
    assert result.exit_code != 0

def test_export_json(tmp_path):
    with patch("cli.storage.DB_PATH", tmp_path / "test.db"):
        runner.invoke(app, ["quotes", "add", "Export me", "--author", "X"])
        out = tmp_path / "out.json"
        result = runner.invoke(app, ["export", "quotes", "--format", "json", "--output", str(out)])
        assert result.exit_code == 0
        assert out.exists()

def test_export_csv(tmp_path):
    with patch("cli.storage.DB_PATH", tmp_path / "test.db"):
        runner.invoke(app, ["quotes", "add", "CSV quote", "--author", "Y"])
        out = tmp_path / "out.csv"
        result = runner.invoke(app, ["export", "quotes", "--format", "csv", "--output", str(out)])
        assert result.exit_code == 0
        assert out.exists()


# ── stats ─────────────────────────────────────────────────────────────────────

def test_stats_empty():
    result = runner.invoke(app, ["stats", "show"])
    assert result.exit_code == 0
    assert "0" in result.output

def test_stats_after_add():
    runner.invoke(app, ["quotes", "add", "Stat quote", "--author", "Z", "--type", "game"])
    result = runner.invoke(app, ["stats", "show"])
    assert result.exit_code == 0
    assert "1" in result.output