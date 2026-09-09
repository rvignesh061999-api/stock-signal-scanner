"""
candle_history_report.py
Builds a candle-pattern history table for each stock in the intraday
watchlist, over ~2 years of hourly bars: Stock, Date, Time (IST, 24hr),
High/Low, Direction (UP/DOWN/FLAT), Candle Pattern, Volume.

Produces BOTH a PDF and a plain-text (.txt) version of the same table
per stock, both sent to Telegram.

This is a raw historical record, not a signal/backtest report — it
shows what candle pattern was detected on EVERY bar, not just the ones
that became actionable BUY/SHORT signals.

Times: Yahoo's raw timestamps are stored/fetched in UTC internally
(see data_fetch.py) — this script converts to IST for display only,
since these are Indian stocks and UTC times don't intuitively line up
with NSE market hours (9:15 AM-3:30 PM IST). The underlying data model
used elsewhere (scan_intraday.py's bar-matching logic) is untouched.

SIZE WARNING: ~3,000 hourly bars/stock x 8 stocks ≈ 24,000 rows total.
One PDF + one TXT per stock is built (not one giant combined file) to
keep each file a manageable size. Even so, each per-stock PDF will run
~100+ pages — this is an inherent consequence of the data volume
requested, not a bug.

Triggered manually via .github/workflows/candle_history.yml.
"""

import os
from datetime import datetime, timedelta

from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle

from config import INTRADAY_WATCHLIST
from data_fetch import fetch_intraday_candles
from signal_engine import detect_candle_pattern
from telegram_alert import send_telegram_document, send_telegram_message

INTERVAL = "1h"
OUTPUT_DIR = "candle_history_pdfs"
IST_OFFSET = timedelta(hours=5, minutes=30)


def _to_ist(date_str: str):
    """
    Converts a stored UTC 'YYYY-MM-DD HH:MM:SS' string to IST date/time
    parts. Falls back to the raw string split if parsing fails for any
    reason (e.g. an unexpected format from a fallback data source).
    """
    try:
        dt_utc = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
        dt_ist = dt_utc + IST_OFFSET
        return dt_ist.strftime("%Y-%m-%d"), dt_ist.strftime("%H:%M:%S")
    except ValueError:
        parts = date_str.split(" ")
        return parts[0], parts[1] if len(parts) > 1 else ""


def build_symbol_rows(symbol: str):
    """
    Fetches 2yr hourly data and returns a list of row tuples:
    (date, time, high, low, direction, pattern_name, volume) in
    chronological order. Date/time are IST, 24-hour format.
    """
    rows, source = fetch_intraday_candles(symbol, interval=INTERVAL)
    if not rows:
        return None, None

    chrono = list(reversed(rows))  # oldest first
    table_rows = []
    for i in range(2, len(chrono)):
        # detect_candle_pattern expects newest-first: [current, prev, prev-prev]
        window = [chrono[i], chrono[i - 1], chrono[i - 2]]
        pattern_name, _, _ = detect_candle_pattern(window)

        bar = chrono[i]
        date_part, time_part = _to_ist(bar["date"])

        if bar["close"] > bar["open"]:
            direction = "UP"
        elif bar["close"] < bar["open"]:
            direction = "DOWN"
        else:
            direction = "FLAT"

        table_rows.append((
            date_part, time_part,
            f"{bar['high']} / {bar['low']}",
            direction,
            pattern_name,
            f"{bar['volume']:,}",
        ))
    return table_rows, source


