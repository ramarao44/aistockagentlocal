"""LLM reasoning orchestration for stock analysis reports."""

import os
import subprocess
import importlib
import time
from typing import Any, cast

from src.fetcher.market_fetcher import fetch_indian_stock_data

MAIN_MODEL = os.getenv("MAIN_LLM_MODEL", "qwen2.5:3b")
FAST_MODEL = os.getenv("FAST_LLM_MODEL", "llama3.2:3b")
LOGIC_MODEL = os.getenv("LOGIC_LLM_MODEL", "phi3:3.8b")
CLOUD_MODEL = os.getenv("CLOUD_MODEL", "gpt-4o-mini")


def _safe_get(data: dict, key: str, default: str = "N/A"):
    value = data.get(key)
    if value is None:
        return default
    return value


def _build_market_snapshot(data: dict) -> str:
    return (
        f"Ticker: {_safe_get(data, 'ticker')}\n"
        f"Exchange: {_safe_get(data, 'exchange')}\n"
        f"Current Price: {_safe_get(data, 'current_price')}\n"
        f"RSI(14): {_safe_get(data, 'rsi')}\n"
        f"MA50: {_safe_get(data, 'ma50')}\n"
        f"MA200: {_safe_get(data, 'ma200')}\n"
        f"Bollinger Upper: {_safe_get(data, 'bollinger_upper')}\n"
        f"Bollinger Lower: {_safe_get(data, 'bollinger_lower')}\n"
        f"Last Updated: {_safe_get(data, 'last_updated')}"
    )


def run_model(model: str, prompt: str) -> str:
    """Call a local Ollama model via subprocess CLI."""
    print(f"[DEBUG] run_model called - model={model}, prompt_length={len(prompt)}")
    start_time = time.time()
    
    try:
        result = subprocess.run(
            ["ollama", "run", model],
            input=prompt,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=120,
            check=False,
        )
        
        elapsed = time.time() - start_time
        print(f"[DEBUG] run_model completed - model={model}, elapsed={elapsed:.2f}s, returncode={result.returncode}")
        
        if result.returncode != 0:
            detail = (result.stderr or "unknown error").strip()
            print(f"[DEBUG] LLM error - stderr={detail[:100]}")
            return f"[Local LLM Error] model={model} detail={detail}"

        output = (result.stdout or "").strip()
        if not output:
            print(f"[DEBUG] LLM returned empty output")
            return f"[Local LLM Error] model={model} returned empty output"
        
        print(f"[DEBUG] LLM success - output_length={len(output)}")
        return output
        
    except FileNotFoundError:
        print(f"[DEBUG] LLM FileNotFoundError - ollama command not found")
        return "[Local LLM Error] 'ollama' command not found"
    except subprocess.TimeoutExpired:
        print(f"[DEBUG] LLM TimeoutExpired - model={model}")
        return f"[Local LLM Error] model={model} timed out"
    except Exception as exc:
        print(f"[DEBUG] LLM Exception - {type(exc).__name__}: {exc}")
        return f"[Local LLM Exception] {exc}"


def main_reasoning(prompt: str) -> str:
    print(f"[DEBUG] main_reasoning using model={MAIN_MODEL}")
    return run_model(MAIN_MODEL, prompt)


def fast_reasoning(prompt: str) -> str:
    print(f"[DEBUG] fast_reasoning using model={FAST_MODEL}")
    return run_model(FAST_MODEL, prompt)


def logic_reasoning(prompt: str) -> str:
    print(f"[DEBUG] logic_reasoning using model={LOGIC_MODEL}")
    return run_model(LOGIC_MODEL, prompt)


def run_cloud_llm(prompt: str) -> str:
    print(f"[DEBUG] run_cloud_llm called, prompt_length={len(prompt)}")
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print(f"[DEBUG] Missing OPENAI_API_KEY for cloud fallback")
        return "[Cloud LLM Error] Missing OPENAI_API_KEY"

    try:
        openai_client = cast(Any, importlib.import_module("openai"))

        openai_client.api_key = api_key
        completion = openai_client.ChatCompletion.create(
            model=CLOUD_MODEL,
            messages=[{"role": "user", "content": prompt}],
        )
        print(f"[DEBUG] Cloud LLM success")
        return completion.choices[0].message["content"]
    except ImportError:
        print(f"[DEBUG] openai package not installed")
        return "[Cloud LLM Error] openai package is not installed"
    except Exception as exc:
        print(f"[DEBUG] Cloud LLM Exception - {type(exc).__name__}: {exc}")
        return f"[Cloud LLM Exception] {exc}"


