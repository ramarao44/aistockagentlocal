from sqlalchemy import Column, Integer, Float, String, DateTime, JSON
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
