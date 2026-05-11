"""Конфигурация приложения"""
import os
from pathlib import Path

HOME_DIR = Path.home()
MEDIAQUOTE_DIR = HOME_DIR / ".mediaquote"
DB_PATH = MEDIAQUOTE_DIR / "quotes.db"

LOCAL_API_URL = "http://127.0.0.1:8000"
ZENQUOTES_API_URL = "https://zenquotes.io/api/random"

MEDIAQUOTE_DIR.mkdir(exist_ok=True)

REQUEST_TIMEOUT = 5.0
MAX_EXPORT_LINES = 1000