from src.ai.llm_reasoner import generate_llm_report


def generate_ai_report(data: dict, trend_score: float):
    """Generate an AI report summary, recommendations, and sentiment."""
    # Use a lightweight prompt-driven summary for now.
    # This can be replaced by a more advanced LLM prompt later.
    summary = (
        f"{data['ticker']} is trading at ₹{data['current_price']:.2f} on {data['last_updated']}. "
        f"The stock has a trend score of {trend_score:.1f}. "
        f"VWAP is ₹{data['vwap']:.2f} and the current price is {'above' if data['current_price'] > data['vwap'] else 'below'} VWAP. "
        f"Delivery volume is {data['delivery_volume_pct'] or 0:.1f}% and volume breakout is {'present' if data['volume_breakout'] else 'absent'}."
    )

    recommendations = []
    if data['volume_breakout']:
        recommendations.append("Watch for continued strength above the breakout level.")
    else:
        recommendations.append("Wait for a clear volume breakout before adding new exposure.")

    if data['current_price'] > data['vwap']:
        recommendations.append("Maintain a bullish stance while price stays above VWAP.")
    else:
        recommendations.append("Be cautious while price remains below VWAP.")

    if (data['delivery_volume_pct'] or 0) >= 40:
        recommendations.append("Delivery strength is healthy, supporting accumulation.")
    else:
        recommendations.append("Monitor delivery volume for signs of weakening participation.")

    recommendation_text = " ".join(recommendations)

    sentiment = "neutral"
    if trend_score >= 70:
        sentiment = "bullish"
    elif trend_score <= 40:
        sentiment = "bearish"

    return summary, recommendation_text, sentiment
