"""Rich форматтеры"""
import json
import csv
from io import StringIO
from typing import List, Dict, Optional
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box

console = Console()

ICONS = {"person": "🧠", "movie": "🎬", "game": "🎮", "local": "💾"}
COLORS = {"zenquotes": "cyan", "local-api": "magenta", "local": "yellow"}


def _icon(t): return ICONS.get(t, "📝")
def _color(a): return COLORS.get(a, "white")


def fmt_panel(q: Dict, rating=None, is_fav=False):
    icon = _icon(q.get("source_type", ""))
    fav = " ⭐" if is_fav else ""
    source = q.get("source") or ""
    rating_str = f"\n⭐ Оценка: {rating}/5" if rating else ""
    tags = ", ".join(q.get("tags", []))
    tags_str = f"\n🏷  {tags}" if tags else ""
    color = _color(q.get("api", ""))

    console.print(Panel(
        f'[italic]"{q["content"]}"[/italic]\n\n'
        f'[bold]— {q.get("author","Unknown")}[/bold]'
        + (f'  [dim]({source})[/dim]' if source and source != q.get("author") else "")
        + tags_str + rating_str,
        title=f'{icon} [{color}]{q["id"]}[/{color}]{fav}',
        border_style=color,
        padding=(1, 2),
    ))


def fmt_table(quotes: List[Dict]):
    if not quotes:
        console.print("[yellow]Цитаты не найдены[/yellow]")
        return
    table = Table(box=box.ROUNDED, show_lines=True)
    table.add_column("ID", style="dim", max_width=12, no_wrap=True)
    table.add_column("Тип", justify="center", max_width=6)
    table.add_column("Цитата", max_width=50)
    table.add_column("Автор", style="green", max_width=15)
    table.add_column("Источник", style="yellow", max_width=20)
    for q in quotes:
        content = q.get("content", "")
        short = content[:70] + "…" if len(content) > 70 else content
        source = q.get("source", "") or ""
        if source == q.get("author"): source = ""
        qid = q.get("id", "")
        short_id = qid[:12] if len(qid) > 12 else qid
        stype = q.get("source_type", "")
        type_label = {"person": "person", "movie": "movie", "game": "game"}.get(stype, stype)
        table.add_row(short_id, type_label, short, q.get("author","Unknown"), source)
    console.print(table)
    console.print(f"[dim]Найдено: {len(quotes)}[/dim]")


def fmt_stats(stats: Dict):
    t = Table(title="📊 Статистика", box=box.SIMPLE_HEAVY)
    t.add_column("Показатель", style="cyan")
    t.add_column("Значение", style="bold green", justify="right")
    t.add_row("Всего цитат", str(stats.get("total", 0)))
    t.add_row("В избранном", str(stats.get("favorites", 0)))
    avg = stats.get("avg_rating")
    t.add_row("Средняя оценка", f"{avg}/5" if avg else "—")
    console.print(t)
    by_type = stats.get("by_type", {})
    if by_type:
        t2 = Table(title="По типу", box=box.SIMPLE)
        t2.add_column("Тип")
        t2.add_column("Кол-во", justify="right")
        for k, v in by_type.items():
            t2.add_row(f"{_icon(k)} {k}", str(v))
        console.print(t2)


def fmt_export(quotes: List[Dict], fmt: str) -> str:
    if fmt == "json":
        return json.dumps(quotes, ensure_ascii=False, indent=2)
    out = StringIO()
    if quotes:
        w = csv.DictWriter(out, fieldnames=["id","content","author","source","source_type","api"], extrasaction="ignore")
        w.writeheader()
        w.writerows(quotes)
    return out.getvalue()