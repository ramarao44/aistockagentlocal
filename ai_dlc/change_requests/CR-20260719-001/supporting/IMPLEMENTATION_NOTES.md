# Implementation Notes

- Keep baseline-copy unchanged.
- Do not manually pre-stage proposed artifacts for Option A.
- Agent mode will create implementation artifacts after approval.
- Scope is documentation/process guidance only.
- Do not modify product code.
- Do not modify build hooks, CI gates, migration reports, or unrelated governance files.
- Do not modify ai_dlc/psc.md.
- Do not modify ai_dlc/AI_DLC_MANIFEST.yaml unless CCS separately approves it.
- Update ai_dlc/prompts/doc.prompt only under governed approval because prompts are CCS-controlled.
- Generated summaries must be one canonical PDF-style Markdown file per request.
- Tables, Mermaid diagrams, or ASCII maps may be embedded only when they add distinct information.
- Existing proposed/ snapshot content must not be treated as authoritative for this CR until Agent mode regenerates or replaces it.