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
from datetime import datetime

from config import INTRADAY_WATCHLIST, DEFAULT_CAPITAL
from data_fetch import fetch_intraday_candles
from signal_engine import compute_signal
from telegram_alert import send_telegram_message, format_signal_message

DATA_FILE = "docs/intraday_data.json"
ALERTED_FILE = "intraday_alerted_keys.json"
LOG_FILE = "intraday_signal_log.json"
INTERVAL = "1h"


def scan_symbol(symbol: str, capital: float = DEFAULT_CAPITAL):
    rows, source = fetch_intraday_candles(symbol, interval=INTERVAL)
    if not rows:
        return {"symbol": symbol, "signal": "ERROR", "error": "No data from any source"}
    return compute_signal(symbol, rows, source, capital, interval=INTERVAL).to_dict()


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
            "symbol": sig["symbol"],
            "signal": sig["signal"],
            "price": sig["price"],
            "sl_price": sig["sl_price"],
            "tgt_price": sig["tgt_price"],
            "candle": sig["candle"],
            "near_level": sig["near_level"],
            "volume_confirmed": sig["volume_confirmed"],
            "source": sig["source"],
            # These stay null until a future check-in script evaluates
            # what actually happened after this signal fired.
            "outcome": None,
            "outcome_checked_at": None,
        })

    with open(LOG_FILE, "w") as f:
        json.dump(log, f, indent=2)


def main():
    print(f"[intraday-scan] Starting at {datetime.now().isoformat()}")
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
        parts = []
        if buys:
            parts.append("🟢 BUY (intraday, 1h)")
            parts.extend(format_signal_message(r) for r in buys)
        if shorts:
            parts.append("🔴 SHORT (intraday, 1h)")
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
