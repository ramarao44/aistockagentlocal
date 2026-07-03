import json

from yfinance import ticker
from src.reasoning.reasoning_node import (
    generate_daily_summary,
    generate_trend_analysis
)

from src.db.database import (
    load_news,
    load_sentiment,
    load_market_data,
    load_indicators
)

# -----------------------------
# Local Llama 3.1 Reasoner
# -----------------------------
def run_local_llama(prompt: str):
    try:
        from llama_cpp import Llama
    except ImportError:
        raise RuntimeError("Please install llama-cpp-python: pip install llama-cpp-python")

import requests

def run_local_llama(prompt):
    response = requests.post(
        "http://localhost:11434/api/chat",
        json={
            "model": "llama3.1:8b",
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "stream": False
        }
    )

    data = response.json()

    # Handle errors cleanly
    if "error" in data:
        return f"[Ollama Error] {data['error']}"

    # Standard chat response
    if "message" in data and "content" in data["message"]:
        return data["message"]["content"]

    # Fallback for /api/generate format
    if "output" in data:
        return data["output"]

    # Unknown format fallback
    return str(data)



    output = llm(
        prompt,
        max_tokens=800,
        temperature=0.3,
        top_p=0.9,
        stop=["</analysis>"]
    )

    return output["choices"][0]["text"].strip()


# -----------------------------
# Cloud Reasoner (OpenAI / Azure)
# -----------------------------
def run_cloud_llm(prompt: str):
    try:
        from openai import OpenAI
    except ImportError:
        raise RuntimeError("Install openai: pip install openai")

    client = OpenAI()

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a financial analyst."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=800,
        temperature=0.3
    )

    return response.choices[0].message.content


# -----------------------------
# Unified Prompt Builder
# -----------------------------
def build_prompt(ticker: str):
    daily = generate_daily_summary(ticker)
    trend = generate_trend_analysis(ticker)

    news = load_news(ticker).head(5)
    sentiment = load_sentiment(ticker).head(5)

    # Convert timestamps in market + indicators
    def convert_timestamps(obj):
        for key, value in obj.items():
            if hasattr(value, "isoformat"):
                obj[key] = value.isoformat()
        return obj

    market = convert_timestamps(
        load_market_data(ticker).tail(1).to_dict("records")[0]
    )

    indicators = convert_timestamps(
        load_indicators(ticker).tail(1).to_dict("records")[0]
    )

    news_block = "\n".join([f"- {row['title']}" for _, row in news.iterrows()])
    sentiment_block = "\n".join([f"- {row['title']} → {row['sentiment']:.3f}" for _, row in sentiment.iterrows()])

    prompt = f"""
<analysis>
You are a financial analyst. Produce a clear, structured report combining:

1. Daily Summary
2. Trend Analysis
3. Technical Indicators
4. News Impact
5. Sentiment Interpretation
6. Market Tone
7. Risks & Opportunities

Ticker: {ticker}

--------------------
DAILY SUMMARY
--------------------
{daily}

--------------------
TREND ANALYSIS
--------------------
{trend}

--------------------
LATEST NEWS
--------------------
{news_block}

--------------------
SENTIMENT SNAPSHOT
--------------------
{sentiment_block}

--------------------
LATEST MARKET DATA
--------------------
{json.dumps(market, indent=2)}

--------------------
LATEST INDICATORS
--------------------
{json.dumps(indicators, indent=2)}

Write a professional analyst-style report.
</analysis>
"""

    return prompt


# -----------------------------
# Unified Interface
# -----------------------------
def generate_llm_report(ticker: str, mode="local"):
    prompt = build_prompt(ticker)

    if mode == "local":
        return run_local_llama(prompt)

    elif mode == "cloud":
        return run_cloud_llm(prompt)

    else:
        raise ValueError("mode must be 'local' or 'cloud'")
