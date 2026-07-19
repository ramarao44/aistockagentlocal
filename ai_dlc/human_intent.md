# Human Intent: Governed Role Prompt Upgrade

## Request

Update the active AI-DLC role prompts and related guidance so prompt files are treated as governed, versioned, CCS-controlled artifacts rather than permanently frozen text.

## Objective

Improve AI-DLC role clarity, governance safety, traceability, and operational usefulness by adapting the updated detailed role prompt guidance into the current project framework.

The implementation should strengthen role responsibilities and outputs while keeping the workflow lightweight enough for normal development, documentation, cleanup, and validation work.

## Scope

Update active project guidance and active AI-DLC prompt artifacts:

- `ai_dlc/prompts/hir.prompt`
- `ai_dlc/prompts/pl.prompt`
- `ai_dlc/prompts/aa.prompt`
- `ai_dlc/prompts/dev.prompt`
- `ai_dlc/prompts/qa.prompt`
- `ai_dlc/prompts/ops.prompt`
- `ai_dlc/prompts/doc.prompt`
- `ai_dlc/prompts/dme.prompt`
- `ai_dlc/prompts/ccs.prompt`
- `ai_dlc/prompts/aisa.prompt`
- `ai_dlc/docs/governance_docs/prompt_versioning_policy.md`
- `README.md`

## Required Prompt Updates

For each active prompt file, add concise metadata:

- `Prompt-Version`
- `Status: Active`
- `Governance: CCS-controlled versioned artifact`
- `Scope: AI Stock Agent / Indian stock analysis`

Use the updated detailed role prompt content as source material, but adapt it to this repository’s current AI-DLC structure.

## Role Guidance

### HIR

- Validate Human Intent and defect reports against PSC and governance rules.
- Classify intent as New Feature, Enhancement, Bug Fix, Refactor, Performance Improvement, or Removal Request.
- Produce one of:
  - ACCEPT
  - REJECT
  - CLARIFICATION REQUIRED
  - SCOPE EXPANSION REQUEST
- If accepted, draft or propose FIS updates for PL approval.
- Create or update decision, clarification, or scope expansion tickets as applicable.
- Must not modify PSC, specs, bolts, tests, or runtime code.

### PL

- Review HIR FIS drafts.
- Approve or reject FIS updates with rationale.
- Validate alignment with PSC and project/product strategy.
- Trigger AA work only after FIS approval.
- Must not generate specs, bolts, tests, or runtime code.

### AA

- Generate feature, contract, and architecture specs from approved FIS.
- Map specs to existing modules and architecture boundaries.
- Preserve orchestrator-centric and non-breaking design.
- Must not implement code or tests.

### DEV

- Implement approved scope according to specs and bolts.
- Create or follow bolts when required by the approved workflow.
- Maintain backward compatibility unless explicitly approved.
- Link implementation to specs, bolts, and traceability.
- Must not modify PSC or FIS.
- Must not generate specs or QA-owned tests.

### QA

- Validate functionality, defects, and regression safety.
- Create or update tests using project conventions:
  - `ai_dlc/tests/**`
  - root `tests/**`
  - `scripts/test_*.py`
- Confirm defect reproduction and fix validation where applicable.
- Must not modify PSC, FIS, specs, or bolts.

### OPS

- Validate runtime behavior, safety, stability, and compliance.
- Ensure outputs do not provide trading or financial advice.
- Produce runtime evidence under `ai_dlc/runtime/**` where applicable.
- Must not modify PSC, FIS, specs, bolts, tests, or runtime code.

### DOC

- Maintain documentation, release notes, summaries, diagrams, manuals, and governance docs.
- Keep documentation aligned with current code, tests, runtime evidence, and AI-DLC artifacts.
- Produce one canonical summary/doc per request unless Human explicitly asks for another format.
- Avoid duplicate same-content docs.
- Must not modify PSC or FIS.

### DME

- Maintain traceability, coverage, drift analysis, and audit readiness.
- Link:
  `PSC -> Human Intent -> FIS -> Specs -> Bolts -> Tests -> OPS -> Docs -> Release`
- Update traceability, coverage, drift, and audit artifacts.
- Must not own narrative documentation, specs, bolts, tests, or runtime code.

### CCS

- Act as final governance gate for protected changes and release readiness.
- Validate lineage, safety, compliance, and protected artifact changes.
- Block unsafe, incomplete, or non-compliant transitions.
- Document PASS/BLOCK decisions with evidence.

### AISA

- Govern brownfield migration, cleanup, archive/delete recommendations, and AI-DLC structure alignment.
- Must not perform destructive cleanup without Human approval.
- Must preserve historical evidence unless deletion is explicitly approved.

## Prompt Versioning Policy

Create `ai_dlc/docs/governance_docs/prompt_versioning_policy.md`.

The policy must explain:

- Prompts are governed and versioned, not permanently frozen.
- `frozen_versions` in the manifest means current controlled baseline versions, not immutable forever.
- Prompt changes require Human Intent or CR context.
- Prompt changes require CCS-controlled review.
- Minor wording clarifications may keep the same major version.
- Role responsibility or ownership changes require a version bump.
- Prompt changes must pass AI-DLC validation before commit or push.

## README Updates

Update `README.md` to clarify:

- `gen/**` remains disposable generated output.
- Archived historical docs live under `ai_dlc/docs/archive/legacy-requirements/**`.
- Archived docs are historical reference only, not active acceptance criteria, traceability authority, or release evidence.
- Active AI-DLC prompts under `ai_dlc/prompts/**` are CCS-controlled versioned artifacts.

## Out of Scope

Do not modify:

- runtime application code
- baseline snapshots under `ai_dlc/baseline/snapshots/**`
- CR baseline copies under `ai_dlc/change_requests/**/baseline-copy/**`
- CR proposed copies under `ai_dlc/change_requests/**/proposed/**`
- generated `gen/**` output
- current report evidence unless validation tools update it automatically
- `ai_dlc/AI_DLC_MANIFEST.yaml` structure unless absolutely required for validation

Do not rename `frozen_versions` in the manifest in this pass. Document its interpretation instead.

## Governance Constraints

- Prompt files are protected artifacts and require CCS-controlled review.
- No role may bypass PSC, PL, or CCS.
- No role may approve trading, financial advice, unsafe behavior, or out-of-domain scope.
- No role may expand project scope without approved Change Request.
- Historical baseline and CR artifacts must remain unchanged unless a separate governed baseline/CR refresh is requested.

## Acceptance Criteria

- Active prompt files contain clear metadata headers.
- Active prompt files reflect the improved role responsibilities, constraints, and outputs.
- Prompt wording is concise and operational, not copied verbatim from long frozen templates.
- Prompt versioning policy exists and explains governed prompt evolution.
- README accurately describes archive, generated output, and prompt governance.
- No historical baseline snapshot or CR copy is edited.
- AI-DLC validation passes.

## Preferred Validation

```powershell
python scripts/build.py --profile ai-dlc-check
```

If committing and pushing:

```powershell
$env:AISA_CR_ID='CR-20260719-001'
git push origin RefactorProjectwithAIDLC
```

## Start Command

```text
HIR, process Human Intent.
```