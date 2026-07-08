# Product Roadmap - AI Stock Agent

**Version:** 1.0
**Last Updated:** 2026-07-07
**Status:** Living Document

---

## 🎯 Vision
Build a comprehensive, local-first AI stock analysis platform for Indian markets that provides real-time technical analysis, sentiment analysis, and actionable investment insights.

---

## 📊 Current Phase: Phase 2 - Database Layer

| Status | Phase | Description |
|--------|-------|-------------|
| ✅ DONE | Phase 1 | Core Agent (UI, LLM, Basic Analysis) |
| 🔄 IN PROGRESS | Phase 2 | Database Layer (SQLite + SQLAlchemy) |
| ⏳ PENDING | Phase 3 | Charts & Visualization |
| ⏳ PENDING | Phase 4 | Multi-Agent Architecture |
| ⏳ PENDING | Phase 5 | Model Selector |
| ⏳ PENDING | Phase 6 | Streaming Output |
| ⏳ PENDING | Phase 7 | Enhanced Data Sources |
| ⏳ PENDING | Phase 8 | Fundamental Analysis |

---

## 🚀 Phase 1 - Core Agent (COMPLETED)

### Features Implemented
- [x] Chainlit UI for interactive analysis
- [x] Local LLM integration (Ollama)
- [x] Cloud LLM fallback (OpenAI)
- [x] Market data fetching (yfinance)
- [x] Technical indicators (RSI, MACD, MA20, MA50)
- [x] Basic report generation
- [x] Email delivery
- [x] Webhook API

### Test Status
- ✅ All tests passing (2026-07-07)

---

## 🔄 Phase 2 - Database Layer (UPDATED: 87.5% Complete ✨)

### Status Update (2026-07-09)
🔍 **Comprehensive Audit Completed:** Phase 2 audit revealed 3 critical issues affecting real completion rate:

**Before Audit:** 62.5% (claimed 100%)
**After Fixes:** 87.5% (3 issues resolved, 1 known limitation documented)

**Key Findings:**
- ✅ **FIXED:** Indicator storage schema was incomplete - added 13 new columns to capture all technical indicators
- ✅ **FIXED:** MA200 was returning None - extended data fetch period from 6mo to 1y 
- ⚠️ **IMPROVED:** Delivery volume gracefully handles web scraping failures (experimental feature)

**See:** `docs/AUDIT_REPORT_2026_07_09.md` for comprehensive findings and learning points

### Features
| Feature | Status | Implementation | Notes |
|---------|--------|---|---|
| SQLite database setup | ✅ DONE | `src/db/database.py` + `src/database/engine.py` | Dual-layer support (legacy + new SQLAlchemy) |
| SQLAlchemy models | ✅ DONE | `src/database/models.py` (30 columns) | Updated with all technical indicators |
| CRUD operations | ✅ DONE | `src/database/crud.py` | Full create/read operations working |
| Market data storage | ✅ DONE | OHLCV + 13 indicators | Now stores: RSI, MACD, MA20/50/200, ADX, Bollinger Bands, etc. |
| Indicator storage | ✅ **FIXED** | All 13 indicators persisted | **Audit Fix:** Was 0% implemented, now 100% complete |
| News storage | ✅ DONE | `src/fetcher/news_fetcher.py` | RSS feed pipeline working |
| Sentiment storage | ✅ DONE | `src/analyzer/sentiment_analyzer.py` | VADER sentiment scoring working |
| Delivery data storage | ⚠️ EXPERIMENTAL | Moneycontrol web scraping + NSE API option | **Known Limitation:** Web scraping unreliable, gracefully returns None |

### Known Issues & Limitations
- [ ] ~~Delivery percentage returns 0.0~~ → **Updated:** Returns None with graceful fallback (experimental, non-critical)
- [ ] ~~MA200 sometimes returns None~~ → **Fixed:** Extended data period from 6mo to 1y (now 252+ trading days)

---

## ⏳ Phase 3 - Charts & Visualization (PENDING)

### Features
| Feature | Status | Priority |
|---------|--------|----------|
| Price trend charts | ⏳ TODO | High |
| RSI chart visualization | ⏳ TODO | High |
| MACD chart visualization | ⏳ TODO | High |
| Bollinger Bands charts | ⏳ TODO | Medium |
| Support/Resistance visualization | ⏳ TODO | Medium |
| Interactive charts in Chainlit | ⏳ TODO | High |

---

