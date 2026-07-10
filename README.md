# AI Stock Agent (Local-First)

Local-first AI stock analysis application focused on Indian markets (NSE/BSE).

## Overview

The project combines deterministic market-data processing with LLM-based reasoning.

- Market data and indicators are fetched/computed in Python modules.
- LLM reasoning supports local Ollama models and optional OpenAI fallback.
- Reports can run in standard or optimized mode.
- Market fetcher resolves free-text company names and caches resolved symbols for reuse.

## LLM Reasoning Modes

`src/reasoning/llm_reasoner.py` supports:

- `mode="local"`: full-quality local report using model wrappers.
- `mode="optimized"`: compact prompt/response path for faster output.
- `mode="cloud"`: cloud-only report via OpenAI API.

Local model routing:

- Main reasoning: `qwen2.5:3b`
- Fast reasoning: `llama3.2:3b`
- Logic reasoning: `phi3:3.8b`

## Setup

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Install local models:

```powershell
ollama pull qwen2.5:3b
ollama pull llama3.2:3b
ollama pull phi3:3.8b
```

Optional cloud fallback configuration (`.env`):

```text
OPENAI_API_KEY=your_key
ENABLE_CLOUD_FALLBACK=1
MAIN_LLM_MODEL=qwen2.5:3b
FAST_LLM_MODEL=llama3.2:3b
LOGIC_LLM_MODEL=phi3:3.8b
```

## Run Targeted Tests

```powershell
python scripts/test_llm_reasoning.py
python scripts/test_reasoning.py
python scripts/test_ai_report.py
```

## Webhook Test Runner

`run_tests.py` posts to webhook URL from `TEST_REPORT_URL` environment variable.

- Default: `http://localhost:8000/report`
- Override example (PowerShell):

```powershell
$env:TEST_REPORT_URL="http://localhost:8000/report"
python run_tests.py
```
