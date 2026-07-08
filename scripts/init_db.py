from src.database.engine import Base, engine
from src.database.models import StockDaily, AIReport

if __name__ == "__main__":
    Base.metadata.create_all(bind=engine)
    print("Database initialized.")
