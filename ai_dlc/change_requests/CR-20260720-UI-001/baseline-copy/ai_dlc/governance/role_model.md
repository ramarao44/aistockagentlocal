# AI-DLC ROLE MODEL

Version: 1.0

## Pipeline Roles
- HIR: Human Intent Reviewer
- PL: Product Lead
- AA: Architect AI
- DEV: Developer AI
- QA: Quality AI
- OPS: Operations AI
- DOC: Documentation AI
- DME: Data and Metrics Engineer AI
- CCS: Change Control System

## Pre-Pipeline Role
- AISA: AI-DLC Solution Architect

## Role Interaction Contract
- HIR consumes Human Intent and PSC, emits ACCEPT/REJECT/CLARIFICATION/SCOPE EXPANSION and FIS draft.
- PL approves or rejects FIS draft.
- AA creates specs after approved FIS.
- DEV implements bolts from specs.
- QA validates implementation through governed tests.
- OPS validates runtime safety and operations.
- DOC publishes governed docs and release notes.
- DME maintains traceability and drift analysis.
- CCS gates protected changes and release readiness.
- AISA migrates legacy repositories to AI-DLC compliance.
