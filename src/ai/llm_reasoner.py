"""LLM reasoning orchestration for stock analysis reports."""

import os
import subprocess
import importlib
import time
import re
from typing import Any, cast

from src.ingestion.market_fetcher import fetch_indian_stock_data
from src.analysis.fundamental import analyze_fundamentals
from src.database.sqlite_legacy import load_latest_fundamental_data

MAIN_MODEL = os.getenv("MAIN_LLM_MODEL", "qwen2.5:3b")
FAST_MODEL = os.getenv("FAST_LLM_MODEL", "llama3.2:3b")
LOGIC_MODEL = os.getenv("LOGIC_LLM_MODEL", "phi3:3.8b")
CLOUD_MODEL = os.getenv("CLOUD_MODEL", "gpt-4o-mini")
REQUIRED_SECTIONS = [
    "Summary",
    "Indicators",
    "Sentiment",
    "Risks",
    "Opportunities",
    "Recommendation",
]

SCORE_SECTION_ORDER = [
    "Summary",
    "Indicators",
    "Sentiment",
    "Risks",
    "Opportunities",
    "Recommendation",
]


def _safe_get(data: dict, key: str, default: str = "N/A"):
    value = data.get(key)
    if value is None:
        return default
    return value


def _format_fundamental_context(fundamentals: dict | None) -> str:
    if not fundamentals:
        return "Fundamental Data: unavailable"

    valuation = fundamentals.get("valuation", {})
    growth = fundamentals.get("growth", {})
    profitability = fundamentals.get("profitability", {})
    risk = fundamentals.get("risk", {})
    quality = fundamentals.get("data_quality", {})

    return (
        "Fundamental Data:\n"
        f"- Period: {fundamentals.get('period', 'quarterly')}\n"
        f"- P/E: {valuation.get('pe_ratio', 'N/A')} | PBV: {valuation.get('pbv_ratio', 'N/A')} | EV/EBITDA: {valuation.get('ev_ebitda', 'N/A')}\n"
        f"- Revenue YoY: {growth.get('revenue_yoy', 'N/A')} | Earnings YoY: {growth.get('earnings_yoy', 'N/A')}\n"
        f"- ROE: {profitability.get('roe', 'N/A')} | ROA: {profitability.get('roa', 'N/A')} | ROCE: {profitability.get('roce', 'N/A')}\n"
        f"- Debt/Equity: {risk.get('debt_to_equity', 'N/A')} | Current Ratio: {risk.get('current_ratio', 'N/A')} | Interest Coverage: {risk.get('interest_coverage', 'N/A')}\n"
        f"- Fundamental Coverage: {quality.get('coverage_pct', 'N/A')}"
    )


def _load_or_compute_fundamentals(ticker: str, period: str = "quarterly") -> dict | None:
    try:
        cached = load_latest_fundamental_data(ticker, period=period)
        if cached:
            return cached
    except Exception:
        pass

    try:
        return analyze_fundamentals(ticker, period=period, persist=True)
    except Exception:
        return None


def _build_market_snapshot(data: dict, fundamentals: dict | None = None) -> str:
    fundamental_context = _format_fundamental_context(fundamentals)
    return (
        f"Ticker: {_safe_get(data, 'ticker')}\n"
        f"Exchange: {_safe_get(data, 'exchange')}\n"
        f"Current Price: {_safe_get(data, 'current_price')}\n"
        f"RSI(14): {_safe_get(data, 'rsi')}\n"
        f"MA50: {_safe_get(data, 'ma50')}\n"
        f"MA200: {_safe_get(data, 'ma200')}\n"
        f"Bollinger Upper: {_safe_get(data, 'bollinger_upper')}\n"
        f"Bollinger Lower: {_safe_get(data, 'bollinger_lower')}\n"
        f"Last Updated: {_safe_get(data, 'last_updated')}\n"
        f"{fundamental_context}"
    )


