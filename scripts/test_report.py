from src.ingestion.market_fetcher import fetch_indian_stock_data, generate_stock_report

tickers = ["RELIANCE", "TCS", "INFY"]

for t in tickers:
    print(f"\n=== AI Stock Report for {t} ===")
    data = fetch_indian_stock_data(t)
    print(generate_stock_report(data))
