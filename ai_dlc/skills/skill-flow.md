# AI-DLC Skill Flow Diagram

## Skill → Role → Output Relationship

```mermaid
graph TD
    subgraph "Skills Framework"
        HI[human-intent] --> HIR[HIR]
        HI --> FIS_DRAFT[FIS Draft]
        
        CP[cr-prepare] --> HIR
        CP --> CR_FILE[CR File]
        
        CI[cr-impact] --> AA[AA]
        CI --> IMPACT[Impact Report]
        
        CA[cr-approve] --> PL[PL]
        CA --> APPROVED[Approved Status]
        
        BD[build-dev] --> DEV[DEV]
        BD --> BA[DEV/QA]
        BD --> BUILD_DEV[Build Artifacts]
        
        BR[build-release] --> CCS[CCS]
        BR --> QA_GATE[QA]
        BR --> OPS_GATE[OPS]
        BR --> DOC_GATE[DOC]
        BR --> RELEASE[Release Package]
        
        GC[govern-check] --> CCS
        GC --> PSC_CHECK[PSC Check]
        GC --> FIS_CHECK[FIS Check]
        GC --> SPECS_CHECK[Specs Check]
        GC --> GOVERNANCE_REPORT[Governance Report]
        
        TS[test-suite] --> QA
        TS --> TEST_RESULTS[Test Results]
        
        DS[doc-summary] --> DOC
        DS --> SUMMARIES[Summary Tables]
        DS --> DIAGRAMS[Mermaid Diagrams]
        
        TL[trace-link] --> DME[DME]
        TL --> MATRICES[Traceability Matrices]
    end

    style HIR fill:#e1f5fe
    style AA fill:#e8f5e1
    style PL fill:#fff3e0
    style DEV fill:#fce4ec
    style CCS fill:#f3e5f5
    style QA fill:#e0f2f1
    style OPS fill:#ffebee
    style DOC fill:#e3f2fd
    style DME fill:#f1f8e9
```

## Skill Execution Patterns

### Feature Development Flow
```mermaid
flowchart LR
    A[Human Intent] --> B[Create CR]
    B --> C[Impact Analysis]
    C --> D[PL Approval]
    D --> E[DEV Implementation]
    E --> F[Test Suite]
    F --> G[Govern Check]
    G --> H[Push to Remote]
```

### Build Profiles Flow
```mermaid
flowchart LR
    BUILD_DEV[build-dev] --> TEST[test-suite]
    TEST --> TRACE[trace-link]
    
    GOVERN[govern-check] --> BUILD_RELEASE[build-release]
    BUILD_RELEASE --> PUSH[git push]