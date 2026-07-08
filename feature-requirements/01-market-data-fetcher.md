# Feature: Market Data Fetcher

## User Story
- **As a** stock analyst
- **I want** to fetch real-time market data for Indian stocks
- **So that** I can analyze stock performance with accurate data

## Sub-Requirements

### 1.1 Ticker Normalization
- **As a** user
- **I want** to input stock symbols in various formats
- **So that** the system can handle NSE and BSE tickers
- **Acceptance Criteria:**
  - [x] Convert "RELIANCE" to "RELIANCE.NS" and "RELIANCE.BO"
  - [x] Convert "TCS.NS" to "TCS.NS" and "TCS.BO"
  - [x] Convert "INFY.BO" to "INFY.NS" and "INFY.BO"
- **Status:** Complete

### 1.2 Price History Fetching
- **As a** user
- **I want** to get historical OHLCV data
- **So that** I can analyze price trends
- **Acceptance Criteria:**
  - [x] Fetch 6-month daily data
  - [x] Handle MultiIndex column normalization
  - [x] Return clean DataFrame with Open, High, Low, Close, Volume
  - [x] Graceful error handling for invalid tickers
- **Status:** Complete

### 1.3 Intraday Data
- **As a** trader
- **I want** to get intraday 5-minute data
- **So that** I can calculate VWAP
- **Acceptance Criteria:**
  - [x] Fetch 1-day intraday data
  - [x] Return clean DataFrame
  - [x] Used for VWAP calculation
- **Status:** Complete

## Implementation Details

### Functions to Create/Modify
- `src/fetcher/market_fetcher.py` - Main market data fetcher
  - `normalize_ticker(user_input: str)` - Convert to NSE/BSE format
  - `fetch_price_history(ticker: str, period: str, interval: str)` - Get OHLCV data
  - `fetch_indian_stock_data(user_input: str)` - Combined fetcher
  - `fetch_nse_delivery_data(symbol: str)` - Get delivery percentage
  - `fetch_moneycontrol_delivery(symbol: str)` - Scrape Moneycontrol

### Code Structure
```
src/
├── fetcher/
│   └── market_fetcher.py
```

### API Integration
- Yahoo Finance: `yf.download()` for price data
- Moneycontrol: Web scraping for delivery data
- NSE India: API for delivery percentage

### Data Flow
1. User inputs stock symbol
2. `normalize_ticker()` converts to NSE/BSE format
3. `fetch_price_history()` gets daily data
4. `fetch_indian_stock_data()` combines all data
5. Data stored in database

### Example Code Pattern
```python
def fetch_indian_stock_data(user_input: str) -> dict:
    """
    Fetch complete market data for Indian stocks.
    
    Args:
        user_input: Stock symbol (e.g., "RELIANCE", "TCS.NS")
        
    Returns:
        dict with success status, ticker, price, indicators
    """
    tickers = normalize_ticker(user_input)
    df = fetch_price_history(tickers["nse"])
    # ... compute indicators ...
    return {
        "success": True,
        "ticker": tickers["nse"],
        "current_price": price,
        "rsi": rsi,
        # ... more fields ...
    }
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
- Uses yfinance library for Yahoo Finance data
- Handles MultiIndex columns from yfinance
- Moneycontrol scraping for delivery volume
- NSE API for alternative delivery data

## Dependencies
- yfinance
- pandas
- requests
- beautifulsoup4
- cloudscraper (optional)

## Test Cases
- `scripts/test_market_fetcher.py` - Main fetcher tests
- `scripts/test_mvp.py` - Integration tests
- `scripts/test_vwap.py` - VWAP calculation tests
- `scripts/test_delivery.py` - Delivery data tests