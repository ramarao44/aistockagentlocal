# Documentation Index

This folder contains project design, audit, roadmap, and testing documentation.

## Key Documents

- `DESIGN_DEVELOPMENT_DOCUMENT.md` - architecture, module specs, configuration, and test flow
- `AUDIT_REPORT_2026_07_09.md` - implementation audit findings and remediations
- `TEST_REPORT_2026-07-07.md` - historical test summary
- `AI_INSTRUCTIONS.md` - contributor/agent operating rules
- `PRODUCT_ROADMAP.md` - phase-wise delivery plan

## LLM Reasoning Notes

Current reasoning implementation is in `src/reasoning/llm_reasoner.py`.

Supported report modes:

- `local`: standard multi-step local reasoning
- `optimized`: compact prompt/output path for speed
- `cloud`: force OpenAI cloud generation

Local model mapping:

- Main summary: `qwen2.5:3b`
- Fast sentiment/compact path: `llama3.2:3b`
- Logic explanation: `phi3:3.8b`

## Validation Scripts

Run these after reasoning changes:

```powershell
python scripts/test_llm_reasoning.py
python scripts/test_reasoning.py
python scripts/test_ai_report.py
```
