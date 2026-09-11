"""
forward_accuracy_report.py
Reads intraday_signal_log.json and reports REAL forward performance —
how signals actually played out after they fired, as opposed to
backtest.py which only measures historical replay.

Reports TWO separate sections, since they measure fundamentally
different things and shouldn't be averaged together:
1. General 7-stock section (price-target/stop-loss resolution) — the
   real answer to "does the filtered watchlist have genuine edge, or
   was it overfit to the backtest window it was picked from?"
2. PCJEWELLER.NS section (next-bar-direction resolution) — checks the
   validated SELL setup's real win rate against its 64% test / ~49%
   baseline from the source analysis, and the weak BUY setup separately
   since it has much thinner evidence behind it.

Sends a summary to Telegram. Safe to run anytime — if few or no
signals have resolved yet, it says so honestly rather than presenting
a misleadingly small sample as conclusive.

Triggered manually via .github/workflows/forward_accuracy.yml, or run locally.
"""

import json
import os

from telegram_alert import send_telegram_message

LOG_FILE = "intraday_signal_log.json"
MIN_SAMPLE_FOR_CONFIDENCE = 100  # general 7-stock section: below this, flag as too small to trust
PCJEWELLER_MIN_SAMPLE = 20        # PCJEWELLER section: smaller threshold, matching the scale the
                                   # source analysis itself was validated on (13-96 trades per split)


def load_log():
    if not os.path.exists(LOG_FILE):
        return []
    with open(LOG_FILE) as f:
        return json.load(f)


def _split_log(log):
    """Separates PCJEWELLER (direction-prediction) entries from the general (price-target) ones."""
    pcj = [e for e in log if e.get("symbol") == "PCJEWELLER.NS"]
    general = [e for e in log if e.get("symbol") != "PCJEWELLER.NS"]
    return general, pcj


def summarize_general(log):
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


def summarize_pcjeweller(log):
    """
    Splits PCJEWELLER entries by predicted direction (SELL/DOWN vs
    BUY/UP), since they have very different evidence strength behind
    them and should be judged separately, not blended into one number.
    """
    resolved = [e for e in log if e.get("outcome") in ("WIN", "LOSS")]
    pending = [e for e in log if e.get("outcome") is None]

    def _stats_for(direction):
        subset = [e for e in resolved if e.get("predicted_direction") == direction]
        wins = sum(1 for e in subset if e["outcome"] == "WIN")
        losses = sum(1 for e in subset if e["outcome"] == "LOSS")
        decided = wins + losses
        win_rate = round(wins / decided * 100, 1) if decided else None
        return {"wins": wins, "losses": losses, "decided": decided, "win_rate_pct": win_rate}

    return {
        "total_logged": len(log),
        "resolved": len(resolved),
        "pending": len(pending),
        "sell_down": _stats_for("DOWN"),
        "buy_up": _stats_for("UP"),
    }


def format_general_section(summary):
    lines = ["📊 General Forward Accuracy (7 stocks, price-target resolution)"]
    lines.append(f"Total signals logged: {summary['total_logged']}")
    lines.append(f"Resolved: {summary['resolved']} | Still pending: {summary['pending']}")

    if summary["resolved"] == 0:
        lines.append("No signals have resolved yet — check back after more market hours have passed.")
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
                f"(vs. the 37.3% the backtest predicted for these 7 stocks + PCJEWELLER combined)."
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


def format_pcjeweller_section(summary):
    lines = ["\n📐 PCJEWELLER.NS — Direction-Prediction Strategy"]
    lines.append(f"Total signals logged: {summary['total_logged']}")
    lines.append(f"Resolved: {summary['resolved']} | Still pending: {summary['pending']}")

    if summary["resolved"] == 0:
        lines.append("No PCJEWELLER signals have resolved yet.")
        return "\n".join(lines)

    sell = summary["sell_down"]
    lines.append(f"\nSELL (DOWN) setup — validated, 64% in original test / ~49% baseline:")
    if sell["decided"] == 0:
        lines.append("  No SELL signals resolved yet.")
    else:
        lines.append(f"  {sell['wins']}W / {sell['losses']}L ({sell['decided']} decided) → {sell['win_rate_pct']}% real win rate")
        if sell["decided"] < PCJEWELLER_MIN_SAMPLE:
            lines.append(f"  ⚠️ Only {sell['decided']} trades — too few to judge yet (aim for {PCJEWELLER_MIN_SAMPLE}+)")
        else:
            gap = sell["win_rate_pct"] - 64.0
            verdict = "holding up" if gap > -10 else "underperforming the original analysis — worth reviewing"
            lines.append(f"  vs. 64% test result: {gap:+.1f} points — {verdict}")

    buy = summary["buy_up"]
    lines.append(f"\nBUY (UP) setup — weak evidence, 13 validation trades originally:")
    if buy["decided"] == 0:
        lines.append("  No BUY signals resolved yet.")
    else:
        lines.append(f"  {buy['wins']}W / {buy['losses']}L ({buy['decided']} decided) → {buy['win_rate_pct']}% real win rate")
        lines.append(f"  (Still being monitored — original evidence was too thin to set a firm expectation)")

    return "\n".join(lines)


def main():
    log = load_log()
    general_log, pcj_log = _split_log(log)

    general_summary = summarize_general(general_log)
    pcj_summary = summarize_pcjeweller(pcj_log)

    message = format_general_section(general_summary) + "\n" + format_pcjeweller_section(pcj_summary)
    print(message)
    sent = send_telegram_message(message)
    print(f"\n[forward-accuracy] Sent to Telegram: {sent}")


if __name__ == "__main__":
    main()
