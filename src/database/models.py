from sqlalchemy import Column, Integer, Float, String, DateTime, JSON, Text
from datetime import datetime
from .engine import Base


class StockDaily(Base):
    __tablename__ = "stock_daily"

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String, index=True)

    open = Column(Float)
    high = Column(Float)
    low = Column(Float)
    close = Column(Float)
    volume = Column(Integer)

    delivery_pct = Column(Float)
    delivery_qty = Column(Integer)
    total_volume = Column(Integer)
    vwap = Column(Float)
    volume_breakout = Column(Integer)

    supports = Column(JSON)
    resistances = Column(JSON)
    pivot_points = Column(JSON)

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
