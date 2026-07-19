# Legacy Documentation Cleanup Recommendation

## Document Metadata

| Field | Value |
|-------|-------|
| Project | AI Stock Agent |
| Review Type | Legacy documentation cleanup analysis |
| Governance Mode | AI-DLC archive implementation approved by Human |
| Human Intent | Review Legacy Documentation Cleanup |
| Generated At | 2026-07-19 |
| Deletion Approved | No |
| Archive Approved | Yes |
| Archive Completed | Yes |

## Purpose

This document classifies legacy documentation and historical evidence candidates and records the approved archive action. No files are approved for deletion by this document.

Active governance authority remains with current code, tests, runtime evidence, README guidance, and AI-DLC artifacts. Legacy requirement catalogs are historical references only under `ai_dlc/docs/governance_docs/code_first_traceability_policy.md`.

## Cleanup Boundaries

The following paths are protected or current evidence and must not be deleted by this cleanup review:

- `ai_dlc/baseline/**`
- `ai_dlc/change_requests/**`
- `ai_dlc/runtime/**`
- `ai_dlc/traceability/**`
- `reports/TEST_REPORT.md`
- `reports/run_summary_latest.csv`
- `reports/test_case_results_latest.csv`
- `reports/module_status_latest.csv`
- `reports/failing_test_cases_latest.csv`
- `reports/failing_requirements_latest.csv`

## Recommendation Summary

| Path | Current Purpose | Authoritative? | Drift Risk | Recommendation | Impact of Archive/Delete |
|------|-----------------|----------------|------------|----------------|--------------------------|
| `feature-requirements/01-market-data-fetcher.md` | Historical feature requirements for market data fetching | No | Medium | Archive | Preserves early requirement intent while removing it from active guidance surface |
| `feature-requirements/02-technical-indicators.md` | Historical feature requirements for technical indicators | No | Medium | Archive | Keeps implementation reference without treating it as current governance authority |
| `feature-requirements/03-database-layer.md` | Historical feature requirements for database layer | No | Medium | Archive | Retains design history; active validation should remain code/test/report based |
| `feature-requirements/04-llm-reasoning.md` | Historical LLM reasoning requirements | No | High | Archive | Avoids conflict with current README/AI-DLC guidance while preserving local/cloud design history |
| `feature-requirements/05-charts-visualization.md` | Historical or future visualization requirements | No | Medium | Needs Human/CCS decision | May represent future scope; do not delete until roadmap status is confirmed |
| `feature-requirements/06-cloud-llm-integration.md` | Historical cloud fallback requirements | No | High | Archive | Preserves OpenAI fallback history; current dependency/API decisions must come from code and README |
| `feature-requirements/Template4_Feature‑from‑Code Specification.md` | Legacy feature-from-code template | No | Low | Archive | Low functional impact, but useful as historical template reference |
| `feature-requirements/input/feature_input.md` | Legacy feature input material | No | Medium | Needs Human decision | Content may be human-authored input; archive rather than delete unless Human confirms it has no value |
| `RefactorDesign/**` | Historical architecture prompts, MVP phase notes, and production design constitution | No | Medium | Archive | Preserves early refactor/design intent while removing it from the active repository guidance surface |
| `reports/TEST_REPORT_AUDIT_2026_07_09.md` | Historical Phase 2 audit report | No for current release gate; yes as audit history | Medium | Archive | Keeps historical audit trail while removing old conclusions from current evidence surface |
| `build/docs/**` | Historical generated build documentation | Not present | None | No action | No files found during review |
| `reports/TEST_REPORT.md` | Current canonical test report | Yes | Low | Keep active | Deletion would remove current validation evidence |
| `reports/*_latest.csv` | Current canonical report/evidence outputs | Yes | Low | Keep active | Deletion would break report evidence and AI-DLC validation expectations |
| `ai_dlc/docs/governance_docs/code_first_traceability_policy.md` | Current AI-DLC traceability authority policy | Yes | Low | Keep active | Deletion would remove the policy that defines legacy catalog status |
| `ai_dlc/docs/governance_docs/migration_deletion_inventory.md` | Historical deletion inventory for completed migration cleanup | Yes as governance record | Low | Keep active | Deletion would remove audit trail for previous governed cleanup |

## Recommended Archive Strategy

Prefer archive over deletion for the first implementation pass. Recommended archive destination:

```text
ai_dlc/docs/archive/legacy-requirements/
```

Suggested future moves, subject to Human approval:

| Source | Proposed Archive Destination |
|--------|------------------------------|
| `feature-requirements/*.md` | `ai_dlc/docs/archive/legacy-requirements/feature-requirements/` |
| `feature-requirements/input/feature_input.md` | `ai_dlc/docs/archive/legacy-requirements/feature-requirements/input/` |
| `RefactorDesign/**` | `ai_dlc/docs/archive/legacy-requirements/refactor-design/` |
| `reports/TEST_REPORT_AUDIT_2026_07_09.md` | `ai_dlc/docs/archive/legacy-requirements/reports/` |

Do not move or delete active report outputs under `reports/` in the same change.

## Archive Implementation Status

Human approved the archive-only cleanup after reviewing this recommendation. The following moves were completed:

| Source | Archived To | Status |
|--------|-------------|--------|
| `feature-requirements/*.md` | `ai_dlc/docs/archive/legacy-requirements/feature-requirements/` | Completed |
| `feature-requirements/input/feature_input.md` | `ai_dlc/docs/archive/legacy-requirements/feature-requirements/input/` | Completed |
| `RefactorDesign/**` | `ai_dlc/docs/archive/legacy-requirements/refactor-design/` | Completed |
| `reports/TEST_REPORT_AUDIT_2026_07_09.md` | `ai_dlc/docs/archive/legacy-requirements/reports/` | Completed |

The original `feature-requirements/` and `RefactorDesign/` source folders were removed after their contents were archived. Current canonical report outputs under `reports/` were not moved or deleted.

## Files Requiring Human or CCS Decision

| Path | Decision Needed |
|------|-----------------|
| `feature-requirements/05-charts-visualization.md` | Confirm whether this is future active roadmap input or purely historical |
| `feature-requirements/input/feature_input.md` | Confirm whether this human-authored input should be archived or retained in place |

No CCS-controlled file changes are required for the review-only recommendation. If a future implementation changes protected AI-DLC governance files, CCS approval is required.

## Proposed Next Human Intent

After reviewing this recommendation, Human approved the archive-only cleanup. Any future delete action should still use a separate implementation Human Intent that names the exact files to delete.

Completed implementation scope:

1. Created `ai_dlc/docs/archive/legacy-requirements/`.
2. Moved approved `feature-requirements/**` files into the archive path.
3. Moved approved `RefactorDesign/**` files into the archive path.
4. Moved `reports/TEST_REPORT_AUDIT_2026_07_09.md` into the archive path.
5. Preserved current canonical reports and AI-DLC evidence.
6. Ran AI-DLC validation after the archive move.

## Validation Recommendation

For this review-only artifact:

```powershell
python scripts/build.py --profile ai-dlc-check
```

For a future approved archive/delete implementation linked to a CR:

```powershell
python scripts/build.py --profile ci --cr-id <CR-ID>
```

## Conclusion

The highest drift-risk items were the legacy `feature-requirements/**` catalog, the unreferenced `RefactorDesign/**` architecture prompts, and the old `reports/TEST_REPORT_AUDIT_2026_07_09.md` audit report. They have been archived under AI-DLC documentation after Human approval so current guidance remains centered on README, code/test evidence, and AI-DLC governed artifacts.