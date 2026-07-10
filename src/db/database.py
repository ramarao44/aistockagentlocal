"""
SQLite Database Module - AI Stock Agent

Handles SQLite database operations for market data, indicators, and news.
Database file is stored in the data/ directory.

Author: AI Stock Agent Team
Version: 1.0
Last Updated: 2026-07-08
"""

import sqlite3
from pathlib import Path
import pandas as pd

# Database path: data/agent.db (relative to project root)
DB_PATH = Path("data/agent.db")

def get_connection():
    return sqlite3.connect(DB_PATH)


def ensure_symbol_resolution_cache_table():
    with get_connection() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS symbol_resolution_cache (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                input_key TEXT NOT NULL UNIQUE,
                resolved_nse TEXT NOT NULL,
                resolved_bse TEXT NOT NULL,
                source TEXT,
                last_used_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        conn.commit()

def save_market_data(df: pd.DataFrame, ticker: str):
    df = df.copy()
    df["ticker"] = ticker
    df.reset_index(inplace=True)  # Date becomes a column

    records = []
    for _, row in df.iterrows():
        records.append(
            (
                row["ticker"],
                row["Date"].strftime("%Y-%m-%d"),
                row["Open"],
                row["High"],
                row["Low"],
                row["Close"],
                int(row["Volume"]),
            )
        )

    with get_connection() as conn:
        conn.executemany(
            """
            INSERT OR REPLACE INTO market_data
            (ticker, date, open, high, low, close, volume)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            records,
        )
        conn.commit()

def save_indicators(df: pd.DataFrame, ticker: str):
    df = df.copy()
    df["ticker"] = ticker
    df.reset_index(inplace=True)

    records = []
    for _, row in df.iterrows():
        records.append(
            (
                row["ticker"],
                row["Date"].strftime("%Y-%m-%d"),
                row.get("RSI"),
                row.get("MACD"),
                row.get("MACD_signal"),
                row.get("MACD_hist"),
                row.get("MA20"),
                row.get("MA50"),
            )
        )

    with get_connection() as conn:
        conn.executemany(
            """
            INSERT OR REPLACE INTO technical_indicators
            (ticker, date, rsi, macd, macd_signal, macd_hist, ma20, ma50)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            records,
        )
        conn.commit()

def load_market_data(ticker: str):
    with get_connection() as conn:
        df = pd.read_sql_query(
            """
            SELECT date, open, high, low, close, volume
            FROM market_data
            WHERE ticker = ?
            ORDER BY date ASC
            """,
            conn,
            params=(ticker,),
            parse_dates=["date"]
        )
    return df

def load_indicators(ticker: str):
    with get_connection() as conn:
        df = pd.read_sql_query(
            """
            SELECT date, rsi, macd, macd_signal, macd_hist, ma20, ma50
            FROM technical_indicators
            WHERE ticker = ?
            ORDER BY date ASC
            """,
            conn,
            params=(ticker,),
            parse_dates=["date"]
        )
    return df

def load_latest_market_data(ticker: str):
    with get_connection() as conn:
        df = pd.read_sql_query(
            """
            SELECT date, open, high, low, close, volume
            FROM market_data
            WHERE ticker = ?
            ORDER BY date DESC
            LIMIT 1
            """,
            conn,
            params=(ticker,),
            parse_dates=["date"]
        )
    return df.iloc[0] if not df.empty else None


def load_latest_indicators(ticker: str):
    with get_connection() as conn:
        df = pd.read_sql_query(
            """
            SELECT date, rsi, macd, macd_signal, macd_hist, ma20, ma50
            FROM technical_indicators
            WHERE ticker = ?
            ORDER BY date DESC
            LIMIT 1
            """,
            conn,
            params=(ticker,),
            parse_dates=["date"]
        )
    return df.iloc[0] if not df.empty else None


def save_news(news_items):
    records = []
    for item in news_items:
        records.append((
            item["ticker"],
            item["title"],
            item["publisher"],
            item["link"],
            item["published_at"].strftime("%Y-%m-%d %H:%M:%S"),
        ))

    with get_connection() as conn:
        conn.executemany(
            """
            INSERT OR REPLACE INTO news
            (ticker, title, publisher, link, published_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            records,
        )
        conn.commit()


def save_sentiment(ticker: str, title: str, sentiment: float):
    with get_connection() as conn:
        conn.execute(
            """
            INSERT OR REPLACE INTO sentiment
            (ticker, title, sentiment)
            VALUES (?, ?, ?)
            """,
            (ticker, title, sentiment)
        )
        conn.commit()


def load_news(ticker: str):
    with get_connection() as conn:
        df = pd.read_sql_query(
            """
            SELECT title, publisher, link, published_at
            FROM news
            WHERE ticker = ?
            ORDER BY published_at DESC
            """,
            conn,
            params=(ticker,),
            parse_dates=["published_at"]
        )
    return df

def load_sentiment(ticker: str):
    with get_connection() as conn:
        df = pd.read_sql_query(
            """
            SELECT title, sentiment
            FROM sentiment
            WHERE ticker = ?
            ORDER BY sentiment DESC
            """,
            conn,
            params=(ticker,)
        )
    return df


def load_symbol_resolution_cache(input_key: str):
    ensure_symbol_resolution_cache_table()
    with get_connection() as conn:
        row = conn.execute(
            """
            SELECT resolved_nse, resolved_bse, source
            FROM symbol_resolution_cache
            WHERE input_key = ?
            LIMIT 1
            """,
            (input_key,)
        ).fetchone()

        if row is None:
            return None

        conn.execute(
            """
            UPDATE symbol_resolution_cache
            SET last_used_at = CURRENT_TIMESTAMP
            WHERE input_key = ?
            """,
            (input_key,)
        )
        conn.commit()

    return {
        "nse": row[0],
        "bse": row[1],
        "source": row[2],
    }


def save_symbol_resolution_cache(input_key: str, resolved_nse: str, resolved_bse: str, source: str = "resolved"):
    ensure_symbol_resolution_cache_table()
    with get_connection() as conn:
        conn.execute(
            """
            INSERT INTO symbol_resolution_cache (input_key, resolved_nse, resolved_bse, source, last_used_at)
            VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(input_key) DO UPDATE SET
                resolved_nse = excluded.resolved_nse,
                resolved_bse = excluded.resolved_bse,
                source = excluded.source,
                last_used_at = CURRENT_TIMESTAMP
            """,
            (input_key, resolved_nse, resolved_bse, source),
        )
        conn.commit()
