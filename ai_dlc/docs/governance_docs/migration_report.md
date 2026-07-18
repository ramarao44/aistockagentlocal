# BROWNFIELD MIGRATION REPORT

Status: Completed

## 1. Source Governance Inventory
- Legacy governance roots were identified in docs/, gen/docs/, root markdown governance notes, and legacy build gate constants.

## 2. Mapping to AI-DLC
- Governance source of truth moved to ai_dlc/.
- Legacy CR and baseline roots remapped to ai_dlc/change_requests and ai_dlc/baseline.
- Role prompts, governance rules, runtime flow, and traceability templates seeded under ai_dlc/.

## 3. Migration Actions
- Created standalone ai_dlc scaffold with prompts, governance, runtime, docs, traceability, specs/bolts/tests roots.
- Added build profile ai-dlc-check and strict gate validation in scripts/build.py.
- Enforced pre-push AI-DLC gate before CI gate.
- Updated README governance guidance to ai_dlc paths.
- Removed superseded legacy documentation paths listed in migration deletion inventory.

## 4. Validation Outcomes
- AI-DLC gate validation passed using profile ai-dlc-check.
- CR lifecycle validation passed for CR-20260719-001 (cr-prepare -> cr-impact-check -> ci).
- CI run passed with strict fresh-evidence checks and full test gate.

## 5. Pending Risks
- Legacy automation outside build.py may still reference deleted legacy docs and should be checked in future runs.

## 6. Activation Recommendation
- Activation criteria met. AI-DLC is now the active governance framework for this repository.
