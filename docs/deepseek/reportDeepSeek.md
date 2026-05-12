# MediaQuote CLI (DeepSeek-версия в папке `deepseek`)

Демонстрационная версия проекта в каталоге `deepseek`.

По состоянию кода на май 2026:
- API сервер: FastAPI (`mediaquote-api/`) — общий с версией Claude
- CLI: Typer + Rich (`deepseek/`)

## 1. Архитектура

```text
ZenQuotes API (https://zenquotes.io/api)
        |
        v
CLI api_client.py (httpx)
        |
        v
mediaquote-api (FastAPI + датасеты)
        |         |
        v         v
 movie_quotes   db.json
  (753 цитаты)  (20 цитат)
        |
        v
CLI (python cli.py ...)
        |
        v
SQLite (~/.mediaquote/quotes.db)
```

## 2. REST API

Базовый URL локального сервера: `http://localhost:8000`

Используемые endpoint-ы:
- `GET /movies/quotes`, `GET /movies/quotes/random`
- `GET /games/quotes`, `GET /games/quotes/random`
- `GET /quotes/random`, `GET /quotes/search`, `GET /quotes/stats`
- `GET /api/v1/movies/{title}/quotes`, `GET /api/v1/games/{title}/quotes`

Документация: `GET /docs`

## 3. Каталог CLI-команд (для отчёта)

Базовый запуск CLI:

```bash
cd deepseek
python cli.py --help
```

### 3.1 Глобальные команды

| Команда | Описание | Аргументы и опции | Пример | Используемый endpoint API | Ожидаемый результат |
|---|---|---|---|---|---|
| `version` | Показать версию CLI | Без параметров | `python cli.py version` | Не использует REST API | Вывод версии в консоль |
| `info` | Информация о приложении | Без параметров | `python cli.py info` | Не использует REST API | Панель с описанием команд |

### 3.2 `quotes`

Подкоманды: `random`, `search`, `latest`

| Команда | Описание | Аргументы и опции | Пример | Используемый endpoint API | Ожидаемый результат |
|---|---|---|---|---|---|
| `quotes random` | Случайная цитата | `--source [movie/game/zen/all]`; `--save/-s` | `python cli.py quotes random --source movie` | `GET /quotes/random` или ZenQuotes | Панель с цитатой |
| `quotes search` | Поиск по ключевому слову | `keyword [required]`; `--source`; `--limit/-l` | `python cli.py quotes search "war"` | `GET /quotes/search` | Таблица найденных цитат |
| `quotes latest` | Последние цитаты | `--limit` | `python cli.py quotes latest --limit 5` | `GET /quotes/random` (повтор) | Таблица цитат |

### 3.3 `movies`

Подкоманды: `random`, `list`, `quotes`

| Команда | Описание | Аргументы и опции | Пример | Используемый endpoint API | Ожидаемый результат |
|---|---|---|---|---|---|
| `movies random` | Случайная из фильма | `--save/-s` | `python cli.py movies random` | `GET /movies/quotes/random` | Панель с цитатой |
| `movies list` | Список всех фильмов | Без параметров | `python cli.py movies list` | `GET /movies/quotes` | Таблица фильмов |
| `movies quotes` | Цитаты из конкретного фильма | `movie [required]`; `--save-all` | `python cli.py movies quotes "Star Wars"` | `GET /movies/quotes?movie=` | Таблица цитат |

### 3.4 `games`

Подкоманды: `random`, `list`, `quotes`

| Команда | Описание | Аргументы и опции | Пример | Используемый endpoint API | Ожидаемый результат |
|---|---|---|---|---|---|
| `games random` | Случайная из игры | `--save/-s` | `python cli.py games random` | `GET /games/quotes/random` | Панель с цитатой |
| `games list` | Список всех игр | Без параметров | `python cli.py games list` | `GET /games/quotes` | Таблица игр |
| `games quotes` | Цитаты из конкретной игры | `game [required]`; `--save-all` | `python cli.py games quotes "BioShock"` | `GET /games/quotes?game=` | Таблица цитат |

### 3.5 `favorites`

Подкоманды: `list`, `add`, `remove`, `clear`, `info`

| Команда | Описание | Аргументы и опции | Пример | Используемый endpoint API | Ожидаемый результат |
|---|---|---|---|---|---|
| `favorites list` | Список избранного | Без параметров | `python cli.py favorites list` | Локальное хранилище (SQLite) | Таблица со звёздами рейтинга |
| `favorites add` | Добавить по ID | `quote_id [required]` | `python cli.py favorites add movie_001` | Локальное хранилище (SQLite) | Подтверждение |
| `favorites remove` | Удалить из избранного | `quote_id [required]` | `python cli.py favorites remove movie_001` | Локальное хранилище (SQLite) | Подтверждение |
| `favorites clear` | Очистить всё избранное | Без параметров | `python cli.py favorites clear` | Локальное хранилище (SQLite) | Запрос подтверждения |
| `favorites info` | Детали цитаты | `quote_id [required]` | `python cli.py favorites info movie_001` | Локальное хранилище (SQLite) | Панель с деталями |

