"""UI helpers for the stock catalog dropdown / picker."""
from __future__ import annotations

from src.database import crud


def get_stock_choices() -> list[dict]:
    """Return all active catalog rows as a list of choice dicts.

    Each item has shape: {"label": "RELIANCE — Reliance Industries Ltd",
    "value": "RELIANCE"}
    """
    rows = crud.get_stock_list(active_only=True)
    return [
        {
            "label": f"{r.symbol} \u2014 {r.company_name or 'Unknown'}",
            "value": r.symbol,
        }
        for r in rows
    ]


def get_stock_choice_values() -> list[str]:
    """Return just the symbols (for Cl Select widget values list)."""
    return [r.symbol for r in crud.get_stock_list(active_only=True)]


def search_stock_choices(query: str, limit: int = 50) -> list[dict]:
    """Return choices matching the query (case-insensitive substring)."""
    rows = crud.search_stocks(query=query, limit=limit)
    return [
        {
            "label": f"{r.symbol} \u2014 {r.company_name or 'Unknown'}",
            "value": r.symbol,
        }
        for r in rows
    ]


def catalog_summary_text() -> str:
    """Return a human-readable summary of the current catalog for the welcome message."""
    rows = crud.get_stock_list(active_only=True)
    if not rows:
        return (
            "Stock catalog is empty. Run `python scripts/seed_stock_catalog.py` "
            "to populate the 13 default NSE stocks. New stocks will be added "
            "automatically as you successfully resolve them."
        )
    lines = [f"**Available stocks ({len(rows)}):**"]
    for r in rows[:20]:
        sector = f" \u2014 {r.sector}" if r.sector else ""
        lines.append(f"- `{r.symbol}` ({r.company_name or 'Unknown'}){sector}")
    if len(rows) > 20:
        lines.append(f"- ... and {len(rows) - 20} more")
    return "\n".join(lines)