UI_CONTRACT_V1 = {
    "version": "1.0",

    # Required user inputs
    "symbol": None,            # "HAL.NS"
    "exchange": None,          # "NSE" or "BSE"
    "timeframe": None,         # "daily", "weekly", "monthly", "quarterly", "yearly"

    # Optional analysis types
    "analysis_types": [
        # "technical", "fundamental", "sentiment", "trend", "ai"
    ],

    # Optional advanced settings
    "include_news": False,
    "include_sentiment": False,
    "include_fundamentals": True,
    "include_technical": True,

    # Optional user preferences
    "risk_profile": None,      # "low", "medium", "high"
    "output_format": "json",   # "json", "html", "email"

    # Optional debug flags
    "debug": False,

    # Data quality flag
    "data_quality": "unknown"
}
