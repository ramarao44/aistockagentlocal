# Human Intent: Integrate Skills Framework into AI-DLC Governance

## Request
I want to integrate the newly created `ai_dlc/skills/` framework into the formal AI-DLC governance structure so skills become first-class governed artifacts.

## Objective
Make skills a recognized part of the AI-DLC pipeline with manifest registration, build validation, and governed execution.

## Scope
- Add `ai_dlc/skills/` to `AI_DLC_MANIFEST.yaml` as AI-owned
- Add skill validation to `scripts/build.py` CI gate
- Create skill-runner.py for optional skill execution
- Update skill-catalog.md with execution examples

## Out of Scope
- Modifying PSC (domain boundaries remain unchanged)
- Changing FIS (no product requirement changes)
- Modifying role prompts (prompts work as-is)

## Business Motivation
Skills provide standardized, repeatable workflows for common governance operations. Integration ensures:
- Skills are validated before merge
- Skills are versioned and tracked
- Skills follow clean scope policy
- Skills cannot be bypassed or modified incorrectly

## Governance Constraints
- Do not bypass AI-DLC governance
- Do not modify PSC or FIS
- Do not modify `ai_dlc/AI_DLC_MANIFEST.yaml` without CCS review
- Keep human-owned and AI-owned artifacts aligned

## Domain and Safety Constraints
- Stay within Indian stock analysis domain
- Skills are documentation/workflow only - no trading behavior
- Skills respect existing file access policies

## Required Changes
1. `ai_dlc/AI_DLC_MANIFEST.yaml` - Add SKILLS_DIR to ownership and artifacts
2. `scripts/build.py` - Add AI_DLC_REQUIRED_SKILLS validation list
3. `ai_dlc/skills/skill-catalog.md` - Add execution command examples
4. `ai_dlc/skills/` - Add `__init__.py` marker file

## Acceptance Criteria
- `ai_dlc/skills/` is listed in manifest under AI-owned
- `build.py` validates skills directory on ai-dlc-check profile
- All 10 skills are recognized in CI validation
- Skills follow same governance as prompts/specs/bolts

## Start Command
HIR, process Human Intent and prepare governed AI-DLC workflow for skills integration.