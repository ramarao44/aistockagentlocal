from src.ingestion.market_fetcher import fetch_indian_stock_data

tickers = ["RELIANCE", "TCS", "INFY"]

for t in tickers:
    print(f"\n=== Testing MACD for {t} ===")
    data = fetch_indian_stock_data(t)
    if not data.get("success"):
        print("Error fetching data:", data.get("error"))
        continue

    print("MACD Line:", data.get("macd_line"))
    print("Signal Line:", data.get("macd_signal"))
    print("Histogram:", data.get("macd_histogram"))
