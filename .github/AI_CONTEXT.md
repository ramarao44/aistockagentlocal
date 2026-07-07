# AI Context - AI Stock Agent Project

**Version:** 1.0
**Last Updated:** 2026-07-07

---

## 🎯 Project Mission

Build a **local-first, privacy-preserving AI agent** for stock market analysis focused on **Indian stock markets (NSE/BSE)**. The system combines deterministic Python modules with local LLMs to generate technical analysis reports without sending data to external services.

---

## 🔑 Key Constraints

1. **Local-First:** All processing should work offline
2. **Privacy-Preserving:** No data leaves the local machine
3. **Real Data:** Use actual market data, not hallucinated
4. **Testable:** Every component must be independently testable
5. **Documented:** All changes must be documented

---

## 🏗️ Architecture Principles

1. **Separation of Concerns:**
   - Fetcher: Data retrieval (deterministic)
   - Analyzer: Technical indicators (deterministic)
   - Database: Data persistence
   - Reasoning: LLM interpretation

2. **Bottom-Up Development:**
   - Build and test each layer before moving up
   - Fetcher → Analyzer → Database → Reasoning → UI

3. **Error Handling:**
   - Graceful degradation
   - Clear error messages
   - Fallback mechanisms

---

## 📊 Current State

- **Phase:** 2 (Database Layer)
- **Status:** Working
- **Last Test:** 2026-07-07 (All tests PASS)
- **Next Milestone:** Charts & Visualization

---

## 🚫 Known Limitations

1. **Delivery Percentage:** Moneycontrol scraping returns 0.0 (needs fix)
2. **MA200:** Sometimes returns None due to insufficient data
3. **Large Models:** 8B+ models are slow on CPU

---

## ✅ What Works

1. Market data fetching via yfinance
2. Technical indicators (RSI, MACD, SuperTrend, ADX)
3. LLM integration with Ollama
4. Database storage (SQLite)
5. Chainlit UI
6. Email delivery
7. Webhook API

---

## 📋 Required Reading

Before making any changes, read:
1. `AI_INSTRUCTIONS.md` - Development workflow
2. `DESIGN_DEVELOPMENT_DOCUMENT.md` - Technical reference
3. `QUICK_REFERENCE.md` - Quick commands and locations
4. `TEST_REPORT_*.md` - Current test status

---

## 🔄 Development Flow

```
1. Understand → 2. Plan → 3. Implement → 4. Test → 5. Document → 6. Push
```

**DO NOT SKIP:** Steps 4 and 5 are mandatory before push.