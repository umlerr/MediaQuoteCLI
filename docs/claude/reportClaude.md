# MediaQuote CLI (Claude-версия в папке `claude`)

Демонстрационная версия проекта в каталоге `claude`.

По состоянию кода на май 2026:
- API сервер: FastAPI (`mediaquote-api/`)
- CLI: Typer + Rich (`claude/`)

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

Основные endpoint-ы:
- `GET /movies/quotes`, `GET /movies/quotes/{id}`, `GET /movies/quotes/random`
- `GET /games/quotes`, `GET /games/quotes/{id}`, `GET /games/quotes/random`
- `GET /quotes/random`, `GET /quotes/search`, `GET /quotes/stats`

Документация: `GET /docs`

## 3. Каталог CLI-команд (для отчёта)

Базовый запуск CLI:

```bash
cd claude
python cli.py --help
```

### 3.1 Глобальные команды

| Команда | Описание | Аргументы и опции | Пример | Используемый endpoint API | Ожидаемый результат |
|---|---|---|---|---|---|
| `version` | Показать версию CLI | Без параметров | `python cli.py version` | Не использует REST API | Вывод версии в консоль |
| `config` | Управление конфигурацией | `--show/-s`; `--reset/-r`; `--timeout INT`; `--api-url STR` | `python cli.py config --show` | Не использует REST API | Печатает или сохраняет настройки в `~/.mediaquote/config.json` |

### 3.2 `quotes`

Подкоманды: `list`, `get`, `random`, `search`, `filter`, `add`, `delete`

| Команда | Описание | Аргументы и опции | Пример | Используемый endpoint API | Ожидаемый результат |
|---|---|---|---|---|---|
| `quotes list` | Список цитат | `--author/-a`; `--type/-t`; `--source/-s`; `--limit/-l [default=20]`; `--local` | `python cli.py quotes list --type movie` | ZenQuotes или локальное хранилище | Таблица цитат в консоли |
| `quotes get` | Цитата по ID | `quote_id [required]` | `python cli.py quotes get zen_abc123` | Локальное хранилище (SQLite) | Панель с цитатой или ошибка |
| `quotes random` | Случайная цитата | Без параметров | `python cli.py quotes random` | `GET /quotes/random` + ZenQuotes | Панель с цитатой, интерактивный диалог сохранения/оценки/избранного |
| `quotes search` | Поиск по ключевому слову | `query [required]`; `--limit/-l`; `--local` | `python cli.py quotes search "war"` | `GET /quotes/search` + ZenQuotes | Таблица найденных цитат |
| `quotes filter` | Продвинутая фильтрация | `--type/-t`; `--author/-a`; `--source/-s`; `--sort`; `--order`; `--limit/-l` | `python cli.py quotes filter --type game --sort author` | Локальное хранилище (SQLite) | Таблица отфильтрованных цитат |
| `quotes add` | Добавить вручную | `content [required]`; `--author/-a`; `--source/-s`; `--type/-t`; `--tags` | `python cli.py quotes add "Text" --author "Name"` | Локальное хранилище (SQLite) | Подтверждение сохранения + панель |
| `quotes delete` | Удалить из хранилища | `quote_id [required]`; `--yes/-y` | `python cli.py quotes delete local_abc --yes` | Локальное хранилище (SQLite) | Подтверждение удаления |

### 3.3 `movies`

Подкоманды: `list`, `get`, `random`

| Команда | Описание | Аргументы и опции | Пример | Используемый endpoint API | Ожидаемый результат |
|---|---|---|---|---|---|
| `movies list` | Список цитат из фильмов | `--movie/-m`; `--character/-c`; `--search/-s`; `--limit/-l [default=20]`; `--save` | `python cli.py movies list --movie "Godfather"` | `GET /movies/quotes` | Таблица цитат, в конце `Найдено: N` |
| `movies random` | Случайная из фильма | Без параметров | `python cli.py movies random` | `GET /movies/quotes/random` | Панель с цитатой, интерактивный диалог |
| `movies get` | Цитата по ID | `quote_id [int, required]`; `--save/-s` | `python cli.py movies get 42` | `GET /movies/quotes/42` | Панель с цитатой |

### 3.4 `games`

Подкоманды: `list`, `get`, `random`

| Команда | Описание | Аргументы и опции | Пример | Используемый endpoint API | Ожидаемый результат |
|---|---|---|---|---|---|
| `games list` | Список цитат из игр | `--game/-g`; `--character/-c`; `--search/-s`; `--limit/-l [default=20]`; `--save` | `python cli.py games list --game "Portal"` | `GET /games/quotes` | Таблица цитат, в конце `Найдено: N` |
| `games random` | Случайная из игры | Без параметров | `python cli.py games random` | `GET /games/quotes/random` | Панель с цитатой, интерактивный диалог |
| `games get` | Цитата по ID | `quote_id [int, required]`; `--save/-s` | `python cli.py games get 5` | `GET /games/quotes/5` | Панель с цитатой |

