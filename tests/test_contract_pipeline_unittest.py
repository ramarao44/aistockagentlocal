import unittest
from unittest.mock import patch

import pandas as pd

from src.core.contracts.fundamental_contract import FUNDAMENTAL_CONTRACT_V1
from src.core.contracts.llm_contract import LLM_CONTRACT_V1
from src.core.contracts.sentiment_contract import SENTIMENT_CONTRACT_V1
from src.core.contracts.technical_contract import TECHNICAL_CONTRACT_V1
from src.core.contracts.timeframe_contract import TIMEFRAME_CONTRACT_V1
from src.core.contracts.trend_contract import TREND_CONTRACT_V1
from src.core.contracts.ui_contract import UI_CONTRACT_V1, UI_CONTRACT_V2
from src.core.orchestrator import run_pipeline
from src.ai.llm_reasoner import _build_user_context_block, _build_standardized_report_prompt


def assert_contract_shape(testcase: unittest.TestCase, template, payload, path="root"):
    if isinstance(template, dict):
        testcase.assertIsInstance(payload, dict, f"Expected dict at {path}")
        for key, value in template.items():
            testcase.assertIn(key, payload, f"Missing key {path}.{key}")
            assert_contract_shape(testcase, value, payload[key], f"{path}.{key}")
        return

    if isinstance(template, list):
        testcase.assertIsInstance(payload, list, f"Expected list at {path}")
        if template and isinstance(template[0], dict) and payload:
            assert_contract_shape(testcase, template[0], payload[0], f"{path}[0]")
        return


