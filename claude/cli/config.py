"""Конфигурация CLI"""
import os
import json
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

class Config:
    CONFIG_DIR = Path.home() / ".mediaquote"
    CONFIG_FILE = CONFIG_DIR / "config.json"

    def __init__(self):
        self._config = self._load()

    def _default(self) -> dict:
        return {
            "api_url": os.getenv("MEDIAQUOTE_API_URL", "http://localhost:8000"),
            "timeout": int(os.getenv("MEDIAQUOTE_TIMEOUT", "10")),
            "verbose": os.getenv("MEDIAQUOTE_VERBOSE", "false").lower() == "true",
            "page_size": int(os.getenv("MEDIAQUOTE_PAGE_SIZE", "20")),
        }

    def _load(self) -> dict:
        if self.CONFIG_FILE.exists():
            try:
                with open(self.CONFIG_FILE) as f:
                    return {**self._default(), **json.load(f)}
            except Exception:
                pass
        return self._default()

    def save(self):
        self.CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        with open(self.CONFIG_FILE, "w") as f:
            json.dump(self._config, f, indent=2)

    def get(self, key: str, default=None):
        return self._config.get(key, default)

    def set(self, key: str, value):
        self._config[key] = value
        self.save()

    def reset(self):
        self._config = self._default()
        self.save()