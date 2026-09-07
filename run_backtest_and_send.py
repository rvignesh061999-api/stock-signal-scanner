"""
run_backtest_and_send.py
Runs a backtest and sends PDF report(s) to Telegram.

Two modes:
- Single symbol: python3 run_backtest_and_send.py SYMBOL [INTERVAL] [DURATION_MONTHS] [HOLDING]
- Full watchlist (no symbol given): backtests every stock in config.WATCHLIST,
  one PDF per stock, all sent to Telegram, plus a final summary message.

INTERVAL: "1d" (daily, default), "1h" (hourly, ~2yr history), or "15m"
(~60 days history). DURATION_MONTHS only applies to "1d" mode — intraday
history is capped by the data source, not configurable.

This is NOT an intraday-execution tool — it's a signal/alert generator.
"Holding" means how many bars (not necessarily calendar days) to wait
after a signal before checking if it hit target or stop-loss.

Triggered manually via .github/workflows/backtest.yml, or run locally.

Examples:
  python3 run_backtest_and_send.py                          # full watchlist, daily, 24mo, 10-bar hold
  python3 run_backtest_and_send.py RELIANCE.NS               # single symbol, daily, 24mo, 10-bar hold
  python3 run_backtest_and_send.py RELIANCE.NS 1h             # single symbol, hourly, max history, 10-bar hold
  python3 run_backtest_and_send.py "" 1h 0 10                  # full watchlist, hourly, 10-bar hold
"""

import sys
import time

from config import WATCHLIST
from backtest import run_backtest
from report_pdf import build_backtest_pdf
from telegram_alert import send_telegram_document, send_telegram_message

DEFAULT_DURATION_MONTHS = 24
DEFAULT_HOLDING = 10
DEFAULT_INTERVAL = "1d"


def backtest_one_symbol_and_send(symbol: str, interval: str, duration: int, holding: int):
    label = f"{duration}mo history" if interval == "1d" else f"max available history ({interval})"
    print(f"[backtest] Running {symbol}, {interval}, {label}, {holding}-bar hold...")
    result = run_backtest(symbols=[symbol], holding_days=holding,
                           duration_months=duration, interval=interval)

    overall = result["summary"]["overall"]
    print(f"[backtest] {symbol}: {overall['total_signals']} signals, win rate {overall.get('win_rate_pct')}%")

    if overall["total_signals"] == 0:
        print(f"[backtest] {symbol}: no signals generated, skipping PDF/Telegram send.")
        return overall

    pdf_path = f"backtest_{symbol.replace('.', '_')}_{interval}.pdf"
    build_backtest_pdf(result, output_path=pdf_path)

    win_rate_str = f"{overall['win_rate_pct']}%" if overall.get("win_rate_pct") is not None else "N/A"
    caption = (
        f"Backtest: {symbol} ({interval})\n"
        f"{label}, {holding}-bar hold\n"
        f"Signals: {overall['total_signals']} | Win rate: {win_rate_str}"
    )
    sent = send_telegram_document(pdf_path, caption=caption)
    print(f"[backtest] {symbol}: sent to Telegram = {sent}")

    if result["errors"]:
        print(f"[backtest] {symbol}: errors = {result['errors']}")

    return overall


def main():
    symbol = sys.argv[1] if len(sys.argv) > 1 and sys.argv[1] else None
    interval = sys.argv[2] if len(sys.argv) > 2 and sys.argv[2] else DEFAULT_INTERVAL
    duration = int(sys.argv[3]) if len(sys.argv) > 3 and sys.argv[3] else DEFAULT_DURATION_MONTHS
    holding = int(sys.argv[4]) if len(sys.argv) > 4 and sys.argv[4] else DEFAULT_HOLDING

    if symbol:
        # Single-symbol mode
        backtest_one_symbol_and_send(symbol, interval, duration, holding)
        return

    # Full-watchlist mode: every stock, one PDF each, all sent to Telegram
    all_symbols = []
    for market_list in WATCHLIST.values():
        all_symbols.extend(market_list)

    label = f"{duration}mo history" if interval == "1d" else f"max available history ({interval})"
    print(f"[backtest] Running full watchlist: {len(all_symbols)} symbols, {interval}, {label}, {holding}-bar hold")
    send_telegram_message(
        f"Starting full watchlist backtest: {len(all_symbols)} stocks, "
        f"{interval} candles, {label}, {holding}-bar hold. A PDF will follow for each stock."
    )

    summary_rows = []
    for sym in all_symbols:
        overall = backtest_one_symbol_and_send(sym, interval, duration, holding)
        summary_rows.append((sym, overall))
        time.sleep(1)  # brief pause between symbols to be gentle on data sources and Telegram

    # Final consolidated summary message
    lines = [f"Backtest complete ({interval}) — summary:"]
    for sym, overall in summary_rows:
        wr = f"{overall['win_rate_pct']}%" if overall.get("win_rate_pct") is not None else "N/A"
        lines.append(f"{sym}: {overall['total_signals']} signals, win rate {wr}")
    send_telegram_message("\n".join(lines))
    print("[backtest] Full watchlist backtest complete.")


if __name__ == "__main__":
    main()
