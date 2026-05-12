"""Команды для работы с цитатами"""
import typer
from typing import Optional
from ..api_client import get_random_quote, search_all, zen_list
from ..storage import save_quote, get_quote, delete_quote, list_quotes, search_quotes, rate_quote, add_favorite
from ..formatters import fmt_panel, fmt_table, console

app = typer.Typer(no_args_is_help=True, help="Работа с цитатами")


@app.command("list")
def cmd_list(
    author: Optional[str] = typer.Option(None, "--author", "-a"),
    source_type: Optional[str] = typer.Option(None, "--type", "-t", help="person | movie | game"),
    source: Optional[str] = typer.Option(None, "--source", "-s"),
    limit: int = typer.Option(20, "--limit", "-l"),
    local: bool = typer.Option(False, "--local", help="Только локальное хранилище"),
):
    """GET /quotes — список цитат"""
    if local:
        quotes = list_quotes(author=author, source_type=source_type, source=source, limit=limit)
    else:
        quotes = zen_list(limit=limit)
        if author:
            quotes = [q for q in quotes if author.lower() in q["author"].lower()]
    fmt_table(quotes)


@app.command("get")
def cmd_get(
    quote_id: str = typer.Argument(..., help="ID цитаты"),
):
    """GET /quotes/{id} — цитата по ID"""
    q = get_quote(quote_id)
    if not q:
        console.print(f"[red]Цитата '{quote_id}' не найдена[/red]")
        raise typer.Exit(1)
    fmt_panel(q)


@app.command("random")
def cmd_random(
        save: bool = typer.Option(False, "--save", "-s"),
):
    """GET /quotes/random — случайная цитата"""
    with console.status("[cyan]Получаю...[/cyan]"):
        q = get_random_quote()
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


@app.command("search")
def cmd_search(
    query: str = typer.Argument(..., help="Ключевое слово"),
    limit: int = typer.Option(20, "--limit", "-l"),
    local: bool = typer.Option(False, "--local"),
):
    """GET /quotes/search — поиск"""
    if local:
        results = search_quotes(query, limit=limit)
    else:
        with console.status(f"[cyan]Ищу '{query}'...[/cyan]"):
            results = search_all(query, limit=limit)
    fmt_table(results)


@app.command("add")
def cmd_add(
    content: str = typer.Argument(..., help="Текст цитаты"),
    author: str = typer.Option("Unknown", "--author", "-a"),
    source: str = typer.Option("", "--source", "-s"),
    source_type: str = typer.Option("person", "--type", "-t"),
    tags: str = typer.Option("", "--tags"),
):
    """POST /quotes — добавить вручную"""
    q = {
        "content": content, "author": author, "source": source,
        "source_type": source_type,
        "tags": [t.strip() for t in tags.split(",") if t.strip()],
        "api": "local",
    }
    saved = save_quote(q)
    console.print(f"[green]✅ Добавлено: {saved['id']}[/green]")
    fmt_panel(saved)


@app.command("delete")
def cmd_delete(
    quote_id: str = typer.Argument(..., help="ID цитаты"),
    yes: bool = typer.Option(False, "--yes", "-y"),
):
    """DELETE /quotes/{id} — удалить"""
    if not yes:
        typer.confirm(f"Удалить '{quote_id}'?", abort=True)
    ok = delete_quote(quote_id)
    if ok:
        console.print(f"[green]✅ Удалено: {quote_id}[/green]")
    else:
        console.print(f"[red]Не найдено: {quote_id}[/red]")
        raise typer.Exit(1)


@app.command("filter")
def cmd_filter(
        source_type: Optional[str] = typer.Option(None, "--type", "-t", help="person | movie | game"),
        author: Optional[str] = typer.Option(None, "--author", "-a"),
        source: Optional[str] = typer.Option(None, "--source", "-s"),
        sort_by: str = typer.Option("created_at", "--sort", help="created_at | author | source"),
        order: str = typer.Option("desc", "--order", help="asc | desc"),
        limit: int = typer.Option(20, "--limit", "-l"),
):
    """GET /quotes/filter — продвинутая фильтрация и сортировка"""
    quotes = list_quotes(author=author, source_type=source_type, source=source, limit=500)

    # Сортировка
    reverse = order == "desc"
    if sort_by == "author":
        quotes.sort(key=lambda q: q.get("author", "").lower(), reverse=reverse)
    elif sort_by == "source":
        quotes.sort(key=lambda q: q.get("source", "").lower(), reverse=reverse)
    else:
        quotes.sort(key=lambda q: q.get("created_at", ""), reverse=reverse)

    fmt_table(quotes[:limit])
