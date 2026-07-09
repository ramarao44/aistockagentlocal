import os
import sys
from unittest.mock import patch

ROOT = os.path.dirname(os.path.dirname(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from src.reasoning.reasoning_node import generate_combined_report
from src.reasoning.llm_reasoner import generate_llm_report


def test_reasoning():
    with patch("src.reasoning.reasoning_node.generate_daily_summary", return_value="Daily section"), patch(
        "src.reasoning.reasoning_node.generate_trend_analysis", return_value="Trend section"
    ):
        report = generate_combined_report("AAPL")
    assert isinstance(report, str)
    assert "Daily section" in report
    assert "Trend section" in report
    print("Combined reasoning report generated")


def test_reasoning_optimized_llm_mode():
    market_data = {
        "success": True,
        "ticker": "AAPL",
        "exchange": "NASDAQ",
        "current_price": 210.0,
        "rsi": 55.0,
        "ma50": 205.0,
        "ma200": 190.0,
        "bollinger_upper": 220.0,
        "bollinger_lower": 200.0,
        "last_updated": "2026-07-10",
    }
    with patch("src.reasoning.llm_reasoner.fetch_indian_stock_data", return_value=market_data), patch(
        "src.reasoning.llm_reasoner.fast_reasoning", return_value="Optimized summary"
    ), patch("src.reasoning.llm_reasoner.logic_reasoning", return_value="Optimized logic"):
        llm_report = generate_llm_report("AAPL", mode="optimized")
        assert "AI Stock Report (Optimized)" in llm_report
        assert "Optimized summary" in llm_report
    print("Optimized LLM reasoning mode validated")


if __name__ == "__main__":
    test_reasoning()
    test_reasoning_optimized_llm_mode()
    print("test_reasoning.py: all tests passed")
