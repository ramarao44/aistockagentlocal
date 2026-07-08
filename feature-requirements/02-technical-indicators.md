# Feature: Technical Indicators

## User Story
- **As a** technical analyst
- **I want** to compute technical indicators for stock analysis
- **So that** I can make informed trading decisions

## Sub-Requirements

### 2.1 RSI (Relative Strength Index)
- **As a** trader
- **I want** to see RSI values
- **So that** I can identify overbought/oversold conditions
- **Acceptance Criteria:**
  - [x] Calculate 14-day RSI
  - [x] Return values between 0-100
  - [x] Handle insufficient data gracefully
- **Status:** Complete

### 2.2 MACD (Moving Average Convergence Divergence)
- **As a** momentum trader
- **I want** to see MACD line, signal, and histogram
- **So that** I can identify momentum changes
- **Acceptance Criteria:**
  - [x] Calculate MACD (12, 26, 9)
  - [x] Return MACD line, signal line, histogram
  - [x] Color coding for positive/negative histogram
- **Status:** Complete

### 2.3 Moving Averages
- **As a** trend follower
- **I want** to see MA20 and MA50
- **So that** I can identify trend direction
- **Acceptance Criteria:**
  - [x] Calculate 20-day moving average
  - [x] Calculate 50-day moving average
  - [x] Handle insufficient data (return None)
- **Status:** Complete

### 2.4 SuperTrend
- **As a** trend trader
- **I want** to see SuperTrend indicator
- **So that** I can follow trend direction
- **Acceptance Criteria:**
  - [x] Calculate SuperTrend (10, 3)
  - [x] Return trend direction (UP/DOWN)
  - [x] Return SuperTrend value
- **Status:** Complete

### 2.5 VWAP (Volume Weighted Average Price)
- **As a** intraday trader
- **I want** to see VWAP
- **So that** I can identify fair price
- **Acceptance Criteria:**
  - [x] Calculate VWAP from intraday data
  - [x] Return single VWAP value
  - [x] Handle missing volume data
- **Status:** Complete

### 2.6 ADX (Average Directional Index)
- **As a** trend strength analyst
- **I want** to see ADX values
- **So that** I can identify strong trends
- **Acceptance Criteria:**
  - [x] Calculate 14-day ADX
  - [x] Return +DI and -DI values
  - [x] Values above 25 indicate strong trend
- **Status:** Complete

### 2.7 Bollinger Bands
- **As a** volatility trader
- **I want** to see Bollinger Bands
- **So that** I can identify volatility levels
- **Acceptance Criteria:**
  - [x] Calculate 20-day Bollinger Bands
  - [x] Return upper and lower bands
  - [x] Price near bands indicates volatility
- **Status:** Complete

### 2.8 Volume Breakout
- **As a** momentum trader
- **I want** to identify volume breakouts
- **So that** I can catch unusual activity
- **Acceptance Criteria:**
  - [x] Compare today's volume to 20-day average
  - [x] Return True/False for breakout
  - [x] Breakout = 2x average volume
- **Status:** Complete

## Implementation Details

### Functions to Create/Modify
- `src/fetcher/market_fetcher.py` - All indicator functions
  - `compute_rsi(df, period=14)` - Calculate RSI
  - `compute_macd(df, fast=12, slow=26, signal=9)` - Calculate MACD
  - `compute_moving_average(df, window=50)` - Calculate MA
  - `compute_supertrend(df, period=10, multiplier=3)` - Calculate SuperTrend
  - `calculate_vwap(df)` - Calculate VWAP
  - `compute_adx(df, period=14)` - Calculate ADX
  - `compute_bollinger_bands(df, window=20)` - Calculate BB
  - `detect_volume_breakout(df)` - Detect breakouts

### Code Structure
```
src/
├── fetcher/
│   └── market_fetcher.py
```

### API Integration
- Uses pandas for calculations
- No external API required

### Data Flow
1. Fetch price data
2. Calculate each indicator
3. Return values in dictionary
4. Store in database

### Example Code Pattern
```python
def compute_rsi(df: pd.DataFrame, period: int = 14) -> float:
    """
    Calculate Relative Strength Index.
    
    Args:
        df: DataFrame with Close prices
        period: RSI period (default 14)
        
    Returns:
        Latest RSI value
    """
    delta = df["Close"].diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    
    avg_gain = gain.rolling(period).mean()
    avg_loss = loss.rolling(period).mean()
    avg_loss = avg_loss.replace(0, 1e-10)
    
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    
    return rsi.iloc[-1]
```

## Source Code Flow Chart
```
[DataFrame with OHLCV]
        |
        v
[compute_rsi()] --> [RSI Value]
[compute_macd()] --> [MACD Line, Signal, Histogram]
[compute_moving_average()] --> [MA20, MA50]
[compute_supertrend()] --> [SuperTrend Value, Direction]
[calculate_vwap()] --> [VWAP Value]
[compute_adx()] --> [ADX, +DI, -DI]
[compute_bollinger_bands()] --> [Upper, Middle, Lower]
[detect_volume_breakout()] --> [True/False]
        |
        v
[Return all indicators in dict]
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
- All indicators use pandas for calculations
- Handle NaN values for insufficient data
- Standard parameters: RSI(14), MACD(12,26,9), BB(20)

## Dependencies
- pandas
- numpy

## Test Cases
- `scripts/test_supertrend.py` - SuperTrend tests
- `scripts/test_macd.py` - MACD tests
- `scripts/test_vwap.py` - VWAP tests
- `scripts/test_adx.py` - ADX tests
- `scripts/test_breakout.py` - Volume breakout tests
- `scripts/test_sr.py` - Support/Resistance tests
