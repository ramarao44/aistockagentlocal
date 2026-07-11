import ta


def compute_macd(df):
    macd_indicator = ta.trend.MACD(close=df["Close"])
    df["MACD"] = macd_indicator.macd()
    df["MACD_signal"] = macd_indicator.macd_signal()
    df["MACD_hist"] = macd_indicator.macd_diff()
    return df
