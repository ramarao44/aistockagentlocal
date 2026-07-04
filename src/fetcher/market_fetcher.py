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
        df = df.dropna()

        # yfinance may return a DataFrame with MultiIndex columns when a ticker
        # includes the symbol as the second level (e.g. ('Close', 'RELIANCE.NS')).
        # Normalize to single-level columns like 'Close', 'High', etc.
        if isinstance(df.columns, pd.MultiIndex):
            try:
                df.columns = df.columns.get_level_values(0)
            except Exception:
                # Fallback: convert to single-level by joining names
                df.columns = ["_".join(map(str, c)).strip() for c in df.columns]

        return df
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


def compute_atr(df, period=10):
    high = df["High"]
    low = df["Low"]
    close = df["Close"]

    tr1 = high - low
    tr2 = (high - close.shift(1)).abs()
    tr3 = (low - close.shift(1)).abs()

    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    atr = tr.rolling(period).mean()

    return atr.iloc[-1]


def compute_supertrend(df, period=10, multiplier=3):
    atr = compute_atr(df, period)
    hl2 = (df["High"] + df["Low"]) / 2

    upper_band = hl2 + (multiplier * atr)
    lower_band = hl2 - (multiplier * atr)

    supertrend = []
    direction = []

    for i in range(len(df)):
        if i == 0:
            supertrend.append(upper_band.iloc[i])
            direction.append("DOWN")
        else:
            if df["Close"].iloc[i] > upper_band.iloc[i-1]:
                direction.append("UP")
                supertrend.append(lower_band.iloc[i])
            elif df["Close"].iloc[i] < lower_band.iloc[i-1]:
                direction.append("DOWN")
                supertrend.append(upper_band.iloc[i])
            else:
                direction.append(direction[i-1])
                if direction[i] == "UP":
                    supertrend.append(lower_band.iloc[i])
                else:
                    supertrend.append(upper_band.iloc[i])

    return supertrend[-1], direction[-1]


def compute_macd(df, fast=12, slow=26, signal=9):
    close = df["Close"]

    ema_fast = close.ewm(span=fast, adjust=False).mean()
    ema_slow = close.ewm(span=slow, adjust=False).mean()

    macd_line = ema_fast - ema_slow
    signal_line = macd_line.ewm(span=signal, adjust=False).mean()
    histogram = macd_line - signal_line

    return macd_line.iloc[-1], signal_line.iloc[-1], histogram.iloc[-1]


def compute_adx(df, period=14):
    high = df["High"]
    low = df["Low"]
    close = df["Close"]

    # True Range
    tr1 = high - low
    tr2 = (high - close.shift(1)).abs()
    tr3 = (low - close.shift(1)).abs()
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)

    # Directional Movement
    up_move = high.diff()
    down_move = low.diff() * -1

    plus_dm = up_move.where((up_move > down_move) & (up_move > 0), 0)
    minus_dm = down_move.where((down_move > up_move) & (down_move > 0), 0)

    # Smoothed ATR and DM
    atr = tr.rolling(period).mean()
    plus_di = 100 * (plus_dm.rolling(period).mean() / atr)
    minus_di = 100 * (minus_dm.rolling(period).mean() / atr)

    dx = (abs(plus_di - minus_di) / (plus_di + minus_di)) * 100
    adx = dx.rolling(period).mean()

    return adx.iloc[-1], plus_di.iloc[-1], minus_di.iloc[-1]


def compute_trend_score(
    supertrend_dir,
    macd_hist,
    adx,
    rsi,
    ma50,
    ma200,
    current_price
):
    score = 50  # start neutral

    # SuperTrend direction
    if supertrend_dir == "UP":
        score += 10
    else:
        score -= 10

    # MACD momentum
    if macd_hist > 0:
        score += min(macd_hist * 2, 10)
    else:
        score += max(macd_hist * 2, -10)

    # ADX strength
    if adx >= 25:
        score += 10
    elif adx <= 15:
        score -= 10

    # RSI
    if rsi < 30:
        score += 10
    elif rsi > 70:
        score -= 10

    # MA50 / MA200 trend
    if ma50 is not None and ma200 is not None:
        if ma50 > ma200:
            score += 10
        else:
            score -= 10

    # Price relative to MA50
    if ma50 is not None:
        if current_price > ma50:
            score += 5
        else:
            score -= 5

    # Clamp score between 0–100
    score = max(0, min(100, score))

    return score


