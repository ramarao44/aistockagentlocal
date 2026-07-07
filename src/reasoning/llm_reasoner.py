"""
LLM Reasoner Module - AI Stock Agent

This module handles LLM integration for generating stock analysis reports.
Supports both local (Ollama) and cloud (OpenAI) LLM providers.

Author: AI Stock Agent Team
Version: 1.0
Last Updated: 2026-07-07
"""

import requests
import os
from src.fetcher.market_fetcher import fetch_indian_stock_data

# ============================================================================
# CONFIGURATION
# ============================================================================
# These settings control which LLM models to use and their endpoints.
# LOCAL_MODEL: Used for local inference via Ollama (recommended for privacy)
# CLOUD_MODEL: Used for cloud inference via OpenAI (requires API key)
# OLLAMA_URL: Local Ollama API endpoint (default: localhost:11434)

LOCAL_MODEL = "llama3.2:3b"  # 2.0GB model, fast on CPU
CLOUD_MODEL = "gpt-4o-mini"   # Cloud fallback model

OLLAMA_URL = "http://localhost:11434/api/generate"  # Use /api/generate for compatibility


# ============================================================================
# LOCAL LLM (OLLAMA)
# ============================================================================
# Ollama provides a simple HTTP API for running LLMs locally.
# Benefits: Privacy-preserving, no API costs, works offline
# Note: Use /api/generate endpoint (not /api/chat) for broader model compatibility

def run_local_llama(prompt: str) -> str:
    """
    Send prompt to local Ollama LLM and return the response.
    
    Args:
        prompt: The text prompt to send to the LLM
        
    Returns:
        str: The LLM response text, or error message if failed
        
    Raises:
        No exceptions raised - errors are returned as strings
    """
    print("DEBUG: Using model:", LOCAL_MODEL)

    try:
        print("DEBUG: Sending request to Ollama...")

        response = requests.post(
            OLLAMA_URL,
            json={
                "model": LOCAL_MODEL,
                "prompt": prompt,
                "stream": False  # Set to True for streaming responses
            },
            timeout=120  # 2-minute timeout for large models
        )

        print("DEBUG: Ollama POST returned status:", response.status_code)

        data = response.json()
        print("DEBUG: Ollama response:", data)

        # Handle different response formats from Ollama
        if "response" in data:
            return data["response"]

        if "output" in data:
            return data["output"]

        if "error" in data:
            return f"[Local LLM Error] {data['error']}"

        return str(data)

    except Exception as e:
        return f"[Local LLM Exception] {str(e)}"


# -----------------------------
# CLOUD LLM (OPENAI / AZURE)
# -----------------------------

def run_cloud_llm(prompt: str) -> str:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return "[Cloud LLM Error] Missing OPENAI_API_KEY"

    try:
        import openai
        openai.api_key = api_key

        completion = openai.ChatCompletion.create(
            model=CLOUD_MODEL,
            messages=[{"role": "user", "content": prompt}]
        )

        return completion.choices[0].message["content"]

    except Exception as e:
        return f"[Cloud LLM Exception] {str(e)}"


# -----------------------------
# MAIN ENTRYPOINT
# -----------------------------

def generate_llm_report(ticker: str, mode: str = "local") -> str:
    print("DEBUG: generate_llm_report called with mode =", mode)

    # ---------------------------------------------------------
    # Fetch REAL Indian stock data (NSE + BSE)
    # ---------------------------------------------------------
    market_data = fetch_indian_stock_data(ticker)

    if not market_data["success"]:
        return f"Error fetching market data: {market_data['error']}"

    print("DEBUG: Market data fetched:", market_data)

    # ---------------------------------------------------------
    # Build prompt using REAL data
    # ---------------------------------------------------------
    prompt = f"""
You are an AI financial analyst specializing in Indian stock markets (NSE/BSE).
Use ONLY the REAL market data provided below to generate the analysis.

REAL MARKET DATA:
- Ticker: {market_data['ticker']}
- Exchange: {market_data['exchange']}
- Current Price: {market_data['current_price']}
- RSI (14): {market_data['rsi']}
- MA50: {market_data['ma50']}
- MA200: {market_data['ma200']}
- Bollinger Upper: {market_data['bollinger_upper']}
- Bollinger Lower: {market_data['bollinger_lower']}
- Last Updated: {market_data['last_updated']}

Generate a structured, concise Indian stock analysis report including:
1. Price Trend Summary
2. Technical Indicators Interpretation
3. Market Sentiment (general)
4. Risks (India-specific)
5. Opportunities (India-specific)
6. Final Recommendation (Buy/Hold/Sell)
7. Next Steps for the Investor

Keep the tone professional, analytical, and India‑focused.
"""

    # ---------------------------------------------------------
    # Run LLM (local or cloud)
    # ---------------------------------------------------------
    if mode == "cloud":
        print("DEBUG: Calling run_cloud_llm() now...")
        return run_cloud_llm(prompt)

    print("DEBUG: Calling run_local_llama() now...")
    result = run_local_llama(prompt)

    # Fallback to cloud if local fails
    if result.startswith("[Local LLM Error]") or result.startswith("[Local LLM Exception]"):
        return f"{result}\n\nFalling back to cloud...\n\n" + run_cloud_llm(prompt)

    return result
