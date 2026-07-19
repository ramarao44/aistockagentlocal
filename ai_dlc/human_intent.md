# Human Intent: Review Legacy Documentation Cleanup

## Request

Review legacy documentation and historical evidence files to determine whether they should be retained, archived, moved, or deleted under AI-DLC governance.

## Objective

Reduce repository drift by separating active AI-DLC governance artifacts from historical or non-authoritative documentation, while preserving any files that are still useful for traceability, audit, or implementation reference.

## Scope

Review these areas:

- `feature-requirements/**`
- old report audit files under `reports/**`
- historical generated documentation under `build/docs/**` if present
- any legacy documentation files that duplicate AI-DLC governed artifacts
- any stale docs that conflict with README or AI-DLC manifest guidance

## Out of Scope

- Do not delete files during review without explicit approval.
- Do not delete `ai_dlc/baseline/**`.
- Do not delete `ai_dlc/change_requests/**`.
- Do not delete `ai_dlc/runtime/**`.
- Do not delete `ai_dlc/traceability/**`.
- Do not delete current canonical report outputs:
  - `reports/TEST_REPORT.md`
  - `reports/run_summary_latest.csv`
  - `reports/test_case_results_latest.csv`
  - `reports/module_status_latest.csv`
  - `reports/failing_test_cases_latest.csv`
  - `reports/failing_requirements_latest.csv`
- Do not modify runtime code.
- Do not modify AI-DLC protected files unless CCS explicitly approves it.

## Governance Constraints

- Treat `feature-requirements/**` as non-authoritative historical reference unless AI-DLC decides otherwise.
- Preserve files needed for audit, baseline comparison, CR history, or traceability.
- Prefer archiving over deletion when a file has historical value but is no longer active.
- Keep active guidance in README and AI-DLC artifacts.
- Avoid duplicate or conflicting guidance.

## Required Analysis

Create a cleanup recommendation that classifies reviewed files into:

1. Keep active
2. Archive
3. Delete
4. Convert into AI-DLC artifact
5. Needs Human/CCS decision

For each file or folder, include:

- current purpose
- whether it is authoritative
- drift risk
- recommended action
- impact of deletion or archive

## Acceptance Criteria

- A cleanup recommendation is produced before any deletion.
- Each reviewed file/folder has a clear classification.
- No protected AI-DLC evidence is deleted.
- No current validation/report evidence is deleted.
- Human approval is required before archive/delete actions.
- AI-DLC validation passes after any approved cleanup.

## Preferred Validation

For review-only analysis:

```powershell
python scripts/build.py --profile ai-dlc-check
```

For approved cleanup implementation linked to a CR:

```powershell
python scripts/build.py --profile ci --cr-id <CR-ID>
```

## Start Command

```text
HIR, process Human Intent.
```