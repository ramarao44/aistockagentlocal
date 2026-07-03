import sys
import os

# Add project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


from src.db.database import (
    load_market_data,
    load_indicators,
    load_latest_market_data,
    load_latest_indicators
)

ticker = "AAPL"

print("Full Market Data:")
print(load_market_data(ticker).tail())

print("\nFull Indicators:")
print(load_indicators(ticker).tail())

print("\nLatest Market Row:")
print(load_latest_market_data(ticker))

print("\nLatest Indicator Row:")
print(load_latest_indicators(ticker))
