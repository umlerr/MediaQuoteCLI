"""Команды для работы с цитатами"""
import typer
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table
from api_client import APIClient
from database import Database

app = typer.Typer()
console = Console()
api = APIClient()
db = Database()


@app.command()
def random(
    source: str = typer.Option("all", help="Источник: movie, game, zen, all"),
    save: bool = typer.Option(False, "--save", "-s", help="Сохранить в избранное")
):
    """Случайная цитата"""
    import random as rnd
    with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), transient=True) as progress:
        progress.add_task("Загрузка...", total=None)
        if source == "zen":
            quote = api.get_zen_quote()
        elif source == "movie":
            quote = api.get_random_quote("movie")
        elif source == "game":
            quote = api.get_random_quote("game")
        else:
            if rnd.choice([True, False]):
                quote = api.get_zen_quote()
                if not quote:
                    quote = api.get_random_quote(rnd.choice(["movie", "game"]))
            else:
                quote = api.get_random_quote(rnd.choice(["movie", "game"]))

    if quote:
        panel = Panel(
            f"[italic]{quote['quote']}[/italic]\n\n[bold cyan]— {quote['author']}"
            f"[/bold cyan]\n[dim]Источник: {quote['source']} ({quote['content_type']})[/dim]",
            title="🎬 MediaQuote",
            border_style="green",
            padding=(1, 2)
        )
        console.print(panel)
        if save:
            db.add_favorite(quote)
            console.print("[green]✓ Сохранено в избранное![/green]")
    else:
        console.print("[red]✗ Не удалось получить цитату[/red]")


@app.command()
def search(
    keyword: str = typer.Argument(..., help="Ключевое слово"),
    source: str = typer.Option("all", help="movie, game, all"),
    limit: int = typer.Option(10, "--limit", "-l")
):
    """Поиск цитат"""
    content_type = None if source == "all" else source
    with console.status(f"Поиск '{keyword}'..."):
        results = api.search_quotes(keyword, content_type, limit)

    if results:
        table = Table(title=f"Результаты: '{keyword}'")
        table.add_column("#", style="cyan", width=4)
        table.add_column("Цитата", style="white")
        table.add_column("Автор", style="green")
        table.add_column("Источник", style="dim")
        for idx, q in enumerate(results[:limit], 1):
            text = q['quote'][:60] + "..." if len(q['quote']) > 60 else q['quote']
            table.add_row(str(idx), text, q['author'], f"{q['source']} ({q['content_type']})")
        console.print(table)
    else:
        console.print(f"[yellow]Ничего не найдено для '{keyword}'[/yellow]")


@app.command()
def latest(limit: int = typer.Option(10, help="Количество")):
    """Последние цитаты"""
    with console.status("Загрузка..."):
        quotes = []
        for _ in range(min(limit, 10)):
            q = api.get_random_quote()
            if q:
                quotes.append(q)

    if quotes:
        table = Table(title="Последние цитаты")
        table.add_column("Цитата", style="white")
        table.add_column("Автор", style="green")
        table.add_column("Источник", style="dim")
        for q in quotes:
            text = q['quote'][:50] + "..." if len(q['quote']) > 50 else q['quote']
            table.add_row(text, q['author'], q['source'])
        console.print(table)
    else:
        console.print("[yellow]Нет цитат[/yellow]")
