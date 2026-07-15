import asyncio
import json
import os
from pathlib import Path

import chainlit as cl
from dotenv import load_dotenv
from src.core.orchestrator import run_pipeline


load_dotenv(Path(__file__).resolve().parents[2] / ".env")


def _env_bool(name: str, default: str = "0") -> bool:
    return str(os.getenv(name, default)).strip().lower() in {"1", "true", "yes", "on"}


DEBUG_ENABLED = _env_bool("AISA_DEBUG", "0")


# Default settings
DEFAULT_SETTINGS = {
    "exchange": "NSE",
    "timeframe": "daily",
    "analysis_types": ["technical", "fundamental", "ai"],
    "risk_profile": "medium",
    "output_format": "json",
    "debug": DEBUG_ENABLED,
}


@cl.on_chat_start
async def on_chat_start():
    """Initialize chat session."""
    cl.user_session.set("analysis_settings", DEFAULT_SETTINGS.copy())

    await cl.Message(
        content=(
            "📈 **Welcome to AI Stock Agent!**\n\n"
            "Configure your preferences using the **settings panel (gear icon ⚙️)** in the chat input.\n\n"
            "**Current Settings:**\n"
            f"- Exchange: {DEFAULT_SETTINGS['exchange']}\n"
            f"- Timeframe: {DEFAULT_SETTINGS['timeframe']}\n"
            f"- Analysis Types: {', '.join(DEFAULT_SETTINGS['analysis_types'])}\n"
            f"- Risk Profile: {DEFAULT_SETTINGS['risk_profile']}\n"
            f"- Output Format: {DEFAULT_SETTINGS['output_format']}\n\n"
            "**Quick Commands (if panel not available):**\n"
            "- `exchange NSE|BSE`\n"
            "- `timeframe daily|weekly|monthly|quarterly|yearly`\n"
            "- `risk low|medium|high`\n"
            "- `format json|html|email`\n"
            "- `analyses technical,fundamental,sentiment,trend,ai`\n\n"
            "**Enter a stock ticker to begin.** (e.g., RELIANCE, TCS)"
        )
    ).send()


@cl.on_message
async def on_message(message: cl.Message):
    """Handle user messages and run analysis pipeline."""
    settings = cl.user_session.get("analysis_settings") or DEFAULT_SETTINGS.copy()

    text = message.content.strip()

    if not text:
        return

    parts = text.split()

    # Handle inline settings commands
    if parts[0].lower() == "exchange" and len(parts) > 1:
        new_val = parts[1].upper()
        if new_val in ["NSE", "BSE"]:
            settings["exchange"] = new_val
            cl.user_session.set("analysis_settings", settings)
            await cl.Message(content=f"✅ Exchange set to: {new_val}").send()
        else:
            await cl.Message(content="Invalid exchange. Use: NSE or BSE").send()
        return

    if parts[0].lower() == "timeframe" and len(parts) > 1:
        new_val = parts[1].lower()
        if new_val in ["daily", "weekly", "monthly", "quarterly", "yearly"]:
            settings["timeframe"] = new_val
            cl.user_session.set("analysis_settings", settings)
            await cl.Message(content=f"✅ Timeframe set to: {new_val}").send()
        else:
            await cl.Message(content="Invalid timeframe. Use: daily, weekly, monthly, quarterly, yearly").send()
        return

    if parts[0].lower() == "risk" and len(parts) > 1:
        new_val = parts[1].lower()
        if new_val in ["low", "medium", "high"]:
            settings["risk_profile"] = new_val
            cl.user_session.set("analysis_settings", settings)
            await cl.Message(content=f"✅ Risk profile set to: {new_val}").send()
        else:
            await cl.Message(content="Invalid risk. Use: low, medium, high").send()
        return

    if parts[0].lower() == "format" and len(parts) > 1:
        new_val = parts[1].lower()
        if new_val in ["json", "html", "email"]:
            settings["output_format"] = new_val
            cl.user_session.set("analysis_settings", settings)
            await cl.Message(content=f"✅ Output format set to: {new_val}").send()
        else:
            await cl.Message(content="Invalid format. Use: json, html, email").send()
        return

    if parts[0].lower() == "analyses" and len(parts) > 1:
        types = [t.strip() for t in parts[1].split(",") if t.strip() in ["technical", "fundamental", "sentiment", "trend", "ai"]]
        settings["analysis_types"] = types if types else ["technical", "fundamental", "ai"]
        cl.user_session.set("analysis_settings", settings)
        await cl.Message(content=f"✅ Analysis types set to: {settings['analysis_types']}").send()
        return

    # Parse ticker for analysis
    ticker = parts[0].upper()
    mode = "local"
    
    if len(parts) >= 2:
        if parts[0].upper() in ["NSE", "BSE"]:
            settings["exchange"] = parts[0].upper()
            ticker = parts[1].upper()
        elif parts[1].lower() in ["local", "cloud"]:
            mode = parts[1].lower()

    # Build ui_payload from user session settings
    ui_payload = {
        "symbol": ticker,
        "exchange": settings.get("exchange", "NSE"),
        "timeframe": settings.get("timeframe", "daily"),
        "analysis_types": settings.get("analysis_types", ["technical", "fundamental", "ai"]),
        "risk_profile": settings.get("risk_profile", "medium"),
        "output_format": settings.get("output_format", "json"),
        "debug": settings.get("debug", DEBUG_ENABLED),
        "mode": mode,
    }

    await cl.Message(
        content=f"🔍 **Running analysis for {ticker}** ({mode} mode)...\n\n"
        f"**Settings:** Exchange={ui_payload['exchange']}, Timeframe={ui_payload['timeframe']}, "
        f"Analyses={', '.join(ui_payload['analysis_types'])}, Risk={ui_payload['risk_profile']}"
    ).send()

    master = await asyncio.to_thread(
        run_pipeline,
        symbol=ticker,
        ui_payload=ui_payload,
    )

    if master.get("orchestrator", {}).get("status") != "complete":
        errors = master.get("errors", [])
        await cl.Message(
            content=f"❌ **Pipeline Failed:**\n```json\n{json.dumps(errors, indent=2, default=str)}\n```"
        ).send()
        return

    ai = master.get("ai_report", {})
    if ai:
        response = (
            f"**📊 Analysis Report for {ticker}**\n\n"
            f"**Summary:** {ai.get('summary', 'N/A')}\n\n"
            f"**Sentiment:** {ai.get('sentiment', 'N/A')}\n"
            f"**Recommendation:** {ai.get('recommendation', 'N/A')}\n"
            f"**Probability:** {ai.get('probability', 'N/A')}"
        )
        await cl.Message(content=response).send()
    else:
        await cl.Message(content="No AI report generated. Ensure 'ai' is selected in Analysis Types.").send()


@cl.on_settings_update
def on_settings_update(settings: dict):
    """Handle settings updates from the UI chat settings panel."""
    cl.user_session.set("analysis_settings", settings)
