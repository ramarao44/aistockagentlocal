import os
import sys
from unittest.mock import patch

ROOT = os.path.dirname(os.path.dirname(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from src.database.engine import Base, engine
from src.database.crud import save_ai_report
from src.ai.llm_reasoner import generate_llm_report

Base.metadata.create_all(bind=engine)

report = save_ai_report(
    symbol="RELIANCE.NS",
    trend_score=78.5,
    sentiment="bullish",
    summary="Price is above VWAP with strong delivery volume and moderate breakout characteristics.",
    recommendations="Monitor for continuation above recent resistance; avoid leverage; reassess if delivery drops below 40%.",
)

print("Saved AI report ID:", report.id)


market_data = {
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

with patch("src.ai.llm_reasoner.fetch_indian_stock_data", return_value=market_data), patch(
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
    optimized_report = generate_llm_report("RELIANCE.NS", mode="optimized")
    assert "AI Stock Report (Optimized)" in optimized_report
    assert "Recommendation:" in optimized_report
    assert "SectionScore Total:" in optimized_report
    print("Optimized AI report generation validated")
