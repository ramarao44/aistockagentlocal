from datetime import datetime
from sqlalchemy import or_

from .engine import SessionLocal, engine
from .models import StockDaily, AIReport, AnalysisHistory, Stock
from src.core.debug import dbg


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


def save_analysis_snapshot(history: dict, master: dict | None = None):
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
        dbg(master, "DB.CRUD", "SAVE", "OK", "Saved analysis snapshot")
        return row
    except Exception as exc:
        dbg(master, "DB.CRUD", "SAVE", "ERR", str(exc))
        raise
    finally:
        db.close()


# ---------------------------------------------------------------------------
# Stock catalog CRUD (UI dropdown + auto-population on symbol resolution)
# ---------------------------------------------------------------------------

def get_stock(symbol: str) -> Stock | None:
    """Return the catalog row for a symbol, or None if not present."""
    if not symbol:
        return None
    db = SessionLocal()
    try:
        return (
            db.query(Stock)
            .filter(Stock.symbol == symbol.strip().upper())
            .one_or_none()
        )
    finally:
        db.close()


def get_stock_list(active_only: bool = True) -> list[Stock]:
    """Return all catalog rows, ordered by symbol. UI dropdown source."""
    db = SessionLocal()
    try:
        q = db.query(Stock)
        if active_only:
            q = q.filter(Stock.active == 1)
        return q.order_by(Stock.symbol.asc()).all()
    finally:
        db.close()


def search_stocks(query: str, limit: int = 50) -> list[Stock]:
    """Substring search on symbol and company_name (case-insensitive)."""
    if not query:
        return get_stock_list(active_only=True)[:limit]
    needle = f"%{query.strip().upper()}%"
    db = SessionLocal()
    try:
        rows = (
            db.query(Stock)
            .filter(Stock.active == 1)
            .filter(or_(Stock.symbol.ilike(needle), Stock.company_name.ilike(needle)))
            .order_by(Stock.symbol.asc())
            .limit(limit)
            .all()
        )
        return rows
    finally:
        db.close()


def upsert_stock(
    symbol: str,
    company_name: str | None = None,
    exchange: str = "NSE",
    sector: str | None = None,
    isin: str | None = None,
    source: str = "auto",
) -> Stock:
    """Insert a new stock row or update an existing one (matched by symbol).

    Called by `market_fetcher` after a successful Yahoo/Moneycontrol
    resolution. Idempotent: safe to call repeatedly with the same symbol.
    """
    if not symbol or not isinstance(symbol, str):
        raise ValueError("symbol is required")

    sym = symbol.strip().upper()
    ex = (exchange or "NSE").strip().upper() or "NSE"
    db = SessionLocal()
    try:
        existing = db.query(Stock).filter(Stock.symbol == sym).one_or_none()
        now = datetime.utcnow()
        if existing is None:
            row = Stock(
                symbol=sym,
                company_name=company_name,
                exchange=ex,
                sector=sector,
                isin=isin,
                active=1,
                source=source,
                first_seen_at=now,
                last_used_at=now,
            )
            db.add(row)
        else:
            # Backfill missing fields without overwriting curated values.
            # Use getattr/setattr to satisfy Pylance (Column[] is invariant).
            if company_name and not getattr(existing, "company_name", None):
                setattr(existing, "company_name", company_name)
            if isin and not getattr(existing, "isin", None):
                setattr(existing, "isin", isin)
            if sector and not getattr(existing, "sector", None):
                setattr(existing, "sector", sector)
            if source:
                setattr(existing, "source", source)
            setattr(existing, "last_used_at", now)
            row = existing
        db.commit()
        db.refresh(row)
        return row
    finally:
        db.close()


def deactivate_stock(symbol: str) -> bool:
    """Mark a stock as inactive (soft delete). Returns True if updated."""
    db = SessionLocal()
    try:
        row = (
            db.query(Stock)
            .filter(Stock.symbol == symbol.strip().upper())
            .one_or_none()
        )
        if row is None:
            return False
        setattr(row, "active", 0)
        db.commit()
        return True
    finally:
        db.close()


# ---------------------------------------------------------------------------
# Backtest / Evaluation CRUD (FIS-02)
# ---------------------------------------------------------------------------

from .models import BacktestRun, BacktestSnapshot, WeightConfig, SectorEvalResult  # noqa: E402


def save_backtest_run(run_data: dict) -> BacktestRun:
    """Insert a backtest run row and return it."""
    db = SessionLocal()
    try:
        row = BacktestRun(**run_data)
        db.add(row)
        db.commit()
        db.refresh(row)
        return row
    finally:
        db.close()


def get_backtest_run(run_id: str) -> BacktestRun | None:
    db = SessionLocal()
    try:
        return db.query(BacktestRun).filter(BacktestRun.run_id == run_id).one_or_none()
    finally:
        db.close()


def list_backtest_runs(limit: int = 20) -> list[BacktestRun]:
    db = SessionLocal()
    try:
        return (
            db.query(BacktestRun)
            .order_by(BacktestRun.ts.desc())
            .limit(limit)
            .all()
        )
    finally:
        db.close()


def save_snapshot(snap: dict) -> BacktestSnapshot:
    db = SessionLocal()
    try:
        row = BacktestSnapshot(**snap)
        db.add(row)
        db.commit()
        db.refresh(row)
        return row
    finally:
        db.close()


def get_snapshots_for_run(run_id: str) -> list[BacktestSnapshot]:
    db = SessionLocal()
    try:
        return (
            db.query(BacktestSnapshot)
            .filter(BacktestSnapshot.run_id == run_id)
            .all()
        )
    finally:
        db.close()


def save_weight_config(cfg: dict) -> WeightConfig:
    db = SessionLocal()
    try:
        row = WeightConfig(**cfg)
        db.add(row)
        db.commit()
        db.refresh(row)
        return row
    finally:
        db.close()


def get_best_weight_config() -> WeightConfig | None:
    db = SessionLocal()
    try:
        return (
            db.query(WeightConfig)
            .filter(WeightConfig.is_best == 1)
            .order_by(WeightConfig.ts.desc())
            .first()
        )
    finally:
        db.close()


def get_latest_weight_config() -> WeightConfig | None:
    db = SessionLocal()
    try:
        return (
            db.query(WeightConfig)
            .order_by(WeightConfig.ts.desc())
            .first()
        )
    finally:
        db.close()


def save_sector_results(sector_rows: list[dict]) -> None:
    db = SessionLocal()
    try:
        for d in sector_rows:
            db.add(SectorEvalResult(**d))
        db.commit()
    finally:
        db.close()


def get_sector_results_for_run(run_id: str) -> list[SectorEvalResult]:
    db = SessionLocal()
    try:
        return (
            db.query(SectorEvalResult)
            .filter(SectorEvalResult.run_id == run_id)
            .all()
        )
    finally:
        db.close()
