"""Команды для работы с фильмами"""
import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from api_client import APIClient
from database import Database

app = typer.Typer()
console = Console()
api = APIClient()
db = Database()


@app.command()
def random(save: bool = typer.Option(False, "--save", "-s")):
    """Случайная цитата из фильма"""
    quote = api.get_random_quote("movie")
    if quote:
        panel = Panel(
            f"[italic]{quote['quote']}[/italic]\n\n[bold cyan]— {quote['author']}"
            f"[/bold cyan]\n[dim]Фильм: {quote['source']}[/dim]",
            title="🎬 Random Movie Quote",
            border_style="blue"
        )
        console.print(panel)
        if save:
            db.add_favorite(quote)
            console.print("[green]✓ Сохранено![/green]")
    else:
        console.print("[red]✗ Не удалось получить цитату[/red]")


@app.command(name="list")
def list_movies():
    """Список всех фильмов в базе"""
    with console.status("Загрузка..."):
        sources = api.get_sources()
        movies = sources.get("movies", [])

    if movies:
        table = Table(title="Список фильмов")
        table.add_column("#", style="cyan", width=4)
        table.add_column("Название", style="white")
        for idx, movie in enumerate(movies, 1):
            table.add_row(str(idx), movie)
        console.print(table)
        console.print(f"[dim]Всего: {len(movies)} фильмов[/dim]")
    else:
        console.print("[yellow]Фильмы не найдены[/yellow]")


@app.command()
def quotes(
    movie: str = typer.Argument(..., help="Название фильма"),
    save_all: bool = typer.Option(False, "--save-all")
):
    """Цитаты из конкретного фильма"""
    with console.status(f"Загрузка цитат из '{movie}'..."):
        result = api.get_movie_quotes(movie)

    if result:
        table = Table(title=f"Цитаты: {movie}")
        table.add_column("#", style="cyan", width=4)
        table.add_column("Цитата", style="white")
        table.add_column("Автор", style="green")
        for idx, q in enumerate(result, 1):
            text = q['quote'][:70] + "..." if len(q['quote']) > 70 else q['quote']
            table.add_row(str(idx), text, q['author'])
        console.print(table)
        if save_all:
            saved = sum(1 for q in result if db.add_favorite(q))
            console.print(f"[green]✓ Сохранено {saved} цитат[/green]")
    else:
        console.print(f"[yellow]Цитаты из '{movie}' не найдены[/yellow]")
