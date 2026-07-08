from src.fetcher.market_fetcher import fetch_indian_stock_data

def test_ticker(ticker):
    print(f"\n=== Testing {ticker} ===")
    result = fetch_indian_stock_data(ticker)
    print(result)

if __name__ == "__main__":
    # Test NSE large-cap
    test_ticker("Reliance")

    # Test NSE IT stock
    test_ticker("TCS")

    # Test BSE fallback
    test_ticker("INFY")

    # Test invalid ticker
    test_ticker("INVALID123")
