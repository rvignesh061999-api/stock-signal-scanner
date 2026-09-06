"""
run_backtest_and_send.py
Runs a backtest for one symbol and sends the PDF report to Telegram.
Triggered manually via .github/workflows/backtest.yml (workflow_dispatch
with symbol/duration/holding inputs), or run locally for testing.

Usage:
  python3 run_backtest_and_send.py SYMBOL DURATION_MONTHS HOLDING_DAYS
  e.g. python3 run_backtest_and_send.py RELIANCE.NS 12 10
"""

import sys

from backtest import run_backtest
from report_pdf import build_backtest_pdf
from telegram_alert import send_telegram_document


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 run_backtest_and_send.py SYMBOL [DURATION_MONTHS] [HOLDING_DAYS]")
        sys.exit(1)

    symbol = sys.argv[1]
    duration = int(sys.argv[2]) if len(sys.argv) > 2 else 12
    holding = int(sys.argv[3]) if len(sys.argv) > 3 else 10

    print(f"[backtest] Running {symbol}, {duration}mo history, {holding}-day hold...")
    result = run_backtest(symbols=[symbol], holding_days=holding, duration_months=duration)

    overall = result["summary"]["overall"]
    print(f"[backtest] Signals: {overall['total_signals']} | Win rate: {overall.get('win_rate_pct')}%")

    pdf_path = f"backtest_{symbol.replace('.', '_')}.pdf"
    build_backtest_pdf(result, output_path=pdf_path)
    print(f"[backtest] PDF built at {pdf_path}")

    win_rate_str = f"{overall['win_rate_pct']}%" if overall.get("win_rate_pct") is not None else "N/A"
    caption = (
        f"Backtest: {symbol}\n"
        f"{duration}mo history, {holding}-day hold\n"
        f"Signals: {overall['total_signals']} | Win rate: {win_rate_str}"
    )
    sent = send_telegram_document(pdf_path, caption=caption)
    print(f"[backtest] Sent to Telegram: {sent}")

    if result["errors"]:
        print(f"[backtest] Errors: {result['errors']}")


if __name__ == "__main__":
    main()
