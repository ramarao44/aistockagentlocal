import ta

def compute_indicators(df):
    """
    Compute RSI, MACD, and moving averages using the 'ta' library.
    """

    try:
        # RSI (Relative Strength Index)
        rsi_indicator = ta.momentum.RSIIndicator(close=df['Close'], window=14)
        df['RSI'] = rsi_indicator.rsi()

        # MACD (Moving Average Convergence Divergence)
        macd_indicator = ta.trend.MACD(close=df['Close'])
        df['MACD'] = macd_indicator.macd()
        df['MACD_signal'] = macd_indicator.macd_signal()
        df['MACD_hist'] = macd_indicator.macd_diff()

        # Simple Moving Averages
        ma20 = ta.trend.SMAIndicator(close=df['Close'], window=20)
        ma50 = ta.trend.SMAIndicator(close=df['Close'], window=50)

        df['MA20'] = ma20.sma_indicator()
        df['MA50'] = ma50.sma_indicator()

        return df

    except Exception as e:
        print(f"[Analyzer Error] {e}")
        return df
