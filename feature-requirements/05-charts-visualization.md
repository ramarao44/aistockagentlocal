# Feature: Charts & Visualization

## User Story
- **As a** stock analyst
- **I want** to visualize stock data with interactive charts
- **So that** I can better understand price trends and technical indicators

## Sub-Requirements

### 5.1 Price Trend Chart
- **As a** user
- **I want** to see price history chart
- **So that** I can identify trends
- **Acceptance Criteria:**
  - [ ] Display 6-month price history
  - [ ] Show moving averages (MA20, MA50)
  - [ ] Interactive zoom/pan in Chainlit
  - [ ] Export to PNG option
- **Status:** Not Started

### 5.2 RSI Chart
- **As a** trader
- **I want** to see RSI indicator chart
- **So that** I can identify overbought/oversold conditions
- **Acceptance Criteria:**
  - [ ] Display RSI values (0-100)
  - [ ] Highlight overbought (>70) in red
  - [ ] Highlight oversold (<30) in green
  - [ ] Show 14-day period
- **Status:** Not Started

### 5.3 MACD Chart
- **As a** technical analyst
- **I want** to see MACD histogram
- **So that** I can identify momentum changes
- **Acceptance Criteria:**
  - [ ] Display MACD line, signal line, histogram
  - [ ] Color coding for positive/negative histogram
  - [ ] Zero line reference
  - [ ] Clear buy/sell signals
- **Status:** Not Started

### 5.4 Bollinger Bands Chart
- **As a** volatility trader
- **I want** to see Bollinger Bands
- **So that** I can identify volatility and price levels
- **Acceptance Criteria:**
  - [ ] Display upper, middle, lower bands
  - [ ] Show price within bands
  - [ ] Highlight price touching bands
- **Status:** Not Started

### 5.5 Volume Breakout Visualization
- **As a** momentum trader
- **I want** to see volume breakout indicators
- **So that** I can identify unusual trading activity
- **Acceptance Criteria:**
  - [ ] Display volume bars
  - [ ] Highlight breakout days (2x average)
  - [ ] Show volume trend
- **Status:** Not Started

## Implementation Details

### Functions to Create/Modify
- `src/charts/chart_generator.py` - Main chart generation module
  - `generate_price_chart(df, ticker)` - Generate price trend chart with MAs
  - `generate_rsi_chart(df, ticker)` - Generate RSI indicator chart
  - `generate_macd_chart(df, ticker)` - Generate MACD histogram chart
  - `generate_bb_chart(df, ticker)` - Generate Bollinger Bands chart
  - `generate_volume_chart(df, ticker)` - Generate volume breakout chart

### Code Structure
```
src/
├── charts/
│   ├── __init__.py
│   └── chart_generator.py
```

### API Integration
- Chainlit: `cl.image(path="chart.png")` or `cl.plotly_chart(chart)`
- Return format: PIL Image or file path

### Data Flow
1. Fetch data from `src/fetcher/market_fetcher.py`
2. Process with `src/analysis/trend_score.py`
3. Generate chart with matplotlib/plotly
4. Display in Chainlit UI
5. Save to `data/charts/` for caching

### Example Code Pattern
```python
def generate_price_chart(df: pd.DataFrame, ticker: str) -> str:
    """
    Generate price trend chart with moving averages.
    
    Args:
        df: DataFrame with Open, High, Low, Close, Volume columns
        ticker: Stock ticker symbol (e.g., "RELIANCE.NS")
        
    Returns:
        Path to generated chart image (e.g., "data/charts/RELIANCE_NS_price.png")
    """
    import matplotlib.pyplot as plt
    
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot(df.index, df['Close'], label='Price', color='blue')
    ax.plot(df.index, df['MA20'], label='MA20', color='orange')
    ax.plot(df.index, df['MA50'], label='MA50', color='red')
    ax.set_title(f'{ticker} Price Trend')
    ax.legend()
    
    chart_path = f"data/charts/{ticker.replace('.', '_')}_price.png"
    plt.savefig(chart_path)
    plt.close()
    
    return chart_path
```

## Definition of Done
- [ ] All sub-requirements implemented
- [ ] Test cases for each sub-feature created
- [ ] All tests pass (positive, negative, edge cases)
- [ ] User has reviewed and approved the changes
- [ ] Documentation updated in `docs/DESIGN_DEVELOPMENT_DOCUMENT.md`
- [ ] Test report generated
- [ ] Changes pushed to repository

## Technical Notes
- Use matplotlib for chart generation
- Integrate with Chainlit using `cl.image` or `cl.plotly_chart`
- Cache chart images to avoid regeneration
- Consider using plotly for interactive charts

## Dependencies
- matplotlib
- plotly (optional)
- pandas
- Chainlit

## Test Cases
- `scripts/test_charts.py` - Main chart tests
- `scripts/test_chart_rsi.py` - RSI chart specific tests
