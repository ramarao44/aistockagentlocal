from datetime import datetime, timedelta
import pandas as pd

from src.database.sqlite_legacy import (
    load_market_data,
    load_indicators,
    load_news,
    load_sentiment
)

def generate_daily_summary(ticker: str):
    market = load_market_data(ticker)
    indicators = load_indicators(ticker)
    news = load_news(ticker)
    sentiment = load_sentiment(ticker)

    latest_price = market.iloc[-1]
    latest_ind = indicators.iloc[-1]

    latest_news = news.head(3)
    latest_sent = sentiment.head(3)

    # Safe formatter
    def fmt(value):
        return "N/A" if value is None else f"{value:.2f}"

    # Safe date
    date_str = (
        latest_price["date"].date()
        if latest_price["date"] is not None
        else "N/A"
    )

    # Build summary
    summary = (
        f"Daily Summary for {ticker} — {date_str}\n\n"
        f"Price:\n"
        f"- Close: {fmt(latest_price['close'])}\n"
        f"- High: {fmt(latest_price['high'])}\n"
        f"- Low: {fmt(latest_price['low'])}\n"
        f"- Volume: {latest_price['volume'] if latest_price['volume'] is not None else 'N/A'}\n\n"
        f"Technical Indicators:\n"
        f"- RSI: {fmt(latest_ind['rsi'])}\n"
        f"- MACD: {fmt(latest_ind['macd'])}\n"
        f"- MACD Signal: {fmt(latest_ind['macd_signal'])}\n"
        f"- MACD Hist: {fmt(latest_ind['macd_hist'])}\n"
        f"- MA20: {fmt(latest_ind['ma20'])}\n"
        f"- MA50: {fmt(latest_ind['ma50'])}\n\n"
        f"Latest News:\n"
    )

    # Add news
    for _, row in latest_news.iterrows():
        summary += f"- {row['title']} ({row['published_at']})\n"

    summary += "\nSentiment (Top Headlines):\n"

    # Add sentiment
    for _, row in latest_sent.iterrows():
        summary += f"- {row['title']} → {row['sentiment']:.3f}\n"

    return summary



def generate_trend_analysis(ticker: str, days: int = 7):
    market = load_market_data(ticker)
    indicators = load_indicators(ticker)
    sentiment = load_sentiment(ticker)

    recent_market = market.tail(days)
    recent_ind = indicators.tail(days)
    recent_sent = sentiment.head(10)

    def safe_diff(a, b):
        if a is None or b is None:
            return "N/A"
        return a - b

    price_change = safe_diff(
        recent_market.iloc[-1]["close"],
        recent_market.iloc[0]["close"]
    )

    rsi_trend = safe_diff(
        recent_ind["rsi"].iloc[-1],
        recent_ind["rsi"].iloc[0]
    )

    macd_trend = safe_diff(
        recent_ind["macd"].iloc[-1],
        recent_ind["macd"].iloc[0]
    )

    avg_sentiment = (
        recent_sent["sentiment"].mean()
        if len(recent_sent) > 0
        else "N/A"
    )

    trend = f"""
Trend Analysis for {ticker} — Last {days} Days

Price Trend:
- Price change: {price_change}

Indicator Trends:
- RSI change: {rsi_trend}
- MACD change: {macd_trend}

Sentiment Trend:
- Average sentiment: {avg_sentiment}
"""

    return trend


def generate_combined_report(ticker: str):
    daily = generate_daily_summary(ticker)
    trend = generate_trend_analysis(ticker)

    return daily + "\n" + trend
