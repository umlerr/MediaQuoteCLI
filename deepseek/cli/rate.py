"""Команды для оценки цитат"""
import typer
from rich.console import Console
from rich.table import Table
from database import Database

app = typer.Typer()
console = Console()
db = Database()


@app.command(name="set")
def set_rating(
    quote_id: str = typer.Argument(..., help="ID цитаты"),
    rating: int = typer.Argument(..., help="Оценка от 1 до 5")
):
    """Оценить цитату от 1 до 5"""
    if not 1 <= rating <= 5:
        console.print("[red]Оценка должна быть от 1 до 5[/red]")
        raise typer.Exit(1)
    favorites = db.get_favorites()
    quote = next((q for q in favorites if q['id'] == quote_id), None)
    if not quote:
        console.print(f"[red]✗ Цитата {quote_id} не найдена в избранном[/red]")
        console.print("[yellow]Сначала добавьте через 'favorites add'[/yellow]")
        raise typer.Exit(1)
    if db.rate_quote(quote_id, rating):
        stars = "★" * rating + "☆" * (5 - rating)
        console.print(f"[green]✓ Оценка {rating} {stars}[/green]")
    else:
        console.print("[red]✗ Ошибка при сохранении оценки[/red]")


@app.command()
def show(quote_id: str = typer.Argument(..., help="ID цитаты")):
    """Показать оценку цитаты"""
    rating = db.get_rating(quote_id)
    if rating is not None:
        stars = "★" * rating + "☆" * (5 - rating)
        console.print(f"Оценка: {rating}/5 {stars}")
    else:
        console.print(f"[yellow]Цитата {quote_id} ещё не оценена[/yellow]")


@app.command()
def stats():
    """Статистика по оценкам"""
    s = db.get_stats()
    distribution = s.get('rating_distribution', {})
    if distribution:
        table = Table(title="📊 Статистика оценок")
        table.add_column("Оценка", style="cyan")
        table.add_column("Количество", style="green")
        table.add_column("Процент", style="yellow")
        total = sum(distribution.values())
        for r in range(1, 6):
            count = distribution.get(str(r), 0)
            percent = (count / total * 100) if total > 0 else 0
            table.add_row(f"{r} ★", str(count), f"{percent:.1f}%")
        console.print(table)
        console.print(f"[bold]Средняя оценка: {s['average_rating']}/5[/bold]")
    else:
        console.print("[yellow]Нет оценённых цитат[/yellow]")