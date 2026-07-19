# Human Intent Template

Use this template as a reference when writing `ai_dlc/human_intent.md` for a governed AI-DLC change. Replace all placeholder text before submitting the intent.

## Request
Describe the change you want in plain language.

Example:
I want to update the documentation generation process so DOC produces one canonical PDF-style Markdown summary per request.

## Objective
State the outcome the change should achieve.

Example:
Create reusable examples, define the generated-summary destination, and prevent duplicate same-content outputs in multiple formats.

## Scope
List what is included.

- In scope item 1
- In scope item 2
- In scope item 3

## Out of Scope
List what must not change.

- Out of scope item 1
- Out of scope item 2
- Out of scope item 3

## Business Motivation
Explain why this change is needed and what problem it solves.

## Governance Constraints
List AI-DLC constraints that must be respected.

- Do not bypass AI-DLC governance.
- Do not modify PSC unless the request explicitly requires a PSC change.
- Do not modify `ai_dlc/AI_DLC_MANIFEST.yaml` unless CCS explicitly approves it.
- Keep human-owned and AI-owned artifacts aligned with the file access policy.
- Keep generated/supporting docs separate from baseline governance docs.

## Domain and Safety Constraints
List domain boundaries and safety rules relevant to the request.

- Stay within Indian stock analysis unless PSC is formally updated.
- Do not add trading execution, portfolio management, or financial-advice behavior.
- Do not introduce unrelated domains or unapproved integrations.

## Required Changes
List the concrete documents, modules, prompts, specs, or workflows expected to change.

1. Change item 1
2. Change item 2
3. Change item 3

## Acceptance Criteria
Define how the AI-DLC roles and Human can verify the change is complete.

- Acceptance criterion 1
- Acceptance criterion 2
- Acceptance criterion 3

## Linked Change Request
If this Human Intent is implemented through a CR, provide the CR ID and path.

- CR ID: `CR-YYYYMMDD-NNN`
- CR path: `ai_dlc/change_requests/CR-YYYYMMDD-NNN/`

## Start Command
Use the relevant start command after the Human Intent is ready.

```text
HIR, process Human Intent.
```

For a linked CR:

```text
HIR, process Human Intent and linked Change Request CR-YYYYMMDD-NNN.
```
