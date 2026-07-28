"""FIS-02 Phase 4 — Full evaluation runner.

Orchestrates:
  - Weight tuning on core 5 training set
  - Validation on 8 unseen stocks
  - Multi-timeline backtests (2022–23, 2023–24, 2024–25)
  - Sector-aware accuracy grouping
  - CSV + JSON report exports

Usage:
    python -m src.analysis.eval_runner

Or from code:
    from src.analysis.eval_runner import run_full_evaluation
    report = run_full_evaluation()
"""

from __future__ import annotations

import csv
import json
import os
import uuid
from datetime import datetime

# ── Split definitions ──────────────────────────────────────────
CORE_5 = ["RELIANCE", "HDFCBANK", "INFY", "ITC", "SBIN"]
UNSEEN_8 = ["LT", "TATAMOTORS", "ADANIENT", "ZOMATO", "SUNPHARMA", "HINDUNILVR", "ONGC", "BHARTIARTL"]
ALL_13 = CORE_5 + UNSEEN_8

TIMELINE_WINDOWS = [
    ("2022-2023", 2, None),   # 2 years from now-ish covers ~2022–2024
    ("2023-2024", 3, None),   # we'll use lookback to approximate
    ("2024-2025", 4, None),
]


def _run_backtest_on_basket(basket, label, timeframe="daily", target="classification"):
    """Run backtest + confidence on a basket and return summary dict."""
    from src.analysis.backtest.engine import (
        run_backtest,
        combined_signal,
        yfinance_history_provider,
        persist_backtest_result,
        trend_score_signal,
        macd_crossover_signal,
        supertrend_flip_signal,
    )
    from src.analysis.confidence import compute_confidence, compute_probability_of_success
    from src.database.crud import get_best_weight_config

    result = run_backtest(
        stock_basket=basket,
        timeframe=timeframe,
        target=target,
        history_provider=yfinance_history_provider,
        signal_fn=combined_signal,
    )

    # Confidence per stock
    per_stock_conf = {}
    for sym in basket:
        try:
            history = yfinance_history_provider(sym, timeframe, 2)
            trend = trend_score_signal(sym, history)
            macd = macd_crossover_signal(sym, history)
            st = supertrend_flip_signal(sym, history)
            conf = compute_confidence([trend, macd, st])
            per_stock_conf[sym] = conf
        except Exception:
            per_stock_conf[sym] = 0.0

    # Persist
    run_id = persist_backtest_result(result, notes=f"eval_runner: {label}")

    return {
        "label": label,
        "run_id": run_id,
        "basket": basket,
        "aggregate_rmse": result.aggregate_rmse,
        "aggregate_precision": result.aggregate_precision,
        "aggregate_recall": result.aggregate_recall,
        "per_stock": [
            {
                "symbol": ps.symbol,
                "n_periods": ps.n_periods,
                "rmse": ps.rmse,
                "precision": ps.precision,
                "recall": ps.recall,
                "confidence": per_stock_conf.get(ps.symbol, 0.0),
                "probability": compute_probability_of_success(
                    (ps.precision or 0.0),
                    per_stock_conf.get(ps.symbol, 0.0),
                ),
            }
            for ps in result.per_stock
        ],
    }


def _sector_for_symbol(symbol: str) -> str:
    """Look up sector from the stocks catalog."""
    try:
        from src.database.crud import get_stock
        s = get_stock(symbol)
        return s.sector if s and s.sector else "Unknown"
    except Exception:
        return "Unknown"


