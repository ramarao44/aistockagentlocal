import yfinance as yf
import datetime
import pandas as pd

def fetch_daily_data(ticker: str):
    """
    Fetch daily OHLCV data for a given ticker.
    """

    try:
        today = datetime.date.today()
        df = yf.download(ticker, start=today - datetime.timedelta(days=30), end=today)

        if df.empty:
            raise ValueError("No data returned from yfinance.")

        # If MultiIndex columns, flatten them
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(1)

        # If columns are still wrong (AAPL, AAPL...), rename them manually
        expected_cols = ['Open', 'High', 'Low', 'Close', 'Volume']
        if list(df.columns) != expected_cols:
            df.columns = expected_cols

        return df

    except Exception as e:
        print(f"[Fetcher Error] {e}")
        return None
