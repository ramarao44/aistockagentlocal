"""Weight tuning (FIS-02 Phase 3) — optimize signal weights via grid search.

Iterates over weight combinations, runs backtests, and picks the
configuration that maximizes aggregate accuracy. Stores best config
to DB so the `combined_signal` function automatically uses tuned weights
in future predictions.

Usage:
    from src.analysis.weight_tuner import tune_weights
    best = tune_weights(stock_basket=["RELIANCE", "INFY"], lookback_years=4)
    print(f"Best: {best}")
"""

from __future__ import annotations

import itertools
import json
import uuid
from datetime import datetime


def _grid_weights(steps: int = 5) -> list[dict[str, float]]:
    """Generate grid of weight combinations that sum to 1.0.

    Covers 4 signals (technical, fundamental, sentiment, trend) at
    `steps` increments. Skips global_weight (0.0 for MVP).
    """
    sig_names = ["technical", "fundamental", "sentiment", "trend"]
    values = [round(i / (steps - 1), 2) for i in range(steps)]  # [0.0, 0.25, 0.5, 0.75, 1.0]
    combos = []

    for combo in itertools.product(values, repeat=4):
        if abs(sum(combo) - 1.0) < 0.001:
            combos.append(dict(zip(sig_names, combo)))

    return combos


def tune_weights(
    stock_basket: list[str] | None = None,
    lookback_years: int = 4,
    timeframe: str = "daily",
    target: str = "classification",
    steps: int = 5,
    history_provider=None,
) -> dict:
    """Grid-search weight combinations and return the best one.

    Args:
        stock_basket: List of NSE symbols. Defaults to core 5 pilot set.
        lookback_years: Historical window (default 4 = 2022–2026).
        timeframe: 'daily' or 'weekly'.
        target: 'classification' (direction accuracy) or 'regression' or 'both'.
        steps: Grid granularity (5 = 0/0.25/0.5/0.75/1.0 increments).
        history_provider: None = yfinance real data.

    Returns:
        dict with keys: best_weights, best_accuracy, run_id, all_results.
    """
    from src.analysis.backtest.engine import (
        DEFAULT_STOCK_BASKET,
        run_backtest,
        combined_signal,
        yfinance_history_provider,
        persist_backtest_result,
    )
    from src.database.crud import save_weight_config, get_best_weight_config

    basket = stock_basket or ["RELIANCE", "HDFCBANK", "INFY", "ITC", "SBIN"]
    provider = history_provider or yfinance_history_provider
    combos = _grid_weights(steps)

    best_acc = -1.0
    best_weights = {}
    best_run_id = ""
    all_results: list[dict] = []

    # Reset best flag
    previous_best = get_best_weight_config()

    for idx, weights in enumerate(combos):
        # Temporarily save these weights so combined_signal can read them
        temp_run_id = f"tune_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:6]}"

        # Save as a temp weight config (no 'best' flag yet)
        cfg = {
            "run_id": temp_run_id,
            "technical_weight": weights["technical"],
            "fundamental_weight": weights["fundamental"],
            "sentiment_weight": weights["sentiment"],
            "trend_weight": weights["trend"],
            "global_weight": 0.0,
            "aggregate_accuracy": None,
            "is_best": 0,
            "ts": datetime.utcnow(),
        }
        try:
            save_weight_config(cfg)
        except Exception:
            pass

        # Run backtest with combined_signal (reads weights from DB)
        result = run_backtest(
            stock_basket=basket,
            timeframe=timeframe,
            target=target,
            params=None,
            history_provider=provider,
            signal_fn=combined_signal,
        )

        acc = result.aggregate_precision or 0.0
        f1 = None
        if result.aggregate_precision and result.aggregate_recall:
            prec = result.aggregate_precision
            rec = result.aggregate_recall
            if (prec + rec) > 0:
                f1 = 2 * prec * rec / (prec + rec)

        all_results.append({
            "weights": weights,
            "accuracy": acc,
            "f1": f1,
            "rmse": result.aggregate_rmse,
            "run_id": temp_run_id,
        })

        # Persist the backtest
        persist_backtest_result(result, run_id=temp_run_id, notes=f"Tuning run {idx + 1}/{len(combos)}")

        # Update best
        if acc > best_acc:
            best_acc = acc
            best_weights = dict(weights)
            best_run_id = temp_run_id

    # Mark the best weight config
    if best_run_id:
        best_cfg = {
            "run_id": best_run_id,
            "technical_weight": best_weights.get("technical", 0.25),
            "fundamental_weight": best_weights.get("fundamental", 0.25),
            "sentiment_weight": best_weights.get("sentiment", 0.25),
            "trend_weight": best_weights.get("trend", 0.25),
            "global_weight": 0.0,
            "aggregate_accuracy": best_acc,
            "is_best": 1,
            "tuned_from_run_id": previous_best.run_id if previous_best else None,
            "ts": datetime.utcnow(),
        }
        try:
            save_weight_config(best_cfg)
        except Exception:
            pass

    return {
        "best_weights": best_weights,
        "best_accuracy": best_acc,
        "run_id": best_run_id,
        "combos_tested": len(combos),
        "all_results": all_results,
    }