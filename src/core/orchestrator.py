"""Contract-driven pipeline orchestrator."""

from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone

from src.ai.llm_reasoner import generate_ai_report
from src.analysis.fundamental import analyze_fundamentals
from src.analysis.sentiment import compute_sentiment_scores
from src.analysis.trend.trend_evolution import compute_trend
from src.core.contracts.analysis_history_contract import ANALYSIS_HISTORY_CONTRACT_V1
from src.core.contracts.error_contract import ERROR_CONTRACT_V1
from src.core.contracts.fundamental_contract import FUNDAMENTAL_CONTRACT_V1
from src.core.contracts.llm_contract import LLM_CONTRACT_V1
from src.core.contracts.market_data_contract import MARKET_DATA_CONTRACT_V1
from src.core.contracts.master_contract import MASTER_CONTRACT_V1
from src.core.contracts.orchestrator_contract import ORCHESTRATOR_CONTRACT_V1
from src.core.contracts.sentiment_contract import SENTIMENT_CONTRACT_V1
from src.core.contracts.technical_contract import TECHNICAL_CONTRACT_V1
from src.core.contracts.timeframe_contract import TIMEFRAME_CONTRACT_V1
from src.core.contracts.trend_contract import TREND_CONTRACT_V1
from src.core.contracts.ui_contract import UI_CONTRACT_V1
from src.database.crud import save_analysis_snapshot
from email_sender import send_email_to
from html_formatter import format_html_report
from src.ingestion.market_fetcher import fetch_indian_stock_data, fetch_price_history, normalize_ticker
from src.ingestion.news_fetcher import fetch_news
from src.timeframe.timeframe_engine import build_timeframe_config


MODULE_MAP = {
    "technical": "technical_analyzer",
    "fundamental": "fundamental_analyzer",
    "sentiment": "sentiment_analyzer",
    "trend": "trend_engine",
    "timeframe": "timeframe_engine",
    "ai": "llm_reasoner",
}


