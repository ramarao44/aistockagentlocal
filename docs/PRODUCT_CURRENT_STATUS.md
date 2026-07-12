# Product Current Status

## Summary
This is the single operational status source for current feature health.

Status is evidence-driven from:
- `gen/docs/requirement_test_traceability.json`
- `reports/TEST_REPORT.md`
- latest CSV outputs in `reports/`

## Working Model
- Working: requirement has passing assertive mapped tests in latest designated run.
- Partial: implementation exists but assertive mapped tests are missing or incomplete.
- Not Working: mapped tests failing or requirement explicitly not implemented.
- Pending Input: repository evidence is insufficient.

## Latest Review Inputs
- Markdown summary: `reports/TEST_REPORT.md`
- Run aggregate: `reports/run_summary_latest.csv`
- Test-case results: `reports/test_case_results_latest.csv`
- Failing requirements: `reports/failing_requirements_latest.csv`
- Requirement status: `reports/requirement_status_latest.csv`

## Feature Snapshot
Use `reports/requirement_status_latest.csv` to filter by `feature` and `status`.

## What Needs Implementation
Current non-implemented items are tracked under feature `charts-visualization` in:
- `gen/docs/requirement_test_traceability.json`
- `reports/requirement_status_latest.csv`

## Notes
- This file stays concise by design.
- Do not duplicate large status tables here; use linked CSV views.
