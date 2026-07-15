import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from src.ingestion.market_fetcher import fetch_indian_stock_data

tickers = ["RELIANCE", "TCS", "INFY"]

for t in tickers:
    print(f"\n=== Testing Delivery Volume for {t} ===")
    data = fetch_indian_stock_data(t)
    print("Delivery %:", data["delivery_volume_pct"])
    print("Delivery Qty:", data["delivery_volume_qty"])
    print("Total Volume:", data["total_volume"])
