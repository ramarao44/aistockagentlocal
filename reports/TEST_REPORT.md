# Test Report - 2026-07-11

## Environment
- Python environment: local virtual environment
- Project: AI Stock Agent
- Date: 2026-07-11

## Tests Run
- `python -m scripts.test_mvp`
- `python -m scripts.test_db`
- `python -m scripts.test_llm_reasoning`
- `python scripts/test_ai_report.py`
- `python scripts/test_reasoning.py`

## Results Summary
- **Pre-push mandatory tests: PASS**
- **LLM Health Checks: PASS** - Ollama server available, all required models installed
- **Reasoning unit/integration tests: PASS**
- **Live smoke checks (local + optimized): PASS**
- **Standardized section scoring trailer present:** `SectionScore Total: 28/30` in both smoke checks

## Changes Validated in This Run
- Standardized evaluation-ready report template (6 fixed sections, deterministic validation path)
- Single-call local reasoning path using `MAIN_LLM_MODEL` for both `local` and `optimized` modes
- Output format enforcement with retry + deterministic fallback for non-compliant model output
- Added machine-parsable scoring block:
  - `SectionScore Summary: X/5`
  - `SectionScore Indicators: X/5`
  - `SectionScore Sentiment: X/5`
  - `SectionScore Risks: X/5`
  - `SectionScore Opportunities: X/5`
  - `SectionScore Recommendation: X/5`
  - `SectionScore Total: Y/30`
- Added Google/Moneycontrol symbol fallback branch in market fetch path with enriched failure message

## LLM Subsystem Health Checks
- [x] Ollama CLI available and responsive
- [x] All required models installed (qwen2.5:3b, llama3.2:3b, phi3:3.8b)
- [x] Server connectivity verified

## LLM Error Handling and Reliability Coverage
- [x] `test_llm_error_response_format` - Validates error format detection
- [x] `test_llm_timeout_handling` - Tests timeout error handling
- [x] `test_llm_file_not_found_handling` - Tests missing CLI handling
- [x] `test_llm_subprocess_error_handling` - Tests subprocess error formatting
- [x] `test_empty_output_handling` - Tests empty response handling
- [x] Ollama CLI health check - Server available and responsive
- [x] Required model availability check - `qwen2.5:3b`, `llama3.2:3b`, `phi3:3.8b`
- [x] `test_subprocess_timeout_value` - Verifies 120s timeout configured
- [x] `test_report_generation_timing` - Validates report generation speed

## Configuration and Runtime Notes
- Ollama call flow tries `--no-ansi` first and auto-retries without it when unsupported by installed CLI versions
- Cloud mode still requires `OPENAI_API_KEY`; missing key path validated and handled

## Source Code Areas Covered
- `src/ai/llm_reasoner.py`
- `scripts/test_llm_reasoning.py`
- `scripts/test_ai_report.py`
- `scripts/test_reasoning.py`
- `src/ingestion/market_fetcher.py`

## Debug Prints Added to Source
- Added timing and model tracking in `src/ai/llm_reasoner.py`:
  - `run_model()` - Tracks model, prompt length, elapsed time, return code
  - All reasoning functions log model selection
  - `generate_llm_report()` - Tracks overall timing

## Known Issues / Debugging Notes
### "Could not reach the server" Error (h11 LocalProtocolError)
- Root cause: Chainlit's h11 HTTP layer times out when LLM subprocess calls block the event loop
- Fixed by using `asyncio.to_thread()` in `main.py` to run LLM calls in a thread pool
- Also added `timeout = 300` to `.chainlit/config.toml` under `[server]` section
- Subprocess timeout is set to 120 seconds in `run_model()`

## Notes
- Pre-push checklist test gate passed with current working tree changes.
- Documentation, tests, and implementation are now aligned to the standardized evaluation format and score-output contract.