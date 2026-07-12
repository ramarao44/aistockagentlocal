"""Timeframe engine for indicator selection and model weighting."""

from src.timeframe.indicator_map import get_indicator_set
from src.timeframe.model_weights import get_model_weights


def build_timeframe_config(
    timeframe: str | None,
    analysis_types: list[str] | None,
    risk_profile: str | None,
) -> dict:
    selected = (timeframe or "daily").strip().lower()
    enabled = set([x.strip().lower() for x in (analysis_types or []) if x])

    weights = get_model_weights(selected, risk_profile)
    if enabled:
        if "fundamental" not in enabled:
            weights["fundamental"] = 0.0
        if "technical" not in enabled:
            weights["technical"] = 0.0
        if "sentiment" not in enabled:
            weights["sentiment"] = 0.0

        total = sum(weights.values())
        if total > 0:
            weights = {k: round(v / total, 4) for k, v in weights.items()}

    return {
        "selected": selected,
        "indicator_set": get_indicator_set(selected),
        "fundamental_horizon": "quarterly" if selected in {"intraday", "daily", "weekly"} else "annual",
        "model_weights": weights,
    }


def evaluate_timeframe(payload: dict) -> dict:
    """Backward-compatible wrapper used by older scripts."""
    return build_timeframe_config(
        timeframe=payload.get("timeframe"),
        analysis_types=payload.get("analysis_types", []),
        risk_profile=payload.get("risk_profile"),
    )
