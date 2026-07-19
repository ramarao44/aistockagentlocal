# AI-DLC Skill Catalog

Version: 1.0

## Available Skills

| Skill | Role | Description | Inputs | Outputs |
|-------|------|-------------|--------|---------|
| human-intent | HIR | Submit new Human Intent and trigger FIS draft | intent_text | FIS Draft, Decision Ticket |
| cr-prepare | HIR | Create CR scaffolding for governance changes | cr_title | CR file |
| cr-impact | AA | Perform impact analysis for CR | cr_id | Impact Analysis Report |
| cr-approve | PL | Approve CR for implementation | cr_id | Approved CR status |
| build-dev | DEV | Run development build | - | Build artifacts |
| build-release | CCS | Run release validation with full gates | - | Release package |
| govern-check | CCS | Validate all AI-DLC artifacts before merge | - | Governance Report |
| test-suite | QA | Run specific test modules | module | Test results |
| doc-summary | DOC | Generate AI-DLC summary tables and diagrams | - | Summary tables, Mermaid diagrams |
| trace-link | DME | Update traceability matrices | - | Updated matrices |

## Skill Execution Patterns

### Human Intent Flow
```
1. Use: human-intent skill
2. Then: cr-prepare skill
3. Then: cr-impact skill
4. Then: cr-approve skill (by PL)
5. Then: govern-check skill (before merge)
```

### Development Flow
```
1. Use: build-dev skill
2. Run: test-suite skill
3. Use: trace-link skill (update evidence)
```

### Release Flow
```
1. Ensure: All tests pass
2. Use: govern-check skill
3. Use: build-release skill
4. Then: git push with CR_ID
```

## Governance Notes

- All skills follow AI-DLC role ownership model
- Skills cannot modify PSC or FIS (unless explicitly allowed)
- CCS-controlled skills require CCS review
- Skills write to governed destinations only