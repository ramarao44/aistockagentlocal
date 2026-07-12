"""Default model weights for timeframe scoring."""

MODEL_WEIGHTS = {
    "intraday": {"technical": 0.75, "fundamental": 0.1, "sentiment": 0.15},
    "daily": {"technical": 0.6, "fundamental": 0.25, "sentiment": 0.15},
    "weekly": {"technical": 0.55, "fundamental": 0.3, "sentiment": 0.15},
    "monthly": {"technical": 0.45, "fundamental": 0.4, "sentiment": 0.15},
    "quarterly": {"technical": 0.35, "fundamental": 0.5, "sentiment": 0.15},
    "yearly": {"technical": 0.3, "fundamental": 0.55, "sentiment": 0.15},
}

RISK_ADJUSTMENTS = {
    "low": {"technical": -0.05, "fundamental": 0.05, "sentiment": 0.0},
    "medium": {"technical": 0.0, "fundamental": 0.0, "sentiment": 0.0},
    "high": {"technical": 0.05, "fundamental": -0.05, "sentiment": 0.0},
}


def get_model_weights(timeframe: str, risk_profile: str | None = None) -> dict:
    key = (timeframe or "daily").strip().lower()
    risk_key = (risk_profile or "medium").strip().lower()

    base = MODEL_WEIGHTS.get(key, MODEL_WEIGHTS["daily"]).copy()
    adjustment = RISK_ADJUSTMENTS.get(risk_key, RISK_ADJUSTMENTS["medium"])

    for k in ("technical", "fundamental", "sentiment"):
        base[k] = max(0.0, base[k] + adjustment[k])

    total = base["technical"] + base["fundamental"] + base["sentiment"]
    if total <= 0:
        return MODEL_WEIGHTS["daily"].copy()

    return {k: round(v / total, 4) for k, v in base.items()}
