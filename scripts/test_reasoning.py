import os
import sys
from unittest.mock import patch

ROOT = os.path.dirname(os.path.dirname(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from src.ai.reasoning_node import generate_combined_report
from src.ai.llm_reasoner import generate_llm_report


def test_reasoning():
    with patch("src.ai.reasoning_node.generate_daily_summary", return_value="Daily section"), patch(
        "src.ai.reasoning_node.generate_trend_analysis", return_value="Trend section"
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
    with patch("src.ai.llm_reasoner.fetch_indian_stock_data", return_value=market_data), patch(
        "src.ai.llm_reasoner._load_or_compute_fundamentals",
        return_value={
            "ticker": "AAPL",
            "period": "quarterly",
            "valuation": {"pe_ratio": 30.0},
            "growth": {"revenue_yoy": 8.5},
            "profitability": {"roe": 20.0},
            "risk": {"debt_to_equity": 0.9},
            "data_quality": {"coverage_pct": 80.0},
        },
    ), patch(
        "src.ai.llm_reasoner.main_reasoning",
        return_value=(
            "Summary:\nS1.\nS2.\n\n"
            "Indicators:\nS1.\nS2.\n\n"
            "Sentiment:\nS1.\nS2.\n\n"
            "Risks:\nS1.\nS2.\n\n"
            "Opportunities:\nS1.\nS2.\n\n"
            "Recommendation:\nS1.\nS2."
        ),
    ):
        llm_report = generate_llm_report("AAPL", mode="optimized")
        assert "AI Stock Report (Optimized)" in llm_report
        assert "Indicators:" in llm_report
        assert "SectionScore Total:" in llm_report
    print("Optimized LLM reasoning mode validated")


if __name__ == "__main__":
    test_reasoning()
    test_reasoning_optimized_llm_mode()
    print("test_reasoning.py: all tests passed")