def _build_standardized_report_prompt(market_snapshot: str) -> str:
    return (
        "You are an expert stock analyst.\n"
        "Generate a short, structured, evaluation-ready technical report for the stock below.\n\n"
        "STRICT RULES:\n"
        "- Total output must be under 180 words.\n"
        "- Use EXACTLY these 6 sections: Summary, Indicators, Sentiment, Risks, Opportunities, Recommendation.\n"
        "- Each section must contain EXACTLY 2 sentences.\n"
        "- No special characters, no ANSI codes, no markdown tables, no emojis.\n"
        "- Do NOT repeat the same numeric values more than once.\n"
        "- Focus ONLY on the data provided.\n"
        "- Keep language simple and factual.\n\n"
        "STOCK DATA:\n"
        f"{market_snapshot}\n\n"
        "OUTPUT FORMAT (follow exactly):\n\n"
        "Summary:\n"
        "Sentence 1.\n"
        "Sentence 2.\n\n"
        "Indicators:\n"
        "Sentence 1.\n"
        "Sentence 2.\n\n"
        "Sentiment:\n"
        "Sentence 1.\n"
        "Sentence 2.\n\n"
        "Risks:\n"
        "Sentence 1.\n"
        "Sentence 2.\n\n"
        "Opportunities:\n"
        "Sentence 1.\n"
        "Sentence 2.\n\n"
        "Recommendation:\n"
        "Sentence 1.\n"
        "Sentence 2."
    )


def _strip_ansi(text: str) -> str:
    return re.sub(r"\x1B\[[0-?]*[ -/]*[@-~]", "", text)


def _extract_section_text(report_text: str, section_name: str):
    lines = report_text.splitlines()
    start = None
    for i, line in enumerate(lines):
        if line.strip() == f"{section_name}:":
            start = i + 1
            break
    if start is None:
        return None

    end = len(lines)
    for i in range(start, len(lines)):
        if any(lines[i].strip() == f"{name}:" for name in REQUIRED_SECTIONS):
            end = i
            break
    return " ".join(line.strip() for line in lines[start:end] if line.strip())


def _extract_section_map(report_text: str) -> dict:
    clean = _strip_ansi(report_text or "").strip()
    return {
        section: (_extract_section_text(clean, section) or "").strip()
        for section in REQUIRED_SECTIONS
    }


def _sentence_count(text: str) -> int:
    return len([s for s in re.split(r"(?<=[.!?])\s+", text.strip()) if s.strip()])


def _is_valid_standardized_report(report_text: str) -> bool:
    clean = _strip_ansi(report_text or "").strip()
    if not clean:
        return False

    for section in REQUIRED_SECTIONS:
        if clean.count(f"{section}:") != 1:
            return False

    positions = [clean.find(f"{section}:") for section in REQUIRED_SECTIONS]
    if positions != sorted(positions):
        return False

    for section in REQUIRED_SECTIONS:
        body = _extract_section_text(clean, section)
        if body is None or _sentence_count(body) != 2:
            return False

    return True


def _contains_any(text: str, words: list[str]) -> bool:
    lowered = text.lower()
    return any(word in lowered for word in words)


def _score_summary(text: str) -> int:
    score = 1 if text else 0
    if _contains_any(text, ["uptrend", "downtrend", "bullish", "bearish", "cautious", "mixed", "neutral"]):
        score += 2
    if _contains_any(text, ["trend", "momentum", "setup", "structure", "direction"]):
        score += 2
    return min(5, score)


def _score_indicators(text: str) -> int:
    score = 1 if text else 0
    indicator_hits = 0
    if _contains_any(text, ["rsi"]):
        indicator_hits += 1
    if _contains_any(text, ["ma", "moving average", "ma50", "ma200"]):
        indicator_hits += 1
    if _contains_any(text, ["bollinger", "band", "bands"]):
        indicator_hits += 1
    score += min(3, indicator_hits)
    if _contains_any(text, ["above", "below", "cross", "overbought", "oversold", "volatility"]):
        score += 1
    return min(5, score)


def _score_sentiment(text: str) -> int:
    score = 1 if text else 0
    has_label = _contains_any(text, ["bullish", "bearish", "neutral"])
    has_reason = _contains_any(text, ["because", "given", "as", "since", "signal", "trend", "momentum"])
    if has_label:
        score += 2
    if has_reason:
        score += 2
    return min(5, score)


def _score_risks(text: str) -> int:
    score = 1 if text else 0
    if _contains_any(text, ["risk", "downside", "loss", "drawdown", "whipsaw", "reversal", "volatility"]):
        score += 2
    if _contains_any(text, ["if", "unless", "could", "may", "might"]):
        score += 2
    return min(5, score)


def _score_opportunities(text: str) -> int:
    score = 1 if text else 0
    if _contains_any(text, ["opportunity", "upside", "breakout", "accumulation", "entry", "setup"]):
        score += 2
    if _contains_any(text, ["if", "when", "can", "potential", "reward"]):
        score += 2
    return min(5, score)


def _score_recommendation(text: str) -> int:
    score = 1 if text else 0
    if _contains_any(text, ["recommend", "prefer", "consider", "staged", "cautious", "discipline", "stop"]):
        score += 2
    if _contains_any(text, ["all in", "guaranteed", "certain", "sure shot"]):
        score -= 1
    if _contains_any(text, ["if", "while", "until", "confirmation", "risk"]):
        score += 2
    return max(0, min(5, score))


def score_report_sections(section_map: dict) -> dict:
    scores = {
        "Summary": _score_summary(section_map.get("Summary", "")),
        "Indicators": _score_indicators(section_map.get("Indicators", "")),
        "Sentiment": _score_sentiment(section_map.get("Sentiment", "")),
        "Risks": _score_risks(section_map.get("Risks", "")),
        "Opportunities": _score_opportunities(section_map.get("Opportunities", "")),
        "Recommendation": _score_recommendation(section_map.get("Recommendation", "")),
    }
    total = sum(max(0, min(5, int(v))) for v in scores.values())
    scores["Total"] = max(0, min(30, total))
    return scores


def _format_score_block(scores: dict) -> str:
    lines = [f"SectionScore {section}: {scores.get(section, 0)}/5" for section in SCORE_SECTION_ORDER]
    lines.append(f"SectionScore Total: {scores.get('Total', 0)}/30")
    return "\n".join(lines)


def _deterministic_fallback_report(data: dict) -> str:
    ticker = str(_safe_get(data, "ticker", "Unknown"))
    exchange = str(_safe_get(data, "exchange", "Unknown"))

    current_price = data.get("current_price")
    ma50 = data.get("ma50")
    ma200 = data.get("ma200")
    rsi = data.get("rsi")
    bb_upper = data.get("bollinger_upper")
    bb_lower = data.get("bollinger_lower")

    trend_state = "mixed"
    if isinstance(current_price, (int, float)) and isinstance(ma50, (int, float)):
        trend_state = "bullish" if current_price >= ma50 else "cautious"

    long_trend = "stable"
    if isinstance(ma50, (int, float)) and isinstance(ma200, (int, float)):
        long_trend = "uptrend" if ma50 >= ma200 else "downtrend"

    sentiment_state = "neutral"
    if isinstance(rsi, (int, float)):
        if rsi >= 60:
            sentiment_state = "bullish"
        elif rsi <= 40:
            sentiment_state = "bearish"

    volatility_state = "moderate"
    if isinstance(current_price, (int, float)) and isinstance(bb_upper, (int, float)) and isinstance(bb_lower, (int, float)):
        band_width = abs(bb_upper - bb_lower)
        if current_price > 0:
            volatility_state = "high" if (band_width / current_price) > 0.08 else "moderate"

    return (
        f"Summary:\n{ticker} on {exchange} shows a {trend_state} near-term setup based on moving-average alignment. "
        f"The broader structure looks {long_trend} and suggests disciplined position sizing.\n\n"
        f"Indicators:\nMomentum signals are {sentiment_state} when read against the recent trend context. "
        f"Volatility appears {volatility_state} from the current band behavior and supports selective entries.\n\n"
        f"Sentiment:\nMarket tone is {sentiment_state} with no clear sign of extreme conviction yet. "
        f"A confirmation move is needed before treating this as a strong directional signal.\n\n"
        f"Risks:\nTrend continuation risk remains if price fails to hold near its current support zone. "
        f"Volatility expansion could cause whipsaws and premature exits for short-term trades.\n\n"
        f"Opportunities:\nA controlled breakout can offer a cleaner risk-reward setup for momentum participants. "
        f"A stable pullback can create accumulation opportunities for swing-oriented entries.\n\n"
        f"Recommendation:\nPrefer a cautious, staged approach rather than a full allocation at once. "
        f"Act on confirmation and maintain strict stop discipline to limit downside."
    )


