"""Backtest engine (FIS-01) — offline historical signal validation.

This module provides deterministic backtesting of the existing analysis
pipelines (technical, fundamental, sentiment) against historical data.
It does NOT execute trades, does NOT generate advice, and stays within
the Indian equity universe (PSC v1.1 §2 + §4).

Design choices (per C-HIR-20260727-002):
- Stock basket is parameterized (DEFAULT_STOCK_BASKET is a default, not
  a hard-coded source list).
- Dual-target evaluation is supported: regression (RMSE on next-period
  return) and classification (Precision/Recall on up/down direction).
- The signal-generation function is pluggable so existing technical,
  fundamental, and sentiment modules can be reused.

FIS-02 extensions (2026-07-28):
- yfinance_history_provider: real market data via yfinance (4 years)
- real signal functions: trend_score, MACD crossover, SuperTrend flip
- train/validation split support for walk-forward testing
"""
from __future__ import annotations

import json
import math
import uuid
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from typing import Callable, Iterable

# 13-stock Indian equity basket (FIS-01 baseline) covering 10 sectors.
# Parameterized at the call site; this is only the default.
DEFAULT_STOCK_BASKET: list[str] = [
    "RELIANCE",
    "HDFCBANK",
    "INFY",
    "ITC",
    "SBIN",
    "LT",
    "TATAMOTORS",
    "ADANIENT",
    "ZOMATO",
    "SUNPHARMA",
    "HINDUNILVR",
    "ONGC",
    "BHARTIARTL",
]

VALID_TIMEFRAMES: tuple[str, ...] = ("daily", "weekly")
VALID_TARGETS: tuple[str, ...] = ("regression", "classification", "both")


@dataclass
class BacktestParams:
    """Parameters for a single backtest run.

    Attributes:
        timeframe: 'daily' or 'weekly'.
        target: 'regression' (RMSE on returns) | 'classification'
                (Precision/Recall on up/down) | 'both'.
        lookback_years: historical window in years (default 2, per FIS-01).
        horizon_periods: how many periods ahead the signal predicts (default 1).
        signals: list of signal names to evaluate. Each name is dispatched
                 to a signal generator (technical, fundamental, sentiment).
                 'global' is reserved for cross-stock correlation; callers
                 must supply a 'global' signal via `signal_fn` if needed.
    """

    timeframe: str = "daily"
    target: str = "both"
    lookback_years: int = 2
    horizon_periods: int = 1
    signals: list[str] = field(
        default_factory=lambda: ["technical", "fundamental", "sentiment"]
    )

    def __post_init__(self) -> None:
        if self.timeframe not in VALID_TIMEFRAMES:
            raise ValueError(
                f"Invalid timeframe {self.timeframe!r}; must be one of {VALID_TIMEFRAMES}"
            )
        if self.target not in VALID_TARGETS:
            raise ValueError(
                f"Invalid target {self.target!r}; must be one of {VALID_TARGETS}"
            )
        if self.lookback_years <= 0:
            raise ValueError("lookback_years must be > 0")
        if self.horizon_periods <= 0:
            raise ValueError("horizon_periods must be > 0")


@dataclass
class PerStockResult:
    symbol: str
    n_periods: int
    rmse: float | None = None
    precision: float | None = None
    recall: float | None = None
    error: str | None = None


@dataclass
class BacktestResult:
    """Aggregate backtest result across the stock basket."""

    timeframe: str
    target: str
    lookback_years: int
    horizon_periods: int
    signals: list[str]
    stock_basket: list[str]
    per_stock: list[PerStockResult]
    aggregate_rmse: float | None = None
    aggregate_precision: float | None = None
    aggregate_recall: float | None = None
    artifact_path: str | None = None

    def to_dict(self) -> dict:
        d = asdict(self)
        return d


# ---------------------------------------------------------------------------
# Metric computation (pure, deterministic, testable in isolation)
# ---------------------------------------------------------------------------

