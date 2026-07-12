from src.ingestion.market_fetcher import fetch_indian_stock_data

tickers = ["RELIANCE.NS", "TCS.NS", "INFY.NS"]

for t in tickers:
    print(f"\n=== Testing Support/Resistance for {t} ===")
    data = fetch_indian_stock_data(t)
    print("Supports:", data.get("supports"))
    print("Resistances:", data.get("resistances"))
    print("Pivot Points:", data.get("pivot_points"))
