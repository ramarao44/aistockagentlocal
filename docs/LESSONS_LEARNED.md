# Lessons Learned - AI Stock Agent Project

**Version:** 1.0
**Last Updated:** 2026-07-07
**Purpose:** Document technical challenges, solutions, and best practices for future reference and interview preparation

---

## 📚 Table of Contents
1. [Library Compatibility Issues](#library-compatibility-issues)
2. [Data Handling Challenges](#data-handling-challenges)
3. [LLM Integration Lessons](#llm-integration-lessons)
4. [Architecture Decisions](#architecture-decisions)
5. [Performance Optimizations](#performance-optimizations)
6. [Debugging Techniques](#debugging-techniques)

---

## 🔧 Library Compatibility Issues

### 1. yfinance MultiIndex Column Problem
**Problem:** yfinance often returns DataFrames with MultiIndex columns when downloading data, causing downstream processing failures.

**Solution:**
```python
# Check and flatten MultiIndex columns
if isinstance(df.columns, pd.MultiIndex):
    try:
        df.columns = df.columns.get_level_values(0)
    except Exception:
        df.columns = ["_".join(map(str, c)).strip() for c in df.columns]
```

**Key Takeaway:** Always normalize yfinance output before processing. MultiIndex is common and must be handled explicitly.

---

### 2. llama-cpp-python on Windows
**Problem:** Installing llama-cpp-python on Windows requires special AVX2/AVX512 wheels. Pip often tries to compile from source, which fails without MSVC + CMake.

**Solution:** Use Ollama instead of direct llama-cpp integration.
- Ollama provides a simple HTTP API
- No wheel compatibility issues
- Works instantly on Windows
- Supports multiple models

**Key Takeaway:** For Windows development, prefer Ollama over llama-cpp-python. It's more reliable and easier to set up.

---

### 3. pandas-ta vs ta Library
**Problem:** pandas-ta is abandoned and has compatibility issues.

**Solution:** Use the actively maintained `ta` library for technical indicators.

**Key Takeaway:** Always use actively maintained libraries. Check GitHub activity before choosing a library.

---

## 📊 Data Handling Challenges

### 1. Technical Indicator Minimum Data Requirements
**Problem:** Technical indicators require minimum data points to compute, leading to NaN values.

| Indicator | Minimum Data |
|-----------|------------|
| RSI (14) | 14 days |
| MACD | 26 days |
| MA20 | 20 days |
| MA50 | 50 days |
| MA200 | 200 days |

**Solution:** Handle NaN values gracefully in the code. They are expected and normal.

**Key Takeaway:** Always check data sufficiency before computing indicators. NaN values are not errors.

---

### 2. Python Package Structure Requirements
**Problem:** Python modules fail to import without proper `__init__.py` files in each directory.

**Solution:** Ensure every package directory has `__init__.py`:
```
src/
├── __init__.py
├── fetcher/
│   └── __init__.py
├── analyzer/
│   └── __init__.py
└── database/
    └── __init__.py
```

**Key Takeaway:** Python requires `__init__.py` in every package directory for proper module loading.

---

### 3. DataFrame Normalization for Database
**Problem:** Yahoo Finance returns dates as index, and column names differ (Open vs open).

**Solution:**
```python
df = df.copy()
df.reset_index(inplace=True)  # Date becomes column
df["Date"] = df["Date"].strftime("%Y-%m-%d")  # Format dates
# Normalize column names to lowercase
```

**Key Takeaway:** Always normalize DataFrames before saving to database to prevent silent corruption.

---

## 🤖 LLM Integration Lessons

### 1. Ollama API Endpoint Selection
**Problem:** Using `/api/chat` endpoint with certain models (like phi4) causes hangs.

**Solution:** Use `/api/generate` endpoint for broader model compatibility.

**Key Takeaway:** Test different Ollama endpoints. `/api/generate` is more universally compatible.

---

### 2. Model Size vs Performance on CPU
**Problem:** Large models (8B+) on CPU cause 100% CPU usage and slow inference.

**Solution:** Use smaller, CPU-friendly models:
- `llama3.2:3b` (2.0 GB) - Fast, good quality
- `phi3.5` (2.1 GB) - Fast, good for reasoning
- `mistral:7b` (4.4 GB) - Balanced quality/speed

**Key Takeaway:** For local development on CPU, smaller models (3-4B) provide 3-5x better performance.

---

### 3. Local vs Cloud LLM Strategy
**Problem:** Need reliable fallback when local LLM fails.

**Solution:** Implement dual-mode with automatic fallback:
```python
if mode == "local":
    result = run_local_llama(prompt)
    if result.startswith("[Error]"):
        result = run_cloud_llm(prompt)  # Fallback
```

**Key Takeaway:** Always implement fallback mechanisms for LLM calls.

---

### 4. Environment-Based Configuration for LLMs
**Problem:** Hard-coded LLM settings made local setup less predictable across machines.

**Solution:** Use environment variables for the local model, cloud model, and Ollama endpoint, with a sample `.env.example` file for quick onboarding.

**Key Takeaway:** Keep runtime configuration in environment variables so the same codebase can run consistently across different local setups.

## 🏗️ Architecture Decisions

### 1. Deterministic vs LLM Separation
**Decision:** Keep data computation separate from LLM reasoning.

**Rationale:**
- LLMs interpret data, they don't compute it
- Deterministic modules are testable and reliable
- Clear separation of concerns

**Key Takeaway:** Build a clean architecture with deterministic computation layer and LLM interpretation layer.

---

### 2. SQLite for Local Development
**Decision:** Use SQLite instead of PostgreSQL for local development.

**Rationale:**
- Zero setup required
- File-based, easy to backup
- Fast enough for market data
- Easy to migrate later

**Key Takeaway:** SQLite is ideal for local AI agents. Migrate to PostgreSQL for production.

---

### 3. Bottom-Up Development Approach
**Decision:** Build in this order:
1. Fetcher → 2. Analyzer → 3. Database → 4. Reasoner → 5. Reporter → 6. UI

**Rationale:**
- Each layer can be tested independently
- Clear dependencies between layers
- Easy to debug and maintain

**Key Takeaway:** Build bottom-up for complex AI systems. Test each layer before moving to the next.

---

## ⚡ Performance Optimizations

### 1. VWAP Calculation
**Optimization:** Calculate VWAP from intraday data (5m intervals) for more accurate value.

**Code:**
```python
tp = (df["High"] + df["Low"] + df["Close"]) / 3
vwap = (tp * df["Volume"]).sum() / df["Volume"].sum()
```

**Key Takeaway:** Intraday VWAP is more accurate than daily VWAP.

---

### 2. Trend Score 2.0 Algorithm
**Optimization:** Weighted scoring system combining multiple factors.

**Weights:**
- Delivery Strength: 0-30 points
- VWAP Position: 0-20 points
- Volume Breakout: 0-20 points
- Support/Resistance: 0-15 points
- Pivot Point: 0-10 points
- Volatility: 0-5 points

**Key Takeaway:** Multi-factor scoring provides more robust analysis than single indicators.

---

## 🐛 Debugging Techniques

### 1. Debug Logging Pattern
**Technique:** Add DEBUG print statements throughout the code.

**Example:**
```python
def run_local_llama(prompt: str) -> str:
    print("DEBUG: Using model:", LOCAL_MODEL)
    print("DEBUG: Sending request to Ollama...")
    # ... code ...
    print("DEBUG: Ollama response:", data)
```

**Key Takeaway:** Debug logging is essential for LLM integration debugging.

---

### 2. REPL Reset Handling
**Problem:** Restarting Python clears all imports.

**Solution:** Always re-import modules after restarting REPL.

**Key Takeaway:** Document the need to re-import after REPL restarts.

---

### 3. Cache Clearing
**Problem:** Python loads stale cached modules.

**Solution:** Remove `__pycache__` folders and `.pyc` files when modules change.

**Key Takeaway:** Clear Python cache when making module changes.

---

## 📝 Interview Talking Points

### Technical Challenges
1. **MultiIndex handling** - Real-world data normalization
2. **LLM integration** - Ollama vs llama-cpp on Windows
3. **Performance optimization** - Model selection for CPU inference
4. **Architecture design** - Bottom-up development approach

### Best Practices Demonstrated
1. Separation of concerns (deterministic vs LLM)
2. Testable code structure
3. Error handling and fallback mechanisms
4. Documentation and knowledge capture
5. Configuration management

### Key Skills Showcased
- Python development
- Financial data analysis
- LLM integration
- Database design
- API development
- System architecture

---

**Remember:** This document should be updated with each significant learning during project development.