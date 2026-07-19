# Prompt Versioning Policy

## Purpose

This policy defines how AI-DLC role prompts are governed, versioned, reviewed, and validated for the AI Stock Agent project.

## Policy

Active prompt files under `ai_dlc/prompts/**` are CCS-controlled versioned artifacts. They are governed baselines, not permanently immutable text.

The `frozen_versions` section in `ai_dlc/AI_DLC_MANIFEST.yaml` records the current controlled baseline versions. It does not mean prompts can never change. It means prompt changes must follow Human Intent or Change Request context, protected-path review, and AI-DLC validation.

## Required Change Context

Prompt changes require at least one of:

- Human Intent that names the prompt governance change.
- Approved Change Request that includes prompt or governance scope.
- CCS repair request for a blocked governance state.

## Version Guidance

- Wording clarifications that preserve role ownership and behavior may keep the same major version.
- Responsibility, ownership, output, or constraint changes require a version update.
- Changes that affect multiple roles should update all impacted prompt headers in the same governed change.
- The active prompt header must include `Prompt-Version`, `Status`, `Governance`, and `Scope`.

## Review Rules

- Prompt files are protected artifacts.
- Prompt changes require CCS-controlled review.
- Prompt changes must not bypass PSC, PL, or CCS.
- Prompt changes must not permit trading, financial advice, unsafe behavior, or out-of-domain scope.
- Prompt changes must preserve role separation unless a governed role-model change explicitly approves otherwise.

## Validation

Before commit or push, run:

```powershell
python scripts/build.py --profile ai-dlc-check
```

For CI or push-time validation linked to a CR, use the repository's governed CR validation flow.

## Historical Copies

Baseline snapshots and change request copies are historical comparison artifacts. Do not edit these copies by hand:

- `ai_dlc/baseline/snapshots/**`
- `ai_dlc/change_requests/**/baseline-copy/**`
- `ai_dlc/change_requests/**/proposed/**`

Refresh or replace them only through a deliberate governed baseline or change request workflow.