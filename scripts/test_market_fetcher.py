import os
import sys
from unittest.mock import patch

import pandas as pd

ROOT = os.path.dirname(os.path.dirname(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from src.ingestion.market_fetcher import fetch_indian_stock_data


def _build_price_df(rows: int = 260):
    index = pd.date_range("2025-01-01", periods=rows, freq="D")
    base = pd.Series(range(rows), index=index, dtype=float)
    close = 100.0 + base
    high = close + 2.0
    low = close - 2.0
    volume = pd.Series([1_000_000 + (i * 1000) for i in range(rows)], index=index, dtype=float)

    return pd.DataFrame(
        {
            "Open": close - 1.0,
            "High": high,
            "Low": low,
            "Close": close,
            "Volume": volume,
        },
        index=index,
    )


def _mock_yf_download(*args, **kwargs):
    interval = kwargs.get("interval")
    if interval == "5m":
        return _build_price_df(rows=78)
    return _build_price_df(rows=260)


def test_cache_hit_uses_cached_symbol_without_rewrite():
    cached = {"nse": "HCLTECH.NS", "bse": "HCLTECH.BO", "source": "web"}

    with patch("src.ingestion.market_fetcher.load_symbol_resolution_cache", return_value=cached), patch(
        "src.ingestion.market_fetcher.resolve_symbol_from_web", return_value=None
    ), patch("src.ingestion.market_fetcher.fetch_price_history", return_value=_build_price_df(rows=260)) as fetch_mock, patch(
        "src.ingestion.market_fetcher.save_symbol_resolution_cache"
    ) as save_cache_mock, patch("src.ingestion.market_fetcher.yf.download", side_effect=_mock_yf_download), patch(
        "src.ingestion.market_fetcher.fetch_moneycontrol_delivery",
        return_value={"success": True, "delivery_pct": 45.0, "delivery_qty": 450000, "total_volume": 1000000},
    ), patch("src.ingestion.market_fetcher.save_daily_record"):
        result = fetch_indian_stock_data("HCL Technologies")

        assert result["success"] is True
        assert result["ticker"] == "HCLTECH.NS"
        assert result["exchange"] == "NSE"
        assert fetch_mock.call_args_list[0].args[0] == "HCLTECH.NS"
        save_cache_mock.assert_not_called()


def test_web_resolution_is_used_and_persisted_when_direct_fails():
    web_tickers = {"nse": "HCLTECH.NS", "bse": "HCLTECH.BO"}
    query = "HCL Tech Company"

    def fetch_side_effect(ticker, period="1y", interval="1d", **kwargs):
        if ticker.startswith("HCL TECH COMPANY"):
            return None
        return _build_price_df(rows=260)

    with patch("src.ingestion.market_fetcher.load_symbol_resolution_cache", return_value=None), patch(
        "src.ingestion.market_fetcher.resolve_symbol_from_web", return_value=web_tickers
    ), patch("src.ingestion.market_fetcher.fetch_price_history", side_effect=fetch_side_effect), patch(
        "src.ingestion.market_fetcher.save_symbol_resolution_cache"
    ) as save_cache_mock, patch("src.ingestion.market_fetcher.yf.download", side_effect=_mock_yf_download), patch(
        "src.ingestion.market_fetcher.fetch_moneycontrol_delivery",
        return_value={"success": True, "delivery_pct": 40.0, "delivery_qty": 400000, "total_volume": 1000000},
    ), patch("src.ingestion.market_fetcher.save_daily_record"):
        result = fetch_indian_stock_data(query)

        assert result["success"] is True
        assert result["ticker"] == "HCLTECH.NS"
        save_cache_mock.assert_called_once_with(
            "HCL TECH COMPANY",
            "HCLTECH.NS",
            "HCLTECH.BO",
            source="web",
        )


def test_returns_error_when_all_resolution_paths_fail():
    with patch("src.ingestion.market_fetcher.load_symbol_resolution_cache", return_value=None), patch(
        "src.ingestion.market_fetcher.resolve_symbol_from_web", return_value=None
    ), patch("src.ingestion.market_fetcher.fetch_price_history", return_value=None):
        result = fetch_indian_stock_data("UNKNOWN COMPANY")

        assert result["success"] is False
        assert "Could not fetch data" in result["error"]


if __name__ == "__main__":
    test_cache_hit_uses_cached_symbol_without_rewrite()
    test_web_resolution_is_used_and_persisted_when_direct_fails()
    test_returns_error_when_all_resolution_paths_fail()
    print("test_market_fetcher.py: all tests passed")
