"""Команды для статистики"""
import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from database import Database
from api_client import APIClient

app = typer.Typer()
console = Console()
db = Database()
api = APIClient()


@app.command(name="all")
def all_stats():
    """Показать всю статистику"""
    local_stats = db.get_stats()
    with console.status("Загрузка данных из API..."):
        sources = api.get_sources()

    table = Table(title="📊 MediaQuote Statistics")
    table.add_column("Метрика", style="cyan")
    table.add_column("Значение", style="green")
    table.add_row("Фильмов в базе", str(len(sources.get("movies", []))))
    table.add_row("Игр в базе", str(len(sources.get("games", []))))
    table.add_row("Избранных цитат", str(local_stats['favorites_count']))
    table.add_row("Оценённых цитат", str(local_stats['rated_count']))
    table.add_row("Средняя оценка", f"{local_stats['average_rating']}/5")
    table.add_row("Выполнено экспортов", str(local_stats['export_count']))
    console.print(table)


@app.command()
def favorites():
    """Статистика по избранному"""
    favs = db.get_favorites()
    if not favs:
        console.print("[yellow]Нет избранных цитат[/yellow]")
        return
    from collections import Counter
    sources_counter = Counter(f['source'] for f in favs)
    authors_counter = Counter(f['author'] for f in favs)
    types_counter = Counter(f['content_type'] for f in favs)

    console.print(f"[bold]Всего цитат: [green]{len(favs)}[/green][/bold]\n")

    t1 = Table(title="Топ источников")
    t1.add_column("Источник", style="cyan")
    t1.add_column("Цитат", style="green")
    for source, count in sources_counter.most_common(5):
        t1.add_row(source[:40], str(count))
    console.print(t1)

    t2 = Table(title="Топ авторов")
    t2.add_column("Автор", style="cyan")
    t2.add_column("Цитат", style="green")
    for author, count in authors_counter.most_common(5):
        t2.add_row(author, str(count))
    console.print(t2)

    for ctype, count in types_counter.items():
        console.print(f"  {ctype}: {count} ({count/len(favs)*100:.1f}%)")


@app.command()
def summary():
    """Краткая сводка"""
    db_stats = db.get_stats()
    sources = api.get_sources()
    panel = Panel(
        f"[bold]MediaQuote в цифрах[/bold]\n\n"
        f"Фильмов: {len(sources.get('movies', []))}\n"
        f"Игр: {len(sources.get('games', []))}\n"
        f"Избранное: {db_stats['favorites_count']}\n"
        f"Оценок: {db_stats['rated_count']}\n"
        f"Средний рейтинг: {db_stats['average_rating']}/5\n"
        f"Экспортов: {db_stats['export_count']}",
        title="📈 Краткая сводка",
        border_style="cyan"
    )
    console.print(panel)