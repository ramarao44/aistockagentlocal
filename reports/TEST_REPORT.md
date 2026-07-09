# Test Report - 2026-07-10

## Environment
- Python environment: local virtual environment
- Project: AI Stock Agent
- Date: 2026-07-10

## Tests Run
- `python -m scripts.test_mvp`
- `python -m scripts.test_db`
- `python -m scripts.test_llm_reasoning`
- `python -c "import scripts.test_market_fetcher as t; ..."`

## Results
- `test_mvp`: PASS ✅
- `test_db`: PASS ✅
- `test_llm_reasoning`: PASS ✅
- `test_market_fetcher` (cache + web resolver paths): PASS ✅

## Notes
- MVP analysis tests successful for Indian stocks (RELIANCE.NS, TCS.NS, INFY.NS) with live market prices
- Database CRUD operations working correctly - records saved successfully
- LLM reasoning test fully passed with mode-routing assertions (local, optimized, cloud fallback)
- Market fetcher test now covers symbol-resolution cache hit, web-resolution fallback, cache persistence write, and all-path failure handling
- All core functionality verified and operational
- Subprocess-based LLM engine validated with model wrappers (`qwen2.5:3b`, `llama3.2:3b`, `phi3:3.8b`)
- DeepSeek path removed from active design and test surface as requested
