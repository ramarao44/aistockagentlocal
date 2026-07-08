from src.fetcher.market_fetcher import fetch_indian_stock_data

tickers = ["RELIANCE", "TCS", "INFY"]

for t in tickers:
    print(f"\n=== Testing Trend Score for {t} ===")
    data = fetch_indian_stock_data(t)
    print("Trend Score:", data["trend_score"]) 
