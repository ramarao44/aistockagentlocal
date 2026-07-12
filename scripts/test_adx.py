from src.ingestion.market_fetcher import fetch_indian_stock_data

tickers = ["RELIANCE", "TCS", "INFY"]

for t in tickers:
    print(f"\n=== Testing ADX for {t} ===")
    data = fetch_indian_stock_data(t)
    print("ADX:", data["adx"])
    print("+DI:", data["plus_di"])
    print("-DI:", data["minus_di"])
