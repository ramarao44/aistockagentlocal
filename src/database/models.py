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
