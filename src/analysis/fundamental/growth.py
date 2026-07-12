"""Growth metric calculators."""

from __future__ import annotations


def _growth_pct(current, previous):
    try:
        if current is None or previous in (None, 0):
            return None
        value = ((float(current) - float(previous)) / abs(float(previous))) * 100.0
        if value != value:
            return None
        return value
    except Exception:
        return None


def calculate_growth_metrics(current_income: dict, previous_income_q: dict, previous_income_y: dict) -> dict:
    revenue = current_income.get("revenue")
    net_income = current_income.get("net_income")
    eps_basic = current_income.get("eps_basic")

    return {
        "revenue_qoq": _growth_pct(revenue, previous_income_q.get("revenue")),
        "revenue_yoy": _growth_pct(revenue, previous_income_y.get("revenue")),
        "earnings_qoq": _growth_pct(net_income, previous_income_q.get("net_income")),
        "earnings_yoy": _growth_pct(net_income, previous_income_y.get("net_income")),
        "eps_qoq": _growth_pct(eps_basic, previous_income_q.get("eps_basic")),
        "eps_yoy": _growth_pct(eps_basic, previous_income_y.get("eps_basic")),
    }