class ContractPipelineTests(unittest.TestCase):
    def setUp(self):
        idx = pd.date_range("2026-01-01", periods=5, freq="D")
        self.candles_df = pd.DataFrame(
            {
                "Open": [100, 101, 102, 103, 104],
                "High": [102, 103, 104, 105, 106],
                "Low": [99, 100, 101, 102, 103],
                "Close": [101, 102, 103, 104, 105],
                "Volume": [1000, 1100, 1200, 1300, 1400],
            },
            index=idx,
        )

        self.market_snapshot = {
            "success": True,
            "exchange": "NSE",
            "current_price": 105.0,
            "rsi": 57.2,
            "ma20": 102.0,
            "ma50": 100.0,
            "ma200": 95.0,
            "macd_line": 1.2,
            "macd_signal": 1.0,
            "macd_histogram": 0.2,
            "bollinger_upper": 110.0,
            "bollinger_lower": 96.0,
            "bollinger_middle": 103.0,
            "adx": 22.0,
            "vwap": 103.1,
            "supertrend": 102.5,
            "supertrend_direction": "UP",
            "volume_breakout": True,
        }

        self.fundamental_payload = {
            "period": "quarterly",
            "valuation": {"pe_ratio": 25.5, "pbv_ratio": 4.0, "ev_ebitda": 13.2},
            "growth": {"revenue_yoy": 9.5, "earnings_yoy": 12.0},
            "profitability": {"roe": 18.2, "roce": 20.5, "net_margin": 14.1},
            "risk": {"debt_to_equity": 0.4, "interest_coverage": 8.0},
            "statement_snapshot": {
                "income": {"revenue": 1000, "net_income": 145},
                "balance_sheet": {"total_assets": 2500, "total_liabilities": 900},
            },
        }

    def _base_ui(self, analysis_types, output_format="json"):
        ui = UI_CONTRACT_V1.copy()
        ui.update(
            {
                "symbol": "RELIANCE",
                "exchange": "NSE",
                "timeframe": "daily",
                "analysis_types": analysis_types,
                "risk_profile": "medium",
                "output_format": output_format,
            }
        )
        return ui

    def _common_patches(self):
        return (
            patch("src.core.orchestrator.normalize_ticker", return_value={"nse": "RELIANCE.NS", "bse": "RELIANCE.BO"}),
            patch("src.core.orchestrator.fetch_indian_stock_data", return_value=self.market_snapshot),
            patch("src.core.orchestrator.fetch_price_history", return_value=self.candles_df),
            patch("src.core.orchestrator.save_analysis_snapshot", return_value=None),
        )

    def test_technical_contract_output(self):
        p1, p2, p3, p4 = self._common_patches()
        with p1, p2, p3, p4:
            master = run_pipeline(ui_payload=self._base_ui(["technical"]))

        self.assertEqual(master["orchestrator"]["status"], "complete")
        assert_contract_shape(self, TECHNICAL_CONTRACT_V1, master["technical"], "technical")

    def test_fundamental_contract_output(self):
        p1, p2, p3, p4 = self._common_patches()
        with p1, p2, p3, p4, patch("src.core.orchestrator.analyze_fundamentals", return_value=self.fundamental_payload):
            master = run_pipeline(ui_payload=self._base_ui(["fundamental"]))

        self.assertEqual(master["orchestrator"]["status"], "complete")
        assert_contract_shape(self, FUNDAMENTAL_CONTRACT_V1, master["fundamental"], "fundamental")

    def test_sentiment_contract_output(self):
        p1, p2, p3, p4 = self._common_patches()
        fake_news = [
            {"title": "Company profit beat drives bullish sentiment", "publisher": "Yahoo"},
            {"title": "Broker upgrade after strong quarter", "publisher": "Yahoo"},
        ]
        with p1, p2, p3, p4, patch("src.core.orchestrator.fetch_news", return_value=fake_news):
            master = run_pipeline(ui_payload=self._base_ui(["sentiment"]))

        self.assertEqual(master["orchestrator"]["status"], "complete")
        assert_contract_shape(self, SENTIMENT_CONTRACT_V1, master["sentiment"], "sentiment")

    def test_trend_contract_output(self):
        p1, p2, p3, p4 = self._common_patches()
        with p1, p2, p3, p4:
            master = run_pipeline(ui_payload=self._base_ui(["trend"]))

        self.assertEqual(master["orchestrator"]["status"], "complete")
        assert_contract_shape(self, TREND_CONTRACT_V1, master["trend"], "trend")

    def test_timeframe_contract_output(self):
        p1, p2, p3, p4 = self._common_patches()
        tf_payload = {
            "selected": "daily",
            "indicator_set": ["rsi", "macd"],
            "fundamental_horizon": "quarterly",
            "model_weights": {"technical": 0.6, "fundamental": 0.3, "sentiment": 0.1},
        }
        with p1, p2, p3, p4, patch("src.core.orchestrator.build_timeframe_config", return_value=tf_payload):
            master = run_pipeline(ui_payload=self._base_ui(["timeframe"]))

        self.assertEqual(master["orchestrator"]["status"], "complete")
        assert_contract_shape(self, TIMEFRAME_CONTRACT_V1, master["weights"], "weights")

    def test_llm_contract_output(self):
        p1, p2, p3, p4 = self._common_patches()
        llm_payload = {
            "summary": "Bullish setup with improving momentum.",
            "sentiment": "bullish",
            "risks": ["Volatility spike"],
            "opportunities": ["Momentum continuation"],
            "recommendation": "Accumulate on dips.",
            "probability": 0.67,
            "data_quality": "good",
        }
        with p1, p2, p3, p4, patch("src.core.orchestrator.build_timeframe_config", return_value={
            "selected": "daily",
            "indicator_set": ["rsi", "macd"],
            "fundamental_horizon": "quarterly",
            "model_weights": {"technical": 0.6, "fundamental": 0.3, "sentiment": 0.1},
        }), patch("src.core.orchestrator.generate_ai_report", return_value=llm_payload):
            master = run_pipeline(ui_payload=self._base_ui(["ai"]))

        self.assertEqual(master["orchestrator"]["status"], "complete")
        assert_contract_shape(self, LLM_CONTRACT_V1, master["ai_report"], "ai_report")

    def test_ui_end_to_end_pipeline(self):
        p1, p2, p3, p4 = self._common_patches()
        fake_news = [{"title": "Strong growth outlook", "publisher": "Yahoo"}]
        llm_payload = {
            "summary": "Integrated pipeline output.",
            "sentiment": "neutral",
            "risks": ["Market volatility"],
            "opportunities": ["Fundamental support"],
            "recommendation": "Hold with selective accumulation.",
            "probability": 0.55,
            "data_quality": "good",
        }

        with p1, p2, p3, p4, \
            patch("src.core.orchestrator.analyze_fundamentals", return_value=self.fundamental_payload), \
            patch("src.core.orchestrator.fetch_news", return_value=fake_news), \
            patch("src.core.orchestrator.generate_ai_report", return_value=llm_payload), \
            patch("src.core.orchestrator.build_timeframe_config", return_value={
                "selected": "daily",
                "indicator_set": ["rsi", "macd", "ma50"],
                "fundamental_horizon": "quarterly",
                "model_weights": {"technical": 0.6, "fundamental": 0.3, "sentiment": 0.1},
            }), \
            patch("src.core.orchestrator.format_html_report", return_value="<h1>report</h1>"):
            master = run_pipeline(ui_payload=self._base_ui([], output_format="html"))

        self.assertEqual(master["orchestrator"]["status"], "complete")
        self.assertEqual(
            master["orchestrator"]["modules_triggered"],
            [
                "technical_analyzer",
                "fundamental_analyzer",
                "sentiment_analyzer",
                "trend_engine",
                "timeframe_engine",
                "llm_reasoner",
            ],
        )
        self.assertTrue(master["ai_report"].get("summary"))
        self.assertIn("html_report", master["llm_context"])

    # --- New tests for UI_CONTRACT_V2 user_context feature (CR-20260720-UI-001) ---

    def test_ui_contract_v2_has_user_context_field(self):
        """UI_CONTRACT_V2 must include user_context field and inherit V1 fields."""
        self.assertIn("user_context", UI_CONTRACT_V2)
        self.assertEqual(UI_CONTRACT_V2["version"], "2.0")
        # Backward compatibility: all V1 keys present in V2
        for key in UI_CONTRACT_V1:
            self.assertIn(key, UI_CONTRACT_V2, f"V2 missing V1 key: {key}")

    def test_user_context_propagation_to_master_contract(self):
        """user_context from ui_payload must propagate to master['ui']."""
        p1, p2, p3, p4 = self._common_patches()
        ui = self._base_ui(["technical"])
        ui["user_context"] = "Long-term investor focused on dividend stocks"

        with p1, p2, p3, p4:
            master = run_pipeline(ui_payload=ui)

        self.assertEqual(master["orchestrator"]["status"], "complete")
        self.assertEqual(master["ui"].get("user_context"), "Long-term investor focused on dividend stocks")

    def test_user_context_passed_to_llm_input(self):
        """user_context must flow into generate_ai_report via llm_input['ui']."""
        p1, p2, p3, p4 = self._common_patches()
        captured_llm_input = {}

        def capture_generate_ai_report(llm_input):
            captured_llm_input.update(llm_input)
            return {
                "summary": "Test summary",
                "sentiment": "neutral",
                "risks": ["Test risk"],
                "opportunities": ["Test opportunity"],
                "recommendation": "Test recommendation",
                "probability": 0.5,
                "data_quality": "good",
            }

        ui = self._base_ui(["ai"])
        ui["user_context"] = "Swing trader with 2-week horizon"

        with p1, p2, p3, p4, \
            patch("src.core.orchestrator.build_timeframe_config", return_value={
                "selected": "daily",
                "indicator_set": ["rsi", "macd"],
                "fundamental_horizon": "quarterly",
                "model_weights": {"technical": 0.6, "fundamental": 0.3, "sentiment": 0.1},
            }), \
            patch("src.core.orchestrator.generate_ai_report", side_effect=capture_generate_ai_report):
            master = run_pipeline(ui_payload=ui)

        self.assertEqual(master["orchestrator"]["status"], "complete")
        self.assertIn("ui", captured_llm_input)
        self.assertEqual(
            captured_llm_input["ui"].get("user_context"),
            "Swing trader with 2-week horizon"
        )

    def test_user_context_block_with_context(self):
        """_build_user_context_block must include user text when provided."""
        block = _build_user_context_block("Risk-averse investor")
        self.assertIn("### User Context", block)
        self.assertIn("Risk-averse investor", block)
        self.assertIn("personalize the analysis", block)

    def test_user_context_block_without_context(self):
        """_build_user_context_block must use neutral fallback when empty."""
        block = _build_user_context_block(None)
        self.assertIn("### User Context", block)
        self.assertIn("not provided", block)

        block_empty = _build_user_context_block("")
        self.assertIn("not provided", block_empty)

        block_whitespace = _build_user_context_block("   ")
        self.assertIn("not provided", block_whitespace)

    def test_standardized_prompt_includes_user_context(self):
        """_build_standardized_report_prompt must embed user_context block."""
        prompt = _build_standardized_report_prompt("SNAPSHOT", user_context="My custom context")
        self.assertIn("### User Context", prompt)
        self.assertIn("My custom context", prompt)

        prompt_none = _build_standardized_report_prompt("SNAPSHOT", user_context=None)
        self.assertIn("not provided", prompt_none)


if __name__ == "__main__":
    unittest.main()