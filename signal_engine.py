"""
signal_engine.py
Computes a signal from OHLCV candle data using ONLY candle patterns,
support/resistance proximity, and volume confirmation — no RSI/EMA/MACD.

This is intentional: multi-indicator scoring (RSI+EMA+MACD+volume+candle)
was tried and found to produce noisy, conflicting signals in practice.
Pure candle + level + volume is simpler and easier to trust/verify by eye.

Thresholds are INTERVAL-AWARE. A 1-hour candle and a 1-day candle don't
move the same amount in the same timeframe, so using one flat set of
numbers for both was found (via backtest) to over-fire on hourly data —
nearly every bar was "confirmed" — while the 3%/1.5% target/stop-loss
(sized for a multi-day swing) rarely resolved within a 10-hour window.
Each interval gets its own profile, scaled to that timeframe's typical
volatility. These are a first calibration, not a final answer — re-run
the backtest after any change here to confirm it actually helped.

This is decision-support only — not a guarantee of profitable trades.
"""

from dataclasses import dataclass, field, asdict


# ---- Interval-aware profiles -------------------------------------------
# sl_pct / tgt_pct: stop-loss / target as % of entry price, scaled down
#   for faster intervals since a "3% swing" that's reasonable over days
#   is a much bigger ask within a handful of hours or 15-min bars.
# sr_window: how many bars back to look for support/resistance. Kept
#   proportionally longer in bar-count for faster intervals so the
#   *time* window it covers is still meaningful (e.g. 40 hourly bars
#   ≈ 1 trading week, not 40 days).
# vol_lookback / vol_factor: volume confirmation lookback and required
#   multiple of the average. Tightened for intraday since single-bar
#   volume is noisier and a loose factor confirmed almost everything.
# level_tolerance: how close price must be to support/resistance to
#   count as "near" it. Tightened for intraday for the same reason.
INTERVAL_PROFILES = {
    "1d": {
        "sl_pct": 1.5, "tgt_pct": 3.0,
        "sr_window": 20, "vol_lookback": 20, "vol_factor": 1.3,
        "level_tolerance": 0.015,
    },
    "1h": {
        "sl_pct": 0.6, "tgt_pct": 1.2,
        "sr_window": 40, "vol_lookback": 40, "vol_factor": 1.6,
        "level_tolerance": 0.008,
    },
    "15m": {
        "sl_pct": 0.3, "tgt_pct": 0.6,
        "sr_window": 60, "vol_lookback": 60, "vol_factor": 1.8,
        "level_tolerance": 0.005,
    },
}
DEFAULT_INTERVAL = "1d"


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
                    interval: str = DEFAULT_INTERVAL) -> SignalResult:
    """
    rows: newest-first OHLCV list. At least `sr_window` rows recommended
    for that interval's profile (see INTERVAL_PROFILES).
    interval: "1d", "1h", or "15m" — selects the volatility-appropriate
    thresholds for stop-loss/target, support/resistance window, and
    volume/level confirmation. Falls back to "1d" profile if unknown.

    Pure candle-pattern approach: a candle only becomes an actionable
    BUY/SELL signal if it's also near a support/resistance level OR
    backed by above-average volume. Otherwise it's AVOID (noise).
    """
    P = INTERVAL_PROFILES.get(interval, INTERVAL_PROFILES[DEFAULT_INTERVAL])

    reasons = []
    closes = [r["close"] for r in rows]
    current_price = closes[0]
    prev_close = closes[1] if len(closes) > 1 else current_price
    price_change_pct = (current_price - prev_close) / prev_close * 100 if prev_close else 0

    vol_lookback = P["vol_lookback"]
    avg_vol = sum(r["volume"] for r in rows[1:vol_lookback + 1]) / max(1, len(rows[1:vol_lookback + 1])) if len(rows) > 1 else 0
    vol_ratio = rows[0]["volume"] / avg_vol if avg_vol else 0

    candle_name, candle_signal, candle_strength = detect_candle_pattern(rows)

    support, resistance = find_support_resistance(rows, window=P["sr_window"])
    near_level = "none"
    if is_near_level(current_price, support, tolerance=P["level_tolerance"]):
        near_level = "support"
    elif is_near_level(current_price, resistance, tolerance=P["level_tolerance"]):
        near_level = "resistance"

    vol_ok = volume_confirms(rows, lookback=vol_lookback, factor=P["vol_factor"])

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
        reasons.append(f"Volume confirmed: {vol_ratio:.2f}x average (needs {P['vol_factor']}x for {interval})")
    else:
        reasons.append(f"Volume not confirmed: {vol_ratio:.2f}x average — lower conviction")
    if signal == "AVOID" and candle_signal in ("BUY", "SELL"):
        reasons.insert(0, f"Candle reading ({candle_signal}) not confirmed by level or volume — treated as noise")

    # SL / Target, scaled to this interval's typical volatility
    sl_pct, tgt_pct = P["sl_pct"], P["tgt_pct"]
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
