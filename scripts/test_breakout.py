from src.ingestion.market_fetcher import fetch_indian_stock_data

tickers = ["RELIANCE.NS", "TCS.NS", "INFY.NS"]

for t in tickers:
    print(f"\n=== Testing Volume Breakout for {t} ===")
    data = fetch_indian_stock_data(t)
    print("Today's Volume:", data.get("today_volume"))
    print("Breakout:", data.get("volume_breakout"))
