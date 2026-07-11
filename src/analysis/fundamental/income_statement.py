"""Income statement extraction helpers."""

from __future__ import annotations

from typing import Iterable


def _to_number(value):
    if value is None:
        return None
    try:
        if hasattr(value, "item"):
            value = value.item()
        value = float(value)
        if value != value:
            return None
        return value
    except Exception:
        return None


def _extract_line_item(df, candidates: Iterable[str]):
    if df is None or getattr(df, "empty", True):
        return None

    for key in candidates:
        if key in df.index:
            row = df.loc[key]
            if getattr(row, "empty", False):
                continue
            if hasattr(row, "iloc"):
                return _to_number(row.iloc[0])
            return _to_number(row)
    return None


def extract_income_statement_items(income_df) -> dict:
    return {
        "revenue": _extract_line_item(income_df, ["Total Revenue", "Operating Revenue", "Revenue"]),
        "gross_profit": _extract_line_item(income_df, ["Gross Profit"]),
        "operating_income": _extract_line_item(income_df, ["Operating Income", "EBIT"]),
        "ebit": _extract_line_item(income_df, ["EBIT", "Operating Income"]),
        "pretax_income": _extract_line_item(income_df, ["Pretax Income", "Pre Tax Income"]),
        "net_income": _extract_line_item(income_df, ["Net Income", "Net Income Common Stockholders"]),
        "interest_expense": _extract_line_item(income_df, ["Interest Expense", "Net Interest Income"]),
        "eps_basic": _extract_line_item(income_df, ["Basic EPS", "Diluted EPS"]),
    }
