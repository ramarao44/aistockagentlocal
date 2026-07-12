from ta.trend import MACD


def compute_macd(df):
    macd_indicator = MACD(close=df["Close"])
    df["MACD"] = macd_indicator.macd()
    df["MACD_signal"] = macd_indicator.macd_signal()
    df["MACD_hist"] = macd_indicator.macd_diff()
    return df