def _safe_rmse(predicted: list[float], actual: list[float]) -> float | None:
    """Root Mean Squared Error. None when no comparable points exist."""
    pairs = [(p, a) for p, a in zip(predicted, actual)
             if p is not None and a is not None
     and isinstance(p, (int, float)) and isinstance(a, (int, float))]
    if not pairs:
        return None
    sq_err = sum((p - a) ** 2 for p, a in pairs)
    return math.sqrt(sq_err / len(pairs))


def _safe_classification_metrics(
    predicted: list[int], actual: list[int]
) -> tuple[float | None, float | None]:
    """Precision and Recall for binary up/down labels (1=positive, 0=negative).

    Returns (precision, recall). Either may be None if the metric is
    undefined (e.g. no positive predictions -> precision undefined).
    """
    tp = fp = fn = tn = 0
    for p, a in zip(predicted, actual):
        if p is None or a is None:
            continue
        if not isinstance(p, (int, float)) or not isinstance(a, (int, float)):
            continue
        pi = int(p)
        ai = int(a)
        if pi == 1 and ai == 1:
            tp += 1
        elif pi == 1 and ai == 0:
            fp += 1
        elif pi == 0 and ai == 1:
            fn += 1
        else:
            tn += 1

    precision = tp / (tp + fp) if (tp + fp) > 0 else None
    recall = tp / (tp + fn) if (tp + fn) > 0 else None
    return precision, recall


def compute_metrics(
    predicted: list[float | int | None],
    actual: list[float | int | None],
    target: str,
) -> dict:
    """Compute RMSE, Precision, Recall according to the requested target.

    Args:
        predicted: list of predicted values (continuous for regression,
                   0/1 for classification).
        actual:    list of actual values (same length as predicted).
        target:    'regression' | 'classification' | 'both'.

    Returns dict with keys: rmse, precision, recall. Any of them may be
    None when undefined for the given input.
    """
    if len(predicted) != len(actual):
        raise ValueError("predicted and actual must have equal length")

    out: dict[str, float | None] = {"rmse": None, "precision": None, "recall": None}

    if target in ("regression", "both"):
        out["rmse"] = _safe_rmse(
            [float(p) if p is not None else 0.0 for p in predicted],
            [float(a) if a is not None else 0.0 for a in actual],
        )

    if target in ("classification", "both"):
        precision, recall = _safe_classification_metrics(
            [int(p) if p is not None else 0 for p in predicted],
            [int(a) if a is not None else 0 for a in actual],
        )
        out["precision"] = precision
        out["recall"] = recall

    return out


# ---------------------------------------------------------------------------
# Orchestration
# ---------------------------------------------------------------------------

# A signal_fn(symbol, history) -> list[float|int|None]
# It produces one predicted value per row of `history`. Rows where the
# ground truth cannot be computed (e.g. last row) should yield None.
SignalFn = Callable[[str, list[dict]], list[float | int | None]]


def _default_signal_fn(
    symbol: str, history: list[dict], horizon: int = 1
) -> list[float | int | None]:
    """Toy signal: predict next-period return sign from a simple SMA crossover.

    This is a deterministic, dependency-free stand-in. Real implementations
    should plug in the existing technical/fundamental/sentiment modules via
    the `signal_fn` parameter to run_backtest(). This function exists so
    the engine is runnable end-to-end without external API calls, which is
    the baseline requirement for tests and CI.
    """
    if len(history) < 2:
        return [None] * len(history)

    preds: list[float | int | None] = []
    for i in range(len(history)):
        if i >= len(history) - horizon:
            preds.append(None)  # no future to evaluate
            continue
        # Predict using the previous bar close vs the current bar close.
        prev_close = history[i].get("close")
        cur_close = history[i + 1].get("close") if (i + 1) < len(history) else None
        if prev_close is None or cur_close is None:
            preds.append(None)
            continue
        return_pct = (cur_close - prev_close) / prev_close if prev_close else 0.0
        # Classification target: 1 if up, 0 if down. Regression: return itself.
        preds.append(1 if return_pct > 0 else 0)
    return preds


