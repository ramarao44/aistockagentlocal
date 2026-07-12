from src.ingestion.market_fetcher import fetch_indian_stock_data

tickers = ["RELIANCE.NS", "TCS.NS", "INFY.NS"]

for t in tickers:
    print(f"\n=== Testing VWAP for {t} ===")
    data = fetch_indian_stock_data(t)
    print("Current Price:", data.get("current_price"))
    print("VWAP:", data.get("vwap"))
