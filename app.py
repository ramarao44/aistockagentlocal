import chainlit as cl
from src.reasoning.llm_reasoner import generate_llm_report

@cl.on_chat_start
async def start():
    await cl.Message(
        content=(
            "📈 Welcome to the AI Stock Agent!\n\n"
            "Enter a stock ticker (e.g., AAPL, MSFT, TSLA) and choose mode:\n"
            "- **local** → fast, uses Ollama (phi4)\n"
            "- **cloud** → uses GPT-4o-mini (if configured)\n"
        )
    ).send()

    await cl.sleep(0.1)

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

    # Call your reasoning engine
    
    report = generate_llm_report(ticker, mode=mode)
    await cl.Message(content=report).send()


