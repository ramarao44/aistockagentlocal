# PROJECT SCOPE CONTRACT (PSC)

## 1. Project Identity
Project Name: AI Stock Agent
Domain: Stock Analysis (Indian Equity Market)
Primary Purpose: Provide structured, AI-assisted analysis of Indian stocks using technical, fundamental, sentiment, and timeframe layers.
High-Level Description: AI Stock Agent ingests Indian market data, applies layered analysis engines, and produces human-readable reports and outputs for research and monitoring. It does not execute trades or provide financial advice.
Target Users: Individual investors, analysts, and researchers who want structured analysis of Indian stocks.
Business Context: Research and decision-support tool, not a trading or advisory platform.

## 2. In-Scope Domain Areas
- Technical Analysis (trend, momentum, volatility, patterns)
- Fundamental Analysis (financials, ratios, growth, quality)
- Sentiment Analysis (news, events, basic sentiment signals)
- Timeframe Analysis (short/medium/long horizon reasoning)
- Market Data Ingestion (Indian stocks, NSE/BSE symbols)
- Report Generation (HTML, text, CSV, email, UI)
- Persistence and Storage (local DB, historical outputs)
- UI/UX for Stock Analysis (web UI, CLI, local tools)
- Metrics and Evaluation (trend scores, quality metrics)

## 3. Out-of-Scope / Forbidden Areas
- Real-time trade execution
- Portfolio management and optimization
- Crypto, Forex, Options, Futures analysis
- Social media scraping (Twitter, Reddit, etc.)
- Weather, macro forecasting, unrelated domains
- Blockchain integrations
- ML training pipelines for live models
- Personalized financial advice or recommendations

## 4. Domain Boundaries
- Only Indian stocks (NSE/BSE universe)
- Primary timeframe: daily; intraday only if explicitly added later via PSC update
- No real-time streaming feeds; batch or periodic ingestion only
- No external trading APIs (for example, Zerodha, Upstox) for execution
- No storage of personal financial data or user portfolios
- No Buy/Sell/Hold recommendations

## 5. Allowed Feature Categories
- New analysis modules (technical, fundamental, sentiment, timeframe)
- Enhancements to existing analysis engines
- Improvements to ingestion, normalization, and symbol handling
- UI/UX improvements for reports and workflows
- Performance improvements (speed, memory, scalability)
- Bug fixes and defect resolutions
- Documentation improvements (manuals, READMEs, diagrams)
- Testing improvements (coverage, regression, reliability)
- Refactors that preserve behavior and governance

## 6. Forbidden Feature Categories
- Trading automation
- Features that imply portfolio management or advisory
- Features that imply real-time execution or HFT
- Features that introduce unapproved external integrations
- Features that violate compliance, safety, or PSC boundaries

## 7. Compliance & Safety Constraints
- System must not generate explicit financial advice (for example, Buy X now).
- System must not execute trades or connect to brokerage APIs for orders.
- System must not store personal financial data or user portfolios.
- System must respect market data licensing and usage constraints.
- System must clearly label outputs as analysis and not advice.

## 8. Architectural Constraints
- Must use the existing orchestrator as the central coordination layer.
- Must preserve modular architecture (ingestion, analysis, AI reasoning, output).
- Must not bypass AI-DLC governance for any change.
- Must not introduce breaking changes without CCS-approved migration.
- Must keep traceability between PSC -> FIS -> Specs -> Code -> Tests -> Reports.

## 9. Scope Expansion Rules
- Any expansion (for example, new asset classes, new markets, new timeframes) requires:
	- Explicit human approval via Change Request (CR).
	- PSC update with version bump.
	- PL approval and CCS validation.
	- Documentation and traceability updates.

## 10. PSC Versioning
PSC Version: 1.0
Last Updated By: Rama Rao
Reason for Update: Initial AI-DLC installation for AI Stock Agent.
Decision Ticket ID: PSC-INIT-2026-07-19
