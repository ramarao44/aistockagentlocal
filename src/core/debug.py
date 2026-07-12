def dbg(master, module, action, status, msg, t=None):
    """
    Minimal debug logger.
    Only logs when master['ui']['debug'] == True.
    Appends tiny JSON messages to master['debug'].
    """
    try:
        if not master or not master.get("ui", {}).get("debug", False):
            return

        if "debug" not in master:
            master["debug"] = []

        master["debug"].append(
            {
                "m": module,
                "a": action,
                "s": status,
                "msg": msg,
                "t": t,
            }
        )
    except Exception:
        # Debug must never break pipeline
        pass
