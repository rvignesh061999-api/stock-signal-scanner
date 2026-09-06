"""
signal_engine.py
Computes a signal from daily OHLCV candle data using ONLY candle patterns,
support/resistance proximity, and volume confirmation — no RSI/EMA/MACD.

This is intentional: multi-indicator scoring (RSI+EMA+MACD+volume+candle)
was tried and found to produce noisy, conflicting signals in practice.
Pure candle + level + volume is simpler and easier to trust/verify by eye.

This is decision-support only — not a guarantee of profitable trades.
"""

from dataclasses import dataclass, field, asdict


def detect_candle_pattern(rows):
    """
    rows: newest-first list of OHLCV dicts, needs at least 3.
    Returns (name, signal, strength).
    """
    if len(rows) < 3:
        return "No Pattern", "NEUTRAL", "Weak"

    c0, c1, c2 = rows[0], rows[1], rows[2]
    o, h, l, c = c0["open"], c0["high"], c0["low"], c0["close"]
    po, pc = c1["open"], c1["close"]
    ppo, ppc = c2["open"], c2["close"]

    body = abs(c - o)
    rng = (h - l) or 0.001
    upper_shadow = h - max(o, c)
    lower_shadow = min(o, c) - l
    bull_candle = c > o
    prev_bull = pc > po
    pp_bull = ppc > ppo

    # Morning Star
    if not pp_bull and abs(pc - po) < (c1["high"] - c1["low"]) * 0.3 and bull_candle and c > (ppo + ppc) / 2:
        return "Morning Star", "BUY", "Strong"
    # Evening Star
    if pp_bull and abs(pc - po) < (c1["high"] - c1["low"]) * 0.3 and not bull_candle and c < (ppo + ppc) / 2:
        return "Evening Star", "SELL", "Strong"
    # Bullish Engulfing
    if not prev_bull and bull_candle and o <= pc and c >= po and body > abs(pc - po):
        return "Bullish Engulfing", "BUY", "Strong"
    # Bearish Engulfing
    if prev_bull and not bull_candle and o >= pc and c <= po and body > abs(pc - po):
        return "Bearish Engulfing", "SELL", "Strong"
    # Hammer
    if not prev_bull and bull_candle and lower_shadow > body * 2 and upper_shadow < body * 0.5:
        return "Hammer", "BUY", "Moderate"
    # Shooting Star
    if prev_bull and upper_shadow > body * 2 and lower_shadow < body * 0.5:
        return "Shooting Star", "SELL", "Moderate"
    # Strong Bullish / Bearish
    if bull_candle and body > rng * 0.7:
        return "Strong Bullish Candle", "BUY", "Moderate"
    if not bull_candle and body > rng * 0.7:
        return "Strong Bearish Candle", "SELL", "Moderate"
    # Doji
    if body < rng * 0.1:
        return "Doji", "NEUTRAL", "Weak"

    return ("Bullish Candle" if bull_candle else "Bearish Candle",
            "BUY" if bull_candle else "SELL", "Weak")


# ---- Support / Resistance & volume helpers ---------------------------

def find_support_resistance(rows, window: int = 20):
    """rows: newest-first. Uses the most recent `window` days' low/high."""
    recent = rows[:window]
    support = min(r["low"] for r in recent)
    resistance = max(r["high"] for r in recent)
    return support, resistance


def is_near_level(price: float, level: float, tolerance: float = 0.015) -> bool:
    if not level:
        return False
    return abs(price - level) / level <= tolerance


def volume_confirms(rows, lookback: int = 20, factor: float = 1.3) -> bool:
    """rows: newest-first. True if latest volume is well above its recent average."""
    if len(rows) < lookback + 1:
        return False
    avg_vol = sum(r["volume"] for r in rows[1:lookback + 1]) / lookback
    return rows[0]["volume"] >= avg_vol * factor if avg_vol else False


# ---- Result -----------------------------------------------------------

@dataclass
class SignalResult:
    symbol: str
    signal: str            # BUY / SHORT / AVOID (based on candle direction + confirmation)
    price: float
    price_change_pct: float
    candle: str
    candle_signal: str      # BUY / SELL / NEUTRAL (raw candle reading)
    candle_strength: str
    near_level: str          # "support" / "resistance" / "none"
    support: float
    resistance: float
    volume_confirmed: bool
    vol_ratio: float
    sl_price: float
    tgt_price: float
    reasons: list = field(default_factory=list)
    source: str = ""

    def to_dict(self):
        return asdict(self)


def compute_signal(symbol: str, rows: list, source: str, capital: float = 10000,
                    sl_pct: float = 1.5, tgt_pct: float = 3.0) -> SignalResult:
    """
    rows: newest-first OHLCV list, at least 25 rows recommended.
    Pure candle-pattern approach: a candle only becomes an actionable
    BUY/SELL signal if it's also near a support/resistance level OR
    backed by above-average volume. Otherwise it's AVOID (noise).
    """
    reasons = []
    closes = [r["close"] for r in rows]
    current_price = closes[0]
    prev_close = closes[1] if len(closes) > 1 else current_price
    price_change_pct = (current_price - prev_close) / prev_close * 100 if prev_close else 0

    avg_vol = sum(r["volume"] for r in rows[1:21]) / max(1, len(rows[1:21])) if len(rows) > 1 else 0
    vol_ratio = rows[0]["volume"] / avg_vol if avg_vol else 0

    candle_name, candle_signal, candle_strength = detect_candle_pattern(rows)

    support, resistance = find_support_resistance(rows)
    near_level = "none"
    if is_near_level(current_price, support):
        near_level = "support"
    elif is_near_level(current_price, resistance):
        near_level = "resistance"

    vol_ok = volume_confirms(rows)

    # Only turn a raw candle reading into an actionable signal if it's
    # confirmed by a level or volume — otherwise it's just noise.
    confirmed = near_level != "none" or vol_ok
    if candle_signal == "BUY" and confirmed:
        signal = "BUY"
    elif candle_signal == "SELL" and confirmed:
        signal = "SHORT"
    else:
        signal = "AVOID"

    reasons.append(f"Candle: {candle_name} ({candle_strength})")
    if near_level != "none":
        reasons.append(f"Price near {near_level} (support {support}, resistance {resistance})")
    else:
        reasons.append(f"Not near a key level (support {support}, resistance {resistance})")
    if vol_ok:
        reasons.append(f"Volume confirmed: {vol_ratio:.2f}x average")
    else:
        reasons.append(f"Volume not confirmed: {vol_ratio:.2f}x average — lower conviction")
    if signal == "AVOID" and candle_signal in ("BUY", "SELL"):
        reasons.insert(0, f"Candle reading ({candle_signal}) not confirmed by level or volume — treated as noise")

    # SL / Target
    if signal == "SHORT":
        sl_price = current_price * (1 + sl_pct / 100)
        tgt_price = current_price * (1 - tgt_pct / 100)
    else:
        sl_price = current_price * (1 - sl_pct / 100)
        tgt_price = current_price * (1 + tgt_pct / 100)

    return SignalResult(
        symbol=symbol,
        signal=signal,
        price=round(current_price, 2),
        price_change_pct=round(price_change_pct, 2),
        candle=candle_name,
        candle_signal=candle_signal,
        candle_strength=candle_strength,
        near_level=near_level,
        support=round(support, 2),
        resistance=round(resistance, 2),
        volume_confirmed=vol_ok,
        vol_ratio=round(vol_ratio, 2),
        sl_price=round(sl_price, 2),
        tgt_price=round(tgt_price, 2),
        reasons=reasons,
        source=source,
    )
