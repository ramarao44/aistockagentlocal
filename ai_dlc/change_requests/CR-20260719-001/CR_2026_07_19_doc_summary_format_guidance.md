# Human Intent: Add AI-DLC Output Examples and PDF-Style DOC Summary Guidance

## Request
Add AI-DLC documentation examples and DOC generation guidance so AI-DLC roles can generate consistent, governed summary documentation without duplicating the same content across multiple formats.

## Objective
Create a reusable examples reference under `ai_dlc/docs/examples/` and update DOC guidance so generated summaries are written to `ai_dlc/docs/summary/` as one canonical PDF-style Markdown file per request.

## Required Changes
1. Create `ai_dlc/docs/examples/AI_DLC_OUTPUT_FORMATS.md`.
2. Include examples for:
   - AI-DLC request/review table
   - Role Responsibilities
   - Artifact Ownership
   - File Access Matrix
   - Governance Rules
   - Installation Checklist
   - Mermaid workflow diagram
   - PDF-style Markdown summary
   - README-style quick reference
   - Visual ASCII architecture map
3. Treat examples as templates/reference material, not as required duplicate generated outputs.
4. Update `ai_dlc/prompts/doc.prompt` so DOC uses:
   - `ai_dlc/docs/examples/` as the examples/template source
   - `ai_dlc/docs/summary/` as the output destination
   - PDF-style `.md` files as the preferred generated summary format
5. DOC must generate one canonical PDF-style Markdown summary per request unless Human explicitly asks for another format.
6. DOC must not generate duplicate summaries in README-style, ASCII, Mermaid-only, PDF-style, or other formats when the content is the same.
7. Tables, Mermaid diagrams, or ASCII maps may be embedded inside the PDF-style summary only when they add distinct information.
8. Use this generated summary filename convention:
   - `ai_dlc/docs/summary/YYYY_MM_DD_<topic>_summary.md`
9. Add `ai_dlc/human_intent_template.md` as a reusable reference for writing future Human Intent entries.

## Governance Authorization
This request authorizes a governed update to `ai_dlc/prompts/doc.prompt` for DOC summary output guidance, subject to CCS review.

## Governance Constraints
- Do not edit `ai_dlc/psc.md`.
- Do not edit `ai_dlc/human_intent.md` except for this human-authored request.
- Do not edit `ai_dlc/defects/` or `ai_dlc/change_requests/`.
- Do not modify `ai_dlc/AI_DLC_MANIFEST.yaml` unless CCS explicitly approves it.
- Keep generated/supporting docs separate from baseline governance docs.
- If prompt or documentation convention changes require traceability, update evidence under `ai_dlc/traceability/`.

## Preferred Output Style
Generated summaries must use PDF-style Markdown:
- clear title
- document metadata
- overview
- workflow/context
- tables where useful
- governance notes
- traceability note where applicable
- concise conclusion or next action

## Acceptance Criteria
- `ai_dlc/docs/examples/AI_DLC_OUTPUT_FORMATS.md` exists.
- The examples file contains all requested tables and output examples.
- `ai_dlc/human_intent_template.md` exists and provides a reusable Human Intent structure.
- `ai_dlc/prompts/doc.prompt` explicitly names PDF-style Markdown as the preferred generated summary format.
- `ai_dlc/prompts/doc.prompt` prevents duplicate generated summaries in different formats for the same content.
- `ai_dlc/docs/summary/` is the documented target for generated summary outputs.
- Generated summary filename convention is documented.
- Human-owned files remain unchanged except this Human Intent.
- `ai_dlc/AI_DLC_MANIFEST.yaml` remains unchanged unless separately approved by CCS.

## Start Command
HIR, process this Human Intent and prepare the governed AI-DLC workflow for implementation.