## ⏳ Phase 4 - Multi-Agent Architecture (PENDING)

### Features
| Feature | Status | Priority |
|---------|--------|----------|
| Data Agent | ⏳ TODO | High |
| Analysis Agent | ⏳ TODO | High |
| LLM Agent | ⏳ TODO | High |
| Agent orchestration | ⏳ TODO | High |
| Inter-agent communication | ⏳ TODO | Medium |

---

## ⏳ Phase 5 - Model Selector (PENDING)

### Features
| Feature | Status | Priority |
|---------|--------|----------|
| UI dropdown for model selection | ⏳ TODO | High |
| Model performance metrics | ⏳ TODO | Medium |
| Auto model selection | ⏳ TODO | Low |
| Model comparison view | ⏳ TODO | Low |

---

## ⏳ Phase 6 - Streaming Output (PENDING)

### Features
| Feature | Status | Priority |
|---------|--------|----------|
| Stream report generation | ⏳ TODO | High |
| Loading spinner | ⏳ TODO | Medium |
| Progress indicators | ⏳ TODO | Low |
| Real-time updates | ⏳ TODO | Medium |

---

## ⏳ Phase 7 - Enhanced Data Sources (PENDING)

### Features
| Feature | Status | Priority |
|---------|--------|----------|
| Alpha Vantage API | ⏳ TODO | Medium |
| Finnhub API | ⏳ TODO | Medium |
| Polygon.io API | ⏳ TODO | Low |
| Multiple data source fallback | ⏳ TODO | High |

---

## ⏳ Phase 8 - Fundamental Analysis (PENDING)

### Features
| Feature | Status | Priority |
|---------|--------|----------|
| Financial statements fetching | ⏳ TODO | High |
| P/E ratio analysis | ⏳ TODO | High |
| P/B ratio analysis | ⏳ TODO | Medium |
| Debt-to-equity ratio | ⏳ TODO | Medium |
| ROE/ROCE calculations | ⏳ TODO | High |
| Revenue/Profit growth analysis | ⏳ TODO | High |
| Earnings calendar integration | ⏳ TODO | Medium |
| Fundamental score algorithm | ⏳ TODO | High |
| Fundamental + Technical combined report | ⏳ TODO | High |

### Fundamental Metrics to Implement
- **Valuation Ratios:** P/E, P/B, PEG, EV/EBITDA
- **Profitability:** ROE, ROCE, ROA, Net Margin
- **Growth:** Revenue growth, EPS growth, 3-year CAGR
- **Financial Health:** Debt/Equity, Current Ratio, Interest Coverage
- **Efficiency:** Asset Turnover, Inventory Turnover
- **Dividend:** Dividend Yield, Payout Ratio

---

## 📈 Future Enhancements (BACKLOG)

### Advanced Features
- [ ] Portfolio analysis
- [ ] Multi-stock comparison
- [ ] Alert system
- [ ] Backtesting engine
- [ ] Custom indicator builder
- [ ] Export to PDF/Excel
- [ ] Mobile-responsive UI

### AI Improvements
- [ ] Fine-tuned model for stock analysis
- [ ] Multi-modal (charts + text)
- [ ] Voice input/output
- [ ] Natural language queries

### Infrastructure
- [ ] Docker deployment
- [ ] Cloud deployment option
- [ ] CI/CD pipeline
- [ ] Automated testing
- [ ] Performance monitoring

---

## 📊 Feature Priority Matrix

| Priority | Features |
|----------|----------|
| **High** | Charts, Multi-Agent, Model Selector, Multiple Data Sources |
| **Medium** | Streaming, VWAP improvements, Export features |
| **Low** | Voice, Mobile UI, Advanced backtesting |

---

## 📅 Timeline (Estimated)

| Phase | Target Date | Status |
|-------|-------------|--------|
| Phase 2 | 2026-07-15 | In Progress |
| Phase 3 | 2026-07-30 | Pending |
| Phase 4 | 2026-08-15 | Pending |
| Phase 5 | 2026-08-30 | Pending |
| Phase 6 | 2026-09-15 | Pending |
| Phase 7 | 2026-09-30 | Pending |
| Phase 8 | 2026-10-15 | Pending |

---

## 📝 Change Log

| Date | Version | Changes |
|------|---------|---------|
| 2026-07-07 | 1.0 | Initial roadmap creation + Fundamental Analysis phase |

---

**Remember:** This is a living document. Update it as features are implemented and priorities change.