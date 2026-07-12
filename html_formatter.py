def format_html_report(master: dict) -> str:
    technical = master.get("technical") or {}
    trend = master.get("trend") or {}
    ai_report = master.get("ai_report") or {}
    sentiment = master.get("sentiment") or {}

    # Legacy flat payload compatibility for existing local webhook tests/flows.
    if not technical and any(k in master for k in ("trend_score", "ai_summary", "supports")):
        supports = ", ".join(str(item) for item in master.get("supports", []))
        resistances = ", ".join(str(item) for item in master.get("resistances", []))
        alerts = "<br>".join(str(item) for item in master.get("alerts", []))
        return f"""
        <h2>AIStockAgent Daily Report</h2>
        <b>Symbol:</b> {master.get('symbol')}<br>
        <b>Trend Score:</b> {master.get('trend_score')}<br>
        <b>Trend Direction:</b> {master.get('trend_direction')}<br>
        <b>Delivery %:</b> {master.get('delivery_pct')}<br>
        <b>VWAP:</b> {master.get('vwap')}<br>
        <b>Breakout:</b> {master.get('breakout')}<br><br>

        <b>Supports:</b> {supports}<br>
        <b>Resistances:</b> {resistances}<br><br>

        <b>AI Summary:</b><br>{master.get('ai_summary')}<br><br>
        <b>AI Recommendations:</b><br>{master.get('ai_recommendations')}<br><br>
        <b>Sentiment:</b> {master.get('sentiment')}<br><br>

        <b>Alerts:</b><br>{alerts}
        """

    supports = ", ".join(str(item) for item in ((master.get("market_data") or {}).get("supports", [])))
    resistances = ", ".join(str(item) for item in ((master.get("market_data") or {}).get("resistances", [])))

    return f"""
    <h2>AI Stock Agent Report</h2>
    <b>Symbol:</b> {master.get('symbol')}<br>
    <b>Timeframe:</b> {master.get('timeframe')}<br>
    <b>Trend Score:</b> {trend.get('trend_score')}<br>
    <b>Trend Direction:</b> {trend.get('short_term')}<br>
    <b>RSI:</b> {technical.get('rsi')}<br>
    <b>VWAP:</b> {technical.get('vwap')}<br>
    <b>News Sentiment:</b> {sentiment.get('news_sentiment')}<br><br>

    <b>Supports:</b> {supports}<br>
    <b>Resistances:</b> {resistances}<br><br>

    <b>AI Summary:</b><br>{ai_report.get('summary')}<br><br>
    <b>Recommendation:</b><br>{ai_report.get('recommendation')}<br><br>
    <b>Probability:</b> {ai_report.get('probability')}<br>
    """


def generate_html_report(d: dict) -> str:
    """Backward-compatible entry point used by existing local webhook flows."""
    return format_html_report(d)
