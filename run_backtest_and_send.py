"""
run_backtest_and_send.py
Runs a backtest and sends PDF report(s) to Telegram.

Two modes:
- Single symbol: python3 run_backtest_and_send.py SYMBOL [INTERVAL] [DURATION_MONTHS] [HOLDING]
  Sends one PDF for that symbol.
- Full watchlist (no symbol given): backtests every stock — uses
  config.WATCHLIST for daily interval, or config.INTRADAY_WATCHLIST
  (a pre-filtered, smaller list) for 1h/15m intervals — in ONE run,
  and sends ONE consolidated PDF: overall summary plus a per-symbol
  breakdown table (win rate, signal count, etc. for each stock).

INTERVAL: "1d" (daily, default), "1h" (hourly, ~2yr history), or "15m"
(~60 days history). DURATION_MONTHS only applies to "1d" mode — intraday
history is capped by the data source, not configurable.

This is NOT an intraday-execution tool — it's a signal/alert generator.
"Holding" means how many bars (not necessarily calendar days) to wait
after a signal before checking if it hit target or stop-loss.

Triggered manually via .github/workflows/backtest.yml, or run locally.

Examples:
  python3 run_backtest_and_send.py                          # full watchlist, daily, 24mo, 10-bar hold, ONE pdf
  python3 run_backtest_and_send.py RELIANCE.NS               # single symbol, daily, 24mo, 10-bar hold
  python3 run_backtest_and_send.py RELIANCE.NS 1h             # single symbol, hourly, max history, 10-bar hold
  python3 run_backtest_and_send.py "" 1h 0 10                  # full watchlist, hourly, 10-bar hold, ONE pdf
"""

import sys

from config import WATCHLIST, INTRADAY_WATCHLIST
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

    # Full-watchlist mode: ONE backtest run across every stock, ONE
    # consolidated PDF (overall summary + per-symbol breakdown table),
    # sent as a single Telegram document.
    # Intraday intervals use the filtered INTRADAY_WATCHLIST (stocks
    # that cleared breakeven on a prior hourly backtest) — daily uses
    # the full WATCHLIST. See config.py for why these differ.
    watchlist_source = WATCHLIST if interval == "1d" else INTRADAY_WATCHLIST
    all_symbols = []
    for market_list in watchlist_source.values():
        all_symbols.extend(market_list)

    label = f"{duration}mo history" if interval == "1d" else f"max available history ({interval})"
    print(f"[backtest] Running full watchlist: {len(all_symbols)} symbols, {interval}, {label}, {holding}-bar hold")
    send_telegram_message(
        f"Running full watchlist backtest: {len(all_symbols)} stocks, "
        f"{interval} candles, {label}, {holding}-bar hold. One consolidated PDF will follow shortly."
    )

    result = run_backtest(symbols=all_symbols, holding_days=holding,
                           duration_months=duration, interval=interval)

    overall = result["summary"]["overall"]
    print(f"[backtest] Full watchlist: {overall['total_signals']} total signals, win rate {overall.get('win_rate_pct')}%")

    if overall["total_signals"] == 0:
        send_telegram_message("Full watchlist backtest complete — no signals generated across any stock.")
        print("[backtest] No signals generated, skipping PDF/Telegram send.")
        return

    pdf_path = f"backtest_full_watchlist_{interval}.pdf"
    build_backtest_pdf(result, output_path=pdf_path)

    win_rate_str = f"{overall['win_rate_pct']}%" if overall.get("win_rate_pct") is not None else "N/A"
    caption = (
        f"Full Watchlist Backtest ({interval})\n"
        f"{len(all_symbols)} stocks, {label}, {holding}-bar hold\n"
        f"Total signals: {overall['total_signals']} | Overall win rate: {win_rate_str}"
    )
    sent = send_telegram_document(pdf_path, caption=caption)
    print(f"[backtest] Sent consolidated PDF to Telegram: {sent}")

    if result["errors"]:
        print(f"[backtest] Errors: {result['errors']}")
        send_telegram_message("Some symbols had data issues:\n" + "\n".join(result["errors"]))

    print("[backtest] Full watchlist backtest complete.")


if __name__ == "__main__":
    main()