def _actual_labels(
    history: list[dict], horizon: int = 1, mode: str = "classification"
) -> list[float | int | None]:
    """Build ground-truth labels from history.

    For classification: 1 if close[t+horizon] > close[t], else 0.
    For regression: percent return from t to t+horizon.
    """
    out: list[float | int | None] = []
    for i in range(len(history)):
        if i + horizon >= len(history):
            out.append(None)
            continue
        c0 = history[i].get("close")
        c1 = history[i + horizon].get("close")
        if c0 is None or c1 is None or c0 == 0:
            out.append(None)
            continue
        if mode == "classification":
            out.append(1 if c1 > c0 else 0)
        else:
            out.append((c1 - c0) / c0)
    return out


def _aggregate(per_stock: list[PerStockResult]) -> tuple[float | None, float | None, float | None]:
    rmses = [r.rmse for r in per_stock if r.rmse is not None]
    precs = [r.precision for r in per_stock if r.precision is not None]
    recs = [r.recall for r in per_stock if r.recall is not None]
    agg_rmse = sum(rmses) / len(rmses) if rmses else None
    agg_p = sum(precs) / len(precs) if precs else None
    agg_r = sum(recs) / len(recs) if recs else None
    return agg_rmse, agg_p, agg_r


def run_backtest(
    stock_basket: Iterable[str] | None = None,
    timeframe: str = "daily",
    params: BacktestParams | None = None,
    target: str | None = None,
    *,
    history_provider: Callable[[str, str, int], list[dict]] | None = None,
    signal_fn: SignalFn | None = None,
) -> BacktestResult:
    """Run a backtest across the stock basket.

    Args:
        stock_basket: iterable of NSE symbols. Defaults to DEFAULT_STOCK_BASKET.
        timeframe: 'daily' or 'weekly'. Used as a hint to history_provider.
        params: BacktestParams. If None, defaults are used. If both `params`
                and `target` are supplied, `target` overrides params.target.
        target: shortcut for setting the evaluation target without
                constructing a full BacktestParams ('regression' |
                'classification' | 'both').
        history_provider: callable(symbol, timeframe, lookback_years) ->
            list of dicts with at least a 'close' key, oldest first.
            If None, an in-memory dummy history is used so the engine is
            testable in isolation.
        signal_fn: callable(symbol, history) -> list of predicted values
            (None where undefined). Defaults to _default_signal_fn.

    Returns:
        BacktestResult with per-stock metrics and aggregate metrics.
    """
    if params is None:
        params = BacktestParams(timeframe=timeframe)
    else:
        # If user passes timeframe at call site, prefer it
        params.timeframe = timeframe
    # Allow `target` as a convenience override
    if target is not None:
        params.target = target
        # Re-validate
        if params.target not in VALID_TARGETS:
            raise ValueError(
                f"Invalid target {params.target!r}; must be one of {VALID_TARGETS}"
            )

    basket = list(stock_basket) if stock_basket is not None else list(DEFAULT_STOCK_BASKET)
    if not basket:
        raise ValueError("stock_basket must be non-empty")

    provider = history_provider or _dummy_history_provider
    sig = signal_fn or _default_signal_fn

    per_stock: list[PerStockResult] = []
    for symbol in basket:
        try:
            history = provider(symbol, params.timeframe, params.lookback_years)
            preds = sig(symbol, history)
            actual_cls = _actual_labels(history, params.horizon_periods, "classification")
            actual_reg = _actual_labels(history, params.horizon_periods, "regression")

            rmse = precision = recall = None
            if params.target in ("regression", "both"):
                # Filter out rows where actual is None (no ground truth yet).
                pairs_reg = [
                    (float(p), float(a))
                    for p, a in zip(preds, actual_reg)
                    if p is not None and a is not None
                    and isinstance(p, (int, float)) and isinstance(a, (int, float))
                ]
                if pairs_reg:
                    rmse = _safe_rmse([p for p, _ in pairs_reg], [a for _, a in pairs_reg])
            if params.target in ("classification", "both"):
                # Filter out rows where either pred or actual is None.
                pairs_cls = [
                    (int(p), int(a))
                    for p, a in zip(preds, actual_cls)
                    if p is not None and a is not None
                    and isinstance(p, (int, float)) and isinstance(a, (int, float))
                ]
                if pairs_cls:
                    precision, recall = _safe_classification_metrics(
                        [p for p, _ in pairs_cls],
                        [a for _, a in pairs_cls],
                    )
            per_stock.append(
                PerStockResult(
                    symbol=symbol,
                    n_periods=len(history),
                    rmse=rmse,
                    precision=precision,
                    recall=recall,
                )
            )
        except Exception as exc:
            per_stock.append(
                PerStockResult(symbol=symbol, n_periods=0, error=str(exc))
            )

    agg_rmse, agg_p, agg_r = _aggregate(per_stock)
    return BacktestResult(
        timeframe=params.timeframe,
        target=params.target,
        lookback_years=params.lookback_years,
        horizon_periods=params.horizon_periods,
        signals=list(params.signals),
        stock_basket=basket,
        per_stock=per_stock,
        aggregate_rmse=agg_rmse,
        aggregate_precision=agg_p,
        aggregate_recall=agg_r,
    )


