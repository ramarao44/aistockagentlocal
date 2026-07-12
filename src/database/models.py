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
