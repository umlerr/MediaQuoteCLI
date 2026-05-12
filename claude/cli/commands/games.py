"""Команды для цитат из игр"""
import typer
from typing import Optional
from ..api_client import game_list, game_random, game_get
from ..storage import save_quote, rate_quote, add_favorite
from ..formatters import fmt_table, fmt_panel, console

app = typer.Typer(no_args_is_help=True, help="Цитаты из игр")


@app.command("list")
def cmd_list(
    game: Optional[str] = typer.Option(None, "--game", "-g", help="Название игры"),
    character: Optional[str] = typer.Option(None, "--character", "-c"),
    search: Optional[str] = typer.Option(None, "--search", "-s"),
    limit: int = typer.Option(20, "--limit", "-l"),
    save: bool = typer.Option(False, "--save"),
):
    """GET /games/quotes — список цитат из игр"""
    with console.status("[green]Получаю...[/green]"):
        quotes = game_list(game=game, character=character, search=search, limit=limit)
    if not quotes:
        console.print("[yellow]Цитаты не найдены. Проверь что API запущен: uvicorn main:app[/yellow]")
        raise typer.Exit(1)
    fmt_table(quotes)
    if save:
        for q in quotes:
            save_quote(q)
        console.print(f"[green]✅ Сохранено {len(quotes)} цитат[/green]")


@app.command("random")
def cmd_random(
    save: bool = typer.Option(False, "--save", "-s"),
    rate: bool = typer.Option(False, "--rate", "-r", help="Оценить цитату сразу"),
):
    """GET /games/quotes/random — случайная из игры"""
    with console.status("[green]Получаю...[/green]"):
        q = game_random()
    if not q:
        console.print("[red]API недоступен. Запусти: uvicorn main:app[/red]")
        raise typer.Exit(1)
    fmt_panel(q)
    if typer.confirm("Сохранить цитату?", default=False):
        saved = save_quote(q)
        console.print(f"[green]✅ Сохранено: {saved['id']}[/green]")

        if typer.confirm("Добавить в избранное?", default=False):
            add_favorite(saved['id'])
            console.print("[green]⭐ Добавлено в избранное[/green]")

        if typer.confirm("Оценить цитату?", default=False):
            score = typer.prompt("Оценка (1-5)", type=int)
            if 1 <= score <= 5:
                rate_quote(saved['id'], score)
                console.print(f"[green]{'⭐' * score} ({score}/5)[/green]")
            else:
                console.print("[red]Оценка должна быть от 1 до 5[/red]")


@app.command("get")
def cmd_get(
    quote_id: int = typer.Argument(..., help="ID цитаты"),
    save: bool = typer.Option(False, "--save", "-s"),
):
    """GET /games/quotes/{id} — цитата по ID"""
    q = game_get(quote_id)
    if not q:
        console.print(f"[red]Цитата {quote_id} не найдена[/red]")
        raise typer.Exit(1)
    fmt_panel(q)
    if save:
        save_quote(q)
        console.print(f"[green]✅ Сохранено: {q['id']}[/green]")