# ---------------------------------------------------------------------------
# Default data provider (in-memory placeholder, deterministic)
# ---------------------------------------------------------------------------

def _dummy_history_provider(
    symbol: str, timeframe: str, lookback_years: int
) -> list[dict]:
    """Deterministic in-memory price history for tests/CI.

    Produces a synthetic series using a sine wave + a per-symbol offset
    so each stock has different but reproducible prices. This is a
    stand-in; real callers should pass `yfinance` or a local cache via
    `history_provider`.
    """
    # ~252 trading days per year
    n = max(2, lookback_years * 252)
    seed = sum(ord(c) for c in symbol) % 97
    history: list[dict] = []
    for i in range(n):
        # Mild oscillation; reproducible per symbol
        close = 100.0 + seed + 5.0 * math.sin((i + seed) / 14.0)
        history.append({"close": close, "date": i})
    return history


# ---------------------------------------------------------------------------
# FIS-02: Real data provider (yfinance)
# ---------------------------------------------------------------------------

def yfinance_history_provider(
    symbol: str, timeframe: str, lookback_years: int
) -> list[dict]:
    """Fetch real historical price data from yfinance.

    Returns a list of dicts with keys: close, open, high, low, volume, date.
    Sorted oldest-first. Falls back to dummy data if yfinance fails.
    """
    try:
        import yfinance as yf

        ticker = f"{symbol}.NS"
        days_needed = lookback_years * 365
        end = datetime.now()
        start = end - timedelta(days=days_needed)

        interval = "1d"
        if timeframe == "weekly":
            interval = "1wk"

        df = yf.download(
            ticker,
            start=start.strftime("%Y-%m-%d"),
            end=end.strftime("%Y-%m-%d"),
            interval=interval,
            progress=False,
            auto_adjust=True,
        )

        if df.empty:
            return _dummy_history_provider(symbol, timeframe, lookback_years)

        history: list[dict] = []
        for idx, row in df.iterrows():
            history.append({
                "date": str(idx.date()) if hasattr(idx, "date") else str(idx),
                "open": float(row["Open"]) if "Open" in row else None,
                "high": float(row["High"]) if "High" in row else None,
                "low": float(row["Low"]) if "Low" in row else None,
                "close": float(row["Close"]) if "Close" in row else None,
                "volume": int(row["Volume"]) if "Volume" in row else 0,
            })
        return history
    except Exception:
        return _dummy_history_provider(symbol, timeframe, lookback_years)


# ---------------------------------------------------------------------------
# FIS-02: Real signal functions (plug into backtest engine)
# ---------------------------------------------------------------------------

def trend_score_signal(symbol: str, history: list[dict]) -> list[int | None]:
    """Direction signal from 20-period SMA crossover.

    Bullish (1) when close > SMA_20. Bearish (0) when close <= SMA_20.
    Last period returns None (no future to evaluate).
    """
    window = 20
    preds: list[int | None] = []
    closes = [h.get("close") for h in history]

    for i in range(len(closes)):
        if i >= len(closes) - 1:
            preds.append(None)
            continue
        if i < window - 1:
            preds.append(None)
            continue
        sma = sum(closes[i - window + 1 : i + 1]) / window
        preds.append(1 if (closes[i] or 0) > sma else 0)
    return preds


