from sqlalchemy import Column, Integer, Float, String, DateTime, JSON, Text
from datetime import datetime
from .engine import Base


class StockDaily(Base):
    __tablename__ = "stock_daily"

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String, index=True)

    # OHLCV Data
    open = Column(Float)
    high = Column(Float)
    low = Column(Float)
    close = Column(Float)
    volume = Column(Integer)

    # Technical Indicators
    rsi = Column(Float)
    macd_line = Column(Float)
    macd_signal = Column(Float)
    macd_histogram = Column(Float)
    ma20 = Column(Float)
    ma50 = Column(Float)
    ma200 = Column(Float)
    adx = Column(Float)
    plus_di = Column(Float)
    minus_di = Column(Float)
    bollinger_upper = Column(Float)
    bollinger_lower = Column(Float)
    bollinger_middle = Column(Float)

    # Volume & Breakout Data
    delivery_pct = Column(Float)
    delivery_qty = Column(Integer)
    total_volume = Column(Integer)
    vwap = Column(Float)
    volume_breakout = Column(Integer)
    today_volume = Column(Integer)

    # Price Levels
    supports = Column(JSON)
    resistances = Column(JSON)
    pivot_points = Column(JSON)

    # Analysis Results
    trend_score = Column(Float)
    timestamp = Column(DateTime, default=datetime.utcnow)


class AIReport(Base):
    __tablename__ = "ai_report"

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String, index=True)

    trend_score = Column(Float)
    sentiment = Column(String)
    summary = Column(Text)
    recommendations = Column(Text)

    snapshot_time = Column(DateTime, default=datetime.utcnow)


class AnalysisHistory(Base):
    __tablename__ = "analysis_history"

    id = Column(Integer, primary_key=True, index=True)
    version = Column(String, default="1.0")
    symbol = Column(String, index=True)
    date = Column(String, index=True)
    timeframe = Column(String, index=True)

    ui_json = Column(JSON)
    market_data_json = Column(JSON)
    company_profile_json = Column(JSON)
    technical_json = Column(JSON)
    fundamental_json = Column(JSON)
    sentiment_json = Column(JSON)
    trend_json = Column(JSON)
    ai_json = Column(JSON)

    data_quality = Column(String, default="unknown")
    snapshot_time = Column(DateTime, default=datetime.utcnow)


class Stock(Base):
    """Stock catalog row, used by the UI dropdown.

    Populated initially by `scripts/seed_stock_catalog.py` (13 default
    stocks) and grown organically by `market_fetcher.upsert_stock()`
    whenever a new symbol is successfully resolved via Yahoo/Moneycontrol.
    """

    __tablename__ = "stocks"

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String, unique=True, index=True, nullable=False)
    company_name = Column(String)
    exchange = Column(String, default="NSE", nullable=False)
    sector = Column(String)
    isin = Column(String)
    active = Column(Integer, default=1, nullable=False)
    source = Column(String)
    first_seen_at = Column(DateTime, default=datetime.utcnow)
    last_used_at = Column(DateTime, default=datetime.utcnow)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "symbol": self.symbol,
            "company_name": self.company_name,
            "exchange": self.exchange,
            "sector": self.sector,
            "isin": self.isin,
            "active": bool(self.active),
            "source": self.source,
        }


# ---------------------------------------------------------------------------
# Backtest / Evaluation tables (FIS-02)
# ---------------------------------------------------------------------------


class BacktestRun(Base):
    __tablename__ = "backtest_runs"

    id = Column(Integer, primary_key=True, index=True)
    run_id = Column(String, unique=True, nullable=False)
    ts = Column(DateTime, default=datetime.utcnow)
    timeframe = Column(String, nullable=False)
    target = Column(String, nullable=False)
    lookback_years = Column(Integer, nullable=False)
    horizon_periods = Column(Integer, nullable=False)
    stock_basket_json = Column(Text, nullable=False)
    signals_json = Column(Text, default="[]")
    split_json = Column(Text)
    aggregate_rmse = Column(Float)
    aggregate_precision = Column(Float)
    aggregate_recall = Column(Float)
    aggregate_f1 = Column(Float)
    aggregate_accuracy = Column(Float)
    confidence_mean = Column(Float)
    probability_mean = Column(Float)
    params_json = Column(Text)
    notes = Column(Text)


class BacktestSnapshot(Base):
    __tablename__ = "backtest_snapshots"

    id = Column(Integer, primary_key=True, index=True)
    run_id = Column(String, nullable=False)
    symbol = Column(String, nullable=False)
    n_periods = Column(Integer, default=0)
    rmse = Column(Float)
    precision = Column(Float)
    recall = Column(Float)
    f1 = Column(Float)
    accuracy = Column(Float)
    confidence = Column(Float)
    probability = Column(Float, default=0.0)
    error = Column(Text)
    per_stock_json = Column(Text)


class WeightConfig(Base):
    __tablename__ = "weight_configs"

    id = Column(Integer, primary_key=True, index=True)
    run_id = Column(String, nullable=False)
    technical_weight = Column(Float, default=0.25)
    fundamental_weight = Column(Float, default=0.25)
    sentiment_weight = Column(Float, default=0.25)
    trend_weight = Column(Float, default=0.25)
    global_weight = Column(Float, default=0.0)
    rsi_weight = Column(Float, default=0.17)
    volume_breakout_weight = Column(Float, default=0.17)
    aggregate_accuracy = Column(Float)
    is_best = Column(Integer, default=0)
    tuned_from_run_id = Column(String)
    ts = Column(DateTime, default=datetime.utcnow)


class SectorEvalResult(Base):
    __tablename__ = "sector_eval_results"

    id = Column(Integer, primary_key=True, index=True)
    run_id = Column(String, nullable=False)
    sector = Column(String, nullable=False)
    stock_count = Column(Integer, default=0)
    avg_rmse = Column(Float)
    avg_precision = Column(Float)
    avg_recall = Column(Float)
    avg_accuracy = Column(Float)
    avg_confidence = Column(Float)
    ts = Column(DateTime, default=datetime.utcnow)
