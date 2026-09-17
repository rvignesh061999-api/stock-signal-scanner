"""
rtnpower_strategy.py
RattanIndia Power (RTNPOWER.NS) specific signal logic, based on a
statistical analysis of 2,974 hourly bars (2024-09-10 to 2026-09-09).
See RTNPOWER_Intraday_Pattern_Analysis.md for full methodology.

Structurally similar to RPOWER.NS: both rules are time-of-day specific.
- DOWN setup: 10:15 IST bar + BULLISH body (Close > Open) -> predicts
  11:15 bar DOWN. This is a "fade the morning bullish bar" pattern —
  counter-intuitive but the strongest, largest-sample finding for this
  stock (72.4% train / 53.8% val / 66.7% test vs ~47-50% baseline).
- UP setup: 14:15 IST bar + relative volume 1.5-2.5x its own trailing
  20-bar average -> predicts 15:15 bar UP (67.3% / 58.8% / 51.7% vs
  ~40-47% baseline). Same structure as RPOWER's UP rule.

Both rules stayed on the correct side of baseline in all three
chronological periods — neither is flagged as overfit in the source
analysis, unlike the rejected 6-feature model (AUC dropped 0.619 ->
0.545 train-to-test).

Prediction target is the NEXT bar's direction — same "next_bar_close"
resolution mechanism as PCJEWELLER/RPOWER/INFY.
"""

from datetime import datetime, timedelta

IST_OFFSET = timedelta(hours=5, minutes=30)
VOL_BAND_LOW = 1.5
VOL_BAND_HIGH = 2.5
VOL_LOOKBACK = 20


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


def _is_1015_slot(bar_date_str):
    return _ist_time(bar_date_str) == "10:15:00"


def _is_1415_slot(bar_date_str):
    return _ist_time(bar_date_str) == "14:15:00"


def _relative_volume(rows_chrono_desc, index_of_bar):
    trailing = rows_chrono_desc[index_of_bar + 1: index_of_bar + 1 + VOL_LOOKBACK]
    if len(trailing) < VOL_LOOKBACK:
        return None
    avg_vol = sum(b["volume"] for b in trailing) / len(trailing)
    if avg_vol <= 0:
        return None
    return rows_chrono_desc[index_of_bar]["volume"] / avg_vol


def compute_rtnpower_signal(rows: list, source: str, capital: float = 10000):
    """
    rows: newest-first OHLCV list, needs at least VOL_LOOKBACK + 2 bars.
    rows[0] = current/latest bar; rows[1] = last fully-completed bar,
    the bar the rules are evaluated on.
    """
    if len(rows) < VOL_LOOKBACK + 2:
        return _avoid(rows[0]["close"] if rows else None, source, "Not enough bars to evaluate (need 22+)")

    current_bar = rows[0]
    last_completed = rows[1]
    price = current_bar["close"]

    if _is_frozen(last_completed):
        return _avoid(price, source, "Last completed bar is frozen (O=H=L=C) — no real trading, no signal")

    if _is_0915_slot(last_completed.get("date", "")):
        return _avoid(price, source, "09:15 slot — only 15-22 historical observations, statistically unusable")

    # ---- DOWN setup: 10:15 bar with a BULLISH body (fade pattern) ----
    if _is_1015_slot(last_completed.get("date", "")):
        if _direction(last_completed) == "UP":
            reasons = [
                "This is the 10:15 AM IST bar",
                f"Bullish body (close {last_completed['close']} > open {last_completed['open']})",
                "DOWN SCORE = 2 — 'morning bullish bar fades' pattern: historical hit rate "
                "54-72% across train/val/test, vs ~47-50% baseline",
            ]
            return {
                "symbol": "RTNPOWER.NS", "signal": "SHORT", "price": price,
                "reasons": reasons, "source": source, "exit_rule": "next_bar_close",
                "predicted_direction": "DOWN", "confidence": "high",
            }
        return _avoid(price, source, "10:15 bar but not bullish-bodied — DOWN setup requires Close > Open here")

    # ---- UP setup: 14:15 bar with relative volume in the 1.5-2.5x band ----
    if _is_1415_slot(last_completed.get("date", "")):
        rel_vol = _relative_volume(rows, 1)
        if rel_vol is not None and VOL_BAND_LOW <= rel_vol <= VOL_BAND_HIGH:
            reasons = [
                "This is the 2:15 PM IST bar",
                f"Relative volume {rel_vol:.2f}x its own trailing 20-bar average "
                f"(within the {VOL_BAND_LOW}-{VOL_BAND_HIGH}x band)",
                "UP SCORE = 2 — historical hit rate 52-67% across train/val/test, vs ~40-47% baseline",
            ]
            return {
                "symbol": "RTNPOWER.NS", "signal": "BUY", "price": price,
                "reasons": reasons, "source": source, "exit_rule": "next_bar_close",
                "predicted_direction": "UP", "confidence": "high",
            }
        return _avoid(price, source, "14:15 bar but relative volume not in the validated 1.5-2.5x band")

    return _avoid(price, source, "Not the 10:15 (DOWN) or 14:15 (UP) decision hour for RTNPOWER's validated setups")


def _avoid(price, source, reason):
    return {
        "symbol": "RTNPOWER.NS", "signal": "AVOID", "price": price,
        "reasons": [reason], "source": source, "exit_rule": None,
    }
