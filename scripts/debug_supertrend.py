from src.ingestion.market_fetcher import fetch_price_history, compute_supertrend
import traceback

if __name__ == '__main__':
    ticker = 'RELIANCE.NS'
    print('Fetching history for', ticker)
    df = fetch_price_history(ticker)
    print('Type:', type(df))
    print('Length:', None if df is None else len(df))
    if df is None:
        print('No data')
    else:
        print('Index dtype:', df.index.dtype)
        print('Columns:', df.columns.tolist())
        try:
            res = compute_supertrend(df)
            print('compute_supertrend result:', res)
        except Exception:
            traceback.print_exc()
