"""Valuation metric calculators."""

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


def calculate_valuation_metrics(price_snapshot: dict, income_items: dict, balance_items: dict, growth_metrics: dict) -> dict:
    market_cap = price_snapshot.get("market_cap")
    enterprise_value = price_snapshot.get("enterprise_value")
    trailing_pe = price_snapshot.get("trailing_pe")
    forward_pe = price_snapshot.get("forward_pe")
    dividend_yield = price_snapshot.get("dividend_yield")

    net_income = income_items.get("net_income")
    ebit = income_items.get("ebit")
    total_equity = balance_items.get("total_equity")

    pe_ratio = trailing_pe
    pbv_ratio = _safe_div(market_cap, total_equity)
    ev_ebitda = _safe_div(enterprise_value, ebit)

    earnings_yoy = growth_metrics.get("earnings_yoy")
    peg_ratio = _safe_div(pe_ratio, earnings_yoy) if earnings_yoy not in (None, 0) else None

    if dividend_yield is not None:
        dividend_yield = float(dividend_yield) * 100.0

    return {
        "pe_ratio": pe_ratio,
        "forward_pe": forward_pe,
        "pbv_ratio": pbv_ratio,
        "ev_ebitda": ev_ebitda,
        "peg_ratio": peg_ratio,
        "dividend_yield": dividend_yield,
        "price_to_earnings_from_income": _safe_div(market_cap, net_income),
    }
