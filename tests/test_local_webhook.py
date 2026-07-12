import unittest

from html_formatter import generate_html_report


class LocalWebhookFormattingTests(unittest.TestCase):
    def test_generate_html_report_contains_key_fields(self):
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

        self.assertIn("AIStockAgent Daily Report", html)
        self.assertIn("HDFCBANK.NS", html)
        self.assertIn("stable", html)
        self.assertIn("Volume spike detected", html)


if __name__ == "__main__":
    unittest.main()