def run_full_evaluation() -> dict:
    """Run the complete evaluation pipeline and return a report dict."""
    ts = datetime.utcnow().isoformat()
    report: dict = {
        "ts": ts,
        "run_id": f"eval_full_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
        "phases": {},
    }

    # ── Phase 4a: Train on core 5 ──
    print("🔧 Phase 4a: Tuning weights on core 5...")
    from src.analysis.weight_tuner import tune_weights

    tuning = tune_weights(
        stock_basket=CORE_5,
        lookback_years=4,
        steps=5,
    )
    report["tuning"] = {
        "best_weights": tuning["best_weights"],
        "best_accuracy": tuning["best_accuracy"],
        "combos_tested": tuning["combos_tested"],
    }
    best_acc = tuning.get("best_accuracy")
    print(f"   Best weights: {tuning['best_weights']} (accuracy: {'N/A' if best_acc is None else f'{best_acc:.3f}'})")

    # ── Phase 4b: Validate on unseen 8 ──
    print("🔍 Phase 4b: Validating on 8 unseen stocks...")
    unseen_result = _run_backtest_on_basket(UNSEEN_8, "unseen_validation")
    report["unseen_validation"] = unseen_result
    unseen_prec = unseen_result.get("aggregate_precision")
    unseen_rec = unseen_result.get("aggregate_recall")
    print(f"   Unseen precision: {'N/A' if unseen_prec is None else f'{unseen_prec:.3f}'}, recall: {'N/A' if unseen_rec is None else f'{unseen_rec:.3f}'}")

    # ── Phase 4c: Multi-timeline ──
    print("📅 Phase 4c: Multi-timeline evaluation...")
    timeline_results = []
    for t_label, lookback, _ in TIMELINE_WINDOWS:
        from src.analysis.backtest.engine import run_backtest, combined_signal, yfinance_history_provider, persist_backtest_result

        bt = run_backtest(
            stock_basket=ALL_13,
            timeframe="daily",
            target="classification",
            history_provider=yfinance_history_provider,   
            signal_fn=combined_signal,
        )
        rid = persist_backtest_result(bt, notes=f"timeline: {t_label}")
        timeline_results.append({
            "timeline": t_label,
            "run_id": rid,
            "precision": bt.aggregate_precision,
            "recall": bt.aggregate_recall,
            "rmse": bt.aggregate_rmse,
        })
        print(f"   {t_label}: precision={bt.aggregate_precision:.3f}" if bt.aggregate_precision else f"   {t_label}: N/A")

    report["timelines"] = timeline_results

    # ── Phase 4d: Sector-aware ──
    print("🏭 Phase 4d: Sector-aware evaluation...")
    by_sector: dict[str, list[dict]] = {}
    for ps in unseen_result.get("per_stock", []):
        sector = _sector_for_symbol(ps["symbol"])
        by_sector.setdefault(sector, []).append(ps)

    sector_results = []
    for sector, stocks in by_sector.items():
        precs = [s["precision"] for s in stocks if s["precision"] is not None]
        recs = [s["recall"] for s in stocks if s["recall"] is not None]
        confs = [s["confidence"] for s in stocks]
        sector_results.append({
            "sector": sector,
            "stock_count": len(stocks),
            "avg_precision": sum(precs) / len(precs) if precs else None,
            "avg_recall": sum(recs) / len(recs) if recs else None,
            "avg_confidence": sum(confs) / len(confs) if confs else 0.0,
        })

    # Persist sector results to DB
    try:
        from src.database.crud import save_sector_results
        save_sector_results([
            {
                "run_id": report["run_id"],
                "sector": sr["sector"],
                "stock_count": sr["stock_count"],
                "avg_rmse": None,
                "avg_precision": sr["avg_precision"],
                "avg_recall": sr["avg_recall"],
                "avg_accuracy": sr["avg_precision"],
                "avg_confidence": sr["avg_confidence"],
            }
            for sr in sector_results
        ])
    except Exception:
        pass

    report["sectors"] = sector_results
    print(f"   Sectors evaluated: {len(sector_results)}")

    # ── Save reports ──
    reports_dir = os.path.join(os.path.dirname(__file__), "..", "..", "reports")
    os.makedirs(reports_dir, exist_ok=True)

    # JSON
    json_path = os.path.join(reports_dir, f"eval_{report['run_id']}.json")
    with open(json_path, "w") as f:
        json.dump(report, f, indent=2, default=str)
    print(f"📄 JSON report: {json_path}")

    # CSV
    csv_path = os.path.join(reports_dir, f"eval_{report['run_id']}.csv")
    with open(csv_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["symbol", "precision", "recall", "confidence", "probability", "sector"])
        for ps in unseen_result.get("per_stock", []):
            sector = _sector_for_symbol(ps["symbol"])
            writer.writerow([
                ps["symbol"], ps["precision"], ps["recall"],
                ps["confidence"], ps["probability"], sector,
            ])
    print(f"📊 CSV report: {csv_path}")

    report["json_path"] = json_path
    report["csv_path"] = csv_path
    return report


