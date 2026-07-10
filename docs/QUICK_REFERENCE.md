# Quick Reference - AI Stock Agent

**Last Updated:** 2026-07-11

---

## 🚀 Most Used Commands

```bash
# Activate environment
.venv\Scripts\activate

# Run tests
python -m scripts.test_mvp
python -m scripts.test_db
python -m scripts.test_llm_reasoning

# Run UI
chainlit run app.py

# Run server
python local_server.py

# Check Ollama
curl http://localhost:11434/api/tags
```

---

## 📁 File Locations

| Purpose | File |
|---------|------|
| **UI** | `app.py` |
| **LLM** | `src/reasoning/llm_reasoner.py` |
| **Fetcher** | `src/fetcher/market_fetcher.py` |
| **Database** | `src/database/` |
| **Tests** | `scripts/` |
| **Config** | `.env` |
| **Instructions** | `AI_INSTRUCTIONS.md` |
| **Design Doc** | `DESIGN_DEVELOPMENT_DOCUMENT.md` |
| **Lessons** | `LESSONS_LEARNED.md` |

---

## 📊 Technical Indicators

| Indicator | Function | File |
|-----------|----------|------|
| RSI | `compute_rsi()` | `src/fetcher/market_fetcher.py` |
| MACD | `compute_macd()` | `src/fetcher/market_fetcher.py` |
| MA20 | `compute_moving_average(df, 20)` | `src/fetcher/market_fetcher.py` |
| MA50 | `compute_moving_average(df, 50)` | `src/fetcher/market_fetcher.py` |
| SuperTrend | `compute_supertrend()` | `src/fetcher/market_fetcher.py` |
| ADX | `compute_adx()` | `src/fetcher/market_fetcher.py` |
| VWAP | `calculate_vwap()` | `src/fetcher/market_fetcher.py` |
| Bollinger | `compute_bollinger_bands()` | `src/fetcher/market_fetcher.py` |

---

## 🤖 Ollama Models

| Model | Size | Use Case |
|-------|------|----------|
| `qwen2.5:3b` | ~2 GB | Main summary reasoning |
| `llama3.2:3b` | 2.0 GB | Fast/optimized sentiment path |
| `phi3:3.8b` | ~2.3 GB | Trend logic explanation |

### Supported LLM Modes

- `local` - standard local report path
- `optimized` - compact low-latency report path
- `cloud` - OpenAI cloud path (fallback/forced)

### Standardized Report Output Contract

- Fixed sections in order:
    - `Summary`
    - `Indicators`
    - `Sentiment`
    - `Risks`
    - `Opportunities`
    - `Recommendation`
- Machine-parsable score trailer:
    - `SectionScore Summary: X/5`
    - `SectionScore Indicators: X/5`
    - `SectionScore Sentiment: X/5`
    - `SectionScore Risks: X/5`
    - `SectionScore Opportunities: X/5`
    - `SectionScore Recommendation: X/5`
    - `SectionScore Total: Y/30`

---

## 🔎 Symbol Resolution Cache

Market fetch flow (`fetch_indian_stock_data`) uses this order:

1. `symbol_resolution_cache` lookup by normalized input key
2. Direct ticker normalization (`normalize_ticker`)
3. Yahoo Finance search fallback (`resolve_symbol_from_web`)

Resolved NSE/BSE ticker pairs are persisted in SQLite for reuse.

---

## 🐛 Common Issues & Solutions

### yfinance MultiIndex
```python
if isinstance(df.columns, pd.MultiIndex):
    df.columns = df.columns.get_level_values(0)
```

### NaN in Indicators
- Expected for insufficient data
- Handle gracefully in code

### Ollama Timeout
- Use smaller models (3-4B)
- Increase timeout to 120s

### Import Errors
- Check `__init__.py` in all directories
- Clear `__pycache__` folders

---

## 📈 Trend Score Weights

| Factor | Points |
|--------|--------|
| Delivery Strength | 0-30 |
| VWAP Position | 0-20 |
| Volume Breakout | 0-20 |
| Support/Resistance | 0-15 |
| Pivot Point | 0-10 |
| Volatility | 0-5 |
| **Total** | **100** |

---

## 🔗 API Endpoints

| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/report` | Receive webhook reports |

---

## 📝 Test Report Naming

`reports/TEST_REPORT.md`

This file should be overwritten with the latest run results each time tests are executed.