# Validation Gates

## Gate 1: Canonical Structure Validation
- Confirm existence of:
  - 00_AI_Product_Development_Approach.md
  - 01_BusinessCase.md
  - 02_HighLevelArchitecture.md
  - 03_ImplementationDesign.md
  - 04_FeatureRequirements.md
- Confirm each canonical doc contains sections 1..18 in required order (Unified Documentation Template v5.0).

## Gate 2: AI Relevance Consistency
- Verify mandatory classification:
  - 00_AI_Product_Development_Approach.md = AI_CRITICAL
  - 01_BusinessCase.md = AI_CRITICAL
  - 02_HighLevelArchitecture.md = AI_CRITICAL
  - 03_ImplementationDesign.md = AI_CRITICAL
  - 04_FeatureRequirements.md = AI_CRITICAL
- Verify document_index.json ai_relevance values align with AI_relevance_policy.md.
- Verify AI_CRITICAL/ai_critical_manifest.json matches all AI_CRITICAL entries in document_index.json.
- Verify AI_SUPPORTING/ai_supporting_manifest.json matches all AI_SUPPORTING entries in document_index.json.
- Verify PROJECT_ONLY/project_only_manifest.json matches all PROJECT_ONLY entries in document_index.json.

## Gate 3: Mapping Coverage
- Compute denominator from coverage_scope_contract.md.
- Confirm all in-scope files are present in code_document_map.json mappings.
- Confirm no mapping has empty documents list.
- Confirm each mapping has non-empty anchors for each mapped document.
- Confirm unmapped in-scope files are absent, or justified in exception_registry.json.

## Gate 4: Schema Validation
- Validate against:
  - schemas/document_dependencies.schema.json
  - schemas/code_document_map.schema.json
  - schemas/document_index.schema.json
  - schemas/document_changelog.schema.json
  - schemas/exception_registry.schema.json
  - schemas/requirement_test_traceability.schema.json

## Gate 5: Dependency Graph Consistency
- Confirm upstream/downstream links in canonical docs and document_dependencies.json do not conflict.
- Confirm any dependency change is accompanied by changelog update.

## Gate 6: Section-Level Anchor Consistency
- For code_document_map.json, verify anchor strings correspond to section labels used in canonical docs.

## Gate 7: Acceptance
A release is documentation-valid only when all gates pass with zero critical failures.

## Gate 8: Retrieval Boundary Check
- Verify default retrieval flow includes AI_CRITICAL manifest entries and only task-selected AI_SUPPORTING.
- Verify PROJECT_ONLY manifest is excluded unless explicitly requested by task intent.

## Gate 9: Requirement-Test Traceability Integrity
- Verify `gen/docs/requirement_test_traceability.json` exists and parses.
- Verify every active requirement ID has mapped test coverage or justified exception.
- Verify latest run artifacts exist:
  - `reports/TEST_REPORT.md`
  - `reports/run_summary_latest.csv`
  - `reports/test_case_results_latest.csv`
  - `reports/failing_requirements_latest.csv`
  - `reports/requirement_status_latest.csv`

## Gate 10: Anti-Bloat Documentation Check
- Verify `docs/PRODUCT_CURRENT_STATUS.md` remains concise and references generated artifacts instead of duplicating full status tables.
- Verify no duplicate status ownership across canonical docs and generated reports.

## Gate 11: Baseline Integrity
- Verify `docs/baseline/active_baseline.json` exists and points to an existing snapshot.
- Verify active snapshot has `manifest.json` with checksums.
- Verify baseline snapshots are immutable after activation.

## Gate 12: Change Request Structure and Impact Analysis
- Verify each active CR has required folders: `baseline-copy`, `proposed`, `supporting`.
- Verify `metadata.json` exists and includes baseline id, status, and owner.
- Verify `supporting/IMPACT_ANALYSIS.md` contains required sections:
  - Changed Documents
  - Code Impact
  - Test Impact
  - Risks and Rollback
  - Consistency Updates

## Gate 13: Implementation Precondition
- Verify non-trivial implementation tasks reference approved CR id.
- Verify CR status is `approved` before implementation starts.
- Verify AI handoff references active baseline id and impact analysis evidence.
