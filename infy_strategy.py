"""
infy_strategy.py
Infosys (INFY.NS) specific signal logic, based on a statistical analysis
of 2,964 hourly bars (2024-09-10 to 2026-09-09). See
INFY_Intraday_Pattern_Analysis.md for full methodology.

INFY is qualitatively different from every other stock analyzed in this
project: its baseline next-bar direction is almost a coin flip (50.0%
UP / 49.4% DOWN in training), unlike the other stocks' persistent
DOWN-leaning baseline. The ONLY validated edge is narrow and confined
to the 14:15 IST bar — every other hour of the day is genuinely no-edge
for this stock, not just unvalidated.

Both setups evaluate on the 14:15 bar, predicting the 15:15 (final) bar:
- DOWN (higher confidence): 14:15 bar closed in the TOP third of its own
  range -> next bar (15:15) DOWN. Consistent across train/val/test
  (66.4% / 61.3% / 65.4%) vs ~49-54% baseline.
- UP (lower confidence): 14:15 bar has a BEARISH body -> next bar (15:15)
  UP. Solid in train/test (61.1% / 64.9%) but dipped to baseline in
  validation (48.5%) - included per the project's standing "include low-
  confidence setups, monitor and drop if they don't hold" approach.

Priority: DOWN is checked first (per the source analysis's own decision
tree) since it's the higher-confidence, more consistent finding. A bar
could theoretically satisfy both conditions; DOWN takes priority.

Prediction target is the NEXT bar's direction — same "next_bar_close"
resolution mechanism as PCJEWELLER/RPOWER.
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


def _is_1415_slot(bar_date_str):
    return _ist_time(bar_date_str) == "14:15:00"


def compute_infy_signal(rows: list, source: str, capital: float = 10000):
    """
    rows: newest-first OHLCV list, at least 2 bars.
    rows[0] = current/latest bar (may still be forming)
    rows[1] = last fully-completed bar — the 14:15 bar the rules check
    """
    if len(rows) < 2:
        return _avoid(rows[0]["close"] if rows else None, source, "Not enough bars to evaluate")

    current_bar = rows[0]
    last_completed = rows[1]
    price = current_bar["close"]

    if not _is_1415_slot(last_completed.get("date", "")):
        return _avoid(price, source, "Not the 14:15 hour — no validated setup exists for any other hour in this stock")

    # DOWN checked first (higher confidence, per source analysis priority)
    if _close_position_tercile(last_completed) == "top":
        reasons = [
            "This is the 14:15 IST bar",
            "Closed in the top third of its own range",
            "DOWN SCORE = 1 — historical hit rate 61-66% across train/val/test, vs ~49-54% baseline "
            "(the most consistent finding for this stock)",
        ]
        return {
            "symbol": "INFY.NS", "signal": "SHORT", "price": price,
            "reasons": reasons, "source": source, "exit_rule": "next_bar_close",
            "predicted_direction": "DOWN", "confidence": "high",
        }

    # UP (lower confidence) — bearish body at 14:15
    if _direction(last_completed) == "DOWN":
        reasons = [
            "This is the 14:15 IST bar",
            "Bearish body (close < open)",
            "UP SCORE = 1 — LOW CONFIDENCE: strong in train (61.1%) and test (64.9%) but "
            "dipped to baseline in validation (48.5%) — monitor closely",
        ]
        return {
            "symbol": "INFY.NS", "signal": "BUY", "price": price,
            "reasons": reasons, "source": source, "exit_rule": "next_bar_close",
            "predicted_direction": "UP", "confidence": "low",
        }

    return _avoid(price, source, "14:15 bar but neither the top-third-close nor bearish-body condition was met")


def _avoid(price, source, reason):
    return {
        "symbol": "INFY.NS", "signal": "AVOID", "price": price,
        "reasons": [reason], "source": source, "exit_rule": None,
    }
