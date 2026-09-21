"""
sepc_strategy.py
South East Power Company (SEPC.NS) specific signal logic, based on a
statistical analysis of 2,974 hourly bars (2024-09-10 to 2026-09-09).
See SEPC_Intraday_Pattern_Analysis.md for full methodology.

The simplest validated rule of all 8 stocks analyzed in this project —
just two conditions, no gap check, no volume, no engulfing pattern:

DOWN setup: 11:15 IST bar + bearish body (Close < Open) -> predicts
12:15 bar DOWN. 67.9% (train) / 57.6% (val) / 62.8% (test) vs a
~49-55% baseline — SEPC has the strongest DOWN-leaning baseline of any
stock analyzed (55.0% in training alone), so even "no trade" leans
bearish here.

No UP setup exists — the second stock (after YES Bank) where a
systematic scan of the 50 best-looking training UP combinations found
zero that replicated out of sample. Treat any UP-leaning read for this
stock as noise, per the source analysis's explicit conclusion.

Prediction target is the NEXT bar's direction — same "next_bar_close"
resolution mechanism used throughout this project.
"""

from datetime import datetime, timedelta

IST_OFFSET = timedelta(hours=5, minutes=30)


def _ist_time(bar_date_str):
    try:
        dt_utc = datetime.strptime(bar_date_str, "%Y-%m-%d %H:%M:%S")
        return (dt_utc + IST_OFFSET).strftime("%H:%M:%S")
    except (ValueError, TypeError):
        return ""


def _direction(bar):
    if bar["close"] > bar["open"]:
        return "UP"
    elif bar["close"] < bar["open"]:
        return "DOWN"
    return "FLAT"


def _is_frozen(bar):
    return bar["open"] == bar["high"] == bar["low"] == bar["close"]


def _is_0915_slot(bar_date_str):
    return _ist_time(bar_date_str) == "09:15:00"


def _is_1115_slot(bar_date_str):
    return _ist_time(bar_date_str) == "11:15:00"


def compute_sepc_signal(rows: list, source: str, capital: float = 10000):
    """
    rows: newest-first OHLCV list, at least 2 bars.
    rows[0] = current/latest bar (may still be forming)
    rows[1] = last fully-completed bar — must be the 11:15 IST bar
              for this stock's only validated setup to apply
    """
    if len(rows) < 2:
        return _avoid(rows[0]["close"] if rows else None, source, "Not enough bars to evaluate")

    current_bar = rows[0]
    last_completed = rows[1]
    price = current_bar["close"]

    if _is_frozen(last_completed):
        return _avoid(price, source, "Last completed bar is frozen (O=H=L=C) — isolated illiquidity patch, no signal")

    if _is_0915_slot(last_completed.get("date", "")):
        return _avoid(price, source, "09:15 slot — only 19-31 historical observations, statistically unusable")

    if not _is_1115_slot(last_completed.get("date", "")):
        return _avoid(price, source, "Not the 11:15 hour — no validated setup exists for any other hour in this stock")

    if _direction(last_completed) == "DOWN":
        reasons = [
            "This is the 11:15 AM IST bar",
            f"Bearish body (close {last_completed['close']} < open {last_completed['open']})",
            "DOWN SCORE = 2 — historical hit rate 58-68% across train/val/test, vs ~49-55% baseline "
            "(this stock's strongest structural DOWN bias of any analyzed — 55% of all bars are DOWN regardless of setup)",
        ]
        return {
            "symbol": "SEPC.NS", "signal": "SHORT", "price": price,
            "reasons": reasons, "source": source, "exit_rule": "next_bar_close",
            "predicted_direction": "DOWN", "confidence": "high",
        }

    return _avoid(price, source, "11:15 bar but not bearish-bodied — DOWN setup requires Close < Open here. "
                                    "No UP setup exists for this stock — none survived out-of-sample validation.")


def _avoid(price, source, reason):
    return {
        "symbol": "SEPC.NS", "signal": "AVOID", "price": price,
        "reasons": [reason], "source": source, "exit_rule": None,
    }
