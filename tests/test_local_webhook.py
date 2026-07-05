from html_formatter import generate_html_report


def test_generate_html_report_contains_key_fields():
    payload = {
        "symbol": "HDFCBANK.NS",
        "trend_score": 16,
        "trend_direction": "stable",
        "delivery_pct": 32.5,
        "vwap": 1532.45,
        "breakout": "none",
        "supports": [1500, 1480],
        "resistances": [1550, 1580],
        "pivot_points": [1520, 1530],
        "ai_summary": "Stable movement with bearish sentiment.",
        "ai_recommendations": "Hold until sentiment improves.",
        "sentiment": "bearish",
        "alerts": ["Volume spike detected", "Sentiment bearish"],
    }

    html = generate_html_report(payload)

    assert "AIStockAgent Daily Report" in html
    assert "HDFCBANK.NS" in html
    assert "stable" in html
    assert "Volume spike detected" in html
