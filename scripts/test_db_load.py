import sys
import os
import sqlite3
from pathlib import Path

# Add project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


from src.db.database import (
    load_market_data,
    load_indicators,
    load_latest_market_data,
    load_latest_indicators
)


def ensure_db_schema():
    root = Path(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    db_path = root / "data" / "agent.db"
    schema_path = root / "data" / "schema.sql"
    if not schema_path.exists():
        return
    with sqlite3.connect(db_path) as conn:
        conn.executescript(schema_path.read_text(encoding="utf-8"))
        conn.commit()


ensure_db_schema()

ticker = "AAPL"

print("Full Market Data:")
print(load_market_data(ticker).tail())

print("\nFull Indicators:")
print(load_indicators(ticker).tail())

print("\nLatest Market Row:")
print(load_latest_market_data(ticker))

print("\nLatest Indicator Row:")
print(load_latest_indicators(ticker))