def _add_error(master: dict, module: str, message: str, details=None, severity: str = "medium") -> None:
    payload = deepcopy(ERROR_CONTRACT_V1)
    payload.update(
        {
            "module": module,
            "error_type": "pipeline_error",
            "message": message,
            "details": details,
            "severity": severity,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
    )
    master["errors"].append(payload)
    master["orchestrator"]["errors"].append(payload)


def _analysis_enabled(ui: dict, name: str) -> bool:
    selected = [x.strip().lower() for x in (ui.get("analysis_types") or []) if x]
    if not selected:
        return True
    return name in selected


def _to_candles(df) -> list[dict]:
    candles = []
    if df is None or getattr(df, "empty", True):
        return candles

    for idx, row in df.iterrows():
        date = idx.to_pydatetime().date().isoformat() if hasattr(idx, "to_pydatetime") else str(idx)
        candles.append(
            {
                "date": date,
                "open": float(row["Open"]) if row.get("Open") is not None else None,
                "high": float(row["High"]) if row.get("High") is not None else None,
                "low": float(row["Low"]) if row.get("Low") is not None else None,
                "close": float(row["Close"]) if row.get("Close") is not None else None,
                "volume": int(row["Volume"]) if row.get("Volume") is not None else None,
            }
        )
    return candles


def _build_technical_contract(market_snapshot: dict) -> dict:
    contract = deepcopy(TECHNICAL_CONTRACT_V1)
    contract.update(
        {
            "rsi": market_snapshot.get("rsi"),
            "ma": {
                "ma20": market_snapshot.get("ma20"),
                "ma50": market_snapshot.get("ma50"),
                "ma200": market_snapshot.get("ma200"),
            },
            "macd": {
                "macd": market_snapshot.get("macd_line"),
                "signal": market_snapshot.get("macd_signal"),
                "histogram": market_snapshot.get("macd_histogram"),
            },
            "bollinger": {
                "upper": market_snapshot.get("bollinger_upper"),
                "lower": market_snapshot.get("bollinger_lower"),
                "middle": market_snapshot.get("bollinger_middle"),
            },
            "adx": market_snapshot.get("adx"),
            "vwap": market_snapshot.get("vwap"),
            "supertrend": {
                "trend": market_snapshot.get("supertrend_direction"),
                "value": market_snapshot.get("supertrend"),
            },
            "data_quality": "good" if market_snapshot.get("current_price") is not None else "missing-market-data",
        }
    )

    signals = []
    if market_snapshot.get("volume_breakout"):
        signals.append("volume_breakout")
    if market_snapshot.get("current_price") is not None and market_snapshot.get("ma50") is not None:
        if market_snapshot["current_price"] >= market_snapshot["ma50"]:
            signals.append("price_above_ma50")
    contract["signals"] = signals
    return contract


def _build_fundamental_contract(fundamental_payload: dict) -> dict:
    contract = deepcopy(FUNDAMENTAL_CONTRACT_V1)
    valuation = fundamental_payload.get("valuation") or {}
    growth = fundamental_payload.get("growth") or {}
    profitability = fundamental_payload.get("profitability") or {}
    risk = fundamental_payload.get("risk") or {}
    snapshot = fundamental_payload.get("statement_snapshot") or {}

    contract.update(
        {
            "period": fundamental_payload.get("period", "quarterly"),
            "valuation": {
                "pe": valuation.get("pe") if valuation.get("pe") is not None else valuation.get("pe_ratio"),
                "pb": valuation.get("pb") if valuation.get("pb") is not None else valuation.get("pbv_ratio"),
                "ev_ebitda": valuation.get("ev_ebitda"),
            },
            "growth": {
                "revenue_cagr_3y": growth.get("revenue_cagr_3y") if growth.get("revenue_cagr_3y") is not None else growth.get("revenue_yoy"),
                "eps_growth_3y": growth.get("eps_growth_3y") if growth.get("eps_growth_3y") is not None else growth.get("earnings_yoy"),
            },
            "profitability": {
                "roe": profitability.get("roe"),
                "roce": profitability.get("roce"),
                "net_margin": profitability.get("net_margin"),
            },
            "risk": {
                "debt_to_equity": risk.get("debt_to_equity"),
                "interest_coverage": risk.get("interest_coverage"),
                "cashflow_stability": "stable" if (risk.get("interest_coverage") or 0) >= 2 else "fragile",
            },
            "financials": {
                "revenue": (snapshot.get("income") or {}).get("revenue"),
                "profit": (snapshot.get("income") or {}).get("net_income"),
                "assets": (snapshot.get("balance_sheet") or {}).get("total_assets"),
                "liabilities": (snapshot.get("balance_sheet") or {}).get("total_liabilities"),
            },
            "data_quality": "good" if fundamental_payload else "missing-fundamental",
        }
    )
    return contract


def _append_module(master: dict, module_key: str) -> None:
    master["orchestrator"]["modules_triggered"].append(MODULE_MAP[module_key])


def run_pipeline(symbol: str | None = None, ui_payload: dict | None = None) -> dict:
    master = deepcopy(MASTER_CONTRACT_V1)
    master["orchestrator"] = deepcopy(ORCHESTRATOR_CONTRACT_V1)
    master["orchestrator"]["status"] = "running"

    ui_contract = deepcopy(UI_CONTRACT_V1)
    ui_contract.update(ui_payload or {})
    if symbol:
        ui_contract["symbol"] = symbol

    if not ui_contract.get("symbol"):
        _add_error(master, "orchestrator", "Symbol is required", severity="critical")
        master["orchestrator"]["status"] = "failed"
        return master

    master["ui"] = ui_contract
    master["symbol"] = ui_contract["symbol"]
    master["exchange"] = ui_contract.get("exchange")
    master["timeframe"] = ui_contract.get("timeframe") or "daily"

    try:
        normalized = normalize_ticker(master["symbol"])
        ticker = normalized["nse"]

        market_snapshot = fetch_indian_stock_data(master["symbol"])
        if not market_snapshot.get("success"):
            _add_error(master, "market_fetcher", "Failed to fetch market snapshot", market_snapshot)
            master["orchestrator"]["status"] = "failed"
            return master

        candles_df = fetch_price_history(ticker, period="1y", interval="1d")
        market_contract = deepcopy(MARKET_DATA_CONTRACT_V1)
        market_contract.update(
            {
                "symbol": master["symbol"],
                "exchange": market_snapshot.get("exchange"),
                "timeframe": master["timeframe"],
                "candles": _to_candles(candles_df),
                "data_quality": "good" if candles_df is not None and not candles_df.empty else "limited",
            }
        )
        master["market_data"] = market_contract

        master["company_profile"] = {
            "symbol": master["symbol"],
            "exchange": market_snapshot.get("exchange"),
            "name": master["symbol"],
            "data_quality": "limited",
        }

        # Technical analysis
        if _analysis_enabled(ui_contract, "technical"):
            master["technical"] = _build_technical_contract(market_snapshot)
            _append_module(master, "technical")

        # Fundamental analysis
        if _analysis_enabled(ui_contract, "fundamental"):
            fundamentals = analyze_fundamentals(ticker, period="quarterly", persist=True)
            master["fundamental"] = _build_fundamental_contract(fundamentals)
            _append_module(master, "fundamental")

        # Sentiment analysis
        if _analysis_enabled(ui_contract, "sentiment"):
            sentiment_contract = deepcopy(SENTIMENT_CONTRACT_V1)
            news_items = []
            try:
                news_items = fetch_news(ticker, count=10)
            except Exception as ex:
                _add_error(master, "sentiment_analyzer", "News fetch failed", details=str(ex), severity="low")

            sentiment_contract["top_news"] = [
                {
                    "headline": item.get("title"),
                    "sentiment": None,
                    "source": item.get("publisher") or "Yahoo Finance",
                }
                for item in news_items
            ]
            sentiment_contract.update(compute_sentiment_scores(sentiment_contract.get("top_news")))
            master["sentiment"] = sentiment_contract
            _append_module(master, "sentiment")

        # Trend evolution
        if _analysis_enabled(ui_contract, "trend"):
            trend_contract = deepcopy(TREND_CONTRACT_V1)
            trend_contract.update(compute_trend(master["market_data"].get("candles", []), master.get("technical", {})))
            master["trend"] = trend_contract
            _append_module(master, "trend")

        # Timeframe engine
        if _analysis_enabled(ui_contract, "timeframe") or _analysis_enabled(ui_contract, "ai"):
            timeframe_contract = deepcopy(TIMEFRAME_CONTRACT_V1)
            timeframe_contract.update(
                build_timeframe_config(
                    timeframe=master["timeframe"],
                    analysis_types=ui_contract.get("analysis_types"),
                    risk_profile=ui_contract.get("risk_profile"),
                )
            )
            master["weights"] = timeframe_contract
            _append_module(master, "timeframe")

        # AI reasoning
        if _analysis_enabled(ui_contract, "ai"):
            llm_input = {
                "symbol": master["symbol"],
                "timeframe": master["timeframe"],
                "technical": master.get("technical", {}),
                "fundamental": master.get("fundamental", {}),
                "sentiment": master.get("sentiment", {}),
                "trend": master.get("trend", {}),
                "weights": master.get("weights", {}),
                "ui": master["ui"],
            }
            llm_contract = deepcopy(LLM_CONTRACT_V1)
            llm_contract.update(generate_ai_report(llm_input))
            master["ai_report"] = llm_contract
            _append_module(master, "ai")

        output_format = (ui_contract.get("output_format") or "json").strip().lower()
        if output_format in {"html", "email"}:
            html = format_html_report(master)
            master["llm_context"] = {"html_report": html}
            if output_format == "email":
                send_email_to(
                    subject=f"AI Stock Report: {master['symbol']}",
                    body=html,
                    to=ui_contract.get("to") or [],
                )

        history = deepcopy(ANALYSIS_HISTORY_CONTRACT_V1)
        history.update(
            {
                "ui_json": master["ui"],
                "symbol": master["symbol"],
                "date": datetime.now(timezone.utc).isoformat(),
                "timeframe": master["timeframe"],
                "market_data_json": master.get("market_data", {}),
                "company_profile_json": master.get("company_profile", {}),
                "technical_json": master.get("technical", {}),
                "fundamental_json": master.get("fundamental", {}),
                "sentiment_json": master.get("sentiment", {}),
                "trend_json": master.get("trend", {}),
                "ai_json": master.get("ai_report", {}),
                "data_quality": "good" if not master["errors"] else "partial",
            }
        )
        save_analysis_snapshot(history)

        master["data_quality"] = history["data_quality"]
        master["orchestrator"]["status"] = "complete"
        return master

    except Exception as exc:
        _add_error(master, "orchestrator", "Unhandled pipeline failure", details=str(exc), severity="critical")
        master["orchestrator"]["status"] = "failed"
        return master
