# PROJECT SCOPE CONTRACT (PSC)

## 1. Project Identity
Project Name: AI Stock Agent (Local-First)
Domain: Stock analysis
Primary Purpose: Provide stock analysis insights for Indian markets without automated trading
Target Users: Analysts and learners
Business Context: Deterministic analysis with AI-assisted summaries

## 2. In-Scope Domain Areas
- Market data ingestion and normalization
- Technical analysis indicators
- Fundamental and sentiment analysis
- Timeframe and trend evolution analysis
- Report generation, persistence, and delivery
- Testing, observability, and documentation of above

## 3. Out-of-Scope / Forbidden Areas
- Real-time trade execution
- Portfolio management and order routing
- Direct financial advice
- Non-stock domains unrelated to stock analysis

## 4. Domain Boundaries
- Focus on Indian market stock analysis workflows
- No autonomous execution of trades
- No recommendations framed as financial advice

## 5. Allowed Feature Categories
- New analysis modules
- Enhancements to existing analysis
- Bug fixes and reliability improvements
- Performance and usability improvements
- Documentation and traceability improvements

## 6. Forbidden Feature Categories
- Trading automation
- Account management or broker integrations for order placement
- Any workflow violating safety or compliance constraints

## 7. Compliance and Safety Constraints
- No trading actions
- No financial advice
- No unsafe behavior

## 8. Architectural Constraints
- Preserve modular pipeline boundaries
- Preserve governed traceability and test evidence
- Preserve deterministic fallback behavior in core paths

## 9. Scope Expansion Rules
- Requires explicit human approval
- Requires scope expansion ticket
- Requires PL and CCS approval

## 10. PSC Versioning
Version: 1.0
Status: Human-owned
