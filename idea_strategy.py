"""
idea_strategy.py
Vodafone Idea (IDEA.NS) specific signal logic, based on a statistical
analysis of 2,974 hourly bars (2024-09-10 to 2026-09-09). See
IDEA_Intraday_Pattern_Analysis.md for full methodology.

STRUCTURALLY DIFFERENT from every other stock's rule in this project:
IDEA's setup predicts the SAME bar's own close, not the next bar. When a
new bar OPENS with a gap up versus the prior bar's close, that same bar
tends to close DOWN (fade the gap). This is knowable the moment the new
bar opens — no need to wait for it to close before acting, and the
resolution target is that same bar, not the one after it.

This means: exit_rule="same_bar_close" (not "next_bar_close" like every
other stock) — see resolve_pending_signals in scan_intraday.py for the
matching resolution logic that checks the SAME bar's own outcome once
it's confirmed closed (i.e. once a later bar exists after it).

Only ONE validated setup exists for this stock — no UP setup was found
(same as SEPC and YESBANK).

Evidence: DOWN score>=1 (any gap up) held at 59.8% in test vs ~44-50%
baseline, and actually STRENGTHENED from validation (56.0%) to test
(59.8%) — the opposite of overfitting, the cleanest result across all
8 stocks analyzed. A tighter variant (gap up + 2-bar down streak +
bearish prior body, score=3) reached 68.8% in test but on a much smaller
sample — not implemented here, kept as a documented possible upgrade.
"""


def _direction(bar):
    if bar["close"] > bar["open"]:
        return "UP"
    elif bar["close"] < bar["open"]:
        return "DOWN"
    return "FLAT"


def _gap_up_pct(new_open, prev_close):
    if not prev_close:
        return 0
    return (new_open - prev_close) / prev_close * 100


GAP_UP_THRESHOLD_PCT = 0.05  # any meaningfully positive gap counts — not numerically specified
                               # in the source analysis beyond "gap up", chosen as a small
                               # threshold so pure noise/rounding doesn't count as a real gap


def compute_idea_signal(rows: list, source: str, capital: float = 10000):
    """
    rows: newest-first OHLCV list, at least 2 bars.
    rows[0] = the bar that JUST OPENED — this is what we're predicting
              the direction of (its own close), not the bar after it.
    rows[1] = the previous bar, whose close is the gap reference point.
    """
    if len(rows) < 2:
        return _avoid(rows[0]["close"] if rows else None, source, "Not enough bars to evaluate")

    current_bar = rows[0]  # the bar whose OWN direction we're predicting
    prev_bar = rows[1]
    price = current_bar["open"]  # signal fires at this bar's open, not its (unknown-yet) close

    gap_pct = _gap_up_pct(current_bar["open"], prev_bar["close"])

    if gap_pct >= GAP_UP_THRESHOLD_PCT:
        reasons = [
            f"This bar opened with a gap up of {gap_pct:.3f}% vs the prior bar's close",
            "DOWN SCORE = 1 — historical hit rate 56-60% (validation/test), vs ~44-50% baseline "
            "(strengthened out-of-sample — the cleanest single finding across all 8 stocks analyzed)",
            "Predicts THIS SAME bar closes down (fades the gap), not the next bar",
        ]
        return {
            "symbol": "IDEA.NS", "signal": "SHORT", "price": price,
            "reasons": reasons, "source": source, "exit_rule": "same_bar_close",
            "predicted_direction": "DOWN", "confidence": "medium",
        }

    return _avoid(price, source, "No gap-up at open — the only validated setup for this stock requires a gap up")


def _avoid(price, source, reason):
    return {
        "symbol": "IDEA.NS", "signal": "AVOID", "price": price,
        "reasons": [reason], "source": source, "exit_rule": None,
    }