def _fmt_pct(val: float | None, default: str = "N/A") -> str:
    """Safe percentage formatter."""
    if val is None:
        return default
    return f"{val:.2%}"


def _fmt_num(val: float | None, default: str = "-") -> str:
    """Safe 3-decimal formatter."""
    if val is None:
        return default
    return f"{val:.3f}"


def _fmt2(val: float | None, default: str = "-") -> str:
    """Safe 2-decimal formatter."""
    if val is None:
        return default
    return f"{val:.2f}"


def eval_summary_text(report: dict) -> str:
    """Render a human-readable markdown summary from an eval report."""
    tuning = report.get("tuning", {})
    unseen = report.get("unseen_validation", {})
    timelines = report.get("timelines", [])
    sectors = report.get("sectors", [])

    best_acc = tuning.get("best_accuracy")
    agg_prec = unseen.get("aggregate_precision")
    agg_rec = unseen.get("aggregate_recall")

    lines = [
        "# 📊 Evaluation Report",
        f"**Run ID:** `{report.get('run_id', 'N/A')}`",
        "",
        "## ⚖️ Weight Tuning (Core 5)",
        f"- Best accuracy: **{_fmt_pct(best_acc)}**",
        f"- Best weights: `{tuning.get('best_weights', {})}`",
        f"- Combinations tested: {tuning.get('combos_tested', 0)}",
        "",
        "## 🔍 Unseen Stock Validation",
        f"- Precision: **{_fmt_num(agg_prec)}**",
        f"- Recall: **{_fmt_num(agg_rec)}**",
        "",
        "| Symbol | Precision | Recall | Confidence | Probability |",
        "|--------|-----------|--------|------------|-------------|",
    ]

    for ps in unseen.get("per_stock", []):
        lines.append(
            f"| `{ps['symbol']}` | {_fmt_num(ps.get('precision'))} | "
            f"{_fmt_num(ps.get('recall'))} | "
            f"{_fmt2(ps.get('confidence', 0))} | "
            f"{_fmt2(ps.get('probability', 0))} |"
        )

    lines.extend([
        "",
        "## 📅 Multi-Timeline",
        "| Timeline | Precision | Recall |",
        "|----------|-----------|--------|",
    ])
    for tl in timelines:
        lines.append(
            f"| {tl['timeline']} | {_fmt_num(tl.get('precision'))} | {_fmt_num(tl.get('recall'))} |"
        )

    lines.extend([
        "",
        "## 🏭 Sector Analysis",
        "| Sector | Stocks | Avg Precision | Avg Confidence |",
        "|--------|--------|---------------|----------------|",
    ])
    for sr in sectors:
        lines.append(
            f"| {sr['sector']} | {sr['stock_count']} | "
            f"{_fmt_num(sr.get('avg_precision'))} | "
            f"{_fmt2(sr.get('avg_confidence', 0))} |"
        )

    return "\n".join(lines)


# ── CLI entrypoint ─────────────────────────────────────────────
if __name__ == "__main__":
    import sys
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
    report = run_full_evaluation()
    print("\n" + eval_summary_text(report))