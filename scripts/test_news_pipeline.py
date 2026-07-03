from src.fetcher.news_fetcher import fetch_news
from src.analyzer.sentiment_analyzer import compute_sentiment
from src.db.database import save_news, save_sentiment, load_news, load_sentiment

def run_news_pipeline(ticker="AAPL"):
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

