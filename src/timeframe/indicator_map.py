"""Default indicator map by timeframe."""

INDICATOR_MAP = {
    "intraday": ["vwap", "supertrend", "macd", "adx"],
    "daily": ["rsi", "macd", "ma20", "ma50", "adx", "bollinger"],
    "weekly": ["rsi", "macd", "ma50", "ma200", "adx"],
    "monthly": ["ma50", "ma200", "macd", "adx"],
    "quarterly": ["ma50", "ma200", "macd"],
    "yearly": ["ma200", "macd"],
    "swing": ["rsi", "macd", "ma50", "ma200", "adx"],
}


def get_indicator_set(timeframe: str) -> list[str]:
    key = (timeframe or "daily").strip().lower()
    return INDICATOR_MAP.get(key, INDICATOR_MAP["daily"])[:]
