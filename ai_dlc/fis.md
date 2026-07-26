# FINAL INTENT STATEMENT (FIS)

Status: AI-owned artifact. Do not edit directly as human.

## 1. Intent Summary
As a user, I want an interactive UI where I can select exchange (NSE/BSE), timeframe, risk profile, analysis types, and optionally provide my investment context, so that the AI Stock Agent can generate a personalized and accurate stock analysis.

## 2. Intent Type
New Feature Enhancement (UI/UX)

## 3. Scope and Impact
- Area: UI/UX Enhancement
- Files: src/ui/chainlit_ui.py, main.py, src/core/contracts/ui_contract.py, src/core/orchestrator.py, src/ai/llm_reasoner.py
- New Field: user_context (Optional[str]) added to UI contract

## 4. Acceptance Criteria
- UI captures exchange, timeframe, risk_profile, analysis_types selections
- UI provides user_context free-text field
- Orchestrator passes user_context to MASTER_CONTRACT
- LLM Reasoner incorporates user_context in prompt construction
- All tests validate new field presence and propagation
- CI profile passes with zero unintended failures

## 5. Constraints
- Must not modify PSC
- Must not bypass CCS
- Must stay within Indian stock analysis domain
- Must not provide financial advice
- Must preserve existing UI behavior while adding new features

## 6. Version
- 1.0

## 7. Decision Ticket ID
- FIS-UI-20260720-001
```
