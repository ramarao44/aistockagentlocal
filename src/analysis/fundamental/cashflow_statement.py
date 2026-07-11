"""Cash flow extraction helpers."""

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


def extract_cashflow_items(cashflow_df) -> dict:
    return {
        "operating_cashflow": _extract_line_item(cashflow_df, ["Operating Cash Flow", "Cash Flow From Continuing Operating Activities"]),
        "investing_cashflow": _extract_line_item(cashflow_df, ["Investing Cash Flow", "Cash Flow From Continuing Investing Activities"]),
        "financing_cashflow": _extract_line_item(cashflow_df, ["Financing Cash Flow", "Cash Flow From Continuing Financing Activities"]),
        "free_cash_flow": _extract_line_item(cashflow_df, ["Free Cash Flow"]),
        "capital_expenditure": _extract_line_item(cashflow_df, ["Capital Expenditure"]),
    }
