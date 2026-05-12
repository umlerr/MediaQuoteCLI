"""MediaQuote CLI — главный модуль"""
import typer
from typing import Optional
from rich.console import Console

from .commands.quotes import app as quotes_app
from .commands.movies import app as movies_app
from .commands.games import app as games_app
from .commands.favorites import fav_app, rate_app
from .commands.export_stats import export_app, stats_app
from .config import Config

__version__ = "1.0.0"
console = Console()

app = typer.Typer(
    name="mediaquote",
    help="🎬 MediaQuote CLI — цитаты из фильмов, игр и известных людей",
    no_args_is_help=True,
    add_completion=False,
)

app.add_typer(quotes_app,  name="quotes",    help="📝 Цитаты (list, get, random, search, add, delete)")
app.add_typer(movies_app,  name="movies",    help="🎬 Цитаты из фильмов")
app.add_typer(games_app,   name="games",     help="🎮 Цитаты из игр")
app.add_typer(fav_app,     name="favorites", help="⭐ Избранное")
app.add_typer(rate_app,    name="rate",      help="⭐ Оценки")
app.add_typer(export_app,  name="export",    help="📤 Экспорт")
app.add_typer(stats_app,   name="stats",     help="📊 Статистика")


@app.command()
def version():
    """Версия утилиты"""
    console.print(f"[bold cyan]MediaQuote CLI[/bold cyan] v[yellow]{__version__}[/yellow]")


@app.command()
def config(
    show: bool = typer.Option(False, "--show", "-s"),
    reset: bool = typer.Option(False, "--reset", "-r"),
    set_timeout: Optional[int] = typer.Option(None, "--timeout"),
    set_api_url: Optional[str] = typer.Option(None, "--api-url"),
):
    """⚙️ Конфигурация"""
    cfg = Config()
    if reset:
        cfg.reset()
        console.print("[green]✅ Сброшено[/green]")
        return
    if set_timeout:
        cfg.set("timeout", set_timeout)
        console.print(f"[green]✅ Таймаут: {set_timeout}s[/green]")
    if set_api_url:
        cfg.set("api_url", set_api_url)
        console.print(f"[green]✅ API URL: {set_api_url}[/green]")
    if show or not any([set_timeout, set_api_url, reset]):
        console.print("\n[bold cyan]Конфигурация:[/bold cyan]")
        console.print(f"  API URL:  [yellow]{cfg.get('api_url')}[/yellow]")
        console.print(f"  Таймаут:  [yellow]{cfg.get('timeout')}s[/yellow]")
        console.print(f"  Verbose:  [yellow]{cfg.get('verbose')}[/yellow]")
