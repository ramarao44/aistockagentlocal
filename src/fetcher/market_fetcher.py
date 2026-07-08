"""
Market Fetcher Module - AI Stock Agent

This module handles fetching market data from various sources for Indian stocks.
Primary data source: yfinance (Yahoo Finance)
Secondary sources: Moneycontrol, NSE India

Author: AI Stock Agent Team
Version: 1.0
Last Updated: 2026-07-07
"""

import json
import re
import yfinance as yf
import pandas as pd
import requests
from bs4 import BeautifulSoup
from urllib.parse import quote_plus

from src.database.crud import save_daily_record

# Optional: cloudscraper for NSE data (bypasses Cloudflare)
try:
    import cloudscraper
except ImportError:
    cloudscraper = None

# ---------------------------------------------------------
# Ticker Normalization (NSE + BSE)
# ---------------------------------------------------------

def normalize_ticker(user_input: str):
    base = user_input.strip().upper()
    if base.endswith(".NS"):
        base_name = base[:-3]
        return {
            "nse": base,
            "bse": f"{base_name}.BO"
        }
    if base.endswith(".BO"):
        base_name = base[:-3]
        return {
            "nse": f"{base_name}.NS",
            "bse": base
        }
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


def calculate_vwap(df):
    """
    Compute VWAP from intraday OHLCV dataframe.
    df must contain: High, Low, Close, Volume
    """
    if df is None or df.empty:
        return None

    tp = (df["High"] + df["Low"] + df["Close"]) / 3
    vwap = (tp * df["Volume"]).sum() / df["Volume"].sum()

    return float(vwap)


def detect_volume_breakout(df):
    """
    Detect volume breakout using 20-day average volume.
    Returns True/False.
    """
    if df is None or df.empty:
        return None

    if "Volume" not in df.columns:
        return None

    today_volume = df["Volume"].iloc[-1]
    avg_20_volume = df["Volume"].tail(20).mean()
    breakout = today_volume > (2 * avg_20_volume)

    return bool(breakout)


def find_support_resistance(df):
    """
    Detect swing highs (resistance) and swing lows (support).
    Returns lists of levels.
    """
    supports = []
    resistances = []

    highs = df["High"].values
    lows = df["Low"].values

    for i in range(1, len(df) - 1):
        if highs[i] > highs[i - 1] and highs[i] > highs[i + 1]:
            resistances.append(float(highs[i]))

        if lows[i] < lows[i - 1] and lows[i] < lows[i + 1]:
            supports.append(float(lows[i]))

    return supports[-5:], resistances[-5:]


def calculate_pivot_points(df):
    """
    Classic pivot point calculation using last day's OHLC.
    """
    last = df.iloc[-1]
    high = last["High"]
    low = last["Low"]
    close = last["Close"]

    pivot = (high + low + close) / 3
    r1 = (2 * pivot) - low
    s1 = (2 * pivot) - high

    return {
        "pivot": float(pivot),
        "r1": float(r1),
        "s1": float(s1)
    }


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


def analyze_stock(ticker: str):
    """
    Unified wrapper for MVP.
    Returns:
      - raw indicator data (JSON)
      - natural-language AI stock report
    """
    data = fetch_indian_stock_data(ticker)

    # If fetch failed, return error
    if not data.get("success", False):
        return {
            "success": False,
            "error": data.get("error", "Unknown error"),
            "report": f"Could not generate report for {ticker}."
        }

    report = generate_stock_report(data)

    return {
        "success": True,
        "data": data,
        "report": report
    }


