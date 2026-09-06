"""
backtest.py
Runs the current signal engine (candle + support/resistance + volume)
against historical daily data for every symbol in the watchlist, and
reports how often BUY/SHORT signals actually hit their target before
their stop-loss.

This does NOT change any logic — it only measures how the CURRENT
rules perform, so we know whether they're worth trusting or need
tuning before relying on them for real decisions.

Usage:
  python3 backtest.py                        # backtest full watchlist, 12mo history
  python3 backtest.py --symbol AAPL          # backtest a single symbol
  python3 backtest.py --holding 10           # days to hold before giving up (default 10)
  python3 backtest.py --duration 24          # months of history: 6, 12, 24, or 48 (default 12)
"""

import argparse
import json
from datetime import datetime

from data_fetch import fetch_daily_candles
from signal_engine import compute_signal
from config import WATCHLIST


def backtest_symbol(symbol: str, holding_days: int = 10, min_history: int = 30, duration_months: int = 12):
    """
    Fetches historical data (duration_months back), walks forward day by
    day, generates a signal using only data available "as of" that day,
    and checks whether price hits target or stop-loss within `holding_days`.

    Returns a list of trade records: {date, signal, entry, target, sl,
    outcome, exit_price, days_to_exit}
    """
    rows, source = fetch_daily_candles(symbol, duration_months=duration_months)
    if not rows or len(rows) < min_history + holding_days:
        return None, f"Not enough data for {symbol} (got {len(rows) if rows else 0} rows)"

    # rows are newest-first; reverse to chronological for the forward walk
    chrono = list(reversed(rows))
    trades = []

    for t in range(min_history, len(chrono) - holding_days):
        # "as of" day t: only data up to and including day t is visible
        window = list(reversed(chrono[:t + 1]))  # newest-first slice, as compute_signal expects
        if len(window) < min_history:
            continue

        result = compute_signal(symbol, window, source).to_dict()
        signal = result["signal"]

        if signal not in ("BUY", "SHORT"):
            continue  # only track actionable signals

        entry_price = result["price"]
        target = result["tgt_price"]
        sl = result["sl_price"]
        entry_date = chrono[t]["date"]

        # Walk forward up to holding_days to see what gets hit first
        outcome = "NO_HIT"
        exit_price = None
        days_to_exit = None
        for d in range(1, holding_days + 1):
            if t + d >= len(chrono):
                break
            future_high = chrono[t + d]["high"]
            future_low = chrono[t + d]["low"]

            if signal == "BUY":
                hit_target = future_high >= target
                hit_sl = future_low <= sl
            else:  # SHORT
                hit_target = future_low <= target
                hit_sl = future_high >= sl

            # If both could hit same day, we conservatively assume SL hit first (worse case)
            if hit_sl:
                outcome = "LOSS"
                exit_price = sl
                days_to_exit = d
                break
            if hit_target:
                outcome = "WIN"
                exit_price = target
                days_to_exit = d
                break

        trades.append({
            "symbol": symbol,
            "date": entry_date,
            "signal": signal,
            "entry": entry_price,
            "target": target,
            "sl": sl,
            "outcome": outcome,
            "exit_price": exit_price,
            "days_to_exit": days_to_exit,
        })

    return trades, None


def summarize(all_trades: list):
    """Aggregate win rate stats overall and per symbol."""
    by_symbol = {}
    for tr in all_trades:
        by_symbol.setdefault(tr["symbol"], []).append(tr)

    summary = {"overall": _summarize_group(all_trades), "by_symbol": {}}
    for sym, trades in by_symbol.items():
        summary["by_symbol"][sym] = _summarize_group(trades)
    return summary


def _summarize_group(trades: list):
    total = len(trades)
    wins = sum(1 for t in trades if t["outcome"] == "WIN")
    losses = sum(1 for t in trades if t["outcome"] == "LOSS")
    no_hit = sum(1 for t in trades if t["outcome"] == "NO_HIT")
    decided = wins + losses  # exclude no-hit from win-rate denominator
    win_rate = round(wins / decided * 100, 1) if decided else None
    return {
        "total_signals": total,
        "wins": wins,
        "losses": losses,
        "no_hit_within_window": no_hit,
        "win_rate_pct": win_rate,
    }


def run_backtest(symbols=None, holding_days=10, duration_months=12):
    if symbols is None:
        symbols = []
        for market_list in WATCHLIST.values():
            symbols.extend(market_list)

    all_trades = []
    errors = []
    for sym in symbols:
        trades, err = backtest_symbol(sym, holding_days=holding_days, duration_months=duration_months)
        if err:
            errors.append(err)
            continue
        all_trades.extend(trades)

    summary = summarize(all_trades)
    return {
        "run_at": datetime.now().isoformat(),
        "holding_days": holding_days,
        "duration_months": duration_months,
        "symbols_tested": symbols,
        "errors": errors,
        "summary": summary,
        "trades": all_trades,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--symbol", help="Backtest a single symbol instead of the full watchlist")
    parser.add_argument("--holding", type=int, default=10, help="Days to hold before giving up (default 10)")
    parser.add_argument("--duration", type=int, default=12, help="Months of history: 6, 12, 24, or 48 (default 12)")
    args = parser.parse_args()

    symbols = [args.symbol] if args.symbol else None
    result = run_backtest(symbols=symbols, holding_days=args.holding, duration_months=args.duration)

    print(json.dumps(result["summary"], indent=2))
    print(f"\nErrors: {result['errors']}")
    print(f"\nFull results saved to backtest_results.json")

    with open("backtest_results.json", "w") as f:
        json.dump(result, f, indent=2)
