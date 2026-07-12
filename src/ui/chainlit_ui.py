import asyncio
import json

import chainlit as cl

from src.core.orchestrator import run_pipeline


@cl.on_chat_start
async def start():
    await cl.Message(
        content=(
            "📈 Welcome to the AI Stock Agent!\n\n"
            "Enter a stock ticker (e.g., RELIANCE, TCS, INFY) and optional mode:\n"
            "- **local** -> contract pipeline with local-first analysis\n"
            "- **cloud** -> reserved for future cloud-only overrides\n"
        )
    ).send()

    await cl.sleep(1)

    await cl.Message(content="What ticker would you like to analyze?").send()


@cl.on_message
async def main(message: cl.Message):
    text = message.content.strip()

    parts = text.split()
    if len(parts) == 1:
        ticker = parts[0].upper()
        mode = "local"
    else:
        ticker = parts[0].upper()
        mode = parts[1].lower()

    await cl.Message(
        content=f"🔍 Running pipeline for **{ticker}** using **{mode}** mode..."
    ).send()

    master = await asyncio.to_thread(
        run_pipeline,
        symbol=ticker,
        ui_payload={
            "symbol": ticker,
            "timeframe": "daily",
            "analysis_types": [],
            "risk_profile": "medium",
            "output_format": "json",
            "mode": mode,
        },
    )

    if master.get("orchestrator", {}).get("status") != "complete":
        await cl.Message(content=f"Pipeline failed:\n```json\n{json.dumps(master.get('errors', []), indent=2, default=str)}\n```").send()
        return

    ai = master.get("ai_report", {})
    response = (
        f"Summary: {ai.get('summary')}\n\n"
        f"Sentiment: {ai.get('sentiment')}\n"
        f"Recommendation: {ai.get('recommendation')}\n"
        f"Probability: {ai.get('probability')}\n"
    )
    await cl.Message(content=response).send()
