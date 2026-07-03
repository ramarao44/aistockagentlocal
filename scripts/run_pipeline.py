from src.fetcher.market_fetcher import fetch_daily_data
from src.analyzer.technical_analyzer import compute_indicators
from src.db.database import save_market_data, save_indicators

import sys
import os

# Add project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def run_for_ticker(ticker: str):
    df = fetch_daily_data(ticker)
    df2 = compute_indicators(df)

    save_market_data(df, ticker)
    save_indicators(df2, ticker)

    print(f"Saved data and indicators for {ticker}")

if __name__ == "__main__":
    run_for_ticker("AAPL")
