# Change Requests

Each change request (CR) lives in its own folder: `CR-YYYYMMDD-XXX`.

Required structure:
- `metadata.json`
- `baseline-copy/`
- `proposed/`
- `supporting/IMPACT_ANALYSIS.md`
- `supporting/AI_HANDOFF.md`

Rules:
- `baseline-copy` must come from active baseline snapshot.
- Edits are applied only in `proposed`.
- No implementation starts unless impact analysis is complete and CR status is `approved`.
