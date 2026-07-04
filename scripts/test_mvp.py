from src.fetcher.market_fetcher import analyze_stock

tickers = ["RELIANCE", "TCS", "INFY"]

for t in tickers:
    print(f"\n=== MVP Analysis for {t} ===")
    result = analyze_stock(t)
    if not result.get("success"):
        print("Error:", result.get("error"))
    else:
        print(result["report"]) 
