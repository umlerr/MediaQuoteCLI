"""Команды для экспорта цитат"""
import typer
import json
import csv
from pathlib import Path
from datetime import datetime
from rich.console import Console
from rich.table import Table
from database import Database

app = typer.Typer()
console = Console()
db = Database()


@app.command(name="to-json")
def to_json(filepath: str = typer.Argument(..., help="Путь для JSON")):
    """Экспорт избранного в JSON"""
    favorites = db.get_favorites()
    if not favorites:
        console.print("[yellow]Нет цитат для экспорта[/yellow]")
        raise typer.Exit(1)
    export_data = {
        "exported_at": datetime.now().isoformat(),
        "total_quotes": len(favorites),
        "quotes": favorites
    }
    path = Path(filepath).expanduser()
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(export_data, f, indent=2, ensure_ascii=False)
    db.save_export_record('json', str(path), len(favorites))
    console.print(f"[green]✓ Экспортировано {len(favorites)} цитат в {path}[/green]")


@app.command(name="to-csv")
def to_csv(filepath: str = typer.Argument(..., help="Путь для CSV")):
    """Экспорт избранного в CSV"""
    favorites = db.get_favorites()
    if not favorites:
        console.print("[yellow]Нет цитат для экспорта[/yellow]")
        raise typer.Exit(1)
    path = Path(filepath).expanduser()
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, 'w', newline='', encoding='utf-8') as f:
        fieldnames = ['id', 'quote', 'author', 'source', 'content_type', 'rating', 'created_at']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for quote in favorites:
            writer.writerow({k: quote.get(k, '') for k in fieldnames})
    db.save_export_record('csv', str(path), len(favorites))
    console.print(f"[green]✓ Экспортировано {len(favorites)} цитат в {path}[/green]")


@app.command(name="to-markdown")
def to_markdown(filepath: str = typer.Argument(..., help="Путь для Markdown")):
    """Экспорт избранного в Markdown"""
    favorites = db.get_favorites()
    if not favorites:
        console.print("[yellow]Нет цитат для экспорта[/yellow]")
        raise typer.Exit(1)
    path = Path(filepath).expanduser()
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write("# MediaQuote Export\n\n")
        f.write(f"**Exported at:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n---\n\n")
        for idx, quote in enumerate(favorites, 1):
            f.write(f"## {idx}. {quote['author']}\n\n> {quote['quote']}\n\n")
            f.write(f"**Source:** {quote['source']} ({quote['content_type']})\n\n---\n\n")
    db.save_export_record('markdown', str(path), len(favorites))
    console.print(f"[green]✓ Экспортировано {len(favorites)} цитат в {path}[/green]")


@app.command()
def history(limit: int = typer.Option(10, help="Количество записей")):
    """История экспортов"""
    exports = db.get_export_history(limit)
    if exports:
        table = Table(title="📄 История экспортов")
        table.add_column("Дата", style="cyan")
        table.add_column("Формат", style="green")
        table.add_column("Файл", style="white")
        table.add_column("Цитат", style="yellow")
        for exp in exports:
            table.add_row(exp['exported_at'][:19], exp['format'].upper(),
                          Path(exp['file_path']).name, str(exp['quotes_count']))
        console.print(table)
    else:
        console.print("[yellow]Нет истории экспортов[/yellow]")
