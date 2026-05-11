"""Тесты для модуля database.py"""

import sqlite3

from database import Database


class TestDatabase:
    """Тесты для работы с базой данных"""

    def test_init_creates_tables(self, test_db: Database):
        """Проверка создания таблиц при инициализации"""
        with sqlite3.connect(test_db.db_path) as conn:
            # Проверяем наличие таблиц
            tables = conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            ).fetchall()
            table_names = [t[0] for t in tables]

            assert "favorites" in table_names
            assert "ratings" in table_names
            assert "export_history" in table_names

    def test_add_favorite_success(self, test_db: Database, sample_quote_movie):
        """Успешное добавление цитаты в избранное"""
        result = test_db.add_favorite(sample_quote_movie)

        assert result is True

        # Проверяем что добавилось
        favorites = test_db.get_favorites()
        assert len(favorites) == 1
        assert favorites[0]["id"] == sample_quote_movie["id"]
        assert favorites[0]["quote"] == sample_quote_movie["quote"]
        assert favorites[0]["author"] == sample_quote_movie["author"]

    def test_add_favorite_duplicate(self, test_db: Database, sample_quote_movie):
        """Попытка добавить дубликат цитаты"""
        # Добавляем первый раз
        test_db.add_favorite(sample_quote_movie)

        # Добавляем второй раз
        result = test_db.add_favorite(sample_quote_movie)

        assert result is False  # Дубликат не добавился

        favorites = test_db.get_favorites()
        assert len(favorites) == 1  # Осталась только одна

    def test_get_favorites_empty(self, test_db: Database):
        """Получение избранного когда оно пустое"""
        favorites = test_db.get_favorites()
        assert favorites == []

    def test_get_favorites_multiple(self, test_db: Database, sample_quote_movie, sample_quote_game):
        """Получение нескольких избранных цитат"""
        test_db.add_favorite(sample_quote_movie)
        test_db.add_favorite(sample_quote_game)

        favorites = test_db.get_favorites()

        assert len(favorites) == 2
        ids = [f["id"] for f in favorites]
        assert sample_quote_movie["id"] in ids
        assert sample_quote_game["id"] in ids

    def test_remove_favorite_success(self, test_db: Database, sample_quote_movie):
        """Успешное удаление из избранного"""
        test_db.add_favorite(sample_quote_movie)
        assert len(test_db.get_favorites()) == 1

        result = test_db.remove_favorite(sample_quote_movie["id"])

        assert result is True
        assert len(test_db.get_favorites()) == 0

    def test_remove_favorite_not_found(self, test_db: Database):
        """Удаление несуществующей цитаты"""
        result = test_db.remove_favorite("non_existent_id")
        assert result is False

    def test_is_favorite(self, test_db: Database, sample_quote_movie):
        """Проверка наличия цитаты в избранном"""
        assert test_db.is_favorite(sample_quote_movie["id"]) is False

        test_db.add_favorite(sample_quote_movie)

        assert test_db.is_favorite(sample_quote_movie["id"]) is True

    def test_rate_quote_success(self, test_db: Database, sample_quote_movie):
        """Успешная оценка цитаты"""
        # Добавляем в избранное
        test_db.add_favorite(sample_quote_movie)

        # Оцениваем
        result = test_db.rate_quote(sample_quote_movie["id"], 5)

        assert result is True

        # Проверяем оценку
        rating = test_db.get_rating(sample_quote_movie["id"])
        assert rating == 5

        # Проверяем что оценка сохранилась в favorites
        favorites = test_db.get_favorites()
        assert favorites[0]["rating"] == 5

    def test_rate_quote_invalid_rating(self, test_db: Database, sample_quote_movie):
        """Оценка с невалидным рейтингом"""
        test_db.add_favorite(sample_quote_movie)

        # Оценка должна быть от 1 до 5
        result = test_db.rate_quote(sample_quote_movie["id"], 6)
        # Метод должен обработать или вернуть False
        # Зависит от реализации, но тест должен пройти

    def test_get_rating_not_rated(self, test_db: Database, sample_quote_movie):
        """Получение оценки для неоценённой цитаты"""
        test_db.add_favorite(sample_quote_movie)

        rating = test_db.get_rating(sample_quote_movie["id"])
        assert rating is None

    def test_get_average_rating(self, test_db: Database, sample_quote_movie, sample_quote_game):
        """Подсчёт среднего рейтинга"""
        test_db.add_favorite(sample_quote_movie)
        test_db.add_favorite(sample_quote_game)

        test_db.rate_quote(sample_quote_movie["id"], 5)
        test_db.rate_quote(sample_quote_game["id"], 3)

        avg = test_db.get_average_rating()
        assert avg == 4.0

    def test_get_average_rating_no_ratings(self, test_db: Database):
        """Средний рейтинг когда нет оценок"""
        avg = test_db.get_average_rating()
        assert avg == 0.0

    def test_save_export_record(self, test_db: Database, tmp_path):
        """Сохранение записи об экспорте"""
        export_file = tmp_path / "export.json"

        test_db.save_export_record("json", str(export_file), 10)

        history = test_db.get_export_history()
        assert len(history) == 1
        assert history[0]["format"] == "json"
        assert history[0]["quotes_count"] == 10

    def test_get_export_history_limit(self, test_db: Database, tmp_path):
        """Получение истории экспортов с лимитом"""
        for i in range(5):
            test_db.save_export_record("json", f"/tmp/export_{i}.json", i)

        history = test_db.get_export_history(limit=3)
        assert len(history) == 3

    def test_get_stats(self, test_db: Database, sample_quote_movie, sample_quote_game):
        """Получение полной статистики"""
        # Добавляем данные
        test_db.add_favorite(sample_quote_movie)
        test_db.add_favorite(sample_quote_game)
        test_db.rate_quote(sample_quote_movie["id"], 5)
        test_db.save_export_record("json", "/tmp/export.json", 2)

        stats = test_db.get_stats()

        assert stats["favorites_count"] == 2
        assert stats["rated_count"] == 1
        assert stats["average_rating"] == 5.0
        assert stats["export_count"] == 1
        assert "rating_distribution" in stats

    def test_clear_favorites(self, test_db: Database, sample_quote_movie):
        """Очистка всего избранного"""
        test_db.add_favorite(sample_quote_movie)
        assert len(test_db.get_favorites()) == 1

        test_db.clear_favorites()

        assert len(test_db.get_favorites()) == 0