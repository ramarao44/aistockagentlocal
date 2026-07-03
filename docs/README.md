Here you go, ramarao — a clean, professional README.md you can drop directly into your repo.
It reflects everything we’ve built so far, written in proper Markdown, structured for real engineering teams.

You can save this as:

Code
README.md
or

Code
docs/README.md
📘 AI Stock Analysis Agent (Local‑First) — README
A fully local, privacy‑preserving AI agent that fetches market data, computes technical indicators, analyzes trends using local LLMs, and produces daily stock insights.
Built with Python, Ollama, LangGraph, Chainlit, and deterministic modules for reliability.

🧩 Project Overview
This project implements a modular, local‑first AI agent for stock analysis.
It combines:

deterministic Python modules (fetching, indicators, DB)

local LLM reasoning (Qwen2.5‑coder, Llama3.1, DeepSeek‑R1, Phi‑3.5)

agent workflow orchestration (LangGraph)

a chat interface (Chainlit)

The architecture ensures:

reproducibility

testability

privacy

modularity

clean separation between data computation and AI reasoning

📁 Folder Structure
Code
ai-stock-agent/
│
├── src/
│   ├── fetcher/              # Market data fetcher (deterministic)
│   ├── analyzer/             # Technical indicator analyzer (deterministic)
│   ├── db/                   # SQLite + pgvector layer
│   ├── reasoning/            # LLM reasoning nodes
│   ├── reporter/             # Summary generation
│   └── utils/                # Helpers
│
├── agents/                   # LangGraph agent definitions
├── tests/                    # Unit tests
├── data/                     # Local DB, cached data
├── notebooks/                # Jupyter notebooks for exploration
│
├── requirements.txt
└── README.md
⚙️ Environment Setup
1. Create virtual environment
Code
python -m venv .venv
Activate:

Code
.venv\Scripts\activate      # Windows
source .venv/bin/activate   # Mac/Linux
2. Install dependencies
Code
pip install -r requirements.txt
3. Install Ollama + local models
Code
ollama pull qwen2.5-coder
ollama pull llama3.1
ollama pull deepseek-r1
ollama pull phi3.5
4. Install Continue.dev (VS Code)
Used for local LLM coding assistance.

📊 Deterministic Modules
✔ Fetcher Module
src/fetcher/market_fetcher.py

Downloads OHLCV data using yfinance

Handles MultiIndex column issues

Renames columns to:
Open, High, Low, Close, Volume

Lesson learned:
yfinance often returns MultiIndex columns → must flatten + rename.

✔ Analyzer Module
src/analyzer/technical_analyzer.py

Computes:

RSI

MACD

MA20

MA50

Using the modern ta library.

Lesson learned:
Technical indicators require minimum data:

Indicator	Minimum Data Needed
RSI	14 days
MACD	26 days
MA20	20 days
MA50	50 days


NaN values are normal and expected.

🧪 Testing Fetcher + Analyzer
Run:

python
from src.fetcher.market_fetcher import fetch_daily_data
from src.analyzer.technical_analyzer import compute_indicators

df = fetch_daily_data("AAPL")
df2 = compute_indicators(df)
print(df2.tail())
Expected:

Correct OHLCV columns

RSI, MACD, MA20, MA50 columns

Some NaN values (normal)

🧠 Lessons Learned (Engineering Knowledge Base)
🔹 Deterministic modules must stay separate from LLM reasoning
LLMs interpret data — they do not compute it.

🔹 yfinance returns inconsistent column formats
Flattening + renaming is mandatory.

🔹 Technical indicators require minimum data
NaN values are expected and normal.

🔹 Restarting Python clears all imports
Always re-import modules after restarting REPL.

🔹 Library maintenance matters
Use actively maintained libraries (ta), avoid abandoned ones (pandas_ta).

🔹 Build bottom-up
Fetcher → Analyzer → DB → Reasoner → Reporter → UI.

🔹 Local-first development is predictable
Ollama + Continue.dev give privacy, speed, reproducibility.

🔹 Debugging is part of the journey
You handled:

MultiIndex columns

missing indicators

library compatibility

REPL resets

These are real-world engineering issues.

🚀 Next Steps (Phase 2)
✔ Step 5 — Build Database Layer
SQLite + pgvector for:

