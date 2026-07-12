from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from src.core.debug import dbg

analyzer = SentimentIntensityAnalyzer()

def compute_sentiment(text: str, master: dict | None = None):
    dbg(master, "ANALYSIS.SENTIMENT", "SCORE", "OK", "Computing sentiment score")
    if not text:
        return 0.0
    score = analyzer.polarity_scores(text)
    return score["compound"]
