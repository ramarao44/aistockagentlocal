# Quick Reference - AI Stock Agent

**Last Updated:** 2026-07-13

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
chainlit run main.py

# Run server
python local_server.py

# Check Ollama
curl http://localhost:11434/api/tags

# Unified build (4 toggles)
python scripts/build.py --profile dev
python scripts/build.py --debug on --tests off --docs on --clean on

# Windows profile launchers
build-profiles\quick.bat
build-profiles\dev.bat
build-profiles\ci.bat
build-profiles\release.bat
build-profiles\all-profiles-smoke.bat
build-profiles\all-profiles-smoke.bat full
build-profiles\baseline-sync.bat
build-profiles\cr-prepare.bat CR-YYYYMMDD-XXX "title"
build-profiles\cr-impact-check.bat CR-YYYYMMDD-XXX

# Baseline + CR workflow
python scripts/build.py --profile baseline-sync
python scripts/build.py --profile cr-prepare --cr-id CR-20260713-001 --cr-title "example"
python scripts/build.py --profile cr-impact-check --cr-id CR-20260713-001
python scripts/build.py --profile ci --cr-id CR-20260713-001

# Clean-only (safe)
python scripts/build.py --profile quick --clean on --docs off --tests off --debug off

# Pre-push hook CR id (required for gated push)
$env:AISA_CR_ID="CR-20260713-001"
git push
```

### Clean Scope Guardrails

- Clean includes only: `build/docs/**`, `gen/debug/**`, `gen/llm/**`, `gen/pipeline-runs/**`, `gen/reports/**`, `gen/tmp/**`.
- Clean must never touch: `docs/**`, `docs/baseline/**`, `docs/change-requests/**`, `gen/docs/**`, `reports/**`.

---

## 📁 File Locations

| Purpose | File |
|---------|------|
| **UI** | `main.py` |
| **LLM** | `src/ai/llm_reasoner.py` |
| **Fetcher** | `src/ingestion/market_fetcher.py` |
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
| RSI | `compute_rsi()` | `src/ingestion/market_fetcher.py` |
| MACD | `compute_macd()` | `src/ingestion/market_fetcher.py` |
| MA20 | `compute_moving_average(df, 20)` | `src/ingestion/market_fetcher.py` |
| MA50 | `compute_moving_average(df, 50)` | `src/ingestion/market_fetcher.py` |
| SuperTrend | `compute_supertrend()` | `src/ingestion/market_fetcher.py` |
| ADX | `compute_adx()` | `src/ingestion/market_fetcher.py` |
| VWAP | `calculate_vwap()` | `src/ingestion/market_fetcher.py` |
| Bollinger | `compute_bollinger_bands()` | `src/ingestion/market_fetcher.py` |

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

---

## 📊 Requirement Outcome Reporting

Primary artifacts:
- `reports/requirement_status_latest.csv`
- `reports/failing_requirements_latest.csv`
- `reports/test_case_results_latest.csv`
- `reports/TEST_REPORT.md`

Outcome semantics in `requirement_status_latest.csv`:
- `Passed`: At least one mapped test ran and all mapped tests passed.
- `Failed`: One or more mapped tests failed.
- `Not Covered`: No mapped tests were executed for the requirement in the run.
- `Partial`: Mixed pass/fail/skip behavior where full pass criteria is not met.

Transition fields for one-cycle ID migration:
- `requirement_id`: Canonical ID (FR-01 style).
- `legacy_requirement_ids_text`: Legacy IDs mapped to the canonical requirement.
- `canonical_requirement_ids_text` in `test_case_results_latest.csv`: Canonical IDs resolved from legacy mappings.

Note:
- Legacy IDs remain supported during the transition cycle for historical comparability.
- New reports should be consumed using canonical `requirement_id` and `outcome`.