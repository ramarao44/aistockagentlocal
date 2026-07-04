import pandas as pd


def compute_trend_score(data: dict) -> float:
    """Compute Trend Score 2.0 using weighted, multi-factor market signals."""
    score = 0.0

    # 1. Delivery Strength (0-30)
    delivery_pct = data.get("delivery_volume_pct")
    delivery_trend = data.get("delivery_trend_pct")
    if delivery_pct is not None:
        if delivery_pct >= 50:
            score += 30
        elif delivery_pct >= 40:
            score += 20
        elif delivery_pct >= 30:
            score += 10

    if delivery_trend is not None:
        if delivery_trend >= 5:
            score += 10
        elif delivery_trend >= 0:
            score += 5

    # 2. VWAP Position (0-20)
    current_price = data.get("current_price")
    vwap = data.get("vwap")
    if current_price is not None and vwap is not None:
        if current_price > vwap:
            score += 20
        else:
            score += 5

    # 3. Volume Breakout Strength (0-20)
    if data.get("volume_breakout"):
        score += 20

    # 4. Support/Resistance Proximity (0-15)
    supports = data.get("supports") or []
    resistances = data.get("resistances") or []
    if current_price is not None:
        nearest_support = None
        nearest_resistance = None
        if supports:
            nearest_support = min(supports, key=lambda s: abs(current_price - s))
        if resistances:
            nearest_resistance = min(resistances, key=lambda r: abs(current_price - r))

        if nearest_support is not None and current_price >= nearest_support:
            if current_price - nearest_support <= current_price * 0.015:
                score += 15
            elif current_price - nearest_support <= current_price * 0.03:
                score += 10

        if nearest_resistance is not None and nearest_resistance >= current_price:
            if nearest_resistance - current_price <= current_price * 0.015:
                score -= 10
            elif nearest_resistance - current_price <= current_price * 0.03:
                score -= 5

    # 5. Pivot Point Position (0-10)
    pivot_points = data.get("pivot_points") or {}
    pivot = pivot_points.get("pivot")
    if current_price is not None and pivot is not None:
        if current_price > pivot:
            score += 10
        else:
            score += 3

    # 6. Volatility Stability (0-5)
    df = data.get("df")
    volatility_score = 0
    if isinstance(df, pd.DataFrame) and "Close" in df.columns:
        close_pct = df["Close"].pct_change().dropna()
        if not close_pct.empty:
            volatility = close_pct.std()
            if volatility < 0.01:
                volatility_score = 5
            elif volatility < 0.02:
                volatility_score = 3
            else:
                volatility_score = 1
    score += volatility_score

    return float(max(0, min(100, round(score, 2))))
