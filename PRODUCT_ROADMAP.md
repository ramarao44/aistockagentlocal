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

## 🔄 Phase 2 - Database Layer (IN PROGRESS)

### Features
| Feature | Status | Notes |
|---------|--------|-------|
| SQLite database setup | ✅ DONE | `src/db/database.py` |
| SQLAlchemy models | ✅ DONE | `src/database/models.py` |
| CRUD operations | ✅ DONE | `src/database/crud.py` |
| Market data storage | ✅ DONE | `save_market_data()` |
| Indicator storage | ✅ DONE | `save_indicators()` |
| News storage | ✅ DONE | `save_news()` |
| Sentiment storage | ✅ DONE | `save_sentiment()` |
| Delivery data storage | ✅ DONE | `save_daily_record()` |

### Known Issues
- [ ] Delivery percentage returns 0.0 (Moneycontrol scraping)
- [ ] MA200 sometimes returns None (insufficient data)

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

---

## 📝 Change Log

| Date | Version | Changes |
|------|---------|---------|
| 2026-07-07 | 1.0 | Initial roadmap creation |

---

**Remember:** This is a living document. Update it as features are implemented and priorities change.