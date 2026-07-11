"""Balance sheet extraction helpers."""

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


def extract_balance_sheet_items(balance_sheet_df) -> dict:
    return {
        "total_assets": _extract_line_item(balance_sheet_df, ["Total Assets"]),
        "current_assets": _extract_line_item(balance_sheet_df, ["Current Assets", "Total Current Assets"]),
        "total_liabilities": _extract_line_item(balance_sheet_df, ["Total Liabilities Net Minority Interest", "Total Liab", "Total Liabilities"]),
        "current_liabilities": _extract_line_item(balance_sheet_df, ["Current Liabilities", "Total Current Liabilities"]),
        "cash_and_equivalents": _extract_line_item(balance_sheet_df, ["Cash And Cash Equivalents", "Cash Cash Equivalents And Short Term Investments", "Cash"]),
        "inventory": _extract_line_item(balance_sheet_df, ["Inventory", "Net Inventory"]),
        "total_equity": _extract_line_item(balance_sheet_df, ["Stockholders Equity", "Total Stockholder Equity", "Common Stock Equity"]),
        "total_debt": _extract_line_item(balance_sheet_df, ["Total Debt", "Long Term Debt", "Long Term Debt And Capital Lease Obligation"]),
    }
