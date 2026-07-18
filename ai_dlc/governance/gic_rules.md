# GIC RULES (GLOBAL INSTRUCTION CHECK)

1. Before every pipeline stage, run GIC validation.
2. GIC validates intent constraints, role boundaries, ownership rules, and protected paths.
3. On GIC failure, stop execution and emit blocking report.
4. GIC report must be persisted under ai_dlc/runtime/gic_latest.md.
