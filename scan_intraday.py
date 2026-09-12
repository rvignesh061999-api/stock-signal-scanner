"""
scan_intraday.py
Live hourly scan of the FILTERED intraday watchlist (config.INTRADAY_WATCHLIST
— the 8 stocks that cleared 35%+ win rate on a prior backtest). Sends
Telegram alerts for new BUY/SHORT signals, same as the daily scanner,
but also appends every signal to a running log file
(intraday_signal_log.json) so we can check REAL forward performance
later against what the backtest predicted.

This is the forward-validation step: the backtest showed 37.3% win rate
on the SAME data used to pick these 8 stocks, which risks overfitting.
This script builds the evidence needed to check whether that edge holds
up on data the stocks weren't selected from — i.e. everything from now
onward.

Run by .github/workflows/scan_intraday.yml on an hourly schedule during
NSE market hours (9:15-15:30 IST). All 8 filtered stocks are Indian.
"""

import json
import os
import time
from datetime import datetime, timezone, timedelta

from config import INTRADAY_WATCHLIST, DEFAULT_CAPITAL
from data_fetch import fetch_intraday_candles
from signal_engine import compute_signal
from pcjeweller_strategy import compute_pcjeweller_signal
from rpower_strategy import compute_rpower_signal
from telegram_alert import send_telegram_message, format_signal_message

DATA_FILE = "docs/intraday_data.json"
ALERTED_FILE = "intraday_alerted_keys.json"
LOG_FILE = "intraday_signal_log.json"
PROFILES_FILE = "per_stock_profiles.json"
INTERVAL = "1h"
IST = timezone(timedelta(hours=5, minutes=30))


def load_per_stock_profiles():
    """
    Loads calibrated per-stock thresholds if calibrate_thresholds.py has
    been run. Returns {} if the file doesn't exist yet — in that case
    every stock just uses the flat interval default, same as before.
    """
    if os.path.exists(PROFILES_FILE):
        try:
            with open(PROFILES_FILE) as f:
                return json.load(f)
        except Exception:
            return {}
    return {}


PER_STOCK_PROFILES = load_per_stock_profiles()


def is_market_open_ist():
    """
    True if it's currently NSE market hours (9:15 AM - 3:30 PM IST,
    Mon-Fri). GitHub's cron scheduler can fire late or early — this is
    a real safety check so a delayed run doesn't scan/alert using
    stale after-hours data and call it a live intraday signal.
    """
    now = datetime.now(IST)
    if now.weekday() > 4:  # 5=Sat, 6=Sun
        return False
    minutes = now.hour * 60 + now.minute
    return 9 * 60 + 15 <= minutes <= 15 * 60 + 30


# Per-stock dedicated strategies — each replaces the generic candle+
# support/resistance+volume logic for its specific symbol, based on
# statistical analysis of that stock's own history. Any symbol not in
# this dict uses the generic strategy with its calibrated profile
# (see PER_STOCK_PROFILES) instead.
DEDICATED_STRATEGIES = {
    "PCJEWELLER.NS": compute_pcjeweller_signal,
    "RPOWER.NS": compute_rpower_signal,
}


def scan_symbol(symbol: str, capital: float = DEFAULT_CAPITAL):
    rows, source = fetch_intraday_candles(symbol, interval=INTERVAL)
    if not rows:
        return {"symbol": symbol, "signal": "ERROR", "error": "No data from any source"}

    if symbol in DEDICATED_STRATEGIES:
        result = DEDICATED_STRATEGIES[symbol](rows, source, capital)
        # Fields the rest of the pipeline (logging, dashboard, Telegram
        # formatting) expects but these simpler dedicated-strategy
        # results don't set — filled with sensible defaults so nothing
        # downstream breaks.
        result.setdefault("price_change_pct", 0)
        result.setdefault("candle", "-")
        result.setdefault("candle_strength", "-")
        result.setdefault("near_level", "-")
        result.setdefault("volume_confirmed", False)
        result.setdefault("vol_ratio", 0)
        result.setdefault("sl_price", None)
        result.setdefault("tgt_price", None)
    else:
        profile_override = PER_STOCK_PROFILES.get(symbol)
        result = compute_signal(symbol, rows, source, capital, interval=INTERVAL,
                                 profile_override=profile_override).to_dict()
        result["exit_rule"] = None  # standard price-target/SL resolution, see resolve_pending_signals

    result["bar_date"] = rows[0]["date"]  # exact candle this signal fired on, needed to resolve it later
    return result