def fetch_nse_delivery_data(symbol: str):
    """
    Fetch delivery volume % from NSE India using cloudscraper.
    This bypasses Cloudflare and returns real delivery data.
    """

    url = f"https://www.nseindia.com/api/quote-equity?symbol={symbol.upper()}"

    if cloudscraper is None:
        return {
            "success": False,
            "error": "cloudscraper is not installed"
        }

    scraper = cloudscraper.create_scraper(
        browser={
            "browser": "chrome",
            "platform": "windows",
            "mobile": False
        }
    )

    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/json",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://www.nseindia.com/",
    }

    try:
        response = scraper.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()

        security_info = data.get("securityInfo", {})
        market_info = data.get("marketDeptOrderBook", {})

        delivery_pct = security_info.get("deliveryToTradedQuantity")
        delivery_qty = security_info.get("deliveryQuantity")
        total_volume = market_info.get("totalTradedVolume")

        return {
            "success": True,
            "delivery_pct": delivery_pct,
            "delivery_qty": delivery_qty,
            "total_volume": total_volume
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


def moneycontrol_find_stock_url(symbol: str):
    """
    Discover the Moneycontrol stock page URL using autosuggestion.
    """
    url = "https://www.moneycontrol.com/mccode/common/autosuggestion.php"
    params = {
        "query": symbol.upper(),
        "type": "1",
    }
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://www.moneycontrol.com/",
    }

    try:
        response = requests.get(url, params=params, headers=headers, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")
        link = soup.select_one("ul.suglist li a")
        if not link or not link.has_attr("href"):
            return None

        href = link.get("href")
        if not isinstance(href, str):
            return None

        href = href.strip()
        if not href:
            return None

        if href.startswith("/"):
            return f"https://www.moneycontrol.com{href}"

        return href

    except Exception:
        return None


def parse_moneycontrol_volume(html: str):
    marker = '"volume":'
    start = html.find(marker)
    if start == -1:
        return None

    start = html.find("{", start + len(marker))
    if start == -1:
        return None

    brace = 0
    in_string = False
    escape = False

    for idx in range(start, len(html)):
        ch = html[idx]
        if ch == "\\" and not escape:
            escape = True
            continue

        if ch == '"' and not escape:
            in_string = not in_string

        if not in_string:
            if ch == "{":
                brace += 1
            elif ch == "}":
                brace -= 1
                if brace == 0:
                    payload = html[start:idx + 1]
                    try:
                        return json.loads(payload)
                    except json.JSONDecodeError:
                        return None

        escape = False

    return None


def parse_percent(text: str):
    match = re.search(r"([0-9]+(?:\.[0-9]+)?)%", text)
    if match:
        return float(match.group(1))
    match = re.search(r"([0-9]+(?:\.[0-9]+)?)", text)
    if match:
        return float(match.group(1))
    return None


def fetch_moneycontrol_delivery(symbol: str):
    """
    Fetch delivery volume % from Moneycontrol by parsing the stock page.
    """
    stock_url = moneycontrol_find_stock_url(symbol)
    if not stock_url:
        return {"success": False, "error": "Could not find Moneycontrol stock page"}

    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://www.moneycontrol.com/",
    }

    try:
        response = requests.get(stock_url, headers=headers, timeout=10)
        response.raise_for_status()

        volume_data = parse_moneycontrol_volume(response.text)
        if not volume_data or "Today" not in volume_data:
            return {"success": False, "error": "Could not parse Moneycontrol volume data"}

        today = volume_data["Today"]
        delivery_qty = today.get("delivery")
        total_volume = today.get("cvol")
        delivery_pct = None

        for field in ("delivery_display_text", "delivery_tooltip_text"):
            text = today.get(field)
            if isinstance(text, str):
                delivery_pct = parse_percent(text)
                if delivery_pct is not None:
                    break

        if delivery_pct is None and delivery_qty is not None and total_volume:
            try:
                delivery_pct = round((delivery_qty / total_volume) * 100, 2)
            except Exception:
                delivery_pct = None

        if delivery_qty is None or total_volume is None:
            return {"success": False, "error": "Incomplete Moneycontrol delivery data"}

        return {
            "success": True,
            "delivery_pct": delivery_pct,
            "delivery_qty": delivery_qty,
            "total_volume": total_volume,
        }

    except Exception as e:
        return {"success": False, "error": str(e)}


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

        data_ticker = tickers["nse"] if exchange == "NSE" else tickers["bse"]
        intraday = yf.download(
            tickers=data_ticker,
            interval="5m",
            period="1d",
            progress=False
        )

        if intraday is None:
            intraday = pd.DataFrame()

        if intraday is None or intraday.empty:
            vwap = None
        else:
            if isinstance(intraday.columns, pd.MultiIndex):
                try:
                    intraday.columns = intraday.columns.get_level_values(0)
                except Exception:
                    intraday.columns = ["_".join(map(str, c)).strip() for c in intraday.columns]
            intraday = intraday.dropna()
            vwap = calculate_vwap(intraday)

        volume_breakout = detect_volume_breakout(df)
        today_volume = None
        if "Volume" in df.columns and not df.empty:
            last_volume = df["Volume"].iloc[-1]
            if pd.notna(last_volume):
                today_volume = int(last_volume)

        if df.empty:
            supports, resistances = [], []
            pivot_points = {"pivot": None, "r1": None, "s1": None}
            rsi = None
            ma50 = None
            ma200 = None
            boll_upper, boll_lower = None, None
            current_price = None
            supertrend_value, supertrend_dir = None, "DOWN"
            macd_line, macd_signal, macd_hist = None, None, None
            adx_val, plus_di_val, minus_di_val = None, None, None
        else:
            supports, resistances = find_support_resistance(df)
            pivot_points = calculate_pivot_points(df)

            # Compute indicators
            rsi = compute_rsi(df)
            ma50 = compute_moving_average(df, 50)
            ma200 = compute_moving_average(df, 200)
            boll_upper, boll_lower = compute_bollinger_bands(df)
            current_price = df["Close"].iloc[-1]

            # SuperTrend
            supertrend_value, supertrend_dir = compute_supertrend(df)

            # MACD
            macd_line, macd_signal, macd_hist = compute_macd(df)

            # ADX
            adx_val, plus_di_val, minus_di_val = compute_adx(df)

        if current_price is not None:
            current_price = safe_float(current_price)
        else:
            current_price = None

        if rsi is not None:
            rsi = safe_float(rsi)
        if ma50 is not None:
            ma50 = safe_float(ma50)
        if ma200 is not None:
            ma200 = None if pd.isna(ma200) else safe_float(ma200)
        if boll_upper is not None:
            boll_upper = safe_float(boll_upper)
        if boll_lower is not None:
            boll_lower = safe_float(boll_lower)

        # Delivery Volume % (Moneycontrol)
        try:
            delivery_data = fetch_moneycontrol_delivery(user_input)
            if delivery_data.get("success"):
                delivery_pct = delivery_data.get("delivery_pct")
                delivery_qty = delivery_data.get("delivery_qty")
                total_volume = delivery_data.get("total_volume")
            else:
                delivery_pct = None
                delivery_qty = None
                total_volume = None
        except Exception:
            delivery_pct = None
            delivery_qty = None
            total_volume = None

        # Delivery trend over the last 3 days
        delivery_trend_pct = None
        if delivery_pct is not None and total_volume is not None and len(df) >= 4:
            recent_volumes = df["Volume"].iloc[-4:-1]
            if recent_volumes.notna().all() and recent_volumes.mean() > 0:
                delivery_trend_pct = round((delivery_pct - (recent_volumes.mean() / total_volume * 100)), 2)

        # Trend Score 2.0
        from src.analysis.trend_score import compute_trend_score

        trend_score = compute_trend_score({
            "delivery_volume_pct": delivery_pct,
            "delivery_trend_pct": delivery_trend_pct,
            "current_price": current_price,
            "vwap": vwap,
            "volume_breakout": bool(volume_breakout),
            "supports": supports,
            "resistances": resistances,
            "pivot_points": pivot_points,
            "df": df,
        })

        if not df.empty:
            record = save_daily_record({
                "symbol": user_input,
                "open": float(df["Open"].iloc[-1]),
                "high": float(df["High"].iloc[-1]),
                "low": float(df["Low"].iloc[-1]),
                "close": float(df["Close"].iloc[-1]),
                "volume": int(df["Volume"].iloc[-1]) if "Volume" in df.columns and not df["Volume"].isna().iloc[-1] else None,
                "delivery_pct": delivery_pct,
                "delivery_qty": delivery_qty,
                "total_volume": total_volume,
                "vwap": vwap,
                "volume_breakout": int(bool(volume_breakout)) if volume_breakout is not None else None,
                "supports": supports,
                "resistances": resistances,
                "pivot_points": pivot_points,
                "trend_score": trend_score,
            })
        else:
            record = None

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
            "delivery_volume_pct": delivery_pct,
            "delivery_volume_qty": delivery_qty,
            "total_volume": total_volume,
            "today_volume": today_volume,
            "vwap": vwap,
            "volume_breakout": volume_breakout,
            "supports": supports,
            "resistances": resistances,
            "pivot_points": pivot_points,
            "trend_score": trend_score,
        }

    except Exception as e:
        return {
            "success": False,
            "error": f"Indicator computation failed: {e}"
        }
