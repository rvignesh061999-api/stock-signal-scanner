"""
candle_history_report.py
Builds a PDF table of every hourly candle over the last ~2 years for
each stock in the intraday watchlist: Stock, Date, Time, High/Low,
Candle Pattern, Volume.

This is a raw historical record, not a signal/backtest report — it
shows what candle pattern was detected on EVERY bar, not just the ones
that became actionable BUY/SHORT signals.

SIZE WARNING: ~3,000 hourly bars/stock x 8 stocks ≈ 24,000 rows total.
One PDF per stock is built (not one giant combined file) to keep each
file a manageable size and easier to send via Telegram. Even so, each
per-stock PDF will run several hundred pages — this is an inherent
consequence of the data volume requested, not a bug.

Triggered manually via .github/workflows/candle_history.yml.
"""

import os

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


def build_symbol_rows(symbol: str):
    """
    Fetches 2yr hourly data and returns a list of row tuples:
    (date, time, high, low, pattern_name, volume) in chronological order.
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
        date_part, time_part = (bar["date"].split(" ") + [""])[:2] if " " in bar["date"] else (bar["date"], "")
        table_rows.append((
            date_part, time_part,
            f"{bar['high']} / {bar['low']}",
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
        Paragraph(f"Interval: hourly | Total bars: {len(table_rows):,} | Source: Yahoo Finance", meta_style),
        Spacer(1, 10),
    ]

    header = ["Date", "Time", "High / Low", "Candle Pattern", "Volume"]
    data = [header] + [list(r) for r in table_rows]

    table = Table(data, colWidths=[1.1 * inch, 0.8 * inch, 1.6 * inch, 2.2 * inch, 1.2 * inch], repeatRows=1)
    table.setStyle(TableStyle([
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
    ]))
    story.append(table)

    doc.build(story)
    return output_path


def main():
    symbols = []
    for market_list in INTRADAY_WATCHLIST.values():
        symbols.extend(market_list)

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    send_telegram_message(
        f"Building candle history PDFs for {len(symbols)} stocks (~2yr hourly each). "
        f"This produces large files (hundreds of pages per stock) — one PDF per stock follows."
    )

    for symbol in symbols:
        print(f"[candle-history] Building {symbol}...")
        table_rows, source = build_symbol_rows(symbol)
        if not table_rows:
            print(f"[candle-history] {symbol}: no data, skipping")
            send_telegram_message(f"{symbol}: no data available, skipped.")
            continue

        pdf_path = os.path.join(OUTPUT_DIR, f"candle_history_{symbol.replace('.', '_')}.pdf")
        build_pdf_for_symbol(symbol, table_rows, pdf_path)
        size_mb = os.path.getsize(pdf_path) / (1024 * 1024)
        print(f"[candle-history] {symbol}: {len(table_rows)} rows, {size_mb:.1f} MB")

        caption = f"Candle History: {symbol}\n{len(table_rows):,} hourly bars | {size_mb:.1f} MB"
        sent = send_telegram_document(pdf_path, caption=caption)
        print(f"[candle-history] {symbol}: sent to Telegram = {sent}")

    print("[candle-history] Done.")


if __name__ == "__main__":
    main()