def scan_watchlist():
    results = []
    for market, symbols in INTRADAY_WATCHLIST.items():
        for symbol in symbols:
            try:
                r = scan_symbol(symbol)
                r["market"] = market
                results.append(r)
            except Exception as e:
                results.append({"symbol": symbol, "market": market, "signal": "ERROR", "error": str(e)})
            time.sleep(0.3)
    return results


def _signal_key(sig):
    return f"{sig['symbol']}|{sig['signal']}|{sig.get('price')}"


def load_json_set(path):
    if os.path.exists(path):
        try:
            with open(path) as f:
                return set(json.load(f))
        except Exception:
            return set()
    return set()


def save_json_set(path, keys):
    with open(path, "w") as f:
        json.dump(list(keys), f)


HOLDING_BARS = 10  # matches the backtest holding period we validated with


def append_to_log(new_signals):
    """
    Appends every new actionable signal to a running log, timestamped,
    so we can look back later and check: did price actually move the
    way the signal predicted? This is what makes forward validation
    possible — the backtest can't tell us this, only real elapsed time can.
    """
    log = []
    if os.path.exists(LOG_FILE):
        try:
            with open(LOG_FILE) as f:
                log = json.load(f)
        except Exception:
            log = []

    for sig in new_signals:
        log.append({
            "logged_at": datetime.now().isoformat(),
            "signal_bar_date": sig.get("bar_date"),  # exact candle timestamp, used to locate it in future data
            "symbol": sig["symbol"],
            "signal": sig["signal"],
            "price": sig["price"],
            "sl_price": sig["sl_price"],
            "tgt_price": sig["tgt_price"],
            "candle": sig["candle"],
            "near_level": sig["near_level"],
            "volume_confirmed": sig["volume_confirmed"],
            "source": sig["source"],
            "exit_rule": sig.get("exit_rule"),  # None = standard price-target/SL resolution;
                                                  # "next_bar_close" = PCJEWELLER-style direction resolution
            "predicted_direction": sig.get("predicted_direction"),  # only set for next_bar_close signals
            # These stay null until resolve_pending_signals() determines
            # what actually happened after this signal fired.
            "outcome": None,
            "outcome_checked_at": None,
            "exit_price": None,
            "bars_to_exit": None,
        })

    with open(LOG_FILE, "w") as f:
        json.dump(log, f, indent=2)


