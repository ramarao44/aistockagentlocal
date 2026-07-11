from src.database.engine import Base, engine
from src.ingestion.market_fetcher import fetch_indian_stock_data

# Create tables
Base.metadata.create_all(bind=engine)

# Fetch and save
result = fetch_indian_stock_data("RELIANCE.NS")
print("Saved current price:", result.get("current_price"))
print("Database record saved for:", result.get("ticker"))
