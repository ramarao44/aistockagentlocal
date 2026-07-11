def analyze_trend_evolution(series):
    """
    series = [{"trend_score": 78, "timestamp": ...}, ...]
    Returns a human-readable evolution summary.
    """
    if not series or len(series) < 2:
        return {
            "latest_score": None,
            "short_term_change": 0,
            "short_term_direction": "insufficient-data",
            "long_term_change": 0,
            "long_term_direction": "insufficient-data",
        }

    scores = [item["trend_score"] for item in series]

    latest = scores[0]
    previous = scores[1]
    change = latest - previous

    direction = (
        "strengthening" if change > 0
        else "weakening" if change < 0
        else "stable"
    )

    long_term_change = latest - scores[-1]
    long_term_direction = (
        "strong upward trend" if long_term_change > 0
        else "strong downward trend" if long_term_change < 0
        else "flat long-term trend"
    )

    return {
        "latest_score": latest,
        "short_term_change": change,
        "short_term_direction": direction,
        "long_term_change": long_term_change,
        "long_term_direction": long_term_direction,
    }
