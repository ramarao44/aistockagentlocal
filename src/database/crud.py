from .engine import SessionLocal, engine
from .models import StockDaily, AIReport, AnalysisHistory


def save_daily_record(data: dict):
    db = SessionLocal()
    try:
        record = StockDaily(**data)
        db.add(record)
        db.commit()
        db.refresh(record)
        return record
    finally:
        db.close()


def save_ai_report(symbol: str, trend_score: float, sentiment: str,
                   summary: str, recommendations: str):
    db = SessionLocal()
    try:
        report = AIReport(
            symbol=symbol,
            trend_score=trend_score,
            sentiment=sentiment,
            summary=summary,
            recommendations=recommendations,
        )
        db.add(report)
        db.commit()
        db.refresh(report)
        return report
    finally:
        db.close()


def get_last_report(symbol: str):
    db = SessionLocal()
    try:
        return (
            db.query(AIReport)
            .filter(AIReport.symbol == symbol)
            .order_by(AIReport.snapshot_time.desc())
            .first()
        )
    finally:
        db.close()


def get_latest_reports(symbol: str, n: int = 10):
    db = SessionLocal()
    try:
        return (
            db.query(AIReport)
            .filter(AIReport.symbol == symbol)
            .order_by(AIReport.snapshot_time.desc())
            .limit(n)
            .all()
        )
    finally:
        db.close()


def get_trend_score_series(symbol: str, n: int = 30):
    db = SessionLocal()
    try:
        rows = (
            db.query(AIReport.trend_score, AIReport.snapshot_time)
            .filter(AIReport.symbol == symbol)
            .order_by(AIReport.snapshot_time.desc())
            .limit(n)
            .all()
        )
        return [{"trend_score": r[0], "timestamp": r[1]} for r in rows]
    finally:
        db.close()


def get_sentiment_history(symbol: str, n: int = 30):
    db = SessionLocal()
    try:
        rows = (
            db.query(AIReport.sentiment, AIReport.snapshot_time)
            .filter(AIReport.symbol == symbol)
            .order_by(AIReport.snapshot_time.desc())
            .limit(n)
            .all()
        )
        return [{"sentiment": r[0], "timestamp": r[1]} for r in rows]
    finally:
        db.close()


def save_analysis_snapshot(history: dict):
    db = SessionLocal()
    try:
        AnalysisHistory.__table__.create(bind=engine, checkfirst=True)
        row = AnalysisHistory(
            version=history.get("version", "1.0"),
            symbol=history.get("symbol"),
            date=history.get("date"),
            timeframe=history.get("timeframe"),
            ui_json=history.get("ui_json"),
            market_data_json=history.get("market_data_json"),
            company_profile_json=history.get("company_profile_json"),
            technical_json=history.get("technical_json"),
            fundamental_json=history.get("fundamental_json"),
            sentiment_json=history.get("sentiment_json"),
            trend_json=history.get("trend_json"),
            ai_json=history.get("ai_json"),
            data_quality=history.get("data_quality", "unknown"),
        )
        db.add(row)
        db.commit()
        db.refresh(row)
        return row
    finally:
        db.close()