def build_pdf_for_symbol(symbol: str, table_rows: list, output_path: str):
    doc = SimpleDocTemplate(output_path, pagesize=landscape(letter),
                             topMargin=0.5 * inch, bottomMargin=0.5 * inch)
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle("TitleCustom", parent=styles["Title"], fontSize=16)
    meta_style = ParagraphStyle("Meta", parent=styles["Normal"], fontSize=8, textColor=colors.grey)

    story = [
        Paragraph(f"Candle History — {symbol}", title_style),
        Paragraph(f"Interval: hourly | Times: IST (24hr) | Total bars: {len(table_rows):,} | Source: Yahoo Finance", meta_style),
        Spacer(1, 10),
    ]

    header = ["Date", "Time (IST)", "High / Low", "Direction", "Candle Pattern", "Volume"]
    data = [header] + [list(r) for r in table_rows]

    table = Table(data, colWidths=[1.0 * inch, 0.9 * inch, 1.4 * inch, 0.8 * inch, 2.0 * inch, 1.1 * inch], repeatRows=1)
    style_commands = [
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1B2430")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 7),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#CCCCCC")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F4F4F4")]),
        ("ALIGN", (2, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ]
    # Color the Direction column text green/red for quick scanning
    for row_idx, row in enumerate(table_rows, start=1):
        if row[3] == "UP":
            style_commands.append(("TEXTCOLOR", (3, row_idx), (3, row_idx), colors.HexColor("#1a7a3c")))
        elif row[3] == "DOWN":
            style_commands.append(("TEXTCOLOR", (3, row_idx), (3, row_idx), colors.HexColor("#b3261e")))
    table.setStyle(TableStyle(style_commands))
    story.append(table)

    doc.build(story)
    return output_path


def build_txt_for_symbol(symbol: str, table_rows: list, output_path: str):
    """Plain-text version of the same table, fixed-width columns, tab-separated fallback friendly."""
    header = ["Date", "Time (IST)", "High / Low", "Direction", "Candle Pattern", "Volume"]
    col_widths = [12, 12, 16, 10, 22, 12]

    def fmt_row(cols):
        return "".join(str(c).ljust(w) for c, w in zip(cols, col_widths))

    with open(output_path, "w") as f:
        f.write(f"Candle History - {symbol}\n")
        f.write(f"Interval: hourly | Times: IST (24hr) | Total bars: {len(table_rows):,} | Source: Yahoo Finance\n")
        f.write("=" * sum(col_widths) + "\n")
        f.write(fmt_row(header) + "\n")
        f.write("-" * sum(col_widths) + "\n")
        for row in table_rows:
            f.write(fmt_row(row) + "\n")
    return output_path


def main():
    symbols = []
    for market_list in INTRADAY_WATCHLIST.values():
        symbols.extend(market_list)

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    send_telegram_message(
        f"Rebuilding candle history (PDF + TXT) for {len(symbols)} stocks (~2yr hourly each). "
        f"Times now shown in IST 24hr format, with a Direction column added."
    )

    for symbol in symbols:
        print(f"[candle-history] Building {symbol}...")
        table_rows, source = build_symbol_rows(symbol)
        if not table_rows:
            print(f"[candle-history] {symbol}: no data, skipping")
            send_telegram_message(f"{symbol}: no data available, skipped.")
            continue

        safe_name = symbol.replace(".", "_")
        pdf_path = os.path.join(OUTPUT_DIR, f"candle_history_{safe_name}.pdf")
        txt_path = os.path.join(OUTPUT_DIR, f"candle_history_{safe_name}.txt")

        build_pdf_for_symbol(symbol, table_rows, pdf_path)
        build_txt_for_symbol(symbol, table_rows, txt_path)

        pdf_size_mb = os.path.getsize(pdf_path) / (1024 * 1024)
        txt_size_mb = os.path.getsize(txt_path) / (1024 * 1024)
        print(f"[candle-history] {symbol}: {len(table_rows)} rows, PDF {pdf_size_mb:.1f} MB, TXT {txt_size_mb:.1f} MB")

        pdf_caption = f"Candle History (PDF): {symbol}\n{len(table_rows):,} hourly bars | {pdf_size_mb:.1f} MB"
        txt_caption = f"Candle History (TXT): {symbol}\n{len(table_rows):,} hourly bars | {txt_size_mb:.1f} MB"

        sent_pdf = send_telegram_document(pdf_path, caption=pdf_caption)
        sent_txt = send_telegram_document(txt_path, caption=txt_caption)
        print(f"[candle-history] {symbol}: PDF sent = {sent_pdf}, TXT sent = {sent_txt}")

    print("[candle-history] Done.")


if __name__ == "__main__":
    main()
