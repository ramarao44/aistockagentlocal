from src.database.engine import Base, engine
from src.database.crud import save_ai_report

Base.metadata.create_all(bind=engine)

report = save_ai_report(
    symbol="RELIANCE.NS",
    trend_score=78.5,
    sentiment="bullish",
    summary="Price is above VWAP with strong delivery volume and moderate breakout characteristics.",
    recommendations="Monitor for continuation above recent resistance; avoid leverage; reassess if delivery drops below 40%.",
)

print("Saved AI report ID:", report.id)
