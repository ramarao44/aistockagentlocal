# 1. Document Title
AI Product Development Approach

# 2. Summary
This document defines the operating approach for building and maintaining a durable, AI-usable documentation system for AI Stock Agent (Local-First).

# 3. Context
The repository has grown across multiple implementation and planning artifacts under docs, feature-requirements, RefactorDesign, and reports. This approach establishes one canonical documentation system under gen/docs to reduce drift and improve AI-assisted implementation reliability.

This model is extended with baseline and change-request governance lanes:
- Source authoring remains in original locations under docs.
- Governance artifacts and validation remain under gen/docs.
- Baseline snapshots are maintained under docs/baseline.
- Proposed changes are isolated under docs/change-requests.

# 4. Dependencies
- 01_BusinessCase.md
- 02_HighLevelArchitecture.md
- 03_ImplementationDesign.md
- 04_FeatureRequirements.md
- AI_relevance_policy.md
- coverage_scope_contract.md
- validation_gates.md
- drift_detection_protocol.md

# 5. Upstream Documents
- README.md
- docs/DESIGN_DEVELOPMENT_DOCUMENT.md
- docs/README.md
- docs/PRODUCT_ROADMAP.md

# 6. Downstream Documents
- document_dependencies.json
- code_document_map.json
- document_index.json
- document_update_protocol.md

# 7. Code File Mapping
- main.py
- src/core/orchestrator.py
- src/core/artifacts.py
- src/ai/llm_reasoner.py
- src/core/contracts/master_contract.py

# 8. Section-Level Anchors
- Section 10 Architecture / Data Flow: approach lifecycle and phase flow.
- Section 16 Freshness Policy: required review cadence.
- Section 17 Ownership: governance ownership model.

# 9. Requirements
- Maintain governance artifacts under gen/docs while preserving source authoring in docs.
- Enforce baseline snapshot governance under docs/baseline for AI comparison workflows.
- Enforce change-request isolation under docs/change-requests.
- Enforce AI relevance taxonomy for all maintained documents.
- Enforce schema-backed machine-readable governance artifacts.
- Ensure repository-only evidence and Pending Input marking for unknowns.

# 10. Architecture / Data Flow
1. Repository evidence is inventoried and classified.
2. Canonical docs are authored with fixed template order.
3. Baseline snapshot is generated from approved source docs.
4. Change request is scaffolded from active baseline and updated in proposed subtree.
5. Mandatory impact analysis compares baseline-copy vs proposed before implementation.
6. Machine-readable maps and dependencies are generated.
7. Validation gates and drift checks enforce consistency.
8. Updates follow document_update_protocol.md before acceptance.

# 11. JSON Contract Impact
This approach requires stable JSON contracts for:
- document_dependencies.json
- code_document_map.json
- document_index.json
- document_changelog.json
- exception_registry.json

# 12. Debug Requirements
- Keep document generation deterministic where possible.
- Record unresolved or ambiguous facts as Pending Input.
- Preserve provenance in archive metadata.

# 13. Testing Requirements
- Validate all machine-readable artifacts against JSON schemas.
- Verify in-scope coverage denominator and mapping completeness.
- Verify AI relevance classification consistency.

# 14. Risks & Mitigations
- Risk: documentation drift after code changes.
  - Mitigation: drift_detection_protocol.md and validation gates.
- Risk: speculative/non-repo facts.
  - Mitigation: repository-only source policy + Pending Input rule.
- Risk: ambiguous file coverage scope.
  - Mitigation: explicit coverage_scope_contract.md denominator.

# 15. Future Extensions
- Symbol-level code-to-doc mapping.
- Automated pull-request level doc impact checks.
- Retrieval-profile variants by task type.

# 16. Freshness Policy
- Mandatory review on every policy-level change.
- Mandatory review at least every 30 days even without policy change.
- Mandatory review when coverage denominator changes.

# 17. Ownership
- Owner: Documentation Governance Maintainer.
- Reviewer: Repository Maintainer.
- Approval Rule: policy changes require owner + reviewer approval.

# 18. Exceptions
- Any policy unknown is marked Pending Input.
- Any temporary divergence must be recorded in exception_registry.json with expiration rationale.
