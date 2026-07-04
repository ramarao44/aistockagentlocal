from typing import List, Dict, Any


def evaluate_alerts(data: Dict[str, Any], trend_score: float, evolution: Dict[str, Any]) -> List[str]:
    alerts = []

    price = data.get("current_price")
    vwap = data.get("vwap")
    delivery_pct = data.get("delivery_volume_pct")
    breakout = data.get("volume_breakout")
    supports = data.get("supports") or []
    resistances = data.get("resistances") or []
    volatility = data.get("volatility")

    # 1. Trend Score Threshold Alerts
    if trend_score is not None:
        if trend_score >= 70:
            alerts.append(f"Strong bullish trend detected (Trend Score: {trend_score:.1f})")
        if trend_score <= 30:
            alerts.append(f"Strong bearish trend detected (Trend Score: {trend_score:.1f})")

    # 2. Trend Score Evolution Alerts
    if evolution.get("short_term_direction") == "insufficient-data":
        alerts.append("Insufficient trend history for evolution analysis")

    short_change = evolution.get("short_term_change", 0)
    if short_change >= 10:
        alerts.append(f"Momentum shift detected: Trend Score up {short_change:.1f} points")
    elif short_change <= -10:
        alerts.append(f"Reversal risk detected: Trend Score down {abs(short_change):.1f} points")

    # 3. Breakout Alerts
    if breakout:
        alerts.append("Volume breakout detected")

    if price is not None and resistances:
        nearest_resistance = min(resistances, key=lambda r: abs(price - r))
        if nearest_resistance - price <= max(1.0, price * 0.01):
            alerts.append(f"Price near resistance ({nearest_resistance:.2f})")
    if price is not None and supports:
        nearest_support = min(supports, key=lambda s: abs(price - s))
        if price - nearest_support <= max(1.0, price * 0.01):
            alerts.append(f"Price near support ({nearest_support:.2f})")

    # 4. VWAP Alerts
    if price is not None and vwap is not None:
        if price > vwap:
            alerts.append("Price is above VWAP (bullish)"
                         if price - vwap > 0 else "Price at VWAP")
        else:
            alerts.append("Price is below VWAP (bearish)"
                         if vwap - price > 0 else "Price at VWAP")

    # 5. Delivery Spike Alerts
    if delivery_pct is not None:
        if delivery_pct >= 50:
            alerts.append(f"High delivery volume detected ({delivery_pct:.2f}%)")

    delivery_trend_pct = data.get("delivery_trend_pct")
    if delivery_trend_pct is not None:
        if delivery_trend_pct >= 3:
            alerts.append(f"Delivery trend is rising ({delivery_trend_pct:.2f}%)")

    # 6. Volatility Alerts
    if volatility is not None:
        if volatility >= 0.03:
            alerts.append(f"Volatility spike detected ({volatility:.2%})")
        elif volatility < 0.01:
            alerts.append(f"Volatility collapse detected ({volatility:.2%})")

    return alerts
