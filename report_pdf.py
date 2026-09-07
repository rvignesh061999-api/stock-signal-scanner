"""
report_pdf.py
Builds a PDF summary report from backtest results (see backtest.py),
suitable for sending via Telegram or downloading directly.
"""

from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
)


def build_backtest_pdf(result: dict, output_path: str = "backtest_report.pdf"):
    """
    result: the dict returned by backtest.run_backtest() (with or without
    the full "trades" list — the report builds mainly from "summary").
    """
    doc = SimpleDocTemplate(output_path, pagesize=letter,
                             topMargin=0.6 * inch, bottomMargin=0.6 * inch)
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle("TitleCustom", parent=styles["Title"], fontSize=20)
    meta_style = ParagraphStyle("Meta", parent=styles["Normal"], fontSize=9, textColor=colors.grey)
    section_style = ParagraphStyle("Section", parent=styles["Heading2"], spaceBefore=16)

    story = []

    # ---- Header ----
    story.append(Paragraph("Signal Scanner — Backtest Report", title_style))
    run_at = result.get("run_at", datetime.now().isoformat())
    interval = result.get("interval", "1d")
    interval_labels = {"1d": "daily candles", "1h": "hourly candles", "15m": "15-minute candles"}
    history_label = (
        f"{result.get('duration_months', '?')} months"
        if interval == "1d"
        else f"max available history ({interval_labels.get(interval, interval)})"
    )
    story.append(Paragraph(
        f"Generated: {run_at.split('T')[0]} {run_at.split('T')[1][:8] if 'T' in run_at else ''} "
        f"&nbsp;|&nbsp; Interval: {interval_labels.get(interval, interval)} "
        f"&nbsp;|&nbsp; History: {history_label} "
        f"&nbsp;|&nbsp; Holding period: {result.get('holding_days', '?')} bars",
        meta_style
    ))
    story.append(Spacer(1, 4))
    story.append(Paragraph(
        "This report shows how the current candle + support/resistance + volume signal "
        "logic would have performed historically. It is a backtest of existing rules, "
        "not a guarantee of future results, and not financial advice.",
        meta_style
    ))
    story.append(Spacer(1, 16))

    # ---- Overall summary ----
    overall = result.get("summary", {}).get("overall", {})
    story.append(Paragraph("Overall Performance", section_style))
    overall_table_data = [
        ["Metric", "Value"],
        ["Total signals tested", str(overall.get("total_signals", 0))],
        ["Wins", str(overall.get("wins", 0))],
        ["Losses", str(overall.get("losses", 0))],
        ["No hit within window", str(overall.get("no_hit_within_window", 0))],
        ["Win rate", f"{overall.get('win_rate_pct', 'N/A')}%" if overall.get("win_rate_pct") is not None else "N/A (no decided trades)"],
    ]
    overall_table = Table(overall_table_data, colWidths=[3 * inch, 2.5 * inch])
    overall_table.setStyle(_table_style())
    story.append(overall_table)
    story.append(Spacer(1, 8))

    breakeven_note = (
        "Note: with the current 3% target / 1.5% stop-loss (2:1 reward-risk), "
        "a win rate above roughly 33% is needed just to break even before costs."
    )
    story.append(Paragraph(breakeven_note, meta_style))

    # ---- Per-symbol breakdown ----
    by_symbol = result.get("summary", {}).get("by_symbol", {})
    if by_symbol:
        story.append(Paragraph("Per-Symbol Breakdown", section_style))
        rows = [["Symbol", "Signals", "Wins", "Losses", "No Hit", "Win Rate"]]
        for sym, stats in sorted(by_symbol.items(), key=lambda kv: kv[0]):
            win_rate = f"{stats['win_rate_pct']}%" if stats.get("win_rate_pct") is not None else "N/A"
            rows.append([
                sym,
                str(stats.get("total_signals", 0)),
                str(stats.get("wins", 0)),
                str(stats.get("losses", 0)),
                str(stats.get("no_hit_within_window", 0)),
                win_rate,
            ])
        symbol_table = Table(rows, colWidths=[1.3 * inch, 0.9 * inch, 0.7 * inch, 0.8 * inch, 0.8 * inch, 0.9 * inch])
        symbol_table.setStyle(_table_style())
        story.append(symbol_table)

    # ---- Errors, if any ----
    errors = result.get("errors", [])
    if errors:
        story.append(Paragraph("Symbols Skipped (data issues)", section_style))
        for e in errors:
            story.append(Paragraph(f"• {e}", styles["Normal"]))

    # ---- Optional: sample trades (only if included in result) ----
    trades = result.get("trades")
    if trades:
        story.append(PageBreak())
        story.append(Paragraph("Sample Trades (first 30)", section_style))
        rows = [["Symbol", "Date", "Signal", "Entry", "Target", "SL", "Outcome"]]
        for t in trades[:30]:
            rows.append([
                t["symbol"], t["date"], t["signal"],
                str(t["entry"]), str(t["target"]), str(t["sl"]), t["outcome"],
            ])
        trade_table = Table(rows, colWidths=[0.9 * inch, 0.9 * inch, 0.7 * inch, 0.7 * inch, 0.7 * inch, 0.7 * inch, 0.8 * inch])
        trade_table.setStyle(_table_style())
        story.append(trade_table)

    doc.build(story)
    return output_path


def _table_style():
    return TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1B2430")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CCCCCC")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F4F4F4")]),
        ("ALIGN", (1, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ])