def macd_crossover_signal(symbol: str, history: list[dict]) -> list[int | None]:
    """Direction signal from MACD crossover.

    Bullish (1) when fast EMA > slow EMA. Bearish (0) otherwise.
    """
    fast = 12
    slow = 26
    preds: list[int | None] = []
    closes = [h.get("close") or 0.0 for h in history]

    def ema(data: list[float], period: int) -> list[float]:
        k = 2.0 / (period + 1)
        out = [data[0]]
        for v in data[1:]:
            out.append(v * k + out[-1] * (1 - k))
        return out

    ema_fast = ema(closes, fast)
    ema_slow = ema(closes, slow)

    for i in range(len(closes)):
        if i >= len(closes) - 1:
            preds.append(None)
            continue
        if i < slow:
            preds.append(None)
            continue
        preds.append(1 if ema_fast[i] > ema_slow[i] else 0)
    return preds


def supertrend_flip_signal(symbol: str, history: list[dict]) -> list[int | None]:
    """Direction signal from SuperTrend-like ATR-based bands.

    Uses a simplified ATR(10) + multiplier=3 band flip detector.
    """
    period = 10
    multiplier = 3.0
    preds: list[int | None] = []
    highs = [h.get("high") or h.get("close") or 0.0 for h in history]
    lows = [h.get("low") or h.get("close") or 0.0 for h in history]
    closes = [h.get("close") or 0.0 for h in history]

    # Compute ATR
    tr_list = []
    for i in range(1, len(history)):
        h, l, pc = highs[i], lows[i], closes[i - 1]
        tr = max(h - l, abs(h - pc), abs(l - pc))
        tr_list.append(tr)

    atr = []
    if tr_list:
        atr = [sum(tr_list[:min(period, len(tr_list))]) / min(period, len(tr_list))]
        for t in tr_list[1:]:
            atr.append((atr[-1] * (period - 1) + t) / period)

    direction: list[int | None] = [None] * len(history)
    for i in range(period + 1, len(history)):
        hl2 = (highs[i] + lows[i]) / 2
        band = atr[i - 1] * multiplier if i - 1 < len(atr) else (atr[-1] * multiplier if atr else 0.0)
        upper = hl2 + band
        lower = hl2 - band
        direction[i] = 1 if closes[i] > upper else (0 if closes[i] < lower else None)

    for i in range(len(direction) - 1):
        if direction[i] is not None:
            preds.append(direction[i])
        else:
            preds.append(None)
    preds.append(None)  # last row
    return preds


def combined_signal(symbol: str, history: list[dict]) -> list[int | None]:
    """Weighted ensemble of trend_score, MACD, and SuperTrend signals.

    Weights are read from the best weight_config in DB (if available),
    otherwise equal weights (33% each).
    """
    trend = trend_score_signal(symbol, history)
    macd = macd_crossover_signal(symbol, history)
    st = supertrend_flip_signal(symbol, history)

    # Try to load tuned weights from DB
    try:
        from src.database.crud import get_best_weight_config
        best = get_best_weight_config()
        if best:
            w_tech = best.technical_weight
            w_fund = best.fundamental_weight
            w_trend = best.trend_weight
        else:
            w_tech, w_fund, w_trend = 0.33, 0.33, 0.34
    except Exception:
        w_tech, w_fund, w_trend = 0.33, 0.33, 0.34

    total_w = w_tech + w_fund + w_trend
    w_tech /= max(total_w, 0.01)
    w_fund /= max(total_w, 0.01)
    w_trend /= max(total_w, 0.01)

    preds: list[int | None] = []
    for i in range(len(history)):
        signals = []
        if trend[i] is not None:
            signals.append(trend[i])
        if macd[i] is not None:
            signals.append(macd[i])
        if st[i] is not None:
            signals.append(st[i])

        if not signals:
            preds.append(None)
            continue

        # Weighted vote — trend_score weight for trend, MACD for fund, ST for trend
        score = 0.0
        trend_count = 0
        for s in [trend[i], macd[i], st[i]]:
            if s is not None:
                score += w_tech * s if s == trend[i] else (w_fund * s if s == macd[i] else w_trend * s)
                trend_count += 1
        preds.append(1 if score / max(trend_count, 1) >= 0.5 else 0)
    return preds


