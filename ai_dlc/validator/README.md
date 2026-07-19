# AI-DLC Skill Validator

## Overview

Enterprise-grade validator that ensures skills cannot:
- Drift from governance
- Violate PSC domain boundaries
- Bypass role constraints
- Write to protected paths
- Produce unsafe outputs

## Usage

```powershell
# Validate all skills
python ai_dlc/validator/validate_skills.py

# Or via build profile
python scripts/build.py --profile ai-dlc-check
```

## Validation Rules

| Rule | Description |
|------|-------------|
| Schema | Required fields: name, version, role, description, constraints, writes-to, governed-flow |
| PSC Boundary | No trading, portfolio management, financial advice, crypto, forex keywords |
| Role Boundary | Skills can only write to paths allowed for their role |
| Protected Paths | Skills cannot write to PSC, FIS, prompts, governance |
| Output Location | Skills must write to governed destinations only |

## Role Permissions

| Role | Allowed Write Paths |
|------|---------------------|
| HIR | tickets/, change_requests/ |
| PL | fis.md |
| AA | specs/, traceability/ |
| DEV | bolts/, src/, scripts/ |
| QA | tests/ |
| OPS | runtime/ |
| DOC | docs/ |
| DME | traceability/ |
| CCS | governance/, tickets/ |

## Integration

The validator is automatically run during:
- `ai-dlc-check` build profile
- Pre-push hook (via gated CI validation)

## Adding New Skills

1. Create YAML with required schema
2. Validate: `python ai_dlc/validator/validate_skills.py`
3. Run: `HIR, use skill <path-to-skill>`