# Code-First Traceability Policy

## Purpose
Define AI-DLC traceability authority for this repository after migration.

## Policy
1. Active traceability is generated from code, test execution, runtime evidence, and governed docs.
2. Traceability lineage must follow:
   PSC -> Human Intent -> FIS -> Specs -> Code -> Tests -> Runtime -> Docs -> Reports.
3. Legacy requirement catalogs are historical references only and are not governance authority.
4. Merge and release decisions must use current code-execution evidence, not archived requirement-only mappings.

## Required Evidence Categories
- Code evidence: changed modules, symbols, and interfaces.
- Test evidence: executed test cases and outcomes.
- Runtime evidence: GIC and CCS latest status artifacts.
- Documentation evidence: impacted AI-DLC docs and governance notes.

## Operational Guidance
- When conflict exists between historical requirement mappings and code execution evidence, use code execution evidence.
- Missing code-to-test linkage is a governance gap and must be fixed before release.
- Maintain traceability files under ai_dlc/traceability as the canonical record.

## Scope
This policy governs all future AI-DLC changes in this repository.