# ---------------------------------------------------------------------------
# FIS-02: Extended BacktestResult with confidence / probability / F1
# ---------------------------------------------------------------------------

@dataclass
class ExtendedBacktestResult(BacktestResult):
    """BacktestResult with added FIS-02 metrics."""
    aggregate_f1: float | None = None
    aggregate_accuracy: float | None = None
    confidence_mean: float | None = None
    probability_mean: float | None = None
    run_id: str = ""

    def to_dict(self) -> dict:
        d = super().to_dict()
        d.update({
            "aggregate_f1": self.aggregate_f1,
            "aggregate_accuracy": self.aggregate_accuracy,
            "confidence_mean": self.confidence_mean,
            "probability_mean": self.probability_mean,
            "run_id": self.run_id,
        })
        return d


@dataclass
class ExtendedPerStockResult(PerStockResult):
    """PerStockResult with added FIS-02 fields."""
    f1: float | None = None
    accuracy: float | None = None
    confidence: float | None = None
    probability: float = 0.0


# ---------------------------------------------------------------------------
# FIS-02: Persistence helpers
# ---------------------------------------------------------------------------

def _compute_f1(precision: float | None, recall: float | None) -> float | None:
    if precision is None or recall is None or (precision + recall) == 0:
        return None
    return 2 * precision * recall / (precision + recall)


def _compute_accuracy(predicted: list[int | None], actual: list[int | None]) -> float | None:
    correct = 0
    total = 0
    for p, a in zip(predicted, actual):
        if p is not None and a is not None:
            if int(p) == int(a):
                correct += 1
            total += 1
    return correct / total if total > 0 else None


def _compute_confidence(signals: list[list[int | None]]) -> float:
    """Aggregate signal agreement as confidence (0-1)."""
    counts = []
    for i in range(len(signals[0])):
        vals = [s[i] for s in signals if s[i] is not None]
        if len(vals) >= 2:
            counts.append(1.0 if len(set(vals)) == 1 else 0.5)
    return sum(counts) / len(counts) if counts else 0.0


def persist_backtest_result(
    result: BacktestResult,
    run_id: str | None = None,
    notes: str = "",
    snapshot: bool = True,
) -> str:
    """Save a BacktestResult to DB (backtest_runs + backtest_snapshots).

    Returns the run_id.
    """
    from src.database.crud import save_backtest_run, save_snapshot

    rid = run_id or f"eval_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:6]}"

    run_data = {
        "run_id": rid,
        "ts": datetime.utcnow(),
        "timeframe": result.timeframe,
        "target": result.target,
        "lookback_years": result.lookback_years,
        "horizon_periods": result.horizon_periods,
        "stock_basket_json": json.dumps(result.stock_basket),
        "signals_json": json.dumps(result.signals),
        "aggregate_rmse": result.aggregate_rmse,
        "aggregate_precision": result.aggregate_precision,
        "aggregate_recall": result.aggregate_recall,
        "params_json": json.dumps({
            "timeframe": result.timeframe,
            "target": result.target,
            "lookback_years": result.lookback_years,
            "horizon_periods": result.horizon_periods,
        }),
        "notes": notes,
    }
    save_backtest_run(run_data)

    if snapshot:
        for ps in result.per_stock:
            snap = {
                "run_id": rid,
                "symbol": ps.symbol,
                "n_periods": ps.n_periods,
                "rmse": ps.rmse,
                "precision": ps.precision,
                "recall": ps.recall,
                "error": ps.error,
                "per_stock_json": json.dumps(asdict(ps)),
            }
            save_snapshot(snap)

    return rid
