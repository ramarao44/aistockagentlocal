"""
SQLite Database Module - AI Stock Agent

Handles SQLite database operations for market data, indicators, and news.
Database file is stored in the data/ directory.

Author: AI Stock Agent Team
Version: 1.0
Last Updated: 2026-07-08
"""

import sqlite3
import json
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


def ensure_fundamental_data_table():
    with get_connection() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS fundamental_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ticker TEXT NOT NULL,
                period TEXT NOT NULL,
                as_of_date TEXT NOT NULL,
                pe_ratio REAL,
                pbv_ratio REAL,
                ev_ebitda REAL,
                peg_ratio REAL,
                dividend_yield REAL,
                revenue_qoq REAL,
                revenue_yoy REAL,
                earnings_qoq REAL,
                earnings_yoy REAL,
                roe REAL,
                roa REAL,
                roce REAL,
                net_margin REAL,
                operating_margin REAL,
                debt_to_equity REAL,
                current_ratio REAL,
                quick_ratio REAL,
                beta REAL,
                interest_coverage REAL,
                valuation_json TEXT,
                growth_json TEXT,
                profitability_json TEXT,
                risk_json TEXT,
                financial_ratios_json TEXT,
                statement_snapshot_json TEXT,
                data_quality_json TEXT,
                last_updated TEXT,
                UNIQUE(ticker, period, as_of_date)
            )
            """
        )
        conn.commit()


def save_fundamental_data(payload: dict):
    ensure_fundamental_data_table()

    valuation = payload.get("valuation", {})
    growth = payload.get("growth", {})
    profitability = payload.get("profitability", {})
    risk = payload.get("risk", {})

    with get_connection() as conn:
        conn.execute(
            """
            INSERT INTO fundamental_data (
                ticker, period, as_of_date,
                pe_ratio, pbv_ratio, ev_ebitda, peg_ratio, dividend_yield,
                revenue_qoq, revenue_yoy, earnings_qoq, earnings_yoy,
                roe, roa, roce, net_margin, operating_margin,
                debt_to_equity, current_ratio, quick_ratio, beta, interest_coverage,
                valuation_json, growth_json, profitability_json, risk_json,
                financial_ratios_json, statement_snapshot_json, data_quality_json, last_updated
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(ticker, period, as_of_date) DO UPDATE SET
                pe_ratio = excluded.pe_ratio,
                pbv_ratio = excluded.pbv_ratio,
                ev_ebitda = excluded.ev_ebitda,
                peg_ratio = excluded.peg_ratio,
                dividend_yield = excluded.dividend_yield,
                revenue_qoq = excluded.revenue_qoq,
                revenue_yoy = excluded.revenue_yoy,
                earnings_qoq = excluded.earnings_qoq,
                earnings_yoy = excluded.earnings_yoy,
                roe = excluded.roe,
                roa = excluded.roa,
                roce = excluded.roce,
                net_margin = excluded.net_margin,
                operating_margin = excluded.operating_margin,
                debt_to_equity = excluded.debt_to_equity,
                current_ratio = excluded.current_ratio,
                quick_ratio = excluded.quick_ratio,
                beta = excluded.beta,
                interest_coverage = excluded.interest_coverage,
                valuation_json = excluded.valuation_json,
                growth_json = excluded.growth_json,
                profitability_json = excluded.profitability_json,
                risk_json = excluded.risk_json,
                financial_ratios_json = excluded.financial_ratios_json,
                statement_snapshot_json = excluded.statement_snapshot_json,
                data_quality_json = excluded.data_quality_json,
                last_updated = excluded.last_updated
            """,
            (
                payload.get("ticker"),
                payload.get("period", "quarterly"),
                payload.get("last_updated"),
                valuation.get("pe_ratio"),
                valuation.get("pbv_ratio"),
                valuation.get("ev_ebitda"),
                valuation.get("peg_ratio"),
                valuation.get("dividend_yield"),
                growth.get("revenue_qoq"),
                growth.get("revenue_yoy"),
                growth.get("earnings_qoq"),
                growth.get("earnings_yoy"),
                profitability.get("roe"),
                profitability.get("roa"),
                profitability.get("roce"),
                profitability.get("net_margin"),
                profitability.get("operating_margin"),
                risk.get("debt_to_equity"),
                risk.get("current_ratio"),
                risk.get("quick_ratio"),
                risk.get("beta"),
                risk.get("interest_coverage"),
                json.dumps(valuation, default=str),
                json.dumps(growth, default=str),
                json.dumps(profitability, default=str),
                json.dumps(risk, default=str),
                json.dumps(payload.get("financial_ratios", {}), default=str),
                json.dumps(payload.get("statement_snapshot", {}), default=str),
                json.dumps(payload.get("data_quality", {}), default=str),
                payload.get("last_updated"),
            ),
        )
        conn.commit()


def load_latest_fundamental_data(ticker: str, period: str = "quarterly"):
    ensure_fundamental_data_table()
    with get_connection() as conn:
        row = conn.execute(
            """
            SELECT
                ticker, period, as_of_date,
                valuation_json, growth_json, profitability_json, risk_json,
                financial_ratios_json, statement_snapshot_json, data_quality_json,
                last_updated
            FROM fundamental_data
            WHERE ticker = ? AND period = ?
            ORDER BY as_of_date DESC
            LIMIT 1
            """,
            (ticker, period),
        ).fetchone()

    if row is None:
        return None

    return {
        "ticker": row[0],
        "period": row[1],
        "as_of_date": row[2],
        "valuation": json.loads(row[3] or "{}"),
        "growth": json.loads(row[4] or "{}"),
        "profitability": json.loads(row[5] or "{}"),
        "risk": json.loads(row[6] or "{}"),
        "financial_ratios": json.loads(row[7] or "{}"),
        "statement_snapshot": json.loads(row[8] or "{}"),
        "data_quality": json.loads(row[9] or "{}"),
        "last_updated": row[10],
    }
