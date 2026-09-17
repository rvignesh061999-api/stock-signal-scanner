"""
yesbank_strategy.py
YES Bank (YESBANK.NS) specific signal logic, based on a statistical
analysis of ~2,970 hourly bars (2024-09-10 to 2026-09-09). See
YESBANK_Intraday_Pattern_Analysis.md for full methodology.

Only ONE validated setup exists — same as SEPC and IDEA, no UP
combination survived out-of-sample testing, and the source analysis
explicitly declines to provide one rather than present noise as signal.

DOWN setup: 10:15 IST bar + closed in the TOP third of its own range +
next bar opens with NO GAP vs this bar's close -> predicts 11:15 bar
DOWN. Remarkably consistent: 65.4% (train) / 66.7% (val) / 64.0% (test)
vs ~47-52% baseline — described in the source analysis as "the most
trustworthy single rule found" at the time it was written.

Same 3-condition/gap-on-next-bar-open structure as PCJEWELLER's DOWN
rule — score out of 3, gap condition checked using the current
(forming) bar's open vs the last completed bar's close.

Prediction target is the NEXT bar's direction — same "next_bar_close"
resolution mechanism used throughout this project.
"""

from datetime import datetime, timedelta

IST_OFFSET = timedelta(hours=5, minutes=30)
NO_GAP_THRESHOLD_PCT = 0.1  # same reasoning as pcjeweller_strategy.py / rpower_strategy.py


def _ist_time(bar_date_str):
    try:
        dt_utc = datetime.strptime(bar_date_str, "%Y-%m-%d %H:%M:%S")
        return (dt_utc + IST_OFFSET).strftime("%H:%M:%S")
    except (ValueError, TypeError):
        return ""


def _is_frozen(bar):
    return bar["open"] == bar["high"] == bar["low"] == bar["close"]


def _close_position_tercile(bar):
    rng = bar["high"] - bar["low"]
    if rng <= 0:
        return "middle"
    position = (bar["close"] - bar["low"]) / rng
    if position >= 2 / 3:
        return "top"
    elif position <= 1 / 3:
        return "bottom"
    return "middle"


def _gap_pct(new_open, prev_close):
    if not prev_close:
        return 0
    return abs(new_open - prev_close) / prev_close * 100


def _is_0915_slot(bar_date_str):
    return _ist_time(bar_date_str) == "09:15:00"


def _is_1015_slot(bar_date_str):
    return _ist_time(bar_date_str) == "10:15:00"


def compute_yesbank_signal(rows: list, source: str, capital: float = 10000):
    """
    rows: newest-first OHLCV list, at least 2 bars.
    rows[0] = current/latest bar (may still be forming)
    rows[1] = last fully-completed bar — must be the 10:15 IST bar
              for this stock's only validated setup to apply
    """
    if len(rows) < 2:
        return _avoid(rows[0]["close"] if rows else None, source, "Not enough bars to evaluate")

    current_bar = rows[0]
    last_completed = rows[1]
    price = current_bar["close"]

    if _is_frozen(last_completed):
        return _avoid(price, source, "Last completed bar is frozen (O=H=L=C) — no real trading, no signal")

    if _is_0915_slot(last_completed.get("date", "")):
        return _avoid(price, source, "09:15 slot — statistically unusable, too few observations")

    if not _is_1015_slot(last_completed.get("date", "")):
        return _avoid(price, source, "Not the 10:15 hour — no validated setup exists for any other hour in this stock")

    top_third = _close_position_tercile(last_completed) == "top"
    gap = _gap_pct(current_bar["open"], last_completed["close"])
    no_gap = gap < NO_GAP_THRESHOLD_PCT

    if top_third and no_gap:
        reasons = [
            "This is the 10:15 AM IST bar",
            "Closed in the top third of its own range (looked strong)",
            f"No gap into current bar ({gap:.3f}% < {NO_GAP_THRESHOLD_PCT}% threshold)",
            "DOWN SCORE = 3 — historical hit rate 64-67% across train/val/test, vs ~47-52% baseline "
            "(described as the most trustworthy single rule found across this stock's own analysis)",
        ]
        return {
            "symbol": "YESBANK.NS", "signal": "SHORT", "price": price,
            "reasons": reasons, "source": source, "exit_rule": "next_bar_close",
            "predicted_direction": "DOWN", "confidence": "high",
        }

    return _avoid(price, source, "10:15 bar but DOWN conditions not fully met (needs top-third close + no gap)")


def _avoid(price, source, reason):
    return {
        "symbol": "YESBANK.NS", "signal": "AVOID", "price": price,
        "reasons": [reason], "source": source, "exit_rule": None,
    }
