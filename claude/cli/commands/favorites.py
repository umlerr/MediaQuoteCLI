"""Избранное и оценки"""
import typer

from ..formatters import fmt_panel, console
from ..storage import add_favorite, list_favorites, rate_quote, get_rating, get_quote

fav_app = typer.Typer(no_args_is_help=True, help="Избранные цитаты")
rate_app = typer.Typer(no_args_is_help=True, help="Оценка цитат")


@fav_app.command("add")
def cmd_fav_add(quote_id: str = typer.Argument(...)):
    """POST /quotes/{id}/favorite"""
    q = get_quote(quote_id)
    if not q:
        console.print("[red]Сначала сохрани цитату: quotes random --save[/red]")
        raise typer.Exit(1)
    add_favorite(quote_id)
    console.print(f"[green]⭐ Добавлено в избранное: {quote_id}[/green]")


@fav_app.command("list")
def cmd_fav_list():
    """Список избранного"""
    quotes = list_favorites()
    if not quotes:
        console.print("[yellow]Избранное пусто[/yellow]")
        return
    for q in quotes:
        fmt_panel(q, is_fav=True)


@rate_app.command("set")
def cmd_rate(
        quote_id: str = typer.Argument(...),
        score: int = typer.Argument(..., help="Оценка 1-5"),
):
    """POST /quotes/{id}/rate"""
    if not 1 <= score <= 5:
        console.print("[red]Оценка должна быть от 1 до 5[/red]")
        raise typer.Exit(1)
    q = get_quote(quote_id)
    if not q:
        console.print(f"[red]Цитата не найдена: {quote_id}[/red]")
        raise typer.Exit(1)
    rate_quote(quote_id, score)
    console.print(f"[green]✅ {'⭐' * score} ({score}/5) — {quote_id}[/green]")


@rate_app.command("get")
def cmd_get_rating(quote_id: str = typer.Argument(...)):
    """Получить оценку"""
    q = get_quote(quote_id)
    if not q:
        console.print(f"[red]Цитата не найдена: {quote_id}[/red]")
        raise typer.Exit(1)
    rating = get_rating(quote_id)
    fmt_panel(q, rating=rating)
