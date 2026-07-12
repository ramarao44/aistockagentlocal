"""Profitability metric calculators."""

from __future__ import annotations


def _safe_div(numerator, denominator):
    try:
        if numerator is None or denominator in (None, 0):
            return None
        value = float(numerator) / float(denominator)
        if value != value:
            return None
        return value
    except Exception:
        return None


def _to_pct(value):
    if value is None:
        return None
    return value * 100.0


def calculate_profitability_metrics(income_items: dict, balance_items: dict) -> dict:
    net_income = income_items.get("net_income")
    revenue = income_items.get("revenue")
    operating_income = income_items.get("operating_income")
    gross_profit = income_items.get("gross_profit")
    ebit = income_items.get("ebit")

    total_assets = balance_items.get("total_assets")
    total_equity = balance_items.get("total_equity")
    total_debt = balance_items.get("total_debt")

    capital_employed = None
    if total_assets is not None and balance_items.get("current_liabilities") is not None:
        capital_employed = total_assets - balance_items.get("current_liabilities")
    elif total_equity is not None and total_debt is not None:
        capital_employed = total_equity + total_debt

    return {
        "roa": _to_pct(_safe_div(net_income, total_assets)),
        "roe": _to_pct(_safe_div(net_income, total_equity)),
        "roce": _to_pct(_safe_div(ebit, capital_employed)),
        "gross_margin": _to_pct(_safe_div(gross_profit, revenue)),
        "operating_margin": _to_pct(_safe_div(operating_income, revenue)),
        "net_margin": _to_pct(_safe_div(net_income, revenue)),
    }
