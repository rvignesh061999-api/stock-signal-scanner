"""
pcjeweller_strategy.py
PCJEWELLER.NS-specific signal logic, based on a statistical analysis of
2,983 hourly bars (2024-09-10 to 2026-09-09), chronologically split into
train/validation/test with no shuffling. See PCJEWELLER_Intraday_Pattern_Analysis.md
for the full methodology.

This REPLACES the generic candle+support/resistance+volume logic for
this one stock only — the validated rule here is a different kind of
pattern (body direction + close position within the bar's own range +
gap behavior), found through systematic testing, not assumed in advance.

IMPORTANT — confidence differs sharply between the three outcomes:
- SELL (DOWN setup): well-evidenced, held up out-of-sample (65.7%
  train / 52.8% validation / 64.0% test vs ~49% baseline)
- BUY (UP setup): weak evidence, only 13 validation trades — included
  per explicit request, to be monitored and dropped if it doesn't hold
  up going forward
- AVOID: well-supported no-trade conditions (frozen bars, Doji, thin
  09:15 slot, 2+ flat streak)

Prediction target is the NEXT bar's direction, not a price target — so
resolution/outcome checking works differently from the other 7 stocks
(see resolve_pcjeweller_signal in scan_intraday.py): a signal here
resolves after exactly 1 bar, as WIN if the next bar's direction
matched the prediction, LOSS if not.
"""

NO_GAP_THRESHOLD_PCT = 0.1  # gap smaller than this counts as "no gap" — not specified numerically
                             # in the source analysis, chosen as a reasonable small threshold;
                             # revisit if forward results look off because of this choice


def _direction(bar):
    if bar["close"] > bar["open"]:
        return "UP"
    elif bar["close"] < bar["open"]:
        return "DOWN"
    return "FLAT"


def _is_frozen(bar):
    return bar["open"] == bar["high"] == bar["low"] == bar["close"]


def _close_position_tercile(bar):
    """Returns 'top', 'middle', or 'bottom' third of the bar's own High-Low range."""
    rng = bar["high"] - bar["low"]
    if rng <= 0:
        return "middle"  # frozen/zero-range bar, arbitrary but harmless since frozen is checked separately
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
    """bar_date_str is 'YYYY-MM-DD HH:MM:SS' in whatever timezone the data was fetched in."""
    return bar_date_str.endswith("09:15:00") if len(bar_date_str) >= 8 else False


def compute_pcjeweller_signal(rows: list, source: str, capital: float = 10000):
    """
    rows: newest-first OHLCV list, at least 3 bars.
    rows[0] = current/latest bar (may still be forming during market hours)
    rows[1] = last fully-completed bar
    rows[2] = bar before that

    Returns a dict shaped similarly to signal_engine's SignalResult, plus
    an "exit_rule" field ("next_bar_close") that tells scan_intraday.py
    to resolve this signal differently from the other 7 stocks.
    """
    if len(rows) < 3:
        return {"symbol": "PCJEWELLER.NS", "signal": "AVOID", "price": rows[0]["close"] if rows else None,
                "reasons": ["Not enough bars to evaluate"], "source": source, "exit_rule": None}

    current_bar = rows[0]       # forming or just-completed bar
    last_completed = rows[1]    # the bar the rule conditions are evaluated on
    prior_bar = rows[2]

    price = current_bar["close"]
    reasons = []

    # ---- NO-TRADE conditions first (Part 11) ----
    if _is_frozen(last_completed):
        return _avoid(price, source, "Last completed bar is frozen (O=H=L=C) — no real trading, no signal")

    if _is_0915_slot(last_completed.get("date", "")):
        return _avoid(price, source, "09:15 slot — only 20-29 historical observations, statistically unusable")

    if _direction(last_completed) == "FLAT" and _direction(prior_bar) == "FLAT":
        return _avoid(price, source, "2+ consecutive FLAT bars — dead/illiquid patch, not a directional signal")

    # ---- SELL / DOWN setup (Part 10, the well-evidenced rule) ----
    # Conditions 1 & 2 evaluated on the last COMPLETED bar; condition 3
    # (gap) evaluated using the current bar's open vs that completed bar's close.
    bearish_body = _direction(last_completed) == "DOWN"
    middle_third_down = _close_position_tercile(last_completed) == "middle"
    gap = _gap_pct(current_bar["open"], last_completed["close"])
    no_gap = gap < NO_GAP_THRESHOLD_PCT

    down_score = sum([bearish_body, middle_third_down, no_gap])
    if down_score == 3:
        reasons = [
            f"Bearish body confirmed (close {last_completed['close']} < open {last_completed['open']})",
            "Closed in middle third of its own range (not climactic)",
            f"No gap into current bar ({gap:.3f}% < {NO_GAP_THRESHOLD_PCT}% threshold)",
            "DOWN SCORE = 3 — historical hit rate ~64% (test), ~49% baseline",
        ]
        return {
            "symbol": "PCJEWELLER.NS", "signal": "SHORT", "price": price,
            "reasons": reasons, "source": source, "exit_rule": "next_bar_close",
            "predicted_direction": "DOWN", "confidence": "high",
        }

    # ---- BUY / UP setup (Part 9, weak evidence — included per explicit request) ----
    two_bar_up_streak = _direction(last_completed) == "UP" and _direction(prior_bar) == "UP"
    middle_third_up = _close_position_tercile(last_completed) == "middle"

    up_score = sum([two_bar_up_streak, middle_third_up])
    if up_score == 2:
        reasons = [
            "Last 2 completed bars both UP",
            "Most recent bar closed in middle third of its own range",
            "UP SCORE = 2 — LOW CONFIDENCE: only 13 validation trades in original analysis, "
            "included for monitoring only, historical hit rate ranged 46-64% across splits",
        ]
        return {
            "symbol": "PCJEWELLER.NS", "signal": "BUY", "price": price,
            "reasons": reasons, "source": source, "exit_rule": "next_bar_close",
            "predicted_direction": "UP", "confidence": "low",
        }

    # ---- Everything else: AVOID ----
    return _avoid(price, source, "Neither the validated SELL nor BUY setup conditions were met")


def _avoid(price, source, reason):
    return {
        "symbol": "PCJEWELLER.NS", "signal": "AVOID", "price": price,
        "reasons": [reason], "source": source, "exit_rule": None,
    }