def generate_stock_report(data):
    """
    Generate a natural-language AI stock report based on computed indicators.
    """

    ticker = data.get("ticker", "Unknown")
    price = data.get("current_price")
    trend = data.get("supertrend_direction")
    macd_line = data.get("macd_line")
    macd_signal = data.get("macd_signal")
    macd_hist = data.get("macd_histogram")
    adx = data.get("adx")
    plus_di = data.get("plus_di")
    minus_di = data.get("minus_di")
    rsi = data.get("rsi")
    ma50 = data.get("ma50")
    ma200 = data.get("ma200")
    trend_score = data.get("trend_score")

    # --- Trend Summary ---
    if trend == "UP":
        trend_text = "The SuperTrend indicator shows an upward trend."
    else:
        trend_text = "The SuperTrend indicator shows a downward trend."

    # --- MACD Summary ---
    if macd_hist > 0:
        macd_text = "MACD momentum is positive, indicating bullish pressure."
    else:
        macd_text = "MACD momentum is negative, indicating bearish pressure."

    # --- ADX Summary ---
    if adx >= 25:
        adx_text = "ADX suggests a strong trend."
    elif adx <= 15:
        adx_text = "ADX indicates a weak or fading trend."
    else:
        adx_text = "ADX shows a moderate trend strength."

    # --- RSI Summary ---
    if rsi < 30:
        rsi_text = "RSI indicates the stock is oversold."
    elif rsi > 70:
        rsi_text = "RSI indicates the stock is overbought."
    else:
        rsi_text = "RSI is in a neutral zone."

    # --- MA Summary ---
    if ma50 and ma200:
        if ma50 > ma200:
            ma_text = "The 50-day MA is above the 200-day MA, indicating long-term bullish structure."
        else:
            ma_text = "The 50-day MA is below the 200-day MA, indicating long-term bearish structure."
    else:
        ma_text = "Insufficient data for MA trend analysis."

    # --- Trend Score Summary ---
    if trend_score >= 70:
        score_text = "Overall trend score suggests a strong bullish outlook."
    elif trend_score >= 40:
        score_text = "Overall trend score suggests a neutral or mixed outlook."
    else:
        score_text = "Overall trend score suggests a bearish outlook."

    # --- Final Report ---
    report = (
        f"📈 AI Stock Report for {ticker}\n"
        f"Current Price: ₹{price:.2f}\n\n"
        f"{trend_text}\n"
        f"{macd_text}\n"
        f"{adx_text}\n"
        f"{rsi_text}\n"
        f"{ma_text}\n\n"
        f"🔎 Trend Score: {trend_score}/100\n"
        f"{score_text}\n"
    )

    return report



# ---------------------------------------------------------
# Combined Market Data Fetcher (NSE + BSE)
# ---------------------------------------------------------

def fetch_indian_stock_data(user_input: str):
    tickers = normalize_ticker(user_input)

    df = fetch_price_history(tickers["nse"])
    exchange = "NSE"

    if df is None:
        df = fetch_price_history(tickers["bse"])
        exchange = "BSE"

    if df is None:
        return {
            "success": False,
            "error": f"Could not fetch data for {user_input}"
        }

    try:
        # safe_float MUST be defined before usage
        def safe_float(val):
            if isinstance(val, pd.Series):
                return float(val.iloc[-1])
            return float(val)

        # Compute indicators
        rsi = compute_rsi(df)
        ma50 = compute_moving_average(df, 50)
        ma200 = compute_moving_average(df, 200)
        boll_upper, boll_lower = compute_bollinger_bands(df)
        current_price = df["Close"].iloc[-1]

        # SuperTrend
        supertrend_value, supertrend_dir = compute_supertrend(df)
        supertrend_value = safe_float(supertrend_value)

        # MACD
        macd_line, macd_signal, macd_hist = compute_macd(df)
        macd_line = safe_float(macd_line)
        macd_signal = safe_float(macd_signal)
        macd_hist = safe_float(macd_hist)

        # ADX
        adx_val, plus_di_val, minus_di_val = compute_adx(df)
        adx_val = safe_float(adx_val)
        plus_di_val = safe_float(plus_di_val)
        minus_di_val = safe_float(minus_di_val)

        # Normalize
        current_price = safe_float(current_price)
        rsi = safe_float(rsi)
        ma50 = safe_float(ma50)
        ma200 = None if pd.isna(ma200) else safe_float(ma200)
        boll_upper = safe_float(boll_upper)
        boll_lower = safe_float(boll_lower)

        # Trend Score
        trend_score = compute_trend_score(
            supertrend_dir,
            macd_hist,
            adx_val,
            rsi,
            ma50,
            ma200,
            current_price,
        )

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
            "supertrend": supertrend_value,
            "supertrend_direction": supertrend_dir,
            "last_updated": df.index[-1].strftime("%Y-%m-%d"),
            "macd_line": macd_line,
            "macd_signal": macd_signal,
            "macd_histogram": macd_hist,
            "adx": adx_val,
            "plus_di": plus_di_val,
            "minus_di": minus_di_val,
            "trend_score": trend_score,
        }

    except Exception as e:
        return {
            "success": False,
            "error": f"Indicator computation failed: {e}"
        }
