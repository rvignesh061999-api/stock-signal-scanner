"""
forward_accuracy_report.py
Reads intraday_signal_log.json and reports REAL forward performance —
how signals actually played out after they fired, as opposed to
backtest.py which only measures historical replay.

This is the actual answer to "does the filtered 8-stock intraday
watchlist have a genuine edge, or was it overfit to the backtest
window it was picked from?" Only real elapsed time can answer that,
and this script summarizes what's accumulated so far.

Sends a summary to Telegram. Safe to run anytime — if few or no
signals have resolved yet, it says so honestly rather than presenting
a misleadingly small sample as conclusive.

Triggered manually via .github/workflows/forward_accuracy.yml, or run locally.
"""

import json
import os

from telegram_alert import send_telegram_message

LOG_FILE = "intraday_signal_log.json"
MIN_SAMPLE_FOR_CONFIDENCE = 100  # below this, explicitly flag the result as too small to trust


def load_log():
    if not os.path.exists(LOG_FILE):
        return []
    with open(LOG_FILE) as f:
        return json.load(f)


def summarize(log):
    resolved = [e for e in log if e.get("outcome") in ("WIN", "LOSS", "NO_HIT")]
    pending = [e for e in log if e.get("outcome") is None]
    wins = [e for e in resolved if e["outcome"] == "WIN"]
    losses = [e for e in resolved if e["outcome"] == "LOSS"]
    no_hits = [e for e in resolved if e["outcome"] == "NO_HIT"]

    decided = len(wins) + len(losses)
    win_rate = round(len(wins) / decided * 100, 1) if decided else None

    by_symbol = {}
    for e in resolved:
        by_symbol.setdefault(e["symbol"], {"wins": 0, "losses": 0, "no_hit": 0})
        if e["outcome"] == "WIN":
            by_symbol[e["symbol"]]["wins"] += 1
        elif e["outcome"] == "LOSS":
            by_symbol[e["symbol"]]["losses"] += 1
        else:
            by_symbol[e["symbol"]]["no_hit"] += 1

    return {
        "total_logged": len(log),
        "resolved": len(resolved),
        "pending": len(pending),
        "wins": len(wins),
        "losses": len(losses),
        "no_hits": len(no_hits),
        "win_rate_pct": win_rate,
        "by_symbol": by_symbol,
    }


def format_message(summary):
    lines = ["📊 Forward Accuracy Report (live intraday signals)"]
    lines.append(f"Total signals logged: {summary['total_logged']}")
    lines.append(f"Resolved: {summary['resolved']} | Still pending: {summary['pending']}")

    if summary["resolved"] == 0:
        lines.append("\nNo signals have resolved yet — check back after more market hours have passed.")
        return "\n".join(lines)

    lines.append(f"Wins: {summary['wins']} | Losses: {summary['losses']} | No-hit: {summary['no_hits']}")

    if summary["win_rate_pct"] is not None:
        lines.append(f"Real forward win rate: {summary['win_rate_pct']}%")
        decided = summary["wins"] + summary["losses"]
        if decided < MIN_SAMPLE_FOR_CONFIDENCE:
            lines.append(
                f"⚠️ Sample size is only {decided} decided trades — too small to draw real "
                f"conclusions yet (aim for {MIN_SAMPLE_FOR_CONFIDENCE}+ before trusting this number)."
            )
        else:
            comparison = "ABOVE" if summary["win_rate_pct"] > 33.3 else "AT OR BELOW"
            lines.append(
                f"This is {comparison} the ~33.3% breakeven line "
                f"(vs. the 37.3% the backtest predicted for these same 8 stocks)."
            )
    else:
        lines.append("No decided (win/loss) trades yet — all resolved signals were no-hit.")

    if summary["by_symbol"]:
        lines.append("\nPer-symbol (resolved only):")
        for sym, stats in sorted(summary["by_symbol"].items()):
            decided = stats["wins"] + stats["losses"]
            wr = f"{round(stats['wins']/decided*100, 1)}%" if decided else "N/A"
            lines.append(f"{sym}: {stats['wins']}W / {stats['losses']}L / {stats['no_hit']} no-hit ({wr})")

    return "\n".join(lines)


def main():
    log = load_log()
    summary = summarize(log)
    message = format_message(summary)
    print(message)
    sent = send_telegram_message(message)
    print(f"\n[forward-accuracy] Sent to Telegram: {sent}")


if __name__ == "__main__":
    main()