### 3.6 `rate`

Подкоманды: `set`, `show`, `stats`

| Команда | Описание | Аргументы и опции | Пример | Используемый endpoint API | Ожидаемый результат |
|---|---|---|---|---|---|
| `rate set` | Поставить оценку 1-5 | `quote_id [required]`; `rating [int, required]` | `python cli.py rate set movie_001 5` | Локальное хранилище (SQLite) | Подтверждение со звёздами |
| `rate show` | Показать оценку | `quote_id [required]` | `python cli.py rate show movie_001` | Локальное хранилище (SQLite) | Оценка в формате ★★★★★ |
| `rate stats` | Статистика оценок | Без параметров | `python cli.py rate stats` | Локальное хранилище (SQLite) | Таблица распределения |

### 3.7 `export`

Подкоманды: `to-json`, `to-csv`, `to-markdown`, `history`

| Команда | Описание | Аргументы и опции | Пример | Используемый endpoint API | Ожидаемый результат |
|---|---|---|---|---|---|
| `export to-json` | Экспорт в JSON | `filepath [required]` | `python cli.py export to-json quotes.json` | Локальное хранилище (SQLite) | JSON файл |
| `export to-csv` | Экспорт в CSV | `filepath [required]` | `python cli.py export to-csv quotes.csv` | Локальное хранилище (SQLite) | CSV файл |
| `export to-markdown` | Экспорт в Markdown | `filepath [required]` | `python cli.py export to-markdown quotes.md` | Локальное хранилище (SQLite) | MD файл |
| `export history` | История экспортов | `--limit` | `python cli.py export history` | Локальное хранилище (SQLite) | Таблица истории |

### 3.8 `stats`

Подкоманды: `all`, `favorites`, `summary`

| Команда | Описание | Аргументы и опции | Пример | Используемый endpoint API | Ожидаемый результат |
|---|---|---|---|---|---|
| `stats all` | Полная статистика | Без параметров | `python cli.py stats all` | SQLite + `GET /quotes/stats` | Таблица всех метрик |
| `stats favorites` | Статистика избранного | Без параметров | `python cli.py stats favorites` | Локальное хранилище (SQLite) | Топ источников и авторов |
| `stats summary` | Краткая сводка | Без параметров | `python cli.py stats summary` | SQLite + `GET /quotes/stats` | Панель с цифрами |

## 4. API сервер

Общий с версией Claude. Команда запуска:

```bash
cd mediaquote-api
uvicorn main:app --reload
```

Сервер поднимается на `http://localhost:8000`, Swagger на `http://localhost:8000/docs`.

## 5. Технические детали

Библиотеки:
- API сервер: `fastapi`, `uvicorn`.
- CLI: `typer`, `rich`, `httpx`.
- Тесты: `pytest`, `pytest-cov`, `respx`.

Структура проекта:

```text
deepseek/
├── cli.py                    # entry point
├── api_client.py             # HTTP клиент (ZenQuotes + FastAPI)
├── config.py                 # конфигурация
├── database.py               # SQLite (favorites, ratings, export_history)
└── cli/
    ├── __init__.py
    ├── quotes.py
    ├── movies.py
    ├── games.py
    ├── favorites.py
    ├── rate.py
    ├── export.py
    └── stats.py
```

Обработка ошибок:
- HTTP запросы обёрнуты в `try/except`, при ошибке возвращается `None` или пустой список;
- команды проверяют результат и выводят сообщение об ошибке без traceback;
- при недоступном API выводится подсказка запустить сервер.

Конфигурация:
- `LOCAL_API_URL` — URL локального FastAPI сервера (по умолчанию `http://127.0.0.1:8000`);
- `ZENQUOTES_API_URL` — URL ZenQuotes;
- `DB_PATH` — путь к базе данных `~/.mediaquote/quotes.db`.

Логирование:
- статусные сообщения через `rich.console`;
- спиннеры `Progress` при HTTP запросах;
- логов в файлы не ведётся.

Тесты:
- `pytest tests/tests_deepseek/ -vv` — 31 тест.

## 6. Запуск тестов

```bash
cd MediaQuoteCLI
pytest tests/tests_deepseek/ -vv
```