def _enforce_standardized_report(data: dict, raw_output: str, market_snapshot: str) -> str:
    clean = _strip_ansi(raw_output or "").strip()
    if _is_valid_standardized_report(clean):
        return clean

    repair_prompt = (
        "Your previous answer did not follow the required format. Regenerate strictly.\n"
        "Use EXACTLY 6 sections in this order: Summary, Indicators, Sentiment, Risks, Opportunities, Recommendation.\n"
        "Each section must have EXACTLY 2 sentences and no bullets.\n"
        "Do not add any extra text before or after the sections.\n\n"
        + _build_standardized_report_prompt(market_snapshot)
    )
    retry_output = _strip_ansi(main_reasoning(repair_prompt)).strip()
    if _is_valid_standardized_report(retry_output):
        return retry_output

    print("[DEBUG] Using deterministic fallback report due to format mismatch")
    return _deterministic_fallback_report(data)


def run_model(model: str, prompt: str) -> str:
    """Call a local Ollama model via subprocess CLI."""
    print(f"[DEBUG] run_model called - model={model}, prompt_length={len(prompt)}")
    start_time = time.time()
    
    try:
        cmd = ["ollama", "run", model, "--no-ansi"]
        result = subprocess.run(
            cmd,
            input=prompt,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=120,
            check=False,
        )

        # Backward compatibility for older Ollama builds that do not support --no-ansi.
        if result.returncode != 0 and "unknown flag: --no-ansi" in (result.stderr or ""):
            print("[DEBUG] --no-ansi unsupported, retrying without flag")
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
            "You are an expert stock analyst. Generate a short, clean, structured technical analysis.\n"
            "Keep the entire response under 250 words.\n"
            "Use ONLY these sections: Summary, Indicators, Sentiment, Risks, Opportunities, Final Recommendation.\n"
            "- Do NOT include any special characters, ANSI codes, markdown tables, or emojis.\n"
            "- Write in simple, clear English.\n"
            "- Keep each section 2-3 sentences maximum.\n"
            f"STOCK DATA:\n{market_snapshot}"
        )
        return fast_reasoning(prompt)

    prompt = (
        "You are an expert stock analyst. Generate a short, clean, structured technical analysis.\n"
        "Keep the entire response under 250 words.\n"
        "Use ONLY these sections: Summary, Indicators, Sentiment, Risks, Opportunities, Final Recommendation.\n"
        "- Do NOT include any special characters, ANSI codes, markdown tables, or emojis.\n"
        "- Write in simple, clear English.\n"
        "- Keep each section 2-3 sentences maximum.\n"
        f"STOCK DATA:\n{market_snapshot}"
    )
    return main_reasoning(prompt)


def quick_sentiment(data: dict, optimized: bool = False) -> str:
    market_snapshot = _build_market_snapshot(data)
    if optimized:
        prompt = (
            "Classify as Bullish/Bearish/Neutral with 1-2 sentences.\n"
            "- Do NOT include emojis or special characters.\n"
            f"Data:\n{market_snapshot}"
        )
    else:
        prompt = (
            "Classify as Bullish/Bearish/Neutral with 1-2 sentences.\n"
            "- Do NOT include emojis or special characters.\n"
            f"Data:\n{market_snapshot}"
        )
    return fast_reasoning(prompt)


