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
from src.core.debug import dbg
from src.core.artifacts import ensure_gen_dirs, sanitize_name, timestamp_slug, write_json_artifact, write_text_artifact
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
    dbg(master, "ORCH.PIPELINE", "ERROR", "ERR", f"{module}: {message}")


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


def _persist_pipeline_artifacts(master: dict) -> None:
    ensure_gen_dirs()

    ts = timestamp_slug()
    symbol = sanitize_name(master.get("symbol"), default="unknown")
    run_base = f"run_{ts}_{symbol}"

    run_json_path = write_json_artifact("pipeline-runs", f"{run_base}.json", master)

    html_report = ((master.get("llm_context") or {}).get("html_report") or "").strip()
    run_html_path = None
    report_html_path = None
    if html_report:
        run_html_path = write_text_artifact("pipeline-runs", f"{run_base}.html", html_report)
        report_html_path = write_text_artifact("reports", f"daily_report_{ts}_{symbol}.html", html_report)

    debug_json_path = None
    debug_log_path = None
    debug_entries = master.get("debug") or []
    debug_enabled = bool(master.get("ui", {}).get("debug", False))
    if debug_enabled and debug_entries:
        debug_base = f"debug_{ts}_{symbol}"
        debug_json_path = write_json_artifact("debug", f"{debug_base}.json", debug_entries)
        debug_lines = [
            f"{item.get('m')}|{item.get('a')}|{item.get('s')}|{item.get('msg')}|{item.get('t')}"
            for item in debug_entries
        ]
        debug_log_path = write_text_artifact("debug", f"{debug_base}.log", "\n".join(debug_lines))

    master.setdefault("artifacts", {})
    master["artifacts"].update(
        {
            "pipeline_run_json": str(run_json_path),
            "pipeline_run_html": str(run_html_path) if run_html_path else None,
            "report_html": str(report_html_path) if report_html_path else None,
            "debug_json": str(debug_json_path) if debug_json_path else None,
            "debug_log": str(debug_log_path) if debug_log_path else None,
        }
    )
    dbg(master, "ORCH.ARTIFACTS", "WRITE", "OK", f"Saved run artifacts to {run_json_path}")


def run_pipeline(symbol: str | None = None, ui_payload: dict | None = None) -> dict:
    ensure_gen_dirs()
    master = deepcopy(MASTER_CONTRACT_V1)
    master["orchestrator"] = deepcopy(ORCHESTRATOR_CONTRACT_V1)
    master["orchestrator"]["status"] = "running"

    ui_contract = deepcopy(UI_CONTRACT_V1)
    ui_contract.update(ui_payload or {})
    if symbol:
        ui_contract["symbol"] = symbol

    master["ui"] = ui_contract
    dbg(master, "ORCH.PIPELINE", "START", "OK", "Pipeline started")

    if not ui_contract.get("symbol"):
        _add_error(master, "orchestrator", "Symbol is required", severity="critical")
        master["orchestrator"]["status"] = "failed"
        _persist_pipeline_artifacts(master)
        dbg(master, "ORCH.PIPELINE", "END", "ERR", "Pipeline failed: missing symbol")
        return master

    master["symbol"] = ui_contract["symbol"]
    master["exchange"] = ui_contract.get("exchange")
    master["timeframe"] = ui_contract.get("timeframe") or "daily"

    try:
        dbg(master, "ORCH.PIPELINE", "RESOLVE_SYMBOL", "OK", "Resolving ticker")
        normalized = normalize_ticker(master["symbol"])
        ticker = normalized["nse"]

        dbg(master, "INGESTION.MARKET", "FETCH", "OK", "Starting market fetch")
        market_snapshot = fetch_indian_stock_data(master["symbol"], master=master)
        if not market_snapshot.get("success"):
            _add_error(master, "market_fetcher", "Failed to fetch market snapshot", market_snapshot)
            master["orchestrator"]["status"] = "failed"
            _persist_pipeline_artifacts(master)
            dbg(master, "ORCH.PIPELINE", "END", "ERR", "Pipeline failed: market snapshot unavailable")
            return master
        dbg(master, "INGESTION.MARKET", "FETCH", "OK", "Market snapshot fetched")

        candles_df = fetch_price_history(ticker, period="1y", interval="1d", master=master)
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
            dbg(master, "ANALYSIS.TECHNICAL", "BUILD", "OK", "Building technical contract")
            master["technical"] = _build_technical_contract(market_snapshot)
            _append_module(master, "technical")

        # Fundamental analysis
        if _analysis_enabled(ui_contract, "fundamental"):
            dbg(master, "ANALYSIS.FUNDAMENTAL", "BUILD", "OK", "Computing fundamental analysis")
            fundamentals = analyze_fundamentals(ticker, period="quarterly", persist=True, master=master)
            master["fundamental"] = _build_fundamental_contract(fundamentals)
            _append_module(master, "fundamental")

        # Sentiment analysis
        if _analysis_enabled(ui_contract, "sentiment"):
            dbg(master, "ANALYSIS.SENTIMENT", "BUILD", "OK", "Computing sentiment analysis")
            sentiment_contract = deepcopy(SENTIMENT_CONTRACT_V1)
            news_items = []
            try:
                news_items = fetch_news(ticker, count=10, master=master)
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
            sentiment_contract.update(compute_sentiment_scores(sentiment_contract.get("top_news"), master=master))
            master["sentiment"] = sentiment_contract
            _append_module(master, "sentiment")

        # Trend evolution
        if _analysis_enabled(ui_contract, "trend"):
            dbg(master, "ANALYSIS.TREND", "BUILD", "OK", "Computing trend evolution")
            trend_contract = deepcopy(TREND_CONTRACT_V1)
            trend_contract.update(compute_trend(master["market_data"].get("candles", []), master.get("technical", {}), master=master))
            master["trend"] = trend_contract
            _append_module(master, "trend")

        # Timeframe engine
        if _analysis_enabled(ui_contract, "timeframe") or _analysis_enabled(ui_contract, "ai"):
            dbg(master, "TIMEFRAME.ENGINE", "BUILD", "OK", "Building timeframe config")
            timeframe_contract = deepcopy(TIMEFRAME_CONTRACT_V1)
            timeframe_contract.update(
                build_timeframe_config(
                    timeframe=master["timeframe"],
                    analysis_types=ui_contract.get("analysis_types"),
                    risk_profile=ui_contract.get("risk_profile"),
                    master=master,
                )
            )
            master["weights"] = timeframe_contract
            _append_module(master, "timeframe")

        # AI reasoning
        if _analysis_enabled(ui_contract, "ai"):
            dbg(master, "AI.LLM", "START", "OK", "Starting AI reasoning")
            llm_input = {
                "symbol": master["symbol"],
                "timeframe": master["timeframe"],
                "technical": master.get("technical", {}),
                "fundamental": master.get("fundamental", {}),
                "sentiment": master.get("sentiment", {}),
                "trend": master.get("trend", {}),
                "weights": master.get("weights", {}),
                "ui": master["ui"],
                "master": master,
            }
            llm_contract = deepcopy(LLM_CONTRACT_V1)
            llm_contract.update(generate_ai_report(llm_input))
            master["ai_report"] = llm_contract
            _append_module(master, "ai")
            dbg(master, "AI.LLM", "END", "OK", "AI reasoning completed")

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
        save_analysis_snapshot(history, master=master)
        dbg(master, "DB.CRUD", "SAVE", "OK", "Saved analysis snapshot")

        master["data_quality"] = history["data_quality"]
        master["orchestrator"]["status"] = "complete"
        _persist_pipeline_artifacts(master)
        dbg(master, "ORCH.PIPELINE", "END", "OK", "Pipeline completed")
        return master

    except Exception as exc:
        _add_error(master, "orchestrator", "Unhandled pipeline failure", details=str(exc), severity="critical")
        master["orchestrator"]["status"] = "failed"
        _persist_pipeline_artifacts(master)
        dbg(master, "ORCH.PIPELINE", "END", "ERR", "Pipeline failed")
        return master
