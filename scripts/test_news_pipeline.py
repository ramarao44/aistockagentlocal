import os
import sqlite3
import sys
from pathlib import Path

ROOT = os.path.dirname(os.path.dirname(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from src.fetcher.news_fetcher import fetch_news
from src.analyzer.sentiment_analyzer import compute_sentiment
from src.db.database import save_news, save_sentiment, load_news, load_sentiment


def ensure_db_schema():
    root = Path(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    db_path = root / "data" / "agent.db"
    schema_path = root / "data" / "schema.sql"
    if not schema_path.exists():
        return
    with sqlite3.connect(db_path) as conn:
        conn.executescript(schema_path.read_text(encoding="utf-8"))
        conn.commit()

def run_news_pipeline(ticker="AAPL"):
    ensure_db_schema()
    news_items = fetch_news(ticker)
    save_news(news_items)

    for item in news_items:
        score = compute_sentiment(item["title"])
        save_sentiment(ticker, item["title"], score)

    print("News:")
    print(load_news(ticker).head())

    print("\nSentiment:")
    print(load_sentiment(ticker).head())

if __name__ == "__main__":
    run_news_pipeline()

