# AI Stock Agent - Design & Development Document
**Version:** 1.0
**Last Updated:** 2026-07-11
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
- **2026-07-11:** Standardized LLM output to a fixed 6-section evaluation format with strict validation, retry, and deterministic fallback in `src/ai/llm_reasoner.py` - ensures machine-parsable, deterministic report structure for cross-model comparison.
- **2026-07-11:** Added deterministic section scoring (`0-5` each, total `0-30`) appended as `SectionScore` lines in report output - enables quantifiable model evaluation and easy downstream parsing.
- **2026-07-11:** Added compatibility-safe Ollama execution (`--no-ansi` first, auto-retry without flag on older CLI versions) and aligned test suites (`scripts/test_llm_reasoning.py`, `scripts/test_ai_report.py`, `scripts/test_reasoning.py`) - prevents runtime breaks while preserving clean output intent.
- **2026-07-10:** Fixed h11 LocalProtocolError in Chainlit app by using `asyncio.to_thread()` for non-blocking LLM calls - prevents HTTP connection errors when running multiple subprocess-based LLM calls; added comprehensive debug prints to trace LLM operations; added timeout configuration to Chainlit config (300s server timeout, 120s subprocess timeout).
  - **Interview Prep Created:** AI_PM_INTERVIEW_PREP.md documents 7 STAR stories extracted from audit experience. All documentation updated with cross-references to create cohesive learning ecosystem.
  - **Architectural Lessons:** See "Architectural Decision Trade-offs" section below for insights into schema design, data pipeline constraints, and error handling patterns.
- 2026-07-08: Added repo safety layers - created PUSH_CHECKLIST.md and .githooks/pre-push for automated validation. Protects against pushing without tests, accidental .env commits, and large files. Ensures all AI agents follow discipline before pushing.
- 2026-07-08: Added pre-push validation checklist to AI_INSTRUCTIONS.md and standardized change log format for consistency - ensures traceability and continuity across AI sessions. Organized test reports in dedicated reports/ folder for better project organization.
- 2026-07-07: Added defensive handling for empty/partial market data in the fetcher, made cloud LLM imports fail gracefully, and added an environment-based configuration example for local setup.

---

## 🏛️ Architectural Decision Trade-offs

**These insights are captured as interview stories. See** [AI_PM_INTERVIEW_PREP.md](./AI_PM_INTERVIEW_PREP.md) **for complete context.**

### Decision #1: Database Schema Design for Technical Indicators

**Problem Addressed:**
- Computing 13 technical indicators (RSI, MACD, MA20/50/200, ADX, Bollinger Bands)
- Original schema only captured OHLCV (5 columns)
- Data was computed but lost (not persisted to database)
- Phase 3 (Charts) couldn't display any indicators

**Decision Made:**
- Extended StockDaily model from 10 columns → 30 columns
- Added explicit columns for all 13 technical indicators
- Updated data pipeline to populate indicator columns
- Recreated database schema with SQLAlchemy

**Trade-offs:**
| Aspect | Trade-off |
|--------|----------|
| **Schema Complexity** | Simpler 5-column schema vs Complete 30-column schema (chose complete) |
| **Development Time** | Quick MVP vs Robust design (chose robust) |
| **Future Flexibility** | Fixed schema vs Flexible JSON columns (chose fixed for performance) |
| **Query Performance** | Easier queries with explicit columns vs JSON extraction |

**Why This Decision:**
- Incomplete schema was fundamental architectural problem
- Can't build Phase 3 visualization without persisted indicators
- Explicit columns enable better query performance than JSON
- Cost of fixing wrong is high (all of Phase 3); cost of adding columns is low

**Impact:**
- ✅ All indicators now available for Phase 3
- ✅ Better query performance (direct column access)
- ✅ Data integrity (schema enforces indicator presence)
- ⚠️ Schema migration required when adding new indicators

**Interview Insight:**
> "Database schema is a critical product decision. I had to choose between quick MVP (simpler schema) and robust design (complete schema). I chose complete because Phase 3 couldn't work without it. The lesson: understand downstream dependencies when designing your schema."

---

### Decision #2: Data Period for Historical Analysis

**Problem Addressed:**
- MA200 (200-day moving average) returning None
- Default 6-month fetch provides ~130 trading days
- MA200 requires minimum 200+ trading days
- Long-term trend analysis unavailable

**Decision Made:**
- Extended data fetch period from "6mo" → "1y"
- Now fetches ~252 trading days (1 year)
- Sufficient for MA200 and other long-term indicators

