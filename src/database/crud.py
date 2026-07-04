from .engine import SessionLocal
from .models import StockDaily


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
