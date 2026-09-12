"""
rpower_strategy.py
RPOWER.NS (Reliance Power) specific signal logic, based on a statistical
analysis of 2,988 hourly bars (2024-09-10 to 2026-09-09), chronologically
split into train/validation/test with no shuffling. See
RPOWER_Intraday_Pattern_Analysis.md for full methodology.

Unlike PCJEWELLER's rule (which can fire on any hour), BOTH of RPOWER's
validated rules are TIME-OF-DAY SPECIFIC:
- DOWN setup only evaluates on the 10:15 AM IST bar, predicting the 11:15 bar
- UP setup only evaluates on the 2:15 PM IST bar, predicting the 3:15 PM bar

IMPORTANT — evidence strength:
- DOWN (10:15 bearish body + no gap): stable ~59-61% across train/val/test
  vs ~48-54% baseline — the most stable finding across both stocks analyzed
- UP (14:15 bar + relative volume 1.5-2.5x its 20-bar average): STRENGTHENED
  out of sample (51.7% -> 68.2% -> 64.3%) — the strongest single finding
  across both PCJEWELLER and RPOWER analyses
- Both rules are well-evidenced (unlike PCJEWELLER's weak BUY setup) —
  still genuinely new/unproven in live forward trading, just built on
  stronger historical evidence

Prediction target is the NEXT bar's direction — same "next_bar_close"
resolution mechanism as PCJEWELLER (see resolve_pending_signals in
scan_intraday.py), reused generically for any symbol with this exit_rule.
"""

from datetime import datetime, timedelta

IST_OFFSET = timedelta(hours=5, minutes=30)
NO_GAP_THRESHOLD_PCT = 0.1  # same reasoning as pcjeweller_strategy.py — not numerically
                             # specified in the source analysis, chosen as a small threshold
VOL_BAND_LOW = 1.5   # "roughly 1.5-2.5x its own trailing 20-bar average" per the analysis
VOL_BAND_HIGH = 2.5
VOL_LOOKBACK = 20


def _ist_time(bar_date_str):
    """Converts stored UTC 'YYYY-MM-DD HH:MM:SS' to IST 'HH:MM:SS'."""
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


def _gap_pct(new_open, prev_close):
    if not prev_close:
        return 0
    return abs(new_open - prev_close) / prev_close * 100


def _is_0915_slot(bar_date_str):
    return _ist_time(bar_date_str) == "09:15:00"


def _is_1015_slot(bar_date_str):
    return _ist_time(bar_date_str) == "10:15:00"


def _is_1415_slot(bar_date_str):
    return _ist_time(bar_date_str) == "14:15:00"


def _relative_volume(rows_chrono_desc, index_of_bar):
    """
    rows_chrono_desc: newest-first list (same convention as everywhere else).
    index_of_bar: index of the bar to compute relative volume FOR.
    Returns bar_volume / (average of the 20 bars immediately BEFORE it),
    or None if there isn't enough history.
    """
    trailing = rows_chrono_desc[index_of_bar + 1: index_of_bar + 1 + VOL_LOOKBACK]
    if len(trailing) < VOL_LOOKBACK:
        return None
    avg_vol = sum(b["volume"] for b in trailing) / len(trailing)
    if avg_vol <= 0:
        return None
    return rows_chrono_desc[index_of_bar]["volume"] / avg_vol


def compute_rpower_signal(rows: list, source: str, capital: float = 10000):
    """
    rows: newest-first OHLCV list, needs at least VOL_LOOKBACK + 2 bars
    for the UP rule's volume average to be computable.
    rows[0] = current/latest bar (may still be forming)
    rows[1] = last fully-completed bar — the bar the rules are evaluated on
    """
    if len(rows) < VOL_LOOKBACK + 2:
        return _avoid(rows[0]["close"] if rows else None, source, "Not enough bars to evaluate (need 22+)")

    current_bar = rows[0]
    last_completed = rows[1]
    price = current_bar["close"]

    # ---- NO-TRADE conditions first ----
    if _is_frozen(last_completed):
        return _avoid(price, source, "Last completed bar is frozen (O=H=L=C) — no real trading, no signal")

    if _is_0915_slot(last_completed.get("date", "")):
        return _avoid(price, source, "09:15 slot — only 27-35 historical observations, statistically unusable")

    # ---- DOWN setup: only evaluated on the 10:15 IST bar ----
    if _is_1015_slot(last_completed.get("date", "")):
        bearish_body = _direction(last_completed) == "DOWN"
        gap = _gap_pct(current_bar["open"], last_completed["close"])
        no_gap = gap < NO_GAP_THRESHOLD_PCT

        if bearish_body and no_gap:
            reasons = [
                "This is the 10:15 AM IST bar",
                f"Bearish body confirmed (close {last_completed['close']} < open {last_completed['open']})",
                f"No gap into current bar ({gap:.3f}% < {NO_GAP_THRESHOLD_PCT}% threshold)",
                "DOWN SCORE = 3 — historical hit rate 59-61% across train/val/test, vs ~48-54% baseline "
                "(the most stable finding across both stocks analyzed)",
            ]
            return {
                "symbol": "RPOWER.NS", "signal": "SHORT", "price": price,
                "reasons": reasons, "source": source, "exit_rule": "next_bar_close",
                "predicted_direction": "DOWN", "confidence": "high",
            }
        return _avoid(price, source, "10:15 bar but DOWN conditions not fully met (needs bearish body + no gap)")

    # ---- UP setup: only evaluated on the 14:15 IST bar ----
    if _is_1415_slot(last_completed.get("date", "")):
        rel_vol = _relative_volume(rows, 1)  # index 1 = last_completed
        if rel_vol is not None and VOL_BAND_LOW <= rel_vol <= VOL_BAND_HIGH:
            reasons = [
                "This is the 2:15 PM IST bar",
                f"Relative volume {rel_vol:.2f}x its own trailing 20-bar average "
                f"(within the {VOL_BAND_LOW}-{VOL_BAND_HIGH}x band)",
                "UP SCORE = 2 — historical hit rate 52-68% across train/val/test, vs ~38-43% baseline "
                "(strengthened out of sample — the strongest single finding across both stocks analyzed)",
            ]
            return {
                "symbol": "RPOWER.NS", "signal": "BUY", "price": price,
                "reasons": reasons, "source": source, "exit_rule": "next_bar_close",
                "predicted_direction": "UP", "confidence": "high",
            }
        return _avoid(price, source, "14:15 bar but relative volume not in the validated 1.5-2.5x band")

    # ---- Any other hour: neither rule applies ----
    return _avoid(price, source, "Not the 10:15 (DOWN) or 14:15 (UP) decision hour for RPOWER's validated setups")


def _avoid(price, source, reason):
    return {
        "symbol": "RPOWER.NS", "signal": "AVOID", "price": price,
        "reasons": [reason], "source": source, "exit_rule": None,
    }
