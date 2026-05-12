"""Экспорт и статистика"""
import typer
from pathlib import Path
from typing import Optional
from ..storage import list_quotes, get_stats
from ..formatters import fmt_export, fmt_stats, console

export_app = typer.Typer(no_args_is_help=True, help="Экспорт цитат")
stats_app = typer.Typer(no_args_is_help=True, help="Статистика")


@export_app.command("quotes")
def cmd_export(
    fmt: str = typer.Option("json", "--format", "-f", help="json | csv"),
    output: Optional[Path] = typer.Option(None, "--output", "-o"),
    source_type: Optional[str] = typer.Option(None, "--type", "-t"),
    limit: int = typer.Option(500, "--limit", "-l"),
):
    """GET /quotes/export"""
    quotes = list_quotes(source_type=source_type, limit=limit)
    if not quotes:
        console.print("[yellow]Нет цитат. Сохрани что-нибудь сначала.[/yellow]")
        raise typer.Exit(1)
    data = fmt_export(quotes, fmt)
    if output:
        output.write_text(data, encoding="utf-8")
        console.print(f"[green]✅ Экспортировано {len(quotes)} цитат → {output}[/green]")
    else:
        console.print(data)


@stats_app.command("show")
def cmd_stats():
    """GET /quotes/stats"""
    fmt_stats(get_stats())