def explain_trend_score(data: dict, optimized: bool = False) -> str:
    market_snapshot = _build_market_snapshot(data)
    if optimized:
        prompt = (
            "Explain the trend-score logic in 2-3 sentences.\n"
            "- Mention if score is strong (70+) or weak (<40).\n"
            "- Do NOT include emojis or special characters.\n"
            f"Data:\n{market_snapshot}"
        )
    else:
        prompt = (
            "Explain the trend-score logic in 2-3 sentences.\n"
            "- Mention if score is strong (70+) or weak (<40).\n"
            "- Do NOT include emojis or special characters.\n"
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

    fundamentals = _load_or_compute_fundamentals(market_data.get("ticker", ticker), period="quarterly")
    market_snapshot = _build_market_snapshot(market_data, fundamentals=fundamentals)
    standardized_prompt = _build_standardized_report_prompt(market_snapshot)

    if mode_value == "cloud":
        return run_cloud_llm(standardized_prompt)

    optimized = mode_value in {"optimized", "token_optimized", "token-optimized", "fast"}
    print(f"[DEBUG] Running in {'optimized' if optimized else 'standard'} mode")

    report_body = main_reasoning(standardized_prompt)
    if _is_error_response(report_body):
        print(f"[DEBUG] Report generation failed locally, checking cloud fallback")
        if os.getenv("ENABLE_CLOUD_FALLBACK", "1") == "1":
            cloud_report = run_cloud_llm(standardized_prompt)
            if cloud_report.startswith("[Cloud LLM Error]") or cloud_report.startswith("[Cloud LLM Exception]"):
                return cloud_report
            report_body = _enforce_standardized_report(market_data, cloud_report, market_snapshot)
        else:
            return report_body
    else:
        report_body = _enforce_standardized_report(market_data, report_body, market_snapshot)

    section_map = _extract_section_map(report_body)
    section_scores = score_report_sections(section_map)
    score_block = _format_score_block(section_scores)

    elapsed = time.time() - start_time
    print(f"[DEBUG] Report generation completed - elapsed={elapsed:.2f}s")

    return (
        f"AI Stock Report ({'Optimized' if optimized else 'Standard'}) for {market_data.get('ticker', ticker)}\n\n"
        f"{report_body}\n\n"
        f"{score_block}"
    )


def generate_ai_report(llm_input: dict) -> dict:
    """Build a contract-friendly AI output from pipeline context."""
    symbol = llm_input.get("symbol") or "UNKNOWN"
    timeframe = llm_input.get("timeframe") or "daily"
    technical = llm_input.get("technical") or {}
    fundamental = llm_input.get("fundamental") or {}
    sentiment = llm_input.get("sentiment") or {}
    trend = llm_input.get("trend") or {}
    weights = llm_input.get("weights") or {}

    trend_score = trend.get("trend_score")
    news_sentiment = sentiment.get("news_sentiment")
    pe = ((fundamental.get("valuation") or {}).get("pe"))
    rsi = technical.get("rsi")

    sentiment_label = "neutral"
    if isinstance(trend_score, (int, float)):
        if trend_score >= 65:
            sentiment_label = "bullish"
        elif trend_score <= 40:
            sentiment_label = "bearish"

    summary_parts = [
        f"{symbol} on {timeframe} timeframe shows {sentiment_label} trend context.",
    ]

    if isinstance(rsi, (int, float)):
        summary_parts.append(f"RSI is {round(rsi, 2)}, indicating momentum-aware positioning.")
    if isinstance(news_sentiment, (int, float)):
        summary_parts.append(f"News sentiment score is {news_sentiment}.")
    if isinstance(pe, (int, float)):
        summary_parts.append(f"Valuation reference P/E is {round(pe, 2)}.")

    risks = []
    if isinstance(rsi, (int, float)) and rsi >= 70:
        risks.append("Momentum is extended and may trigger short-term pullback risk.")
    if isinstance(news_sentiment, (int, float)) and news_sentiment < 0:
        risks.append("Recent news tone is negative and can pressure near-term price action.")
    if isinstance(trend_score, (int, float)) and trend_score < 45:
        risks.append("Trend score is weak, so signal confidence remains limited.")
    if not risks:
        risks.append("No major red flags detected from current contract inputs.")

    opportunities = []
    if isinstance(trend_score, (int, float)) and trend_score >= 60:
        opportunities.append("Trend strength supports momentum-aligned opportunities.")
    if isinstance(news_sentiment, (int, float)) and news_sentiment > 0:
        opportunities.append("Positive headline flow can reinforce upside continuation.")
    opportunities.append(
        "Timeframe weighting favors "
        f"technical={((weights.get('model_weights') or {}).get('technical'))}, "
        f"fundamental={((weights.get('model_weights') or {}).get('fundamental'))}, "
        f"sentiment={((weights.get('model_weights') or {}).get('sentiment'))}."
    )

    if sentiment_label == "bullish":
        recommendation = "Accumulate in staggered entries while maintaining stop-loss discipline."
        probability = 0.68
    elif sentiment_label == "bearish":
        recommendation = "Reduce fresh exposure and wait for technical confirmation before re-entry."
        probability = 0.35
    else:
        recommendation = "Hold neutral stance and wait for stronger directional confirmation."
        probability = 0.52

    return {
        "summary": " ".join(summary_parts),
        "sentiment": sentiment_label,
        "risks": risks,
        "opportunities": opportunities,
        "recommendation": recommendation,
        "probability": probability,
        "data_quality": "good",
    }