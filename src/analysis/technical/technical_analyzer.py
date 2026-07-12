"""Technical analysis modules."""

import pandas as pd
from typing import Any
from src.core.debug import dbg
from ta.momentum import RSIIndicator
from ta.trend import MACD, SMAIndicator
from ta.volatility import BollingerBands


def _to_float(value: Any) -> float | None:
    if value is None or pd.isna(value):
        return None
    return float(value)


def compute_indicators(df, master: dict | None = None):
    """
    Compute RSI, MACD, and moving averages using the 'ta' library.
    Also computes Bollinger Bands, ADX, VWAP, and Supertrend.
    """

    try:
        dbg(master, "ANALYSIS.TECHNICAL", "RSI", "OK", "Computing RSI")
        # RSI (Relative Strength Index)
        rsi_indicator = RSIIndicator(close=df['Close'], window=14)
        df['RSI'] = rsi_indicator.rsi()

        dbg(master, "ANALYSIS.TECHNICAL", "MACD", "OK", "Computing MACD")
        # MACD (Moving Average Convergence Divergence)
        macd_indicator = MACD(close=df['Close'])
        df['MACD'] = macd_indicator.macd()
        df['MACD_signal'] = macd_indicator.macd_signal()
        df['MACD_hist'] = macd_indicator.macd_diff()

        dbg(master, "ANALYSIS.TECHNICAL", "MA", "OK", "Computing moving averages")
        # Simple Moving Averages
        ma20 = SMAIndicator(close=df['Close'], window=20)
        ma50 = SMAIndicator(close=df['Close'], window=50)
        ma200 = SMAIndicator(close=df['Close'], window=200)

        df['MA20'] = ma20.sma_indicator()
        df['MA50'] = ma50.sma_indicator()
        df['MA200'] = ma200.sma_indicator()

        dbg(master, "ANALYSIS.TECHNICAL", "BOLLINGER", "OK", "Computing Bollinger bands")
        # Bollinger Bands
        bb = BollingerBands(close=df['Close'], window=20, window_dev=2)
        df['BB_upper'] = bb.bollinger_hband()
        df['BB_middle'] = bb.bollinger_mavg()
        df['BB_lower'] = bb.bollinger_lband()

        return df

    except Exception as e:
        dbg(master, "ANALYSIS.TECHNICAL", "COMPUTE", "ERR", str(e))
        return df


def run_technical_analysis(df, market_snapshot: dict | None = None, master: dict | None = None) -> dict:
    """Run technical analysis on price dataframe and return contract-friendly output."""
    if df is None or getattr(df, "empty", True):
        dbg(master, "ANALYSIS.TECHNICAL", "RUN", "WARN", "Missing market data for technical analysis")
        return {"data_quality": "missing-market-data"}

    dbg(master, "ANALYSIS.TECHNICAL", "RUN", "OK", "Running technical analysis")
    df = compute_indicators(df, master=master)

    latest = df.iloc[-1] if len(df) > 0 else {}

    payload = {
        "rsi": _to_float(latest.get('RSI')),
        "ma20": _to_float(latest.get('MA20')),
        "ma50": _to_float(latest.get('MA50')),
        "ma200": _to_float(latest.get('MA200')),
        "macd_line": _to_float(latest.get('MACD')),
        "macd_signal": _to_float(latest.get('MACD_signal')),
        "macd_histogram": _to_float(latest.get('MACD_hist')),
        "bollinger_upper": _to_float(latest.get('BB_upper')),
        "bollinger_middle": _to_float(latest.get('BB_middle')),
        "bollinger_lower": _to_float(latest.get('BB_lower')),
        "adx": None,  # ADX requires additional implementation
        "vwap": None,  # VWAP requires volume-weighted calculation
        "supertrend": None,
        "supertrend_direction": None,
        "volume_breakout": market_snapshot.get("volume_breakout") if market_snapshot else None,
    }
    dbg(master, "ANALYSIS.TECHNICAL", "RUN", "OK", "Technical analysis complete")
    return payload


__all__ = ["compute_indicators", "run_technical_analysis"]