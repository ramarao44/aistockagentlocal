# Document Update Protocol

## Purpose
Define the mandatory order of operations for updating canonical documentation and governance artifacts.

## Update Trigger Types
1. Code change in in-scope file.
2. Policy or taxonomy change.
3. Dependency/ownership/freshness change.
4. Exception creation or closure.
5. Baseline snapshot refresh.
6. Change request creation, approval, or closure.

## Mandatory Update Order
1. Identify impacted files from code_document_map.json.
2. Resolve impacted canonical docs using mapped documents and anchors.
3. Traverse dependency impact from document_dependencies.json.
4. For change requests, require baseline-copy and proposed structure under docs/change-requests.
5. Produce impact analysis before implementation with required sections:
- Changed Documents
- Code Impact
- Test Impact
- Risks and Rollback
- Consistency Updates
6. Apply required updates to canonical docs.
7. Update machine-readable governance artifacts:
- document_index.json
- document_dependencies.json (if relationships changed)
- code_document_map.json (if file coverage/anchors changed)
- exception_registry.json (if temporary gap exists)
- requirement_test_traceability.json (if requirement IDs, test mappings, or statuses changed)
- AI_CRITICAL/ai_critical_manifest.json (if AI_CRITICAL set changed)
- AI_SUPPORTING/ai_supporting_manifest.json (if AI_SUPPORTING set changed)
- PROJECT_ONLY/project_only_manifest.json (if PROJECT_ONLY set changed)
- document_changelog.json
8. Regenerate designated test run artifacts when test mappings or statuses are affected:
- reports/TEST_REPORT.md
- reports/run_summary_latest.csv
- reports/test_case_results_latest.csv
- reports/failing_requirements_latest.csv
- reports/requirement_status_latest.csv
9. Run validation_gates.md checks.
10. Run drift detection checks from drift_detection_protocol.md.

## Implementation Gate Rule
No implementation starts for a change request unless:
1. CR metadata status is approved.
2. Impact analysis is complete with no Pending Input placeholders.
3. Baseline id and CR id are recorded in implementation handoff.

## Strategy Coherence Rule
Any policy-level change must update:
- 00_AI_Product_Development_Approach.md
- AI_relevance_policy.md
- document_index.json
- document_changelog.json

## Approach Primacy Rule
00_AI_Product_Development_Approach.md is AI_CRITICAL and cannot be downgraded without explicit governance approval.

## Pending Input Rule
If repository evidence is insufficient, add Pending Input note in affected canonical doc section and record changelog entry.

## Classification Folder Rule
1. AI_CRITICAL, AI_SUPPORTING, and PROJECT_ONLY folders are classification views, not source-of-truth repositories.
2. document_index.json remains authoritative for ai_relevance assignments.
3. Manifests must be synchronized with document_index.json on every classification change.

## Exit Criteria
An update is complete only when:
1. Required canonical docs updated.
2. Required governance JSON updated.
3. Designated generated report artifacts are refreshed when applicable.
4. Schema checks pass.
5. Coverage checks pass.
6. Changelog entry exists.
