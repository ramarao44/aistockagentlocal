# AI Stock Agent - Design & Development Document
**Version:** 1.0
**Last Updated:** 2026-07-08
**Status:** Living Document

---

## 📋 Table of Contents
1. [Project Overview](#project-overview)
2. [Architecture](#architecture)
3. [Source Code Structure](#source-code-structure)
4. [Function Specifications](#function-specifications)
5. [Data Models](#data-models)
6. [API Endpoints](#api-endpoints)
7. [Configuration](#configuration)
8. [Testing](#testing)
9. [Deployment](#deployment)
10. [Future Enhancements](#future-enhancements)

---

## 📝 Change Log
- 2026-07-08: Added pre-push validation checklist to AI_INSTRUCTIONS.md and standardized change log format for consistency - ensures traceability and continuity across AI sessions. Organized test reports in dedicated reports/ folder for better project organization.
- 2026-07-07: Added defensive handling for empty/partial market data in the fetcher, made cloud LLM imports fail gracefully, and added an environment-based configuration example for local setup.

## 🎯 Project Overview

### Purpose
A **local-first, privacy-preserving AI agent** for stock market analysis focused on **Indian stock markets (NSE/BSE)**. Combines deterministic Python modules with local LLMs to generate technical analysis reports.

### Key Features
- Real-time market data fetching via yfinance
- 10+ technical indicators computation
- Local LLM reasoning (Ollama) with cloud fallback
- SQLite database for data persistence
- Chainlit UI for interactive analysis
- Email delivery of reports
- Scheduled daily analysis

---

## 🏗️ Architecture

### High-Level Flow
```
┌─────────────┐     ┌──────────────┐     ┌─────────────────┐
│   User UI   │────▶│ LLM Reasoner │────▶│ Market Fetcher  │
│(Chainlit)   │     │              │     │                 │
└─────────────┘     └──────────────┘     └─────────────────┘
                                           │        │
                                           ▼        ▼
                                ┌─────────────────┐  ┌──────────────┐
                                │ Technical       │  │ News         │
                                │ Analyzer        │  │ Fetcher      │
                                └─────────────────┘  └──────────────┘
                                           │        │
                                           ▼        ▼
                                ┌───────────────────────────┐
                                │       Database            │
                                │  (SQLite + SQLAlchemy)    │
                                └───────────────────────────┘
                                           │
                                           ▼
                                ┌───────────────────────────┐
                                │     Report Output         │
                                │  (HTML/Email/Webhook)     │
                                └───────────────────────────┘
```

### Component Diagram
```
aistockagentlocal/
├── UI Layer: app.py (Chainlit)
├── API Layer: local_server.py (FastAPI)
├── Core Layer:
│   ├── src/reasoning/llm_reasoner.py
│   ├── src/fetcher/market_fetcher.py
│   ├── src/analyzer/technical_analyzer.py
│   └── src/analysis/trend_score.py
├── Data Layer:
│   ├── src/database/ (SQLAlchemy)
│   └── src/db/database.py (SQLite)
└── Utilities:
    ├── email_sender.py
    ├── html_formatter.py
    └── scheduler.py
```

---

## 📁 Source Code Structure

### Root Files
| File | Purpose |
|------|---------|
| `app.py` | Chainlit UI entrypoint - handles user input and displays reports |
| `local_server.py` | FastAPI webhook server for receiving reports |
| `scheduler.py` | APScheduler for daily automated jobs |
| `email_sender.py` | Gmail SMTP integration for report delivery |
| `html_formatter.py` | HTML report generation for email/webhook |
| `requirements.txt` | Python dependencies |
| `.env` | Environment configuration (Gmail, N8N webhook) |

### Source Modules (`src/`)

#### `src/reasoning/llm_reasoner.py`
Main LLM integration module. Handles:
- Local LLM calls via Ollama
- Cloud LLM calls via OpenAI
- Report generation with real market data

#### `src/reasoning/reasoning_node.py`
Report generation utilities:
- `generate_daily_summary()` - Creates daily summary from DB
- `generate_trend_analysis()` - Multi-day trend analysis
- `generate_combined_report()` - Combined daily + trend report

#### `src/fetcher/market_fetcher.py`
Core market data fetching:
- `normalize_ticker()` - Converts user input to NSE/BSE format
- `fetch_price_history()` - yfinance integration
- `compute_rsi()` - Relative Strength Index
- `compute_moving_average()` - SMA calculation
- `compute_bollinger_bands()` - Bollinger Bands
- `compute_supertrend()` - SuperTrend indicator
- `compute_macd()` - MACD calculation
- `compute_adx()` - Average Directional Index
- `calculate_vwap()` - Volume Weighted Average Price
- `detect_volume_breakout()` - Volume spike detection
- `find_support_resistance()` - Support/Resistance levels
- `calculate_pivot_points()` - Pivot point calculation
- `fetch_indian_stock_data()` - Main wrapper for Indian stocks

#### `src/fetcher/news_fetcher.py`
News fetching via Yahoo Finance RSS:
- `fetch_news()` - RSS feed parsing

#### `src/analyzer/technical_analyzer.py`
Technical indicator computation using `ta` library:
- `compute_indicators()` - RSI, MACD, MA20, MA50

#### `src/analyzer/sentiment_analyzer.py`
Sentiment analysis using VADER:
- `compute_sentiment()` - Returns compound sentiment score

#### `src/analysis/trend_score.py`
Trend Score 2.0 algorithm:
- `compute_trend_score()` - Weighted scoring (0-100)

#### `src/database/`
SQLAlchemy database layer:
- `engine.py` - Database connection setup
- `models.py` - SQLAlchemy models
- `crud.py` - Create/Read/Update/Delete operations

#### `src/db/database.py`
SQLite database operations:
- `save_market_data()` - Store OHLCV data
- `save_indicators()` - Store technical indicators
- `load_market_data()` - Retrieve OHLCV data
- `load_indicators()` - Retrieve indicators
- `save_news()` - Store news articles
- `save_sentiment()` - Store sentiment scores
- `load_news()` - Retrieve news
- `load_sentiment()` - Retrieve sentiment

#### `src/logger.py`
Logging utilities:
- `get_logger()` - Configured logger with file rotation

---

## 🔧 Function Specifications

### Core Functions

#### `fetch_indian_stock_data(user_input: str) -> dict`
**Location:** `src/fetcher/market_fetcher.py`
**Purpose:** Main entry point for fetching Indian stock data
**Parameters:**
- `user_input` - Stock ticker (e.g., "RELIANCE", "TCS.NS", "INFY.BO")
**Returns:**
```python
{
    "success": bool,
    "ticker": str,           # Normalized ticker
    "exchange": str,         # "NSE" or "BSE"
    "current_price": float,
    "rsi": float,
    "ma50": float,
    "ma200": float,
    "bollinger_upper": float,
    "bollinger_lower": float,
    "supertrend": float,
    "supertrend_direction": str,  # "UP" or "DOWN"
    "macd_line": float,
    "macd_signal": float,
    "macd_histogram": float,
    "adx": float,
    "plus_di": float,
    "minus_di": float,
    "delivery_volume_pct": float,
    "vwap": float,
    "volume_breakout": bool,
    "supports": list[float],
    "resistances": list[float],
    "pivot_points": dict,
    "trend_score": float,
    "last_updated": str,       # YYYY-MM-DD
}
```

#### `generate_llm_report(ticker: str, mode: str = "local") -> str`
**Location:** `src/reasoning/llm_reasoner.py`
**Purpose:** Generate AI-powered stock analysis report
**Parameters:**
- `ticker` - Stock symbol
- `mode` - "local" (Ollama) or "cloud" (OpenAI)
**Returns:** Full text report with sections:
- Price Trend Summary
- Technical Indicators Interpretation
- Market Sentiment
- Risks (India-specific)
- Opportunities (India-specific)
- Final Recommendation
- Next Steps

#### `compute_trend_score(data: dict) -> float`
**Location:** `src/analysis/trend_score.py`
**Purpose:** Calculate weighted trend score (0-100)
**Parameters:**
```python
{
    "delivery_volume_pct": float,
    "delivery_trend_pct": float,
    "current_price": float,
    "vwap": float,
    "volume_breakout": bool,
    "supports": list[float],
    "resistances": list[float],
    "pivot_points": dict,
    "df": pd.DataFrame,
}
```
**Scoring Weights:**
- Delivery Strength: 0-30 points
- VWAP Position: 0-20 points
- Volume Breakout: 0-20 points
- Support/Resistance: 0-15 points
- Pivot Point: 0-10 points
- Volatility: 0-5 points

#### `save_daily_record(data: dict) -> StockDaily`
**Location:** `src/database/crud.py`
**Purpose:** Save market data to database
**Parameters:**
```python
{
    "symbol": str,
    "open": float,
    "high": float,
    "low": float,
    "close": float,
    "volume": int,
    "delivery_pct": float,
    "delivery_qty": int,
    "total_volume": int,
    "vwap": float,
    "volume_breakout": int,
    "supports": list,
    "resistances": list,
    "pivot_points": dict,
    "trend_score": float,
}
```

---

## 🗄️ Data Models

### `StockDaily` (SQLAlchemy)
**Location:** `src/database/models.py`
```python
class StockDaily(Base):
    __tablename__ = "stock_daily"
    
    id: int (PK)
    symbol: str (indexed)
    open: float
    high: float
    low: float
    close: float
    volume: int
    delivery_pct: float
    delivery_qty: int
    total_volume: int
    vwap: float
    volume_breakout: int
    supports: JSON
    resistances: JSON
    pivot_points: JSON
    trend_score: float
    timestamp: DateTime (default: utcnow)
```

### `AIReport` (SQLAlchemy)
```python
class AIReport(Base):
    __tablename__ = "ai_report"
    
    id: int (PK)
    symbol: str (indexed)
    trend_score: float
    sentiment: str
    summary: Text
    recommendations: Text
    snapshot_time: DateTime (default: utcnow)
```

### `market_data` (SQLite)
```sql
CREATE TABLE market_data (
    ticker TEXT,
    date TEXT,
    open REAL,
    high REAL,
    low REAL,
    close REAL,
    volume INTEGER
)
```

### `technical_indicators` (SQLite)
```sql
CREATE TABLE technical_indicators (
    ticker TEXT,
    date TEXT,
    rsi REAL,
    macd REAL,
    macd_signal REAL,
    macd_hist REAL,
    ma20 REAL,
    ma50 REAL
)
```

---

## 🌐 API Endpoints

### FastAPI Server (`local_server.py`)

#### `POST /report`
**Purpose:** Receive stock analysis reports via webhook
**Request Body:**
```json
{
    "symbol": "RELIANCE.NS",
    "trend_score": 16,
    "trend_direction": "stable",
    "delivery_pct": 32.5,
    "vwap": 1532.45,
    "breakout": "none",
    "supports": [1500, 1480],
    "resistances": [1550, 1580],
    "pivot_points": [1520, 1530],
    "ai_summary": "...",
    "ai_recommendations": "...",
    "sentiment": "bearish",
    "alerts": [...]
}
```
**Response:**
```json
{
    "status": "ok",
    "received": {...},
    "email_sent": true
}
```

---

## ⚙️ Configuration

### Environment Variables (`.env`)
```
GMAIL_USER=ramarao.mundruai@gmail.com
GMAIL_PASS=your_app_password_here
N8N_WEBHOOK_URL=http://localhost:8000/report
OPENAI_API_KEY=sk-... (optional, for cloud mode)
```

### Ollama Configuration
- **URL:** `http://localhost:11434/api/generate`
- **Default Model:** `llama3.2:3b`
- **Available Models:**
  - `llama3.2:3b` (2.0 GB) - Primary
  - `phi3.5:latest` (2.1 GB) - Alternative
  - `mistral:7b` (4.4 GB) - High quality
  - `deepseek-r1:latest` (5.2 GB) - Reasoning

---

## 🧪 Testing

### Test Scripts

#### `scripts/test_mvp.py`
Tests the complete analysis pipeline:
```python
from src.fetcher.market_fetcher import analyze_stock
result = analyze_stock("RELIANCE")
# Returns: {"success": bool, "data": dict, "report": str}
```

#### `scripts/test_db.py`
Tests database operations:
- Saves current price to database
- Verifies record creation

#### `scripts/test_llm_reasoning.py`
Tests LLM integration:
- Calls `generate_llm_report()`
- Returns full AI analysis

### Running Tests
```bash
# Activate virtual environment
.venv\Scripts\activate

# Run all tests
python -m scripts.test_mvp
python -m scripts.test_db
python -m scripts.test_llm_reasoning

# Run Chainlit UI
chainlit run app.py

# Run API server
python local_server.py
```

---

## 🚀 Deployment

### Local Development
```bash
# 1. Create virtual environment
python -m venv .venv
.venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Install Ollama models
ollama pull llama3.2:3b
ollama pull phi3.5

# 4. Run application
chainlit run app.py
```

### Production Options
1. **Chainlit Cloud** - Deploy UI to cloud
2. **Docker** - Containerize the application
3. **Local Server** - Run FastAPI server for webhook integration

---

## 📈 Future Enhancements

### Phase 1 - Charts & Visualization
- [ ] Price trend charts
- [ ] RSI/MACD visualization
- [ ] Bollinger Bands charts
- [ ] Support/Resistance visualization

### Phase 2 - Multi-Agent Architecture
- [ ] Data Agent - Fetches real data
- [ ] Analysis Agent - Interprets data
- [ ] LLM Agent - Writes reports

### Phase 3 - Model Selector
- [ ] UI dropdown for model selection
- [ ] Auto model selection based on task

### Phase 4 - Streaming Output
- [ ] Stream report generation in Chainlit
- [ ] Loading spinner during inference

### Phase 5 - Enhanced Data Sources
- [ ] Alpha Vantage API integration
- [ ] Finnhub API integration
- [ ] Polygon.io integration

---

## 📝 Change Log

| Date | Version | Changes |
|------|---------|---------|
| 2026-07-07 | 1.0 | Initial document creation |

---

## 🔗 Quick Reference

### Key Commands
```bash
# Test analysis
python -m scripts.test_mvp

# Run UI
chainlit run app.py

# Run server
python local_server.py

# Check Ollama
curl http://localhost:11434/api/tags
```

### File Locations
- **UI:** `app.py`
- **LLM:** `src/reasoning/llm_reasoner.py`
- **Fetcher:** `src/fetcher/market_fetcher.py`
- **Database:** `src/database/`
- **Tests:** `scripts/`
- **Config:** `.env`