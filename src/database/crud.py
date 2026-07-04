from .engine import SessionLocal
from .models import StockDaily, AIReport


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
