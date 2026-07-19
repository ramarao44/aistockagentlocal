# 1. Feature Name
Short, precise name (e.g., "Market Data Fetcher", "Trend Score Engine").

# 2. Code Scope
List all code files that implement this feature.

- src/ingestion/market_fetcher.py
- src/analysis/trend/trend_score.py
- src/core/orchestrator.py
- src/database/crud.py
(Adjust per feature.)

# 3. Context from Code
- What the existing code does.
- What inputs it expects.
- What outputs it produces.
- Any known limitations or TODOs from comments.

# 4. User Stories (Derived from Code Behavior)
- As a <user>, I want <behavior>, so that <benefit>.
- As a <user>, I want <behavior>, so that <benefit>.

# 5. Functional Requirements (From Code + Intent)
- FR1: <Requirement mapped to specific functions/modules>.
- FR2: <Requirement>.
Link each requirement to code files/functions where possible.

# 6. Non‑Functional Requirements
- Performance expectations.
- Reliability.
- Scalability.
- UX/latency expectations (if relevant).

# 7. Architecture / Data Flow (From Current Implementation)
- Describe how data flows through the modules.
- Ingestion → Analysis → Timeframe → AI → DB → UI → Alerts.
- Mention orchestrator involvement if any.

# 8. Module Mapping (Exact Paths)
- src/ingestion/...
- src/analysis/...
- src/timeframe/...
- src/ai/...
- src/core/...
- src/database/...
- src/ui/...
- src/alerts/...

# 9. JSON Contract Impact
List contracts read/written by this feature:

- MARKET_DATA_CONTRACT_V1
- TECHNICAL_CONTRACT_V1
- FUNDAMENTAL_CONTRACT_V1
- TREND_CONTRACT_V1
- TIMEFRAME_CONTRACT_V1
- MASTER_CONTRACT_V1
(Adjust per feature.)

# 10. Debug Requirements (From Minimal Debug System)
Specify required dbg calls:

- dbg(master, "MODULE.SUBMODULE", "ACTION", "OK|ERR|WARN", "Short message", t)

Where:
- MODULE.SUBMODULE = code file / logical unit.
- ACTION = key operation (fetch, analyze, persist, alert).
- Status = OK/ERR/WARN.

# 11. Testing Requirements (From Existing + Needed)
- Unit tests for core functions.
- Integration tests across modules.
- Contract validation tests.
- Smoke tests (if profile‑related).

# 12. Risks & Mitigations
- Known edge cases from code.
- Data quality risks.
- External dependency risks (APIs, models).

# 13. Future Extensions
- Planned enhancements.
- Refactors.
- New contracts or modules that may be added.

# 14. Traceability Anchors
Map this feature to canonical docs and sections:

- 02_HighLevelArchitecture.md → Section 10 Architecture / Data Flow
- 03_ImplementationDesign.md → Section 7 Code File Mapping
- 04_FeatureRequirements.md → This feature’s section

# 15. AI Notes (For Future Code‑Driven Updates)
- Any assumptions AI should keep when regenerating this feature from code.
- Any files that must always be considered together with this feature.
