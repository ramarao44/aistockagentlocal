import yfinance as yf
import pandas as pd

# ---------------------------------------------------------
# Ticker Normalization (NSE + BSE)
# ---------------------------------------------------------

def normalize_ticker(user_input: str):
    base = user_input.strip().upper()
    return {
        "nse": f"{base}.NS",
        "bse": f"{base}.BO"
    }


# ---------------------------------------------------------
# Fetch Price History
# ---------------------------------------------------------

def fetch_price_history(ticker: str, period="6mo", interval="1d"):
    try:
        df = yf.download(ticker, period=period, interval=interval, progress=False)
        if df is None or df.empty:
            return None
        return df.dropna()
    except Exception as e:
        print(f"[MarketFetcher] Error fetching data for {ticker}: {e}")
        return None


# ---------------------------------------------------------
# Technical Indicators
# ---------------------------------------------------------

def compute_rsi(df, period=14):
    delta = df["Close"].diff()

    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)

    avg_gain = gain.rolling(period).mean()
    avg_loss = loss.rolling(period).mean()

    # Prevent division by zero
    avg_loss = avg_loss.replace(0, 1e-10)

    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))

    return rsi.iloc[-1]



def compute_moving_average(df, window=50):
    if len(df) < window:
        return None
    return df["Close"].rolling(window).mean().iloc[-1]



def compute_bollinger_bands(df, window=20):
    ma = df["Close"].rolling(window).mean()
    std = df["Close"].rolling(window).std()
    upper = ma + (std * 2)
    lower = ma - (std * 2)
    return upper.iloc[-1], lower.iloc[-1]


# ---------------------------------------------------------
# Combined Market Data Fetcher (NSE + BSE)
# ---------------------------------------------------------

def fetch_indian_stock_data(user_input: str):
    tickers = normalize_ticker(user_input)

    # Try NSE first
    df = fetch_price_history(tickers["nse"])
    exchange = "NSE"

    # Fallback to BSE
    if df is None:
        df = fetch_price_history(tickers["bse"])
        exchange = "BSE"

    if df is None:
        return {
            "success": False,
            "error": f"Could not fetch data for {user_input}"
        }

    try:
        # Compute raw indicators
        rsi = compute_rsi(df)
        ma50 = compute_moving_average(df, 50)
        ma200 = compute_moving_average(df, 200)
        boll_upper, boll_lower = compute_bollinger_bands(df)
        current_price = df["Close"].iloc[-1]

        # ---------------------------------------------------------
        # Normalize values (convert Series → float safely)
        # ---------------------------------------------------------
        def safe_float(val):
            if isinstance(val, pd.Series):
                return float(val.iloc[-1])
            return float(val)

        current_price = safe_float(current_price)
        rsi = safe_float(rsi)
        ma50 = safe_float(ma50)
        ma200 = None if pd.isna(ma200) else safe_float(ma200)
        boll_upper = safe_float(boll_upper)
        boll_lower = safe_float(boll_lower)

        # ---------------------------------------------------------
        # Return clean structured output
        # ---------------------------------------------------------
        return {
            "success": True,
            "ticker": tickers["nse"] if exchange == "NSE" else tickers["bse"],
            "exchange": exchange,
            "current_price": current_price,
            "rsi": rsi,
            "ma50": ma50,
            "ma200": ma200,
            "bollinger_upper": boll_upper,
            "bollinger_lower": boll_lower,
            "last_updated": df.index[-1].strftime("%Y-%m-%d"),
        }

    except Exception as e:
        return {
            "success": False,
            "error": f"Indicator computation failed: {e}"
        }
