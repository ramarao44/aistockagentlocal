import chainlit as cl
import asyncio
from src.reasoning.llm_reasoner import generate_llm_report

@cl.on_chat_start
async def start():
    await cl.Message(
        content=(
            "📈 Welcome to the AI Stock Agent!\n\n"
            "Enter a stock ticker (e.g., RELIANCE, TCS, INFY) and choose mode:\n"
            "- **local** → uses Ollama (llama3.2:3b) - private, no API costs\n"
            "- **cloud** → uses GPT-4o-mini (if configured)\n"
        )
    ).send()

    await cl.sleep(1)

    await cl.Message(content="What ticker would you like to analyze?").send()


@cl.on_message
async def main(message: cl.Message):
    text = message.content.strip()

    # Simple input format: "AAPL local" or "AAPL cloud"
    parts = text.split()
    if len(parts) == 1:
        ticker = parts[0].upper()
        mode = "local"
    else:
        ticker = parts[0].upper()
        mode = parts[1].lower()

    await cl.Message(
        content=f"🔍 Generating report for **{ticker}** using **{mode}** mode..."
    ).send()

    # Call your reasoning engine in a thread pool to avoid blocking the event loop
    report = await asyncio.to_thread(generate_llm_report, ticker, mode=mode)
    await cl.Message(content=report).send()