def resolve_pending_signals():
    """
    For every log entry still marked outcome=None, fetches fresh
    intraday candles for that symbol and checks whether price has hit
    the target or stop-loss in the bars AFTER the signal fired — same
    win/loss logic as backtest.py, just applied to live data instead
    of history.

    A signal is only marked NO_HIT once HOLDING_BARS have genuinely
    elapsed since it fired without either level being touched — if not
    enough time has passed yet, it's left pending for the next run to
    check again.
    """
    if not os.path.exists(LOG_FILE):
        return
    with open(LOG_FILE) as f:
        log = json.load(f)

    pending = [e for e in log if e.get("outcome") is None]
    if not pending:
        print("[resolve] No pending signals to check.")
        return

    # Group by symbol so we only fetch each symbol's data once
    by_symbol = {}
    for entry in pending:
        by_symbol.setdefault(entry["symbol"], []).append(entry)

    resolved_count = 0
    for symbol, entries in by_symbol.items():
        rows, source = fetch_intraday_candles(symbol, interval=INTERVAL)
        if not rows:
            print(f"[resolve] {symbol}: could not fetch data to check pending signals, skipping.")
            continue
        chrono = list(reversed(rows))  # oldest first
        date_to_index = {r["date"]: i for i, r in enumerate(chrono)}

        for entry in entries:
            bar_date = entry.get("signal_bar_date")
            if bar_date not in date_to_index:
                # The signal's original bar has rolled out of the fetch
                # window (data source only keeps ~60 days for 15m, ~2yr
                # for 1h) — can't resolve it anymore either way.
                continue

            idx = date_to_index[bar_date]

            if entry.get("exit_rule") == "next_bar_close":
                # PCJEWELLER-style resolution: this predicts NEXT BAR
                # DIRECTION, not a price target. Resolves after exactly
                # 1 bar — WIN if the next bar's actual direction matched
                # the prediction, LOSS if not. Nothing to wait for beyond
                # that single bar, unlike the 10-bar price-target check below.
                if idx + 1 >= len(chrono):
                    continue  # next bar hasn't happened yet, still pending
                next_bar = chrono[idx + 1]
                if next_bar["close"] > next_bar["open"]:
                    actual_direction = "UP"
                elif next_bar["close"] < next_bar["open"]:
                    actual_direction = "DOWN"
                else:
                    actual_direction = "FLAT"

                predicted = entry.get("predicted_direction")
                outcome = "WIN" if actual_direction == predicted else "LOSS"
                entry["outcome"] = outcome
                entry["exit_price"] = next_bar["close"]
                entry["bars_to_exit"] = 1
                entry["outcome_checked_at"] = datetime.now().isoformat()
                resolved_count += 1
                continue

            # Standard price-target/stop-loss resolution (all other stocks)
            outcome = None
            exit_price = None
            bars_to_exit = None

            for d in range(1, HOLDING_BARS + 1):
                if idx + d >= len(chrono):
                    break
                future_high = chrono[idx + d]["high"]
                future_low = chrono[idx + d]["low"]

                if entry["signal"] == "BUY":
                    hit_target = future_high >= entry["tgt_price"]
                    hit_sl = future_low <= entry["sl_price"]
                else:  # SHORT
                    hit_target = future_low <= entry["tgt_price"]
                    hit_sl = future_high >= entry["sl_price"]

                if hit_sl:
                    outcome, exit_price, bars_to_exit = "LOSS", entry["sl_price"], d
                    break
                if hit_target:
                    outcome, exit_price, bars_to_exit = "WIN", entry["tgt_price"], d
                    break

            bars_available = len(chrono) - idx - 1
            if outcome is not None:
                entry["outcome"] = outcome
                entry["exit_price"] = exit_price
                entry["bars_to_exit"] = bars_to_exit
                entry["outcome_checked_at"] = datetime.now().isoformat()
                resolved_count += 1
            elif bars_available >= HOLDING_BARS:
                # Enough real time has passed with no hit either way
                entry["outcome"] = "NO_HIT"
                entry["outcome_checked_at"] = datetime.now().isoformat()
                resolved_count += 1
            # else: not enough time has elapsed yet, leave pending

    with open(LOG_FILE, "w") as f:
        json.dump(log, f, indent=2)
    print(f"[resolve] Resolved {resolved_count} of {len(pending)} pending signals this run.")


def main():
    print(f"[intraday-scan] Starting at {datetime.now().isoformat()}")

    # Resolving pending signals is safe to do anytime (it's just checking
    # what already happened), so this runs regardless of market hours.
    resolve_pending_signals()

    if not is_market_open_ist():
        now_ist = datetime.now(IST).strftime("%Y-%m-%d %H:%M:%S IST")
        print(f"[intraday-scan] {now_ist} is outside NSE market hours (9:15 AM-3:30 PM IST, Mon-Fri). "
              f"Skipping new scan — this run only resolved pending signals, no new data was scanned.")
        return

    results = scan_watchlist()

    os.makedirs("docs", exist_ok=True)
    with open(DATA_FILE, "w") as f:
        json.dump({
            "updated_at": datetime.now().isoformat(),
            "interval": INTERVAL,
            "results": results,
        }, f, indent=2)
    print(f"[intraday-scan] Saved {len(results)} results to {DATA_FILE}")

    alerted = load_json_set(ALERTED_FILE)
    new_signals = []
    for r in results:
        if r.get("signal") in ("BUY", "SHORT"):
            key = _signal_key(r)
            if key not in alerted:
                alerted.add(key)
                new_signals.append(r)

    if new_signals:
        buys = [r for r in new_signals if r["signal"] == "BUY"]
        shorts = [r for r in new_signals if r["signal"] == "SHORT"]
        header = "⏱️⏱️⏱️ INTRADAY SIGNAL (1h candles — filtered 8-stock list) ⏱️⏱️⏱️"
        parts = [header]
        if buys:
            parts.append("🟢 BUY")
            parts.extend(format_signal_message(r) for r in buys)
        if shorts:
            parts.append("🔴 SHORT")
            parts.extend(format_signal_message(r) for r in shorts)
        message = "\n\n".join(parts)
        sent = send_telegram_message(message)
        print(f"[intraday-scan] Sent {len(new_signals)} new signal(s) to Telegram: {sent}")

        append_to_log(new_signals)
        print(f"[intraday-scan] Logged {len(new_signals)} signal(s) to {LOG_FILE} for forward validation")
    else:
        print("[intraday-scan] No new actionable signals this run.")

    save_json_set(ALERTED_FILE, alerted)


if __name__ == "__main__":
    main()