daily market data

indicators

news sentiment

embeddings

agent memory

multi-day analysis

✔ Step 6 — Build News Fetcher + Sentiment Analyzer
✔ Step 7 — Build LangGraph Agent
✔ Step 8 — Build Chainlit UI
✔ Step 9 — Create full documentation (AGENTS.md, workflows)


🧠 Knowledge Base Summary — Steps 5 & 6
🗂️ Step 5 — Database Layer (Market Data + Indicators)
1. SQLite is perfect for local AI agents
Zero setup

File‑based

Fast enough for market data

Deterministic (no external dependencies)

Easy to migrate and back up

This makes it ideal for your local stock agent.

2. Schema design matters
You created two core tables:

market_data

technical_indicators

Key lessons:

Use ticker + date as a natural unique key.

Store dates as text (YYYY-MM-DD) for SQLite compatibility.

Keep column names simple and consistent (open, high, low, close, etc.).

Indicators should be stored numerically (rsi, macd, ma20, etc.).

3. Save functions must normalize DataFrames
You learned that:

Yahoo Finance returns dates as index → must reset_index().

Column names differ (Open vs open) → normalize before saving.

Volume must be cast to int.

Dates must be formatted (strftime("%Y-%m-%d")).

This prevents silent DB corruption.

4. Load functions must return clean DataFrames
You added:

load_market_data

load_indicators

load_latest_market_data

load_latest_indicators

Key lessons:

Always sort by date (ORDER BY date ASC).

Use parse_dates=["date"] for pandas.

Return df.iloc[0] for latest rows.

Handle empty results gracefully.

5. Python imports require proper package structure
This was the biggest practical lesson.

You learned that Python will NOT import modules unless every folder has:

Code
__init__.py
Specifically:

src/

src/db/

src/fetcher/

src/analyzer/

scripts/

Without these:

Python loads stale cached modules

New functions appear “missing”

Imports fail even though code exists

This is a critical Python packaging concept.

6. Clear Python cache when modules change
You learned to remove:

__pycache__ folders

.pyc files

This forces Python to reload modules.

📡 Step 6 — News Fetcher + Sentiment Analyzer
1. Yahoo Finance JSON endpoint is rate‑limited
You discovered:

/v1/finance/search returns 429 errors

It blocks scripts without browser headers

It is not reliable for agents

This is a common pitfall.

2. Yahoo Finance RSS feed is stable
You switched to:

Code
https://feeds.finance.yahoo.com/rss/2.0/headline?s=AAPL
Key advantages:

No rate limits

No API key

Always available

Easy XML parsing

Perfect for automated agents

This is the correct long‑term solution.

3. XML parsing is simple and reliable
You learned:

RSS feeds use <item> nodes

Titles, links, and dates are easy to extract

xml.etree.ElementTree is built‑in and fast

This keeps your pipeline lightweight.

4. Sentiment analysis with VADER is ideal for headlines
You installed and used:

Code
vaderSentiment
Key lessons:

VADER is deterministic

Works offline

Perfect for short text (headlines)

Produces compound sentiment scores

This avoids needing an LLM for basic sentiment.

5. You added two new DB tables
news

sentiment

Lessons:

Use UNIQUE(ticker, title) to avoid duplicates.

Store timestamps as text (YYYY-MM-DD HH:MM:SS).

Store sentiment as REAL.

6. You built a full news pipeline
The pipeline now:

Fetches news

Parses RSS

Computes sentiment

Saves news

Saves sentiment

Loads both for reasoning

This completes the “awareness” layer of your agent.

7. You validated everything with test scripts
You created:

test_db_load.py

test_news_pipeline.py

Lessons:

Always test DB read/write separately.

Always test fetch → analyze → save → load as a full pipeline.

Running scripts with python -m scripts.<name> requires proper package structure.

🎯 High‑Level Takeaways
Step 5 — Database Layer
SQLite is ideal for local agents.

Normalize DataFrames before saving.

Use clean load functions.

Python packages require __init__.py.

Clear cache when modules change.

Step 6 — News + Sentiment
Yahoo JSON is rate‑limited → use RSS instead.

RSS is stable and perfect for agents.

VADER is ideal for headline sentiment.

Store news + sentiment in DB.

Build full test pipelines.