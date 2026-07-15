import os
from datetime import datetime

from src.core.artifacts import ensure_gen_dirs, write_text_artifact


def _env_debug_enabled() -> bool:
    return str(os.getenv("AISA_DEBUG", "0")).strip().lower() in {"1", "true", "yes", "on"}


def dbg(master, module, action, status, msg, t=None):
    """
    Debug logger for pipeline events.
    Writes structured events into master['debug'] and prints to console when enabled.
    """
    try:
        ui_debug = bool(master and master.get("ui", {}).get("debug", False))
        env_debug = _env_debug_enabled()

        if not ui_debug and not env_debug:
            return

        if master is not None and "debug" not in master:
            master["debug"] = []

        event = {
            "m": module,
            "a": action,
            "s": status,
            "msg": msg,
            "t": t,
        }

        if master is not None:
            master["debug"].append(event)

        timing = f" ({t} ms)" if t is not None else ""
        line = f"[AISA-DEBUG] [{module}] {action}/{status}: {msg}{timing}"
        print(line)

        ensure_gen_dirs()
        daily_name = datetime.now().strftime("debug_cli_%Y-%m-%d.log")
        existing = ""
        try:
            from pathlib import Path

            log_path = Path("gen") / "debug" / daily_name
            if log_path.exists():
                existing = log_path.read_text(encoding="utf-8")
        except Exception:
            existing = ""
        write_text_artifact("debug", daily_name, f"{existing}{line}\n")
    except Exception:
        # Debug must never break pipeline
        pass
