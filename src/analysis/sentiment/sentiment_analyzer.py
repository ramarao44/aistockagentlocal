from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

analyzer = SentimentIntensityAnalyzer()

def compute_sentiment(text: str):
    if not text:
        return 0.0
    score = analyzer.polarity_scores(text)
    return score["compound"]
