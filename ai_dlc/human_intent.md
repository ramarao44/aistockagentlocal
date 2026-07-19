# Human Intent: Address OpenAI Dependency and Baseline Snapshot Documentation Feedback

## Request

Update the project to address two valid review findings from expert feedback:

1. Declare the OpenAI dependency used by the cloud LLM fallback path.
2. Add a concise README note explaining the AI-DLC baseline snapshot lifecycle.

## Objective

Ensure fresh project installs can support the documented OpenAI cloud fallback behavior, and improve governance clarity around how AI-DLC baseline snapshots are created, referenced, protected, and cleaned up.

## Business Motivation

The project documentation and feature requirements describe optional OpenAI cloud fallback. However, `requirements.txt` does not currently declare the `openai` package, so a fresh install may not support that documented path without manual dependency installation.

The AI-DLC baseline workflow exists and is already used, but README should make the snapshot lifecycle clearer for future maintainers and governed change requests.

## Scope

- Update `requirements.txt`.
- Update `README.md`.
- Keep the change limited to dependency declaration and baseline lifecycle documentation.
- Preserve existing local/Ollama LLM behavior.
- Preserve the current AI-DLC governance structure.

## Out of Scope

- Do not recreate `ai_dlc/docs/examples/AI_DLC_OUTPUT_FORMATS.md`; it already exists.
- Do not modify `ai_dlc/psc.md`.
- Do not modify `ai_dlc/AI_DLC_MANIFEST.yaml` unless CCS explicitly approves it.
- Do not modify LLM behavior unless required by the OpenAI SDK version decision.
- Do not modernize the OpenAI client in this change.
- Do not change unrelated dependencies.
- Do not clean, delete, or rewrite baseline snapshots.

## Governance Constraints

- Follow the AI-DLC workflow before implementation.
- Keep human-owned and AI-owned artifacts aligned with the file access policy.
- Keep generated/supporting documentation separate from baseline governance documents.
- Treat baseline snapshots as governed comparison evidence.
- Do not bypass CR impact analysis, validation, or CCS approval.

## Required Changes

1. Update `requirements.txt`.
	- Add the OpenAI dependency used by `src/ai/llm_reasoner.py`.
	- Use the smallest compatible dependency decision for the current implementation.
	- Pin the dependency as:

```text
openai<1
```

	- Reason: current code uses the legacy `openai.ChatCompletion.create()` API.

2. Update `README.md`.
	- Add a short section named `Baseline Snapshot Lifecycle` near the existing `Baseline and Change Request Workflow` section.
	- Explain that baseline snapshots are created with:

```powershell
python scripts/build.py --profile baseline-sync
```

	- Explain that `ai_dlc/baseline/active_baseline.json` points to the active baseline snapshot.
	- Explain that snapshots preserve the governance baseline used for CR comparison.
	- Explain that baseline snapshots are protected from default clean/build cleanup.
	- Explain that old snapshot cleanup, if needed, must be deliberate and governed.

## Acceptance Criteria

- `requirements.txt` includes:

```text
openai<1
```

- `README.md` includes a concise `Baseline Snapshot Lifecycle` note.
- README uses the correct baseline command:

```powershell
python scripts/build.py --profile baseline-sync
```

- Existing local/Ollama LLM behavior remains unchanged.
- Cloud fallback dependency is installable from a fresh:

```powershell
pip install -r requirements.txt
```

- No unrelated dependency or runtime behavior changes are introduced.
- Existing AI-DLC governance files remain unchanged unless approved through the workflow.

## Preferred Validation

Run:
Explain that old snapshot cleanup, if needed, must be deliberate and governed.
Acceptance Criteria
requirements.txt includes:
README.md includes a concise Baseline Snapshot Lifecycle note.
README uses the correct baseline command:
Existing local/Ollama LLM behavior remains unchanged.
Cloud fallback dependency is installable from a fresh:
No unrelated dependency or runtime behavior changes are introduced.
Existing AI-DLC governance files remain unchanged unless approved through the workflow.
Preferred Validation
Run:

The validation should pass with no new warnings or errors.

Linked Change Request
CR ID: to be created by AI-DLC workflow
CR path: to be created under change_requests