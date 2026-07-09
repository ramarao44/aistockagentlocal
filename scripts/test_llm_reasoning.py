import os
import sys
from unittest.mock import patch

ROOT = os.path.dirname(os.path.dirname(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from src.reasoning import llm_reasoner


MOCK_MARKET_DATA = {
    "success": True,
    "ticker": "RELIANCE.NS",
    "exchange": "NSE",
    "current_price": 2920.5,
    "rsi": 58.2,
    "ma50": 2860.1,
    "ma200": 2712.9,
    "bollinger_upper": 2998.4,
    "bollinger_lower": 2808.6,
    "last_updated": "2026-07-10",
}


def test_local_standard_mode():
    with patch("src.reasoning.llm_reasoner.fetch_indian_stock_data", return_value=MOCK_MARKET_DATA), patch(
        "src.reasoning.llm_reasoner.main_reasoning", return_value="Standard summary"
    ), patch("src.reasoning.llm_reasoner.fast_reasoning", return_value="Bullish"), patch(
        "src.reasoning.llm_reasoner.logic_reasoning", return_value="Trend logic"
    ):
        report = llm_reasoner.generate_llm_report("RELIANCE.NS", mode="local")
        assert "AI Stock Report (Standard)" in report
        assert "Standard summary" in report
        assert "Bullish" in report


def test_optimized_mode_uses_fast_path_for_summary():
    with patch("src.reasoning.llm_reasoner.fetch_indian_stock_data", return_value=MOCK_MARKET_DATA), patch(
        "src.reasoning.llm_reasoner.fast_reasoning", return_value="Compact output"
    ) as fast_mock, patch("src.reasoning.llm_reasoner.logic_reasoning", return_value="Compact logic"):
        report = llm_reasoner.generate_llm_report("RELIANCE.NS", mode="optimized")
        assert "AI Stock Report (Optimized)" in report
        assert "Compact output" in report
        assert fast_mock.call_count >= 2


def test_local_failure_falls_back_to_cloud():
    with patch("src.reasoning.llm_reasoner.fetch_indian_stock_data", return_value=MOCK_MARKET_DATA), patch(
        "src.reasoning.llm_reasoner.main_reasoning", return_value="[Local LLM Error] model unavailable"
    ), patch("src.reasoning.llm_reasoner.run_cloud_llm", return_value="Cloud fallback report") as cloud_mock:
        report = llm_reasoner.generate_llm_report("RELIANCE.NS", mode="local")
        assert "Cloud fallback report" in report
        assert cloud_mock.called


def test_cloud_mode_missing_key_error():
    with patch("src.reasoning.llm_reasoner.fetch_indian_stock_data", return_value=MOCK_MARKET_DATA), patch.dict(
        "os.environ", {"OPENAI_API_KEY": ""}
    ):
        report = llm_reasoner.generate_llm_report("RELIANCE.NS", mode="cloud")
        assert "Missing OPENAI_API_KEY" in report


if __name__ == "__main__":
    test_local_standard_mode()
    test_optimized_mode_uses_fast_path_for_summary()
    test_local_failure_falls_back_to_cloud()
    test_cloud_mode_missing_key_error()
    print("test_llm_reasoning.py: all tests passed")
