"""Команды для работы с избранным"""
import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from database import Database

app = typer.Typer()
console = Console()
db = Database()


@app.command(name="list")
def list_favorites():
    """Показать избранные цитаты"""
    favorites = db.get_favorites()
    if favorites:
        table = Table(title="⭐ Избранные цитаты")
        table.add_column("ID", style="cyan", width=12)
        table.add_column("Цитата", style="white")
        table.add_column("Автор", style="green")
        table.add_column("Источник", style="dim")
        table.add_column("⭐", style="yellow", width=6)
        for fav in favorites:
            text = fav['quote'][:50] + "..." if len(fav['quote']) > 50 else fav['quote']
            stars = "★" * fav.get('rating', 0) + "☆" * (5 - fav.get('rating', 0))
            table.add_row(fav['id'][:12], text, fav['author'],
                          f"{fav['source']} ({fav['content_type']})", stars)
        console.print(table)
        console.print(f"[dim]Всего: {len(favorites)} цитат[/dim]")
    else:
        console.print("[yellow]⭐ Избранное пусто[/yellow]")


@app.command()
def add(quote_id: str = typer.Argument(..., help="ID цитаты")):
    """Добавить цитату по ID"""
    from ..api_client import APIClient
    api = APIClient()
    results = api.search_quotes("", limit=100)
    quote = next((q for q in results if q['id'] == quote_id), None)
    if quote:
        if db.add_favorite(quote):
            console.print("[green]✓ Цитата добавлена в избранное[/green]")
        else:
            console.print("[yellow]Цитата уже в избранном[/yellow]")
    else:
        console.print(f"[red]✗ Цитата '{quote_id}' не найдена[/red]")


@app.command()
def remove(quote_id: str = typer.Argument(..., help="ID цитаты")):
    """Удалить из избранного"""
    if db.remove_favorite(quote_id):
        console.print("[green]✓ Цитата удалена[/green]")
    else:
        console.print(f"[red]✗ Цитата '{quote_id}' не найдена[/red]")


@app.command()
def clear():
    """Очистить всё избранное"""
    if typer.confirm("Вы уверены?"):
        db.clear_favorites()
        console.print("[green]✓ Избранное очищено[/green]")


@app.command()
def info(quote_id: str = typer.Argument(..., help="ID цитаты")):
    """Детальная информация о цитате"""
    favorites = db.get_favorites()
    quote = next((q for q in favorites if q['id'] == quote_id), None)
    if quote:
        panel = Panel(
            f"[italic]{quote['quote']}[/italic]\n\n"
            f"[bold]Автор:[/bold] {quote['author']}\n"
            f"[bold]Источник:[/bold] {quote['source']}\n"
            f"[bold]Тип:[/bold] {quote['content_type']}\n"
            f"[bold]Оценка:[/bold] {'★' * quote.get('rating', 0)}{'☆' * (5 - quote.get('rating', 0))}\n"
            f"[bold]Добавлена:[/bold] {quote['created_at']}",
            title=f"⭐ {quote_id}",
            border_style="cyan"
        )
        console.print(panel)
    else:
        console.print(f"[red]Цитата {quote_id} не найдена[/red]")
