# Tester Manual

## Purpose
This manual defines how testers validate functionality, regression safety, governance gates, and documentation evidence.

## Test Readiness Checklist
- Confirm CR exists and is approved for non-trivial change.
- Confirm impact analysis has all required sections.
- Confirm test environment is activated.

## Core Validation Sequence
1. Run CR impact gate.
2. Run targeted tests for changed area.
3. Run gated CI profile with CR id.
4. Verify report and summary artifacts.

Commands:
```powershell
python scripts/build.py --profile cr-impact-check --cr-id CR-YYYYMMDD-XXX
python scripts/build.py --profile ci --cr-id CR-YYYYMMDD-XXX
```

## Targeted Test Commands
```powershell
python scripts/test_market_fetcher.py
python scripts/test_vwap.py
python scripts/test_delivery.py
python scripts/test_ai_report.py
python scripts/test_llm_reasoning.py
```

## Profile Launchers
```powershell
build-profiles\ci.bat
build-profiles\all-profiles-smoke.bat
build-profiles\all-profiles-smoke.bat full
```

## Evidence to Validate
- reports/TEST_REPORT.md
- reports/run_summary_latest.csv
- reports/test_case_results_latest.csv
- reports/failing_requirements_latest.csv
- reports/requirement_status_latest.csv
- build/build_summary_latest.txt
- build/docs/index.json (when docs packaging is enabled)

## Non-Breaking Exit Criteria
- CR gate passes.
- CI profile passes.
- No unintended failures in related modules.
- Documentation updates are present for changed behavior.
- Requirement and test evidence are consistent.

## Push-Gate Note
If validating full push path locally, set CR id first:
```powershell
$env:AISA_CR_ID="CR-YYYYMMDD-XXX"
```
