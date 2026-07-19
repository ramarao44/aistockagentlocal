# AI-DLC Skills Framework

## Overview

This directory contains governed skill definitions for the AI Stock Agent project following the AI-DLC architecture.

## What Are Skills?

Skills are **predefined, governed workflows** that encapsulate common operations while ensuring:
- Role-based execution (HIR, AA, DEV, QA, CCS, DOC, DME, PL)
- PSC boundary compliance
- Governance constraint enforcement
- Traceability tracking

## Available Skills

| Skill | File | Role | Purpose |
|-------|------|------|---------|
| Human Intent | `human-intent.yaml` | HIR | Submit feature requests |
| CR Prepare | `cr-prepare.yaml` | HIR | Create change request scaffolding |
| CR Impact | `cr-impact.yaml` | AA | Perform impact analysis |
| CR Approve | `cr-approve.yaml` | PL | Approve change requests |
| Build Dev | `build-dev.yaml` | DEV | Development build |
| Build Release | `build-release.yaml` | CCS | Release validation |
| Govern Check | `govern-check.yaml` | CCS | AI-DLC gate validation |
| Test Suite | `test-suite.yaml` | QA | Selective test execution |
| Doc Summary | `doc-summary.yaml` | DOC | Generate documentation |
| Trace Link | `trace-link.yaml` | DME | Update traceability |

## How to Use Skills

### Option 1: Reference in Human Intent
When submitting a Human Intent, reference the desired skill:

```text
HIR, use skill cr-prepare to scaffold CR-20260720-001 for adding portfolio tracking.
```

### Option 2: Direct Invocation
Call a specific skill by file path:

```text
Use skill: ai_dlc/skills/build-dev.yaml
```

### Option 3: Skill Catalog Reference
See `skill-catalog.md` for complete skill index and execution patterns.

## Skill YAML Schema

Each skill follows this structure:

```yaml
skill:
  name: <skill-name>
  version: 1.0
  role: <AI-DLC role>
  description: <what the skill does>
  inputs: [{name: <input>, required: true/false}]
  outputs: [<output descriptions>]
  governed-flow: [<flow stages>]
  constraints: [<governance rules>]
  writes-to: [<output paths>]
  requires: [<required prompts>]
```

## Governance Rules

1. **Skills cannot modify PSC or FIS** unless explicitly allowed
2. **CCS-controlled skills** require CCS review before execution
3. **Skills write to governed destinations** only
4. **Skills respect clean scope policy** - never touch protected paths

## Flow Diagrams

See `skill-flow.md` for Mermaid diagrams showing:
- Skill → Role → Output relationships
- Feature development flow
- Build profiles flow

## Adding New Skills

To create a new skill:
1. Copy an existing skill YAML as template
2. Update fields per your workflow
3. Submit Human Intent for governance approval
4. Create Change Request if modifying protected paths