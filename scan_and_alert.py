"""
scan_and_alert.py
Runs a full watchlist scan, saves results to docs/data.json (for the
GitHub Pages dashboard to read), and sends Telegram alerts for any
new BUY/SHORT signal not already alerted.

Run by .github/workflows/scan.yml on a schedule. The workflow commits
docs/data.json back to the repo after each run, and also persists
alerted_keys.json so we don't re-alert the same signal every run.
"""

import json
import os
import time
from datetime import datetime

from config import WATCHLIST, DEFAULT_CAPITAL
from data_fetch import fetch_daily_candles
from signal_engine import compute_signal
from telegram_alert import send_telegram_message, format_signal_message

DATA_FILE = "docs/data.json"
ALERTED_FILE = "alerted_keys.json"


def scan_symbol(symbol: str, capital: float = DEFAULT_CAPITAL, duration_months: int = 6):
    rows, source = fetch_daily_candles(symbol, duration_months=duration_months)
    if not rows:
        return {"symbol": symbol, "signal": "ERROR", "error": "No data from any source"}
    return compute_signal(symbol, rows, source, capital).to_dict()


def scan_watchlist():
    results = []
    for market, symbols in WATCHLIST.items():
        for symbol in symbols:
            try:
                r = scan_symbol(symbol)
                r["market"] = market
                results.append(r)
            except Exception as e:
                results.append({"symbol": symbol, "market": market, "signal": "ERROR", "error": str(e)})
            time.sleep(0.3)  # be gentle on rate limits
    return results


def _signal_key(sig):
    return f"{sig['symbol']}|{sig['signal']}|{sig.get('price')}"


def load_alerted_keys():
    if os.path.exists(ALERTED_FILE):
        try:
            with open(ALERTED_FILE) as f:
                return set(json.load(f))
        except Exception:
            return set()
    return set()


def save_alerted_keys(keys):
    with open(ALERTED_FILE, "w") as f:
        json.dump(list(keys), f)


def main():
    print(f"[scan] Starting at {datetime.now().isoformat()}")
    results = scan_watchlist()

    os.makedirs("docs", exist_ok=True)
    with open(DATA_FILE, "w") as f:
        json.dump({
            "updated_at": datetime.now().isoformat(),
            "results": results,
        }, f, indent=2)
    print(f"[scan] Saved {len(results)} results to {DATA_FILE}")

    alerted = load_alerted_keys()
    new_signals = []
    for r in results:
        if r.get("signal") in ("BUY", "SHORT"):
            key = _signal_key(r)
            if key not in alerted:
                alerted.add(key)
                new_signals.append(r)

    if new_signals:
        # One consolidated message: BUY first, then SHORT
        buys = [r for r in new_signals if r["signal"] == "BUY"]
        shorts = [r for r in new_signals if r["signal"] == "SHORT"]
        parts = []
        if buys:
            parts.append("🟢 BUY")
            parts.extend(format_signal_message(r) for r in buys)
        if shorts:
            parts.append("🔴 SHORT")
            parts.extend(format_signal_message(r) for r in shorts)
        message = "\n\n".join(parts)
        sent = send_telegram_message(message)
        print(f"[scan] Sent {len(new_signals)} new signal(s) to Telegram: {sent}")
    else:
        print("[scan] No new actionable signals this run.")

    save_alerted_keys(alerted)


if __name__ == "__main__":
    main()
