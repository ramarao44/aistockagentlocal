import requests
import xml.etree.ElementTree as ET
from datetime import datetime

from src.core.debug import dbg

def fetch_news(ticker: str, count: int = 10, master: dict | None = None):
    dbg(master, "INGESTION.NEWS", "FETCH", "OK", f"Fetching news for {ticker}")
    url = f"https://feeds.finance.yahoo.com/rss/2.0/headline?s={ticker}&region=US&lang=en-US"
    try:
        response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
        response.raise_for_status()

        root = ET.fromstring(response.content)

        news_items = []
        for item in root.findall(".//item")[:count]:
            title = item.find("title").text
            link = item.find("link").text
            pub_date = item.find("pubDate").text

            news_items.append({
                "ticker": ticker,
                "title": title,
                "publisher": "Yahoo Finance",
                "link": link,
                "published_at": datetime.strptime(pub_date, "%a, %d %b %Y %H:%M:%S %z"),
            })

        dbg(master, "INGESTION.NEWS", "FETCH", "OK", f"Fetched {len(news_items)} news items")
        return news_items
    except Exception as exc:
        dbg(master, "INGESTION.NEWS", "FETCH", "ERR", str(exc))
        raise
