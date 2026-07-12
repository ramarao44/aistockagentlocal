"""Risk and solvency metric calculators."""

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


def calculate_risk_metrics(price_snapshot: dict, income_items: dict, balance_items: dict) -> dict:
    total_debt = balance_items.get("total_debt")
    total_equity = balance_items.get("total_equity")
    current_assets = balance_items.get("current_assets")
    current_liabilities = balance_items.get("current_liabilities")
    cash_and_equivalents = balance_items.get("cash_and_equivalents")
    inventory = balance_items.get("inventory")
    ebit = income_items.get("ebit")
    interest_expense = income_items.get("interest_expense")

    quick_assets = None
    if current_assets is not None:
        quick_assets = current_assets - (inventory or 0)

    return {
        "debt_to_equity": _safe_div(total_debt, total_equity),
        "current_ratio": _safe_div(current_assets, current_liabilities),
        "quick_ratio": _safe_div(quick_assets, current_liabilities),
        "cash_ratio": _safe_div(cash_and_equivalents, current_liabilities),
        "interest_coverage": _safe_div(ebit, abs(interest_expense) if interest_expense not in (None, 0) else None),
        "beta": price_snapshot.get("beta"),
    }