def generate_ai_summary(data: dict, optimized: bool = False) -> str:
    market_snapshot = _build_market_snapshot(data)
    if optimized:
        prompt = (
            "You are an Indian stock analyst. Return concise output in <=120 words.\n"
            "Sections: Trend, Indicators, Risks, Recommendation.\n"
            f"Data:\n{market_snapshot}"
        )
        return fast_reasoning(prompt)

    prompt = (
        "You are an AI financial analyst specializing in Indian stock markets (NSE/BSE).\n"
        "Use only provided data. Provide: Price Trend Summary, Technical Indicator Interpretation, "
        "Market Sentiment, Risks, Opportunities, Final Recommendation, Next Steps.\n"
        f"Data:\n{market_snapshot}"
    )
    return main_reasoning(prompt)


def quick_sentiment(data: dict, optimized: bool = False) -> str:
    market_snapshot = _build_market_snapshot(data)
    if optimized:
        prompt = (
            "Classify as Bullish/Bearish/Neutral. Provide one-line reason in <=25 words.\n"
            f"Data:\n{market_snapshot}"
        )
    else:
        prompt = (
            "Classify sentiment as Bullish, Bearish, or Neutral using the stock data and explain briefly.\n"
            f"Data:\n{market_snapshot}"
        )
    return fast_reasoning(prompt)


def explain_trend_score(data: dict, optimized: bool = False) -> str:
    market_snapshot = _build_market_snapshot(data)
    if optimized:
        prompt = (
            "Explain trend logic in <=80 words with 2 bullets: why score is strong/weak and key risk.\n"
            f"Data:\n{market_snapshot}"
        )
    else:
        prompt = (
            "Explain trend-score logic with technical reasoning and risk factors.\n"
            f"Data:\n{market_snapshot}"
        )
    return logic_reasoning(prompt)


def _is_error_response(text: str) -> bool:
    return text.startswith("[Local LLM Error]") or text.startswith("[Local LLM Exception]")


def generate_llm_report(ticker: str, mode: str = "local") -> str:
    """Generate report for a ticker using local models with optional cloud fallback.

    Supported modes:
    - local/default: full report
    - optimized: compact report for token/latency savings
    - cloud: force cloud report
    """
    print(f"[DEBUG] generate_llm_report called - ticker={ticker}, mode={mode}")
    start_time = time.time()
    
    mode_value = (mode or "local").strip().lower()
    market_data = fetch_indian_stock_data(ticker)

    if not market_data.get("success"):
        print(f"[DEBUG] Market data fetch failed - {market_data.get('error', 'Unknown error')}")
        return f"Error fetching market data: {market_data.get('error', 'Unknown error')}"

    if mode_value == "cloud":
        full_prompt = (
            "Generate a structured Indian stock analysis report with sections: "
            "Price Trend, Technical Indicators, Sentiment, Risks, Opportunities, Recommendation, Next Steps.\n"
            f"Data:\n{_build_market_snapshot(market_data)}"
        )
        return run_cloud_llm(full_prompt)

    optimized = mode_value in {"optimized", "token_optimized", "token-optimized", "fast"}
    print(f"[DEBUG] Running in {'optimized' if optimized else 'standard'} mode")

    summary = generate_ai_summary(market_data, optimized=optimized)
    if _is_error_response(summary):
        print(f"[DEBUG] Summary failed, checking cloud fallback")
        if os.getenv("ENABLE_CLOUD_FALLBACK", "1") == "1":
            return run_cloud_llm(
                "Local model failed. Provide concise Indian stock analysis from this data:\n"
                f"{_build_market_snapshot(market_data)}"
            )
        return summary

    sentiment = quick_sentiment(market_data, optimized=optimized)
    trend_logic = explain_trend_score(market_data, optimized=optimized)

    elapsed = time.time() - start_time
    print(f"[DEBUG] Report generation completed - elapsed={elapsed:.2f}s")

    return (
        f"AI Stock Report ({'Optimized' if optimized else 'Standard'}) for {market_data.get('ticker', ticker)}\n\n"
        "1. Summary\n"
        f"{summary}\n\n"
        "2. Quick Sentiment\n"
        f"{sentiment}\n\n"
        "3. Trend Score Logic\n"
        f"{trend_logic}"
    )