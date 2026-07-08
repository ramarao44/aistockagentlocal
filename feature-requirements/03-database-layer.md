# Feature: Database Layer

## User Story
- **As a** system
- **I want** to store and retrieve market data
- **So that** I can maintain historical records and enable analysis

## Sub-Requirements

### 3.1 SQLite Database Setup
- **As a** developer
- **I want** a local SQLite database
- **So that** I can store data without external dependencies
- **Acceptance Criteria:**
  - [x] Create SQLite database in `data/` directory
  - [x] Use SQLAlchemy for ORM
  - [x] Create tables for market data and indicators
- **Status:** Complete

### 3.2 Market Data Storage
- **As a** system
- **I want** to save daily OHLCV data
- **So that** I can track historical prices
- **Acceptance Criteria:**
  - [x] Save open, high, low, close, volume
  - [x] Store ticker and date
  - [x] Handle duplicate entries (UPSERT)
- **Status:** Complete

### 3.3 Indicator Storage
- **As a** system
- **I want** to save technical indicators
- **So that** I can track indicator history
- **Acceptance Criteria:**
  - [x] Save RSI, MACD, MA20, MA50
  - [x] Store with ticker and date
  - [x] Handle missing values
- **Status:** Complete

### 3.4 News and Sentiment Storage
- **As a** system
- **I want** to save news and sentiment
- **So that** I can analyze market sentiment
- **Acceptance Criteria:**
  - [x] Save news headlines
  - [x] Save sentiment scores
  - [x] Link to ticker
- **Status:** Complete

### 3.5 Data Retrieval
- **As a** user
- **I want** to load historical data
- **So that** I can analyze trends
- **Acceptance Criteria:**
  - [x] Load market data by ticker
  - [x] Load latest data
  - [x] Load indicator history
- **Status:** Complete

## Implementation Details

### Functions to Create/Modify
- `src/database/engine.py` - Database configuration
  - `DATABASE_URL` - SQLite connection string
  - `engine` - SQLAlchemy engine
  - `SessionLocal` - Database session
  - `Base` - Declarative base

- `src/database/models.py` - SQLAlchemy models
  - `DailyRecord` - Main data model
  - `News` - News model
  - `Sentiment` - Sentiment model

- `src/db/database.py` - SQLite operations
  - `save_market_data(df, ticker)` - Save OHLCV
  - `save_indicators(df, ticker)` - Save indicators
  - `load_market_data(ticker)` - Load data
  - `load_latest_market_data(ticker)` - Load latest
  - `save_news(news_items)` - Save news
  - `save_sentiment(ticker, title, sentiment)` - Save sentiment

### Code Structure
```
src/
├── database/
│   ├── engine.py
│   └── models.py
└── db/
    └── database.py
```

### API Integration
- SQLAlchemy ORM
- SQLite connection

### Data Flow
1. Fetch market data
2. Create database session
3. Save data to tables
4. Query data for analysis
5. Close session

### Example Code Pattern
```python
def save_market_data(df: pd.DataFrame, ticker: str):
    """
    Save market data to SQLite database.
    
    Args:
        df: DataFrame with OHLCV data
        ticker: Stock ticker symbol
    """
    df = df.copy()
    df["ticker"] = ticker
    df.reset_index(inplace=True)
    
    records = []
    for _, row in df.iterrows():
        records.append((
            row["ticker"],
            row["Date"].strftime("%Y-%m-%d"),
            row["Open"],
            row["High"],
            row["Low"],
            row["Close"],
            int(row["Volume"]),
        ))
    
    with get_connection() as conn:
        conn.executemany(
            "INSERT OR REPLACE INTO market_data VALUES (?, ?, ?, ?, ?, ?, ?)",
            records
        )
        conn.commit()
```

## Source Code Flow Chart
```
[DataFrame with OHLCV]
        |
        v
[save_market_data()] --> [INSERT OR REPLACE]
[save_indicators()] --> [INSERT OR REPLACE]
[save_news()] --> [INSERT OR REPLACE]
[save_sentiment()] --> [INSERT OR REPLACE]
        |
        v
[SQLite Database: data/market.db]
        |
        v
[load_market_data()] <-- [SELECT]
[load_indicators()] <-- [SELECT]
[load_news()] <-- [SELECT]
[load_sentiment()] <-- [SELECT]
        |
        v
[Return DataFrames]
```

## Definition of Done
- [x] All sub-requirements implemented
- [x] Test cases for each sub-feature created
- [x] All tests pass (positive, negative, edge cases)
- [x] User has reviewed and approved the changes
- [x] Documentation updated in `docs/DESIGN_DEVELOPMENT_DOCUMENT.md`
- [x] Test report generated
- [x] Changes pushed to repository

## Technical Notes
- SQLite for local-first approach
- UPSERT for duplicate handling
- Separate modules for SQLAlchemy and raw SQLite

## Dependencies
- sqlalchemy
- sqlite3
- pandas

## Test Cases
- `scripts/test_db.py` - Database tests
- `scripts/test_db_load.py` - Data loading tests
