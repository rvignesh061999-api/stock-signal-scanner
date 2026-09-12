"""
forward_accuracy_report.py
Reads intraday_signal_log.json and reports REAL forward performance —
how signals actually played out after they fired, as opposed to
backtest.py which only measures historical replay.

Reports TWO separate sections, since they measure fundamentally
different things and shouldn't be averaged together:
1. General section (price-target/stop-loss resolution) — stocks using
   the generic candle+support/resistance+volume logic. The real answer
   to "does the filtered watchlist have genuine edge, or was it overfit
   to the backtest window it was picked from?"
2. Direction-prediction section — any stock with a dedicated,
   statistically-derived strategy (PCJEWELLER, RPOWER, and any added
   later — see DEDICATED_STRATEGIES in scan_intraday.py). Each symbol's
   SELL and BUY setups are reported separately since they typically
   have very different evidence strength behind them, and compared
   against that stock's own documented baseline where known.

Sends a summary to Telegram. Safe to run anytime — if few or no
signals have resolved yet, it says so honestly rather than presenting
a misleadingly small sample as conclusive.

Triggered manually via .github/workflows/forward_accuracy.yml, or run locally.
"""

import json
import os

from telegram_alert import send_telegram_message

LOG_FILE = "intraday_signal_log.json"
MIN_SAMPLE_FOR_CONFIDENCE = 100  # general section: below this, flag as too small to trust
DIRECTION_MIN_SAMPLE = 20         # direction-prediction section: smaller threshold, matching the
                                    # scale the source analyses themselves were validated on

# Known documented baselines, so the report can say something concrete
# instead of just "no baseline available." Update this if a symbol's
# source analysis is revised, or add entries for newly added stocks.
BASELINES = {
    ("PCJEWELLER.NS", "DOWN"): {"test_pct": 64.0, "baseline_pct": 49.0,
                                  "label": "SELL (DOWN) setup — validated"},
    ("PCJEWELLER.NS", "UP"): {"test_pct": None, "baseline_pct": None,
                                "label": "BUY (UP) setup — weak evidence, only 13 validation trades originally"},
    ("RPOWER.NS", "DOWN"): {"test_pct": 59.3, "baseline_pct": 51.0,
                              "label": "SELL (DOWN) setup — validated, most stable finding across stocks analyzed"},
    ("RPOWER.NS", "UP"): {"test_pct": 64.3, "baseline_pct": 40.0,
                            "label": "BUY (UP) setup — validated, strengthened out-of-sample"},
}


def load_log():
    if not os.path.exists(LOG_FILE):
        return []
    with open(LOG_FILE) as f:
        return json.load(f)


def _split_log(log):
    """Separates direction-prediction entries (exit_rule=next_bar_close) from general price-target ones."""
    direction = [e for e in log if e.get("exit_rule") == "next_bar_close"]
    general = [e for e in log if e.get("exit_rule") != "next_bar_close"]
    return general, direction


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


def summarize_direction_strategies(log):
    """
    Groups direction-prediction entries by symbol, then by predicted
    direction (SELL/DOWN vs BUY/UP) within each symbol — since each
    setup typically has different evidence strength and should be
    judged independently, not blended together.
    """
    symbols = sorted(set(e["symbol"] for e in log))
    result = {}
    for symbol in symbols:
        symbol_log = [e for e in log if e["symbol"] == symbol]
        resolved = [e for e in symbol_log if e.get("outcome") in ("WIN", "LOSS")]
        pending = [e for e in symbol_log if e.get("outcome") is None]

        def _stats_for(direction):
            subset = [e for e in resolved if e.get("predicted_direction") == direction]
            wins = sum(1 for e in subset if e["outcome"] == "WIN")
            losses = sum(1 for e in subset if e["outcome"] == "LOSS")
            decided = wins + losses
            win_rate = round(wins / decided * 100, 1) if decided else None
            return {"wins": wins, "losses": losses, "decided": decided, "win_rate_pct": win_rate}

        result[symbol] = {
            "total_logged": len(symbol_log),
            "resolved": len(resolved),
            "pending": len(pending),
            "down": _stats_for("DOWN"),
            "up": _stats_for("UP"),
        }
    return result


def format_general_section(summary):
    lines = ["📊 General Forward Accuracy (generic strategy stocks, price-target resolution)"]
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
            lines.append(f"This is {comparison} the ~33.3% breakeven line for the calibrated backtest.")
    else:
        lines.append("No decided (win/loss) trades yet — all resolved signals were no-hit.")

    if summary["by_symbol"]:
        lines.append("\nPer-symbol (resolved only):")
        for sym, stats in sorted(summary["by_symbol"].items()):
            decided = stats["wins"] + stats["losses"]
            wr = f"{round(stats['wins']/decided*100, 1)}%" if decided else "N/A"
            lines.append(f"{sym}: {stats['wins']}W / {stats['losses']}L / {stats['no_hit']} no-hit ({wr})")

    return "\n".join(lines)


def _format_one_direction(symbol, direction, stats):
    baseline = BASELINES.get((symbol, direction))
    label = baseline["label"] if baseline else f"{direction} setup"
    lines = [f"\n{label}:"]
    if stats["decided"] == 0:
        lines.append("  No signals resolved yet.")
        return lines

    lines.append(f"  {stats['wins']}W / {stats['losses']}L ({stats['decided']} decided) → {stats['win_rate_pct']}% real win rate")
    if stats["decided"] < DIRECTION_MIN_SAMPLE:
        lines.append(f"  ⚠️ Only {stats['decided']} trades — too few to judge yet (aim for {DIRECTION_MIN_SAMPLE}+)")
    elif baseline and baseline["test_pct"] is not None:
        gap = stats["win_rate_pct"] - baseline["test_pct"]
        verdict = "holding up" if gap > -10 else "underperforming the original analysis — worth reviewing"
        lines.append(f"  vs. {baseline['test_pct']}% test result: {gap:+.1f} points — {verdict}")
    else:
        lines.append("  (No firm baseline to compare against — monitoring only)")
    return lines


def format_direction_section(summary_by_symbol):
    if not summary_by_symbol:
        return "\n📐 No direction-prediction strategy signals logged yet."

    lines = []
    for symbol, summary in summary_by_symbol.items():
        lines.append(f"\n📐 {symbol} — Direction-Prediction Strategy")
        lines.append(f"Total signals logged: {summary['total_logged']}")
        lines.append(f"Resolved: {summary['resolved']} | Still pending: {summary['pending']}")
        if summary["resolved"] == 0:
            lines.append(f"No {symbol} signals have resolved yet.")
            continue
        lines.extend(_format_one_direction(symbol, "DOWN", summary["down"]))
        lines.extend(_format_one_direction(symbol, "UP", summary["up"]))

    return "\n".join(lines)


def main():
    log = load_log()
    general_log, direction_log = _split_log(log)

    general_summary = summarize_general(general_log)
    direction_summary = summarize_direction_strategies(direction_log)

    message = format_general_section(general_summary) + "\n" + format_direction_section(direction_summary)
    print(message)
    sent = send_telegram_message(message)
    print(f"\n[forward-accuracy] Sent to Telegram: {sent}")


if __name__ == "__main__":
    main()
