from src.database.crud import get_trend_score_series
from src.analysis.trend_evolution import analyze_trend_evolution

series = get_trend_score_series("RELIANCE.NS", n=10)
result = analyze_trend_evolution(series)

print(result)
