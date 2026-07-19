# AI Stock Agent (Local-First)

Local-first AI stock analysis application focused on Indian markets (NSE/BSE).

## Overview

The project combines deterministic market-data processing with LLM-based reasoning.

- Market data and indicators are fetched/computed in Python modules.
- LLM reasoning supports local Ollama models and optional OpenAI fallback.
- Reports can run in standard or optimized mode.
- Market fetcher resolves free-text company names and caches resolved symbols for reuse.

## LLM Reasoning Modes

`src/ai/llm_reasoner.py` supports:

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

## Unified Build Command (4 Switches)

Use one command with only these toggles:

- `debug`: `on|off`
- `tests`: `on|off`
- `docs`: `on|off`
- `clean`: `on|off`

Direct command examples:

```powershell
python scripts/build.py --debug on --tests off --docs on --clean on
python scripts/build.py --profile ci --cr-id CR-YYYYMMDD-XXX
```

Windows profile launchers:

```powershell
build-profiles\quick.bat
build-profiles\dev.bat
build-profiles\ci.bat
build-profiles\release.bat
build-profiles\all-profiles-smoke.bat
build-profiles\baseline-sync.bat
build-profiles\cr-prepare.bat CR-YYYYMMDD-XXX "title"
build-profiles\cr-impact-check.bat CR-YYYYMMDD-XXX
build-profiles\ai-dlc-check.bat
```

## AI-DLC Framework (Standalone Governance)

This repository now includes a standalone AI-DLC framework rooted at `ai_dlc/`.

- Source of truth: `ai_dlc/AI_DLC_MANIFEST.yaml`
- Human-owned inputs: `ai_dlc/psc.md`, `ai_dlc/human_intent.md`, defect reports, and change requests.
- AI-owned governed artifacts: prompts, specs, bolts, tests, runtime, docs, and traceability under `ai_dlc/`.

Run AI-DLC gate validation:

```powershell
python scripts/build.py --profile ai-dlc-check
```

Push-time enforcement now runs AI-DLC gate first, then CR impact + CI profile validation.

Smoke script modes:

```powershell
# Fast profile wiring validation (default)
build-profiles\all-profiles-smoke.bat

# Full run using each profile defaults
build-profiles\all-profiles-smoke.bat full
```

Generated build documentation output is packaged in `build/docs` when `docs=on`.

### Clean Scope Policy (Hard Rule)

`clean=on` is restricted to disposable generated outputs only. Governance and canonical documentation paths are protected and must never be cleaned by default build commands.

Included in clean:
- `build/docs/**`
- `gen/debug/**`
- `gen/llm/**`
- `gen/pipeline-runs/**`
- `gen/reports/**`
- `gen/tmp/**`

Excluded from clean (must never be deleted):
- `ai_dlc/**` (including `ai_dlc/baseline/**` and `ai_dlc/change_requests/**`)
- `reports/**` canonical evidence outputs
- source and test roots (`src/**`, `scripts/**`, `tests/**`, `data/**`, `feature-requirements/**`)

## Baseline and Change Request Workflow

1. Generate baseline snapshot from original docs:

```powershell
python scripts/build.py --profile baseline-sync
```

2. Prepare a change request from active baseline:

```powershell
python scripts/build.py --profile cr-prepare --cr-id CR-20260713-001 --cr-title "example"
```

3. Update only files under `ai_dlc/change_requests/<CR-ID>/proposed`.

4. Complete impact analysis and set CR status to `approved`.

5. Validate implementation gate before coding:

```powershell
python scripts/build.py --profile cr-impact-check --cr-id CR-20260713-001
```

## Webhook Test Runner

`run_tests.py` posts to webhook URL from `TEST_REPORT_URL` environment variable.

- Default: `http://localhost:8000/report`
- Override example (PowerShell):

```powershell
$env:TEST_REPORT_URL="http://localhost:8000/report"
python run_tests.py
```