### 3.5 `favorites`

Подкоманды: `add`, `list`

| Команда | Описание | Аргументы и опции | Пример | Используемый endpoint API | Ожидаемый результат |
|---|---|---|---|---|---|
| `favorites add` | Добавить в избранное | `quote_id [required]` | `python cli.py favorites add zen_abc123` | Локальное хранилище (SQLite) | Подтверждение добавления |
| `favorites list` | Список избранного | Без параметров | `python cli.py favorites list` | Локальное хранилище (SQLite) | Панели с цитатами или сообщение "пусто" |

### 3.6 `rate`

Подкоманды: `set`, `get`

| Команда | Описание | Аргументы и опции | Пример | Используемый endpoint API | Ожидаемый результат |
|---|---|---|---|---|---|
| `rate set` | Поставить оценку | `quote_id [required]`; `score [int, 1-5, required]` | `python cli.py rate set zen_abc123 5` | Локальное хранилище (SQLite) | Подтверждение с звёздами |
| `rate get` | Просмотр оценки | `quote_id [required]` | `python cli.py rate get zen_abc123` | Локальное хранилище (SQLite) | Панель с цитатой и оценкой |

### 3.7 `export`

Подкоманды: `quotes`

| Команда | Описание | Аргументы и опции | Пример | Используемый endpoint API | Ожидаемый результат |
|---|---|---|---|---|---|
| `export quotes` | Экспорт цитат | `--format/-f [json/csv, default=json]`; `--output/-o [path]`; `--type/-t`; `--limit/-l [default=500]` | `python cli.py export quotes --format csv --output quotes.csv` | Локальное хранилище (SQLite) | Файл или вывод в консоль |

### 3.8 `stats`

Подкоманды: `show`

| Команда | Описание | Аргументы и опции | Пример | Используемый endpoint API | Ожидаемый результат |
|---|---|---|---|---|---|
| `stats show` | Статистика хранилища | Без параметров | `python cli.py stats show` | Локальное хранилище (SQLite) | Таблица с общим числом цитат, избранным, средней оценкой, разбивкой по типу |

## 4. API сервер

Команда запуска: `uvicorn main:app --reload`

Описание: независимый FastAPI сервер с датасетами фильмов и игр.

Файлы: `mediaquote-api/main.py`, `mediaquote-api/data.py`.

Пример:

```bash
cd mediaquote-api
pip install -r requirements-test.txt
uvicorn main:app --reload
```

Ожидаемый результат: сервер поднимается на `http://localhost:8000`, Swagger на `http://localhost:8000/docs`.

## 5. Технические детали

Библиотеки:

- API сервер: `fastapi`, `uvicorn`.
- CLI: `typer`, `rich`, `httpx`, `python-dotenv`.
- Тесты: `pytest`, `pytest-cov`, `respx`.

Предполагаемая структура проекта:

```text
MediaQuoteCLI/
├── claude/
│   ├── cli.py                    # entry point
│   └── cli/
│       ├── main.py               # root Typer app
│       ├── config.py             # конфигурация
│       ├── storage.py            # SQLite хранилище
│       ├── api_client.py         # HTTP клиент
│       ├── formatters.py         # Rich вывод
│       └── commands/             # группы команд
├── mediaquote-api/
│   ├── main.py                   # FastAPI сервер
│   ├── data.py                   # датасеты
│   └── requirements.txt
├── tests/
│   └── tests_claude/
└── README.md
```

Обработка ошибок:
- сетевые ошибки и недоступность API обрабатываются в `api_client.py` через `try/except`, выводится понятное сообщение с подсказкой запустить сервер;
- при отсутствии данных команды выводят `Цитаты не найдены`;
- при ошибке ресурс не найден — `raise typer.Exit(1)`.

Конфигурация:
- CLI: env-переменные `MEDIAQUOTE_API_URL`, `MEDIAQUOTE_TIMEOUT`, `MEDIAQUOTE_VERBOSE`, `MEDIAQUOTE_PAGE_SIZE`;
- локальный конфиг CLI: `~/.mediaquote/config.json`;
- база данных: `~/.mediaquote/quotes.db`.

Логирование:
- все статусные сообщения через `rich.console`;
- индикаторы прогресса `console.status()` при HTTP запросах;
- логов в файлы не ведётся.

Тесты:
- CLI: `pytest tests/tests_claude/ -vv`.

## 6. Запуск тестов

```bash
cd MediaQuoteCLI
pytest tests/tests_claude/ -vv
```
