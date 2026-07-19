# AISA Migration Blueprint - AI Stock Agent

## 1. Goal
Migrate the existing AI Stock Agent repository into AI-DLC governance without breaking working features, and establish full traceability from PSC -> FIS -> Specs -> Code -> Tests -> Reports.

## 2. Scope
- Existing modules:
  - UI / Chainlit
  - Orchestrator
  - Ingestion (market_fetcher, symbol normalization)
  - Analysis (technical, fundamental, sentiment, timeframe)
  - AI reasoning (LLM reasoner)
  - Output (HTML, email, CSV, DB)
- Existing docs:
  - DESIGN_DEVELOPMENT_DOCUMENT.md
  - PRODUCT_CURRENT_STATUS.md
  - Quick reference, manuals
- Existing tests and reports.

## 3. Migration Steps (Conceptual)

1. Inventory & Classification
   - Scan repo and list all modules, tests, docs.
   - Map each to feature areas by code module boundaries and test coverage.
   - Record in traceability/fr_traceability_matrix.md using code-first mappings.

2. Baseline FIS Construction
   - From existing specs and docs, build initial FIS describing current behavior.
   - Store in fis.md with FIS_VERSION: 0.1 (baseline).

3. Align PSC & FIS
   - Ensure FIS does not violate PSC boundaries.
   - If any feature is out-of-scope, mark for deprecation via future CR.

4. Specs Backfill
   - For each major feature (UI, ingestion, technical, fundamental, sentiment, timeframe, output), generate specs under specs/.
   - Link specs to existing code and tests via traceability/.

5. Traceability Matrix
    - Build AI-DLC traceability matrix linking:
       - PSC -> FIS -> Specs -> Code -> Tests -> Runtime -> Docs -> Reports.
    - Derive mappings from code structure and test execution evidence, not legacy requirement catalogs.
   - Store in traceability/fr_traceability_matrix.md.

6. Governance Hooks
   - Enforce file access rules as per AI_DLC_MANIFEST.yaml.
   - Mark PSC, Human Intent, DR, CR as human-editable.
   - Mark FIS, specs, bolts, tests, prompts, governance as AI/CCS-controlled.

7. Defect & CR Channels
   - Create defects/ and change_requests/ folders.
   - Define DR and CR templates (already done).
   - Route all future issues and governance changes through DR/CR.

8. Activation
   - Once baseline migration is complete:
     - Human updates human_intent.md for next feature or improvement.
     - Run: HIR, process Human Intent.
     - AI-DLC pipeline becomes the only path for future changes.

## 4. Success Criteria
- No working feature is broken by migration.
- PSC, FIS, specs, bolts, tests, docs, traceability all exist and are consistent.
- All future changes flow through AI-DLC roles and governance.
- Defects and change requests are handled via DR/CR and not ad-hoc edits.

## 5. Notes
This blueprint is conceptual; actual execution is done by AISA (AI-DLC Solution Architect) and other roles using the prompts and artifacts defined in ai_dlc/.
Legacy requirement files may remain for historical context, but are not authoritative inputs for active AI-DLC traceability.
