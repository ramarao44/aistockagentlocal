# AI Repo Snapshot
Generated: 2026-07-27
Branch: RefactorProjectwithAIDLC
Latest Commit: CR-20260720-UI-001 (b91bbd3)

## Project Overview
AI Stock Agent — Contract-driven Indian stock analysis pipeline with interactive Chainlit UI, Ollama LLM reasoning, and AI-DLC governance framework.

## Architecture

### Data Flow
```
User (Chainlit UI) → ui_payload dict
  → src/core/orchestrator.py :: run_pipeline(symbol, ui_payload)
    → master contract (MASTER_CONTRACT_V1)
      → ingestion (market_fetcher, news_fetcher)
      → analysis (technical, fundamental, sentiment, trend)
      → timeframe_engine
      → LLM reasoner (generate_ai_report)
        → Ollama model (qwen2.5:3b / llama3.2:3b)
      → persistence (save_analysis_snapshot)
      → artifacts (pipeline-runs, reports)
```

### Key Files

| Layer | File | Description |
|-------|------|-------------|
| **UI** | `src/ui/chainlit_ui.py` | Chainlit settings panel (dropdowns: Exchange, Timeframe, Risk Profile, Analysis Types, User Context) |
| **Entry** | `main.py` | App entry point, runs chainlit on port 8080 |
| **Orchestrator** | `src/core/orchestrator.py` | Pipeline orchestration, contract assembly, module dispatch |
| **UI Contract** | `src/core/contracts/ui_contract.py` | `UI_CONTRACT_V1` and `UI_CONTRACT_V2` (with user_context) |
| **Master Contract** | `src/core/contracts/master_contract.py` | Top-level pipeline contract |
| **LLM Reasoner** | `src/ai/llm_reasoner.py` | Prompt building, model calling, report enforcement |
| **Tests** | `tests/test_contract_pipeline_unittest.py` | 14 tests (8 original + 6 user_context) |

### All Contracts
- `ui_contract.py` — User input schema
- `master_contract.py` — Pipeline master
- `orchestrator_contract.py` — Orchestrator state
- `market_data_contract.py` — Market data
- `technical_contract.py` — Technical indicators
- `fundamental_contract.py` — Fundamental analysis
- `sentiment_contract.py` — Sentiment analysis
- `trend_contract.py` — Trend evolution
- `timeframe_contract.py` — Timeframe weights
- `llm_contract.py` — AI report output
- `error_contract.py` — Error schema
- `analysis_history_contract.py` — DB persistence

## AI-DLC Governance Structure

```
ai_dlc/
├── AI_DLC_MANIFEST.yaml       — Framework manifest
├── human_intent.md            — Canonical user requirements
├── human_intent_template.md   — Template for new intents
├── human_intent_skills_integration.md — Skills framework integration
├── fis.md                     — Final Intent Statement
├── psc.md                     — Product Scope Charter
├── baseline/                  — Baseline snapshots
├── change_requests/
│   ├── CR-20260720-001/       — ADX fix CR (legacy)
│   └── CR-20260720-UI-001/    — UI Settings Panel CR (latest)
│       ├── metadata.json      — CR status: approved
│       ├── supporting/
│       │   ├── IMPACT_ANALYSIS.md
│       │   ├── AI_HANDOFF.md
│       │   └── IMPLEMENTATION_NOTES.md
│       ├── baseline-copy/     — Pre-CR baseline
│       └── proposed/          — Proposed changes
├── governance/
│   ├── role_model.md          — HIR/DME/DEV/QA/PL/CCS roles
│   ├── file_access_rules.md   — Which role modifies what
│   └── safety_rules.md        — Push gates, validation rules
├── runtime/
│   ├── gic_latest.md          — Global Instruction Check
│   └── ccs_latest.md          — Change Control System
├── skills/                    — AI skills framework (validate_skills.py)
├── tickets/decision_tickets/  — FIS decision tickets
├── traceability/              — PSC→FIS→Specs→Code→Tests→Reports links
└── docs/AI_REPO_SNAPSHOT.md   — THIS FILE
```

## Latest CR: CR-20260720-UI-001

### What Changed
1. **ui_contract.py**: Added `UI_CONTRACT_V2` with `user_context: Optional[str]` field
2. **llm_reasoner.py**: Added `_build_user_context_block()` — inserts personalized context into LLM prompts
3. **chainlit_ui.py**: Replaced text commands with `cl.ChatSettings` widgets:
   - `Select` for Exchange, Timeframe, Risk Profile, Output Format
   - `MultiSelect` for Analysis Types
   - `TextInput(multiline=True)` for User Context
4. **tests**: 6 new tests validating user_context propagation and prompt building

### Test Results
- **Total tests**: 50 (19 script + 31 unittest)
- **Failures**: 0
- **CI Build**: status ok (137.29s)
- **GIC**: PASS
- **CCS**: PASS

## How to Run

### Start UI
```bash
chainlit run src/ui/chainlit_ui.py -w --port 8080
# or:
python -m chainlit run src/ui/chainlit_ui.py -w --port 8080
```

### Run Build/Validation
```bash
# Quick smoke test
scripts\build.py --profile quick

# Development build (with tests)
scripts\build.py --profile dev

# CI gate (full validation + GIC/CCS)
scripts\build.py --profile ci --cr-id CR-XXXXXX-XXX

# Push with gate (requires AISA_CR_ID env var)
$env:AISA_CR_ID="CR-XXXXXX-XXX"
git push
```

### Run Tests
```bash
# Unit tests only
.venv\Scripts\python -m pytest tests\

# Specific test
.venv\Scripts\python -m pytest tests/test_contract_pipeline_unittest.py -v

# Script tests
.venv\Scripts\python scripts\test_mvp.py
```

## UI Contract V2 Schema
```python
UI_CONTRACT_V2 = {
    **UI_CONTRACT_V1,
    "version": "2.0",
    "user_context": None,  # Optional[str] — free-text investment context
}
```

## LLM Prompt Architecture
```
_build_standardized_report_prompt(market_snapshot, user_context=None)
  ├── Expert analyst header
  ├── STRICT RULES (6 sections, 2 sentences each)
  ├── STOCK DATA (snapshot)
  ├── ### User Context (if provided, personalized block; else neutral fallback)
  └── OUTPUT FORMAT (template)
```

## Push Gates
The pre-push hook runs:
1. `ai-dlc-check` — validates frame access rules
2. `ci --cr-id <CR>` — runs all 50 tests, GIC, CCS
3. Push proceeds only if both pass

Set `$env:AISA_CR_ID="CR-XXXXXX-XXX"` before each push.

## Key Models
- MAIN: `qwen2.5:3b` (or `MAIN_LLM_MODEL` env var)
- FAST: `llama3.2:3b` (or `FAST_LLM_MODEL`)
- LOGIC: `phi3:3.8b` (or `LOGIC_LLM_MODEL`)
- CLOUD: `gpt-4o-mini` (or `CLOUD_MODEL`, requires `OPENAI_API_KEY`)