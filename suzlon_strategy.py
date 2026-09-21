"""
suzlon_strategy.py
Suzlon Energy (SUZLON.NS) specific signal logic, based on a statistical
analysis of ~2,970 hourly bars (2024-09-10 to 2026-09-09). See
SUZLON_Intraday_Pattern_Analysis.md for full methodology.

- DOWN setup: 11:15 IST bar + bearish body + closed in the BOTTOM third
  of its own range -> predicts 12:15 bar DOWN. 67.3% (train) / 68.2%
  (val) / 65.7% (test) vs ~50-53% baseline.
- UP setup: bar is a Bullish Engulfing pattern + closed in the TOP third
  of its own range + no gap forming into the next bar -> predicts next
  bar UP. 52.9% (train) / 73.3% (val) / 57.1% (test) vs ~42-49%
  baseline.

Unlike RPOWER/RTNPOWER/YESBANK, SUZLON's DOWN rule is anchored to 11:15
(not 10:15), and its UP rule is NOT time-gated — it can fire whenever a
Bullish Engulfing forms with the right conditions, any hour.

Prediction target is the NEXT bar's direction — "next_bar_close"
resolution mechanism used throughout this project.
"""

from datetime import datetime, timedelta

IST_OFFSET = timedelta(hours=5, minutes=30)
NO_GAP_THRESHOLD_PCT = 0.1


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


def _is_bullish_engulfing(bar, prev_bar):
    prev_bull = prev_bar["close"] > prev_bar["open"]
    curr_bull = bar["close"] > bar["open"]
    body = abs(bar["close"] - bar["open"])
    prev_body = abs(prev_bar["close"] - prev_bar["open"])
    return (not prev_bull and curr_bull
            and bar["open"] <= prev_bar["close"]
            and bar["close"] >= prev_bar["open"]
            and body > prev_body)


def _gap_pct(new_open, prev_close):
    if not prev_close:
        return 0
    return abs(new_open - prev_close) / prev_close * 100


def _is_0915_slot(bar_date_str):
    return _ist_time(bar_date_str) == "09:15:00"


def _is_1115_slot(bar_date_str):
    return _ist_time(bar_date_str) == "11:15:00"


def compute_suzlon_signal(rows, source, capital=10000):
    if len(rows) < 3:
        return _avoid(rows[0]["close"] if rows else None, source, "Not enough bars to evaluate")

    current_bar = rows[0]
    last_completed = rows[1]
    prior_bar = rows[2]
    price = current_bar["close"]

    if _is_frozen(last_completed):
        return _avoid(price, source, "Last completed bar is frozen (O=H=L=C) — no real trading, no signal")

    if _is_0915_slot(last_completed.get("date", "")):
        return _avoid(price, source, "09:15 slot — statistically unusable, too few observations")

    if _is_1115_slot(last_completed.get("date", "")):
        if _direction(last_completed) == "DOWN" and _close_position_tercile(last_completed) == "bottom":
            reasons = [
                "This is the 11:15 AM IST bar",
                f"Bearish body (close {last_completed['close']} < open {last_completed['open']})",
                "Closed in the bottom third of its own range",
                "DOWN SCORE = 3 — historical hit rate 66-68% across train/val/test, vs ~50-53% baseline "
                "(the tightest, most consistent spread found across the stocks analyzed)",
            ]
            return {
                "symbol": "SUZLON.NS", "signal": "SHORT", "price": price,
                "reasons": reasons, "source": source, "exit_rule": "next_bar_close",
                "predicted_direction": "DOWN", "confidence": "high",
            }

    if _is_bullish_engulfing(last_completed, prior_bar) and _close_position_tercile(last_completed) == "top":
        gap = _gap_pct(current_bar["open"], last_completed["close"])
        if gap < NO_GAP_THRESHOLD_PCT:
            reasons = [
                "Last completed bar is a Bullish Engulfing pattern",
                "Closed in the top third of its own range",
                f"No gap into current bar ({gap:.3f}% < {NO_GAP_THRESHOLD_PCT}% threshold)",
                "UP SCORE = 2 — historical hit rate 53-73% across train/val/test, vs ~42-49% baseline",
            ]
            return {
                "symbol": "SUZLON.NS", "signal": "BUY", "price": price,
                "reasons": reasons, "source": source, "exit_rule": "next_bar_close",
                "predicted_direction": "UP", "confidence": "medium",
            }

    return _avoid(price, source, "Neither the validated DOWN nor UP setup conditions were met")


def _avoid(price, source, reason):
    return {
        "symbol": "SUZLON.NS", "signal": "AVOID", "price": price,
        "reasons": [reason], "source": source, "exit_rule": None,
    }
