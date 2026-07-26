✅ 1. HUMAN INTENT (Canonical Form)
Human Intent:  
“As a user, I want an interactive UI where I can select exchange (NSE/BSE), timeframe, risk profile, analysis types, and optionally provide my investment context, so that the AI Stock Agent can generate a personalized and accurate stock analysis.”

Expanded Intent (for AI Reasoning)
User prefers dropdowns instead of commands

User wants multi-select analysis types

User wants context-aware LLM reasoning

User wants structured UI payload

User wants zero ambiguity in settings

User wants MVP-level simplicity

User wants future extensibility (presets, profiles, portfolio mode)

✅ 2. CHANGE REQUEST (CR)
CR ID: CR-20260720-UI-001
Title: Add Interactive Settings Panel + User Context Field
Owner: ramarao
Date: 2026-07-20
Category: Non-trivial (UI + Contract + Orchestrator + LLM Reasoner)
CR Summary
Replace command-driven UI with an interactive settings panel that includes:

Exchange selector (NSE/BSE)

Timeframe selector

Risk profile selector

Analysis type multi-select

User context free-text field

Updated UI contract (UI_CONTRACT_V2)

Orchestrator support for new field

LLM Reasoner support for user_context

This change improves UX, reduces errors, and enhances personalization.

✅ 3. IMPACT ANALYSIS (MANDATORY)
Changed Modules
Area	Files
UI	src/ui/chainlit_ui.py, main.py
Contracts	src/core/contracts/ui_contract.py
Orchestrator	src/core/orchestrator.py
LLM Reasoner	src/ai/llm_reasoner.py
Docs	DESIGN_DEVELOPMENT_DOCUMENT.md, 01-ui-orchestrator-flow.md
Tests	scripts/test_mvp.py, tests/test_contract_pipeline_unittest.py


New Field Added
Code
user_context: Optional[str]
Behavior Impact
Component	Impact
UI	Must capture new field and send in payload
Orchestrator	Must pass user_context into MASTER_CONTRACT
LLM Reasoner	Must include user_context in prompt construction
Contracts	Must add new field to UI_CONTRACT_V2
Tests	Must validate new field presence and propagation


Risk Level: Medium
Mitigation:
Contract-first update

Add tests for new field

Update design docs

Run CI profile with CR ID

✅ 4. UPDATED UI CONTRACT (UI_CONTRACT_V2)
New Contract Definition
json
{
  "symbol": "string",
  "exchange": "NSE | BSE",
  "timeframe": "daily | weekly | monthly | quarterly | yearly",
  "analysis_types": ["technical", "fundamental", "sentiment", "trend", "ai"],
  "risk_profile": "low | medium | high",
  "output_format": "json | html | email",
  "mode": "local | optimized | cloud",
  "user_context": "string | null"
}
FR Traceability
FR-01-002: UI payload must include all required fields

FR-05-001: LLM Reasoner must incorporate user context

FR-04-004: Orchestrator must include/exclude modules based on analysis types

✅ 5. AI IMPLEMENTATION NOTES (For LLM Reasoner)
Prompt Addition
Append this section to the LLM prompt:

Code
### User Context
The user has provided the following investment context:
"{user_context}"

Use this context to personalize the analysis, adjust tone, and highlight relevant risks.
Fallback Behavior
If user_context is empty:

Code
User context not provided. Use default neutral reasoning.
✅ 6. TESTER CHECKLIST (From tester-manual.md)
Targeted Tests
Code
python scripts/test_mvp.py
python scripts/test_llm_reasoning.py
python scripts/test_market_fetcher.py
python scripts/test_delivery.py
tests/test_contract_pipeline_unittest.py
Evidence to Validate
reports/TEST_REPORT.md

reports/run_summary_latest.csv

reports/test_case_results_latest.csv

reports/requirement_status_latest.csv

Exit Criteria
CR gate passes

CI profile passes

No unintended failures

Documentation updated

✅ 7. DEVELOPER CHECKLIST (From developer-manual.md)
Before Implementation
[ ] Run baseline sync

[ ] Create CR workspace

[ ] Complete impact analysis

[ ] Approve CR

After Implementation
[ ] Run all tests

[ ] Update design document

[ ] Update lessons learned

[ ] Update test report

[ ] Get approval before push

🎯 FINAL OUTPUT: What AI Should Do
AI must understand that:
User wants interactive UI

User wants structured settings

User wants context-aware reasoning

AI must update UI contract

AI must update orchestrator

AI must update LLM Reasoner

AI must follow CR governance

AI must update tests and docs

This package gives the AI everything needed to implement the feature safely, correctly, and traceably.