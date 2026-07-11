import os
import sys
from unittest.mock import patch

import pandas as pd

ROOT = os.path.dirname(os.path.dirname(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from src.analysis.fundamental.fundamental_analyzer import analyze_fundamentals


def _build_income_df():
    cols = pd.to_datetime([
        "2026-03-31",
        "2025-12-31",
        "2025-09-30",
        "2025-06-30",
        "2025-03-31",
    ])
    return pd.DataFrame(
        {
            cols[0]: [1000.0, 220.0, 190.0, 45.0, 12.5],
            cols[1]: [940.0, 210.0, 180.0, 40.0, 11.0],
            cols[2]: [920.0, 205.0, 170.0, 38.0, 10.5],
            cols[3]: [900.0, 198.0, 165.0, 37.0, 10.1],
            cols[4]: [860.0, 180.0, 155.0, 33.0, 9.2],
        },
        index=["Total Revenue", "Net Income", "EBIT", "Operating Income", "Basic EPS"],
    )


def _build_balance_df():
    cols = pd.to_datetime(["2026-03-31", "2025-12-31"])
    return pd.DataFrame(
        {
            cols[0]: [2500.0, 900.0, 1300.0, 500.0, 200.0, 150.0, 1200.0, 300.0],
            cols[1]: [2450.0, 880.0, 1260.0, 490.0, 180.0, 145.0, 1190.0, 290.0],
        },
        index=[
            "Total Assets",
            "Current Assets",
            "Total Liabilities Net Minority Interest",
            "Current Liabilities",
            "Cash And Cash Equivalents",
            "Inventory",
            "Stockholders Equity",
            "Total Debt",
        ],
    )


def _build_cashflow_df():
    cols = pd.to_datetime(["2026-03-31", "2025-12-31"])
    return pd.DataFrame(
        {
            cols[0]: [310.0, -120.0, -60.0, 190.0, -80.0],
            cols[1]: [300.0, -110.0, -58.0, 185.0, -78.0],
        },
        index=[
            "Operating Cash Flow",
            "Investing Cash Flow",
            "Financing Cash Flow",
            "Free Cash Flow",
            "Capital Expenditure",
        ],
    )


class MockTicker:
    def __init__(self, symbol):
        self.symbol = symbol
        self.quarterly_financials = _build_income_df()
        self.quarterly_balance_sheet = _build_balance_df()
        self.quarterly_cashflow = _build_cashflow_df()
        self.financials = _build_income_df()
        self.balance_sheet = _build_balance_df()
        self.cashflow = _build_cashflow_df()
        self.info = {
            "marketCap": 350000.0,
            "enterpriseValue": 410000.0,
            "trailingPE": 25.0,
            "forwardPE": 22.0,
            "beta": 1.1,
            "dividendYield": 0.012,
        }


def test_fundamental_payload_shape_and_defaults():
    with patch("src.analysis.fundamental.fundamental_analyzer.yf.Ticker", side_effect=MockTicker), patch(
        "src.analysis.fundamental.fundamental_analyzer.save_fundamental_data"
    ) as save_mock:
        payload = analyze_fundamentals("TCS.NS", persist=True)

    assert payload["ticker"] == "TCS.NS"
    assert payload["period"] == "quarterly"
    assert "valuation" in payload
    assert "growth" in payload
    assert "profitability" in payload
    assert "risk" in payload
    assert "financial_ratios" in payload
    assert "data_quality" in payload
    assert payload["data_quality"]["coverage_pct"] >= 0
    assert save_mock.called


def test_fundamental_period_fallback_and_null_safety():
    class SparseTicker(MockTicker):
        def __init__(self, symbol):
            super().__init__(symbol)
            self.quarterly_financials = pd.DataFrame()
            self.quarterly_balance_sheet = pd.DataFrame()
            self.quarterly_cashflow = pd.DataFrame()
            self.info = {}

    with patch("src.analysis.fundamental.fundamental_analyzer.yf.Ticker", side_effect=SparseTicker), patch(
        "src.analysis.fundamental.fundamental_analyzer.save_fundamental_data"
    ):
        payload = analyze_fundamentals("HCLTECH.NS", period="invalid-period", persist=True)

    assert payload["period"] == "quarterly"
    assert payload["valuation"]["pe_ratio"] is None
    assert payload["risk"]["beta"] is None
    assert payload["data_quality"]["coverage_pct"] >= 0


def run_optional_live_ticker_check():
    if os.getenv("RUN_LIVE_FUNDAMENTAL_TEST", "0") != "1":
        print("Skipping live ticker check. Set RUN_LIVE_FUNDAMENTAL_TEST=1 to enable.")
        return

    # Primary agreed ticker for end-to-end live verification.
    payload = analyze_fundamentals("TCS.NS", period="quarterly", persist=True)
    assert payload["ticker"] == "TCS.NS"
    assert "valuation" in payload
    print("Live ticker check passed for TCS.NS")


if __name__ == "__main__":
    test_fundamental_payload_shape_and_defaults()
    test_fundamental_period_fallback_and_null_safety()
    run_optional_live_ticker_check()
    print("test_fundamental.py: all tests passed")
