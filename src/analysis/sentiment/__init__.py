"""Sentiment analysis modules."""

from __future__ import annotations


POSITIVE_WORDS = {
	"beat", "growth", "surge", "upgrade", "profit", "bullish", "strong", "outperform", "gain",
}
NEGATIVE_WORDS = {
	"miss", "fall", "downgrade", "loss", "bearish", "weak", "underperform", "drop", "risk",
}


def _headline_score(headline: str) -> float:
	text = (headline or "").lower()
	positive_hits = sum(1 for word in POSITIVE_WORDS if word in text)
	negative_hits = sum(1 for word in NEGATIVE_WORDS if word in text)

	if positive_hits == negative_hits == 0:
		return 0.0

	score = (positive_hits - negative_hits) / max(1, positive_hits + negative_hits)
	return max(-1.0, min(1.0, round(score, 3)))


def compute_sentiment_scores(top_news: list[dict] | None) -> dict:
	items = top_news or []
	scores = []
	normalized_news = []

	for item in items:
		headline = item.get("headline") or item.get("title") or ""
		score = _headline_score(headline)
		scores.append(score)
		normalized_news.append(
			{
				"headline": headline,
				"sentiment": score,
				"source": item.get("source") or item.get("publisher") or "unknown",
			}
		)

	avg = round(sum(scores) / len(scores), 3) if scores else 0.0
	return {
		"news_sentiment": avg,
		"social_sentiment": None,
		"analyst_sentiment": None,
		"top_news": normalized_news,
		"data_quality": "good" if normalized_news else "missing-news",
	}


__all__ = ["compute_sentiment_scores"]
