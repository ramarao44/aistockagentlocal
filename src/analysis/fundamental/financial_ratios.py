"""Combined ratio normalization for downstream consumers."""

from __future__ import annotations


def _clean(value):
    if value is None:
        return None
    try:
        value = float(value)
        if value != value:
            return None
        return value
    except Exception:
        return None


def combine_financial_ratios(valuation: dict, growth: dict, profitability: dict, risk: dict) -> dict:
    return {
        "valuation_score_inputs": {
            "pe_ratio": _clean(valuation.get("pe_ratio")),
            "pbv_ratio": _clean(valuation.get("pbv_ratio")),
            "ev_ebitda": _clean(valuation.get("ev_ebitda")),
            "peg_ratio": _clean(valuation.get("peg_ratio")),
        },
        "growth_score_inputs": {
            "revenue_yoy": _clean(growth.get("revenue_yoy")),
            "earnings_yoy": _clean(growth.get("earnings_yoy")),
            "eps_yoy": _clean(growth.get("eps_yoy")),
        },
        "quality_score_inputs": {
            "roe": _clean(profitability.get("roe")),
            "roce": _clean(profitability.get("roce")),
            "net_margin": _clean(profitability.get("net_margin")),
        },
        "risk_score_inputs": {
            "debt_to_equity": _clean(risk.get("debt_to_equity")),
            "current_ratio": _clean(risk.get("current_ratio")),
            "interest_coverage": _clean(risk.get("interest_coverage")),
            "beta": _clean(risk.get("beta")),
        },
    }