**Trade-offs:**
| Aspect | Trade-off |
|--------|----------|
| **Data Volume** | Less data (6 months) vs More data (1 year) (chose 1 year) |
| **API Calls** | Faster fetch vs More data points (chose more data) |
| **Storage** | Smaller database vs Complete historical context (chose context) |
| **Analysis Depth** | Short-term only vs Short+Long-term (chose both) |

**Why This Decision:**
- Features have implicit data requirements
- Better to discover constraint during verification than after launch
- 1 year fetch cost negligible vs Phase 3 value
- Users expect long-term trend analysis for stock decisions

**Impact:**
- ✅ MA200 now computes correctly (values: 1307-2697)
- ✅ Long-term trend analysis available
- ✅ Better investment insights (long-term patterns visible)
- ⚠️ Slightly larger database (not significant)

**Interview Insight:**
> "Features have hidden data requirements. I discovered that MA200 needed 200+ days of data. The lesson: verify data constraints during design, before they break users. Ask: what data does this feature need to work correctly?"

---

### Decision #3: Error Handling for External Dependencies

**Problem Addressed:**
- Delivery percentage fetched via Moneycontrol web scraping
- Web scraping broke when Moneycontrol changed HTML
- All delivery_pct values returned None
- Feature looked broken, but was it critical?

**Decision Made:**
- Made delivery volume "experimental" feature
- Graceful degradation: returns None safely
- Documented limitation and future NSE API option
- Core analysis works without delivery data

**Trade-offs:**
| Aspect | Trade-off |
|--------|----------|
| **Feature Availability** | Fix scraper vs Make experimental (chose experimental) |
| **User Experience** | Missing data vs Silent failure (chose documented None) |
| **Investment** | Heroic fixing vs Move on (chose move on) |
| **Future Path** | Maintain fragile scraper vs Switch to NSE API (chose NSE API path) |

**Why This Decision:**
- Delivery volume is supplementary, not critical
- Trend score works perfectly without this data
- Web scraping is inherently fragile (HTML changes)
- NSE API is better long-term solution
- Cost of maintaining scraper > value of supplementary data

**Impact:**
- ✅ System stable without delivery data
- ✅ Clear documentation of limitation
- ✅ Prioritized effort on critical features
- ✅ Path to better solution (NSE API) documented
- ⚠️ User doesn't get delivery insights (supplementary feature)

**Interview Insight:**
> "Not every feature failure requires heroic fixing. I evaluated criticality and decided delivery volume was supplementary. I chose graceful degradation: system works without it, documentation explains why. The lesson: understand criticality and design error handling appropriately."

---

### Decision Pattern: Schema Before Features

**Architectural Principle:** Design your data layer before building features that depend on it.

**How It Applied:**
1. **Discovered Issue:** Computing indicators but not storing them
2. **Root Cause:** Schema incomplete (only OHLCV, no indicators)
3. **Solution:** Extended schema, updated data pipeline
4. **Result:** Phase 3 can now build on stable foundation

**Future Application:**
- Before Phase 3 (Charts): Verify all data needed for charts is persisted
- Before Phase 4 (Multi-Agent): Design message schema for agent communication
- Before Phase 5 (Model Selection): Design schema for model performance metrics

**Interview Takeaway:**
> "I learned that data layer design cascades through product. Get your schema right early, before features depend on it. The cost of fixing schema late is exponentially higher than fixing it during verification."

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
├── UI Layer: main.py (Chainlit)
├── API Layer: local_server.py (FastAPI)
├── Core Layer:
│   ├── src/ai/llm_reasoner.py
│   ├── src/ingestion/market_fetcher.py
│   ├── src/analysis/technical/technical_analyzer.py
│   └── src/analysis/trend/trend_score.py
├── Data Layer:
│   ├── src/database/ (SQLAlchemy)
│   └── src/database/sqlite_legacy.py (SQLite)
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
| `main.py` | Chainlit UI entrypoint - handles user input and displays reports |
| `local_server.py` | FastAPI webhook server for receiving reports |
| `scheduler.py` | APScheduler for daily automated jobs |
| `email_sender.py` | Gmail SMTP integration for report delivery |
| `html_formatter.py` | HTML report generation for email/webhook |
| `requirements.txt` | Python dependencies |
| `.env` | Environment configuration (Gmail, N8N webhook) |

### Source Modules (`src/`)

