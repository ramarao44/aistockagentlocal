from src.fetcher.market_fetcher import fetch_indian_stock_data

tickers = ["RELIANCE", "TCS", "INFY"]

for t in tickers:
    print(f"\n=== Testing SuperTrend for {t} ===")
    data = fetch_indian_stock_data(t)
    if not data.get("success"):
        print("Error fetching data:", data.get("error"))
        continue

    print("SuperTrend:", data.get("supertrend"))
    print("Direction:", data.get("supertrend_direction"))
