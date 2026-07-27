"""Chainlit UI for AI Stock Agent — Gear Panel Dropdowns + Inline Dashboard.

Two-zone layout:
  Zone 1 — Gear panel (⚙️) with real interactive dropdowns
  Zone 2 — Chat message dashboard with catalog + Run Analysis button

Settings panel order: Exchange → Stock → Timeframe → Risk → Analyses → Output → Context

Bug fix: typed words only override the selected stock if they are valid DB catalog symbols.
"""

import asyncio
import json
import os
from pathlib import Path

import chainlit as cl
from dotenv import load_dotenv
from src.core.orchestrator import run_pipeline
from src.database import crud
from src.ui.stock_catalog_ui import get_stock_choice_values, catalog_summary_text


load_dotenv(Path(__file__).resolve().parents[2] / ".env")


def _env_bool(name: str, default: str = "0") -> bool:
    return str(os.getenv(name, default)).strip().lower() in {"1", "true", "yes", "on"}


DEBUG_ENABLED = _env_bool("AISA_DEBUG", "0")


DEFAULT_SETTINGS = {
    "symbol": None,
    "exchange": "NSE",
    "timeframe": "daily",
    "analysis_types": ["technical", "fundamental", "ai"],
    "risk_profile": "medium",
    "output_format": "json",
    "user_context": "",
    "debug": DEBUG_ENABLED,
}


def _settings_summary(settings: dict) -> str:
    """One-line summary of current settings."""
    sym = settings.get("symbol") or "(no stock)"
    ex = settings.get("exchange", "NSE")
    tf = settings.get("timeframe", "daily")
    risk = settings.get("risk_profile", "medium")
    analyses = ", ".join(settings.get("analysis_types", []))
    fmt = settings.get("output_format", "json")
    return (
        f"📊 **{ex}** | 🏷️ `{sym}` | ⏱️ {tf} | ⚡ {risk} | 📋 {analyses} | 📄 {fmt}"
    )


# ────────────────────────────────────────────────────────────────
#  ZONE 1 — Gear panel with real interactive dropdowns
# ────────────────────────────────────────────────────────────────
@cl.on_chat_start
async def on_chat_start():
    """Send the gear panel (dropdowns) + inline dashboard."""
    settings = DEFAULT_SETTINGS.copy()
    cl.user_session.set("analysis_settings", settings)

    # Build stock choices from DB catalog
    stock_values = get_stock_choice_values()
    stock_initial = stock_values[0] if stock_values else None

    # ── Gear panel: Exchange first ──
    await cl.ChatSettings(
        [
            cl.input_widget.Select(
                id="exchange",
                label="Exchange",
                values=["NSE", "BSE"],
                initial_value="NSE",
            ),
            cl.input_widget.Select(
                id="symbol",
                label="Stock Symbol",
                values=stock_values if stock_values else [""],
                initial_value=stock_initial,
            ),
            cl.input_widget.Select(
                id="timeframe",
                label="Timeframe",
                values=["daily", "weekly", "monthly", "quarterly", "yearly"],
                initial_value="daily",
            ),
            cl.input_widget.Select(
                id="risk_profile",
                label="Risk Profile",
                values=["low", "medium", "high"],
                initial_value="medium",
            ),
            cl.input_widget.MultiSelect(
                id="analysis_types",
                label="Analysis Types",
                values=["technical", "fundamental", "sentiment", "trend", "ai"],
                initial=["technical", "fundamental", "ai"],
            ),
            cl.input_widget.Select(
                id="output_format",
                label="Output Format",
                values=["json", "html", "email"],
                initial_value="json",
            ),
            cl.input_widget.TextInput(
                id="user_context",
                label="Investment Context (optional)",
                placeholder="e.g. Long-term dividend growth investor, 5-year horizon",
                initial="",
                multiline=True,
            ),
        ]
    ).send()

    # ── ZONE 2 — Dashboard message ──
    catalog = catalog_summary_text()

    dashboard = (
        "# 📈 AI Stock Agent\n\n"
        "### ⚙️ Current Settings\n"
        f"{_settings_summary(settings)}\n\n"
        + catalog
        + "\n\n"
        "### 💡 Quick Guide\n"
        "- **⚙️ Gear icon** (below): open dropdowns to pick exchange, stock, timeframe, risk, etc.\n"
        "- **🔍 Run Analysis** (below): run analysis for the selected stock\n"
        "- **Text commands**: type `RELIANCE` or `TCS` to run analysis; "
        "`timeframe weekly`, `risk high`, `exchange BSE` to change settings\n"
        "- **Context**: type `context I am a swing trader` to personalize AI reports"
    )

    await cl.Message(content=dashboard).send()

    # ── Run Analysis action button ──
    actions = [
        cl.Action(
            name="run_analysis",
            payload={},
            label="🔍 Run Analysis",
        )
    ]
    await cl.Message(content="", actions=actions).send()


# ────────────────────────────────────────────────────────────────
#  Gear panel auto-save
# ────────────────────────────────────────────────────────────────
@cl.on_settings_update
async def on_settings_update(settings: dict):
    """Auto-save gear panel changes to the user session."""
    cl.user_session.set("analysis_settings", settings)
    # Show updated summary
    await cl.Message(
        content=f"✅ **Settings updated**\n\n{_settings_summary(settings)}"
    ).send()


# ────────────────────────────────────────────────────────────────
#  "🔍 Run Analysis" button handler
# ────────────────────────────────────────────────────────────────
@cl.action_callback("run_analysis")
async def on_run_analysis(action: cl.Action):
    """User clicked the Run Analysis button."""
    settings = cl.user_session.get("analysis_settings") or DEFAULT_SETTINGS.copy()
    ticker = settings.get("symbol")

    if not ticker:
        await cl.Message(
            content=(
                "⚠️ **No stock selected.**\n\n"
                "Select a stock from the gear panel (⚙️) or type a ticker like `RELIANCE`."
            )
        ).send()
        return

    await _run_pipeline(ticker, settings)


# ────────────────────────────────────────────────────────────────
#  Chat message handler — commands + ticker entry
# ────────────────────────────────────────────────────────────────
@cl.on_message
async def on_message(message: cl.Message):
    """Handle text input: setting commands or ticker analysis."""
    settings = cl.user_session.get("analysis_settings") or DEFAULT_SETTINGS.copy()
    text = message.content.strip()

    if not text:
        return

    parts = text.split()

    # ── Setting commands ──
    if parts[0].lower() == "exchange" and len(parts) > 1:
        new_val = parts[1].upper()
        if new_val in ["NSE", "BSE"]:
            settings["exchange"] = new_val
            cl.user_session.set("analysis_settings", settings)
            await cl.Message(content=f"✅ Exchange → **{new_val}**").send()
        else:
            await cl.Message(content="❌ Use `exchange NSE` or `exchange BSE`").send()
        return

    if parts[0].lower() == "timeframe" and len(parts) > 1:
        new_val = parts[1].lower()
        valid = ["daily", "weekly", "monthly", "quarterly", "yearly"]
        if new_val in valid:
            settings["timeframe"] = new_val
            cl.user_session.set("analysis_settings", settings)
            await cl.Message(content=f"✅ Timeframe → **{new_val}**").send()
        else:
            await cl.Message(content=f"❌ Valid: {', '.join(valid)}").send()
        return

    if parts[0].lower() == "risk" and len(parts) > 1:
        new_val = parts[1].lower()
        if new_val in ["low", "medium", "high"]:
            settings["risk_profile"] = new_val
            cl.user_session.set("analysis_settings", settings)
            await cl.Message(content=f"✅ Risk → **{new_val}**").send()
        else:
            await cl.Message(content="❌ Use `risk low`, `risk medium`, or `risk high`").send()
        return

    if parts[0].lower() == "format" and len(parts) > 1:
        new_val = parts[1].lower()
        if new_val in ["json", "html", "email"]:
            settings["output_format"] = new_val
            cl.user_session.set("analysis_settings", settings)
            await cl.Message(content=f"✅ Output → **{new_val}**").send()
        else:
            await cl.Message(content="❌ Use `format json`, `format html`, or `format email`").send()
        return

    if parts[0].lower() == "analyses" and len(parts) > 1:
        types = [
            t.strip()
            for t in parts[1].split(",")
            if t.strip() in ["technical", "fundamental", "sentiment", "trend", "ai"]
        ]
        settings["analysis_types"] = types if types else ["technical", "fundamental", "ai"]
        cl.user_session.set("analysis_settings", settings)
        await cl.Message(content=f"✅ Analyses → **{', '.join(settings['analysis_types'])}**").send()
        return

    if parts[0].lower() == "context":
        ctx = " ".join(parts[1:]) if len(parts) > 1 else ""
        settings["user_context"] = ctx
        cl.user_session.set("analysis_settings", settings)
        await cl.Message(
            content=f"✅ Context → **\"{ctx}\"**" if ctx else "✅ Context cleared."
        ).send()
        return

    # ── Ticker entry with DB validation ──
    typed_word = parts[0].upper()

    # Only treat as a ticker if it exists in the catalog
    stock = crud.get_stock(typed_word)
    if stock and typed_word not in ["NSE", "BSE"]:
        settings["symbol"] = typed_word
        cl.user_session.set("analysis_settings", settings)
        ticker = typed_word
    else:
        # Use the already-selected stock from the gear panel
        ticker = settings.get("symbol")

    if not ticker:
        await cl.Message(
            content=(
                "⚠️ **No stock selected.**\n\n"
                "Open the gear panel (⚙️) to pick a stock, or type a valid ticker (e.g. `RELIANCE`)."
            )
        ).send()
        return

    await _run_pipeline(ticker, settings)


# ────────────────────────────────────────────────────────────────
#  Shared pipeline executor
# ────────────────────────────────────────────────────────────────
async def _run_pipeline(ticker: str, settings: dict):
    """Build ui_payload and run the orchestrator pipeline."""
    ui_payload = {
        "symbol": ticker,
        "exchange": settings.get("exchange", "NSE"),
        "timeframe": settings.get("timeframe", "daily"),
        "analysis_types": settings.get("analysis_types", ["technical", "fundamental", "ai"]),
        "risk_profile": settings.get("risk_profile", "medium"),
        "output_format": settings.get("output_format", "json"),
        "user_context": settings.get("user_context", ""),
        "debug": settings.get("debug", DEBUG_ENABLED),
        "mode": "local",
    }

    await cl.Message(
        content=(
            f"🔍 **Running analysis for `{ticker}`** …\n\n"
            f"{_settings_summary(settings)}"
            + (f"\n💬 Context: \"{ui_payload['user_context']}\"" if ui_payload.get("user_context") else "")
        )
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
            f"**📊 Analysis Report for `{ticker}`**\n\n"
            f"**Summary:** {ai.get('summary', 'N/A')}\n\n"
            f"**Sentiment:** {ai.get('sentiment', 'N/A')}\n"
            f"**Recommendation:** {ai.get('recommendation', 'N/A')}\n"
            f"**Probability:** {ai.get('probability', 'N/A')}"
        )
        await cl.Message(content=response).send()
    else:
        await cl.Message(
            content="No AI report generated. Ensure **ai** is included in your analysis types."
        ).send()