import sys
import os

# Add project root to Python path
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from src.ingestion.market_fetcher import fetch_price_history, normalize_ticker
from src.analysis.technical.technical_analyzer import compute_indicators
from src.database.sqlite_legacy import save_market_data, save_indicators


def run_for_ticker(ticker: str):
    resolved = normalize_ticker(ticker)
    df = fetch_price_history(resolved["nse"], period="1y", interval="1d")
    if df is None or df.empty:
        print(f"No data fetched for {ticker}")
        return

    df2 = compute_indicators(df)

    save_market_data(df, ticker)
    save_indicators(df2, ticker)

    print(f"Saved data and indicators for {ticker}")

if __name__ == "__main__":
    run_for_ticker("RELIANCE")