#### `src/ai/llm_reasoner.py`
Main LLM integration module. Handles:
- Local LLM calls via Ollama subprocess (`ollama run <model>`)
- Cloud LLM calls via OpenAI
- Mode-aware report generation with real market data (`local`, `optimized`, `cloud`)
- Fallback from local to cloud when enabled

#### `src/ai/reasoning_node.py`
Report generation utilities:
- `generate_daily_summary()` - Creates daily summary from DB
- `generate_trend_analysis()` - Multi-day trend analysis
- `generate_combined_report()` - Combined daily + trend report

#### `src/ingestion/market_fetcher.py`
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

#### `src/ingestion/news_fetcher.py`
News fetching via Yahoo Finance RSS:
- `fetch_news()` - RSS feed parsing

#### `src/analysis/technical/technical_analyzer.py`
Technical indicator computation using `ta` library:
- `compute_indicators()` - RSI, MACD, MA20, MA50

#### `src/analysis/sentiment/sentiment_analyzer.py`
Sentiment analysis using VADER:
- `compute_sentiment()` - Returns compound sentiment score

#### `src/analysis/trend/trend_score.py`
Trend Score 2.0 algorithm:
- `compute_trend_score()` - Weighted scoring (0-100)

#### `src/database/`
SQLAlchemy database layer:
- `engine.py` - Database connection setup
- `models.py` - SQLAlchemy models
- `crud.py` - Create/Read/Update/Delete operations

#### `src/database/sqlite_legacy.py`
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
**Location:** `src/ingestion/market_fetcher.py`
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
**Location:** `src/ai/llm_reasoner.py`
**Purpose:** Generate AI-powered stock analysis report
**Parameters:**
- `ticker` - Stock symbol
- `mode` - `local` (full quality), `optimized` (compact output), or `cloud` (cloud only)
**Returns:** Full text report with sections:
- Summary
- Quick Sentiment
- Trend Score Logic

#### `run_model(model: str, prompt: str) -> str`
**Location:** `src/ai/llm_reasoner.py`
**Purpose:** Execute local LLM through subprocess
**Behavior:**
- Calls `ollama run <model>`
- Returns normalized local error markers for non-zero exit, timeout, missing command, or empty output

#### `compute_trend_score(data: dict) -> float`
**Location:** `src/analysis/trend/trend_score.py`
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
MAIN_LLM_MODEL=qwen2.5:3b
FAST_LLM_MODEL=llama3.2:3b
LOGIC_LLM_MODEL=phi3:3.8b
ENABLE_CLOUD_FALLBACK=1
```

### Ollama Configuration
- **Execution:** `ollama run <model>` (subprocess)
- **Default Models:**
    - `qwen2.5:3b` - primary summary reasoning
    - `llama3.2:3b` - fast/optimized sentiment path
    - `phi3:3.8b` - trend-logic explanation
- **Available Models:**
    - `qwen2.5:3b`
    - `llama3.2:3b`
    - `phi3:3.8b`

---

## 🧪 Testing

### Test Scripts

#### `scripts/test_mvp.py`
Tests the complete analysis pipeline:
```python
from src.ingestion.market_fetcher import analyze_stock
result = analyze_stock("RELIANCE")
# Returns: {"success": bool, "data": dict, "report": str}
```

#### `scripts/test_db.py`
Tests database operations:
- Saves current price to database
- Verifies record creation

#### `scripts/test_llm_reasoning.py`
Tests LLM integration:
- Validates standard mode output structure
- Validates optimized mode routing
- Validates local failure cloud fallback
- Validates missing API key behavior

#### `scripts/test_reasoning.py`
Tests reasoning composition:
- Validates combined deterministic report
- Validates optimized LLM mode path

#### `scripts/test_ai_report.py`
Tests AI report persistence + optimized mode generation check

### Running Tests
```bash
# Activate virtual environment
.venv\Scripts\activate

# Run all tests
python -m scripts.test_llm_reasoning
python -m scripts.test_reasoning
python -m scripts.test_ai_report

# Run Chainlit UI
chainlit run main.py

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
ollama pull qwen2.5:3b
ollama pull llama3.2:3b
ollama pull phi3:3.8b

# 4. Run application
chainlit run main.py
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
chainlit run main.py

# Run server
python local_server.py

# Check Ollama
curl http://localhost:11434/api/tags
```

### File Locations
- **UI:** `main.py`
- **LLM:** `src/ai/llm_reasoner.py`
- **Fetcher:** `src/ingestion/market_fetcher.py`
- **Database:** `src/database/`
- **Tests:** `scripts/`
- **Config:** `.env`