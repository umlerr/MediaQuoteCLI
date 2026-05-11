"""Команды для работы с играми"""
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
    """Случайная цитата из игры"""
    quote = api.get_random_quote("game")
    if quote:
        panel = Panel(
            f"[italic]{quote['quote']}[/italic]\n\n[bold cyan]— {quote['author']}[/bold cyan]\n[dim]Игра: {quote['source']}[/dim]",
            title="🎮 Random Game Quote",
            border_style="magenta"
        )
        console.print(panel)
        if save:
            db.add_favorite(quote)
            console.print("[green]✓ Сохранено![/green]")
    else:
        console.print("[red]✗ Не удалось получить цитату[/red]")


@app.command(name="list")
def list_games():
    """Список всех игр в базе"""
    with console.status("Загрузка..."):
        sources = api.get_sources()
        games = sources.get("games", [])

    if games:
        table = Table(title="Список игр")
        table.add_column("#", style="cyan", width=4)
        table.add_column("Название", style="white")
        for idx, game in enumerate(games, 1):
            table.add_row(str(idx), game)
        console.print(table)
        console.print(f"[dim]Всего: {len(games)} игр[/dim]")
    else:
        console.print("[yellow]Игры не найдены[/yellow]")


@app.command()
def quotes(
    game: str = typer.Argument(..., help="Название игры"),
    save_all: bool = typer.Option(False, "--save-all")
):
    """Цитаты из конкретной игры"""
    with console.status(f"Загрузка цитат из '{game}'..."):
        result = api.get_game_quotes(game)

    if result:
        table = Table(title=f"Цитаты: {game}")
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
        console.print(f"[yellow]Цитаты из '{game}' не найдены[/yellow]")