"""Fundamental analysis orchestrator."""

from __future__ import annotations

from datetime import datetime

import yfinance as yf

from src.database.sqlite_legacy import save_fundamental_data

from .balance_sheet import extract_balance_sheet_items
from .cashflow_statement import extract_cashflow_items
from .financial_ratios import combine_financial_ratios
from .growth import calculate_growth_metrics
from .income_statement import extract_income_statement_items
from .profitability import calculate_profitability_metrics
from .risk import calculate_risk_metrics
from .valuation import calculate_valuation_metrics


def _extract_at(df, idx):
    if df is None or getattr(df, "empty", True):
        return {}
    if idx >= len(df.columns):
        return {}
    return df.iloc[:, idx]


def _extract_income_at(df, idx):
    series_df = _extract_at(df, idx)
    if not hasattr(series_df, "to_frame"):
        return extract_income_statement_items(None)
    return extract_income_statement_items(series_df.to_frame())


def _build_data_quality(sections: dict) -> dict:
    missing = []
    available = []
    for section_name, payload in sections.items():
        for key, value in payload.items():
            qualified = f"{section_name}.{key}"
            if value is None:
                missing.append(qualified)
            else:
                available.append(qualified)

    total = len(available) + len(missing)
    coverage = (len(available) / total) * 100.0 if total else 0.0
    return {
        "available_fields": available,
        "missing_fields": missing,
        "coverage_pct": round(coverage, 2),
    }


def analyze_fundamentals(ticker: str, period: str = "quarterly", persist: bool = True) -> dict:
    period_value = (period or "quarterly").strip().lower()
    if period_value not in {"quarterly", "annual"}:
        period_value = "quarterly"

    tk = yf.Ticker(ticker)

    if period_value == "annual":
        income_df = tk.financials
        balance_df = tk.balance_sheet
        cashflow_df = tk.cashflow
    else:
        income_df = tk.quarterly_financials
        balance_df = tk.quarterly_balance_sheet
        cashflow_df = tk.quarterly_cashflow

    current_income = _extract_income_at(income_df, 0)
    prev_income_q = _extract_income_at(income_df, 1)
    prev_income_y = _extract_income_at(income_df, 4 if period_value == "quarterly" else 1)

    current_balance_df = _extract_at(balance_df, 0)
    current_balance = extract_balance_sheet_items(current_balance_df.to_frame() if hasattr(current_balance_df, "to_frame") else None)

    current_cashflow_df = _extract_at(cashflow_df, 0)
    current_cashflow = extract_cashflow_items(current_cashflow_df.to_frame() if hasattr(current_cashflow_df, "to_frame") else None)

    price_snapshot = {
        "market_cap": tk.info.get("marketCap"),
        "enterprise_value": tk.info.get("enterpriseValue"),
        "trailing_pe": tk.info.get("trailingPE"),
        "forward_pe": tk.info.get("forwardPE"),
        "beta": tk.info.get("beta"),
        "dividend_yield": tk.info.get("dividendYield"),
    }

    growth = calculate_growth_metrics(current_income, prev_income_q, prev_income_y)
    valuation = calculate_valuation_metrics(price_snapshot, current_income, current_balance, growth)
    profitability = calculate_profitability_metrics(current_income, current_balance)
    risk = calculate_risk_metrics(price_snapshot, current_income, current_balance)
    financial_ratios = combine_financial_ratios(valuation, growth, profitability, risk)

    payload = {
        "ticker": ticker,
        "period": period_value,
        "valuation": valuation,
        "growth": growth,
        "profitability": profitability,
        "risk": risk,
        "financial_ratios": financial_ratios,
        "statement_snapshot": {
            "income": current_income,
            "balance_sheet": current_balance,
            "cashflow": current_cashflow,
        },
        "last_updated": datetime.utcnow().strftime("%Y-%m-%d"),
    }

    payload["data_quality"] = _build_data_quality(
        {
            "valuation": valuation,
            "growth": growth,
            "profitability": profitability,
            "risk": risk,
        }
    )

    if persist:
        try:
            save_fundamental_data(payload)
        except Exception:
            pass

    return payload
