from src.core.debug import dbg


def analyze_trend_evolution(series, master: dict | None = None):
    """
    series = [{"trend_score": 78, "timestamp": ...}, ...]
    Returns a human-readable evolution summary.
    """
    if not series or len(series) < 2:
        dbg(master, "ANALYSIS.TREND", "EVOLVE", "WARN", "Insufficient trend history")
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

    dbg(master, "ANALYSIS.TREND", "EVOLVE", "OK", "Trend evolution computed")
    return {
        "latest_score": latest,
        "short_term_change": change,
        "short_term_direction": direction,
        "long_term_change": long_term_change,
        "long_term_direction": long_term_direction,
    }


def compute_trend(candles: list[dict], technical: dict, master: dict | None = None) -> dict:
    dbg(master, "ANALYSIS.TREND", "COMPUTE", "OK", "Computing trend contract")
    closes = [c.get("close") for c in (candles or []) if c.get("close") is not None]
    if len(closes) < 2:
        dbg(master, "ANALYSIS.TREND", "COMPUTE", "WARN", "Insufficient candles for trend")
        return {
            "short_term": "unknown",
            "medium_term": "unknown",
            "long_term": "unknown",
            "trend_score": None,
            "volatility": None,
            "data_quality": "insufficient-candles",
        }

    latest = closes[-1]
    prev = closes[-2]
    first = closes[0]

    ma50 = ((technical or {}).get("ma") or {}).get("ma50")
    ma200 = ((technical or {}).get("ma") or {}).get("ma200")

    short_term = "bullish" if latest > prev else "bearish" if latest < prev else "sideways"
    medium_term = "bullish" if latest > first else "bearish" if latest < first else "sideways"

    if ma50 is not None and ma200 is not None:
        long_term = "bullish" if ma50 >= ma200 else "bearish"
    else:
        long_term = medium_term

    pct_changes = []
    for i in range(1, len(closes)):
        if closes[i - 1] not in (None, 0):
            pct_changes.append((closes[i] - closes[i - 1]) / closes[i - 1])

    volatility = round(sum(abs(x) for x in pct_changes) / len(pct_changes), 4) if pct_changes else 0.0
    score = 50.0
    score += 20 if short_term == "bullish" else -20 if short_term == "bearish" else 0
    score += 15 if medium_term == "bullish" else -15 if medium_term == "bearish" else 0
    score += 10 if long_term == "bullish" else -10 if long_term == "bearish" else 0
    score = max(0.0, min(100.0, round(score, 2)))

    dbg(master, "ANALYSIS.TREND", "COMPUTE", "OK", "Trend contract computed")
    return {
        "short_term": short_term,
        "medium_term": medium_term,
        "long_term": long_term,
        "trend_score": score,
        "volatility": volatility,
        "data_quality": "good",
    }
