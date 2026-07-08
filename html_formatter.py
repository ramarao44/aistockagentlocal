def generate_html_report(d: dict) -> str:
    supports = ", ".join(str(item) for item in d.get("supports", []))
    resistances = ", ".join(str(item) for item in d.get("resistances", []))
    pivots = ", ".join(str(item) for item in d.get("pivot_points", []))
    alerts = "<br>".join(str(item) for item in d.get("alerts", []))

    return f"""
    <h2>AIStockAgent Daily Report</h2>
    <b>Symbol:</b> {d.get('symbol')}<br>
    <b>Trend Score:</b> {d.get('trend_score')}<br>
    <b>Trend Direction:</b> {d.get('trend_direction')}<br>
    <b>Delivery %:</b> {d.get('delivery_pct')}<br>
    <b>VWAP:</b> {d.get('vwap')}<br>
    <b>Breakout:</b> {d.get('breakout')}<br><br>

    <b>Supports:</b> {supports}<br>
    <b>Resistances:</b> {resistances}<br>
    <b>Pivot Points:</b> {pivots}<br><br>

    <b>AI Summary:</b><br>{d.get('ai_summary')}<br><br>
    <b>AI Recommendations:</b><br>{d.get('ai_recommendations')}<br><br>
    <b>Sentiment:</b> {d.get('sentiment')}<br><br>

    <b>Alerts:</b><br>{alerts}
    """
