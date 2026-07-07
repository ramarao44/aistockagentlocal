# Quick Reference - AI Stock Agent

**Last Updated:** 2026-07-07

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
| `llama3.2:3b` | 2.0 GB | Primary (fast, good quality) |
| `phi3.5` | 2.1 GB | Alternative (fast, good reasoning) |
| `mistral:7b` | 4.4 GB | High quality |
| `deepseek-r1` | 5.2 GB | Reasoning tasks |

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

`TEST_REPORT_YYYY-MM-DD_HHMM.md`

Example: `TEST_REPORT_2026-07-07_2230.md`