from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
from src.ingestion.market_fetcher import fetch_indian_stock_data
from src.database.crud import save_ai_report, get_trend_score_series
from src.analysis.trend.trend_evolution import analyze_trend_evolution
from src.ai.llm import generate_ai_report
from src.alerts.alert_rules import evaluate_alerts
from src.alerts.alert_engine import dispatch_alerts
from src.logger import get_logger
from src.alerts.n8n_email import send_report_to_n8n

logger = get_logger(__name__)

WATCHLIST = [
    "RELIANCE.NS",
    "TCS.NS",
    "INFY.NS",
    "HDFCBANK.NS",
]


def run_daily_ingestion():
    logger.info("Running daily ingestion...")

    for symbol in WATCHLIST:
        logger.info(f"Starting ingestion for {symbol}")
        data = fetch_indian_stock_data(symbol)
        if not data.get("success"):
            logger.error(f"Failed to fetch {symbol}: {data.get('error')}")
            continue

        trend_score = data.get("trend_score")
        if trend_score is None:
            from src.analysis.trend.trend_score import compute_trend_score
            trend_score = compute_trend_score({
                "delivery_volume_pct": data.get("delivery_volume_pct"),
                "delivery_trend_pct": data.get("delivery_trend_pct"),
                "current_price": data.get("current_price"),
                "vwap": data.get("vwap"),
                "volume_breakout": data.get("volume_breakout"),
                "supports": data.get("supports"),
                "resistances": data.get("resistances"),
                "pivot_points": data.get("pivot_points"),
                "df": data.get("df"),
            })

        try:
            ai_summary, ai_recommendations, sentiment = generate_ai_report(data, trend_score)

            save_ai_report(
                symbol=symbol,
                trend_score=trend_score,
                sentiment=sentiment,
                summary=ai_summary,
                recommendations=ai_recommendations,
            )

            history = get_trend_score_series(symbol, n=10)
            evolution = analyze_trend_evolution(history)
            if not isinstance(evolution, dict):
                logger.warning(
                    f"{symbol}: Trend evolution returned non-dict value: {evolution}"
                )
                evolution = {}

            alerts = evaluate_alerts(data, trend_score, evolution)
            dispatch_alerts(symbol, alerts)

            payload = {
                "symbol": symbol,
                "trend_score": trend_score,
                "trend_direction": evolution.get("short_term_direction"),
                "delivery_pct": data.get("delivery_volume_pct"),
                "vwap": data.get("vwap"),
                "breakout": data.get("volume_breakout"),
                "supports": data.get("supports"),
                "resistances": data.get("resistances"),
                "pivot_points": data.get("pivot_points"),
                "ai_summary": ai_summary,
                "ai_recommendations": ai_recommendations,
                "sentiment": sentiment,
                "alerts": alerts,
            }

            send_report_to_n8n(payload)

            trend_dir = evolution.get("short_term_direction", "unknown")
            logger.info(
                f"{symbol} ingestion complete - trend: {trend_dir}, "
                f"score: {trend_score:.2f}, sentiment: {sentiment}, alerts: {len(alerts)}"
            )
        except Exception as exc:
            logger.exception(f"Error processing {symbol}: {exc}")


def start_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(run_daily_ingestion, "cron", hour=18, minute=0)
    scheduler.start()
    print("Scheduler started.")
    return scheduler
