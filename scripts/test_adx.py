from src.fetcher.market_fetcher import fetch_indian_stock_data

tickers = ["RELIANCE", "TCS", "INFY"]

for t in tickers:
    print(f"\n=== Testing ADX for {t} ===")
    data = fetch_indian_stock_data(t)
    if not data.get("success"):
        print("Error fetching data:", data.get("error"))
        continue

    print("ADX:", data.get("adx"))
    print("Plus DI:", data.get("plus_di"))
    print("Minus DI:", data.get("minus_di"))
