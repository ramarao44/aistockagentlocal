"""Confidence scoring (FIS-02) — quantify prediction reliability.

Aggregates agreement across multiple signal sources to produce a
per-stock confidence score (0.0–1.0). Combined with historical
backtest accuracy, this feeds the Bayesian Probability of Success.
"""

from __future__ import annotations


def compute_confidence(
    signal_preds: list[list[int | None]],
    agreement_threshold: float = 0.6,
) -> float:
    """Compute average inter-signal agreement as a confidence score.

    Args:
        signal_preds: List of signal output lists. Each inner list is
                      one signal's predictions (0, 1, or None).
        agreement_threshold: Fraction of signals that must agree for a
                      period to count as "confident."

    Returns:
        Confidence score 0.0–1.0. 1.0 = all signals always agree.
        0.0 = no periods have enough signals to evaluate.
    """
    if not signal_preds or not any(signal_preds):
        return 0.0

    n_periods = max(len(s) for s in signal_preds)
    agreement_scores: list[float] = []

    for i in range(n_periods):
        vals = []
        for s in signal_preds:
            if i < len(s) and s[i] is not None:
                vals.append(s[i])

        if len(vals) < 2:
            continue

        # All agree
        if all(v == vals[0] for v in vals):
            agreement_scores.append(1.0)
        # Majority agree
        elif max(vals.count(1), vals.count(0)) / len(vals) >= agreement_threshold:
            agreement_scores.append(0.75)
        else:
            agreement_scores.append(0.5)

    return sum(agreement_scores) / len(agreement_scores) if agreement_scores else 0.0


def compute_probability_of_success(
    backtest_accuracy: float | None,
    confidence: float,
    prior: float = 0.5,
) -> float:
    """Bayesian probability of success = backtest_accuracy × confidence.

    Args:
        backtest_accuracy: Historical accuracy from backtest (0–1).
        confidence: Current signal agreement confidence (0–1).
        prior: Baseline probability (default 0.5 = coin flip).

    Returns:
        Probability score 0.0–1.0. None accuracy → confidence × prior.
    """
    acc = backtest_accuracy if backtest_accuracy is not None else prior
    # Bayesian update: P(success | signal) = P(signal | success) * P(success) / P(signal)
    # Simplified: accuracy × confidence, bounded between 0.1 and 0.9
    raw = acc * confidence
    return max(0.05, min(0.95, raw))


def aggregate_confidence_per_stock(
    per_stock_signals: dict[str, list[list[int | None]]],
) -> dict[str, float]:
    """Compute confidence for each stock from its signal array.

    Returns dict symbol -> confidence score.
    """
    return {
        symbol: compute_confidence(signals)
        for symbol, signals in per_stock_signals.items()
    }