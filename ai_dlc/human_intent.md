# Human Intent: Remove Legacy GitHub AI Context File

## Request

Remove the legacy `.github/AI_CONTEXT.md` file because project guidance is now governed by the AI-DLC framework.

## Objective

Avoid conflicting or stale AI guidance by keeping project review and implementation guidance aligned with AI-DLC artifacts, README, and future `.github/instructions/` files.

## Scope

- Delete `.github/AI_CONTEXT.md`.
- Optionally add `.github/AI_CONTEXT.md` to `.gitignore` if local tools may recreate it.
- Keep `.github/instructions/**` trackable for Copilot/GitHub review instructions.

## Out of Scope

- Do not delete `.github/`.
- Do not ignore `.github/`.
- Do not modify AI-DLC protected files.
- Do not change runtime code.
- Do not change README unless needed to clarify the replacement guidance.

## Acceptance Criteria

- `.github/AI_CONTEXT.md` is removed from the repository.
- `.github/` remains available for future instructions.
- `.github/instructions/*.instructions.md` files can be added and tracked.
- AI-DLC validation passes.

## Preferred Validation

```powershell
python scripts/build.py --profile ai-dlc-check
```

If linked to a CR, run:

```powershell
python scripts/build.py --profile ci --cr-id <CR-ID>
```

## Start Command

```text
HIR, process Human Intent.
```