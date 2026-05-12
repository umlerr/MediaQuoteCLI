#!/usr/bin/env python3
"""MediaQuote CLI (DeepSeek) — Цитаты из фильмов, игр и внешних API"""

from cli.stats import app as stats_app
from cli.export import app as export_app
from cli.rate import app as rate_app
from cli.favorites import app as favorites_app
from cli.games import app as games_app
from cli.movies import app as movies_app
from cli.quotes import app as quotes_app
from rich.panel import Panel
from rich.console import Console
import typer
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))


app = typer.Typer(
    name="mediaquote",
    help="🎬 Получай цитаты из фильмов, игр и внешних API",
    add_completion=False,
    rich_markup_mode="rich"
)

app.add_typer(quotes_app,   name="quotes",    help="Работа с цитатами")
app.add_typer(movies_app,   name="movies",    help="Цитаты из фильмов")
app.add_typer(games_app,    name="games",     help="Цитаты из игр")
app.add_typer(favorites_app, name="favorites", help="Управление избранным")
app.add_typer(rate_app,     name="rate",      help="Оценка цитат")
app.add_typer(export_app,   name="export",    help="Экспорт цитат")
app.add_typer(stats_app,    name="stats",     help="Статистика")

console = Console()


@app.command()
def version():
    """Показать версию"""
    console.print("[bold cyan]MediaQuote v1.0.0 (DeepSeek)[/bold cyan]")


@app.command()
def info():
    """Информация о приложении"""
    panel = Panel(
        "[bold]MediaQuote[/bold] - CLI утилита для получения цитат\n\n"
        "📁 Конфигурация: ~/.mediaquote/\n"
        "💾 База данных: ~/.mediaquote/quotes.db\n\n"
        "[dim]Доступные команды:[/dim]\n"
        "  • quotes random — случайная цитата\n"
        "  • movies list — список фильмов\n"
        "  • games list — список игр\n"
        "  • favorites list — избранное\n"
        "  • rate set — оценить цитату\n"
        "  • export to-json — экспорт\n"
        "  • stats all — статистика",
        title="📖 О программе",
        border_style="cyan"
    )
    console.print(panel)


if __name__ == "__main__":
    app()
