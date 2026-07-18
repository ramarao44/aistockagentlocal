# INPUT OUTPUT TABLE

| Role | Required Inputs | Required Outputs |
| --- | --- | --- |
| HIR | PSC, Human Intent, prior defects/CRs | Accept/reject or ticket + FIS draft |
| PL | FIS draft, PSC | Approved/rejected FIS |
| AA | Approved FIS | feature_specs, contract_specs, architecture_specs |
| DEV | Approved specs and bolts | Code changes, implementation notes |
| QA | Specs and implementation | Test suites and pass/fail evidence |
| OPS | Test evidence and runtime policy | Runtime validation report |
| DOC | FIS, specs, tests, runtime validation | Release notes and governance docs |
| DME | All generated artifacts | Traceability map and drift report |
| CCS | Protected changes and governance state | Gate decision and repair plan |
| AISA | Existing repo + AI-DLC templates | Migration report and cleanup inventory |
