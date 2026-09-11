"""
telegram_alert.py
Sends signal alerts to a Telegram chat via a bot.

Setup:
1. Message @BotFather on Telegram, send /newbot, follow prompts to get a token.
2. Message your new bot once (anything) so it can reply to you.
3. Visit https://api.telegram.org/bot<TOKEN>/getUpdates to find your chat id.
4. In Replit Secrets, add TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID.
"""

import os
import requests

BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "")


def send_telegram_message(text: str) -> bool:
    if not BOT_TOKEN or not CHAT_ID:
        print("[telegram] Skipped: TELEGRAM_BOT_TOKEN / TELEGRAM_CHAT_ID not set.")
        return False
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    try:
        resp = requests.post(url, data={"chat_id": CHAT_ID, "text": text, "parse_mode": "HTML"}, timeout=10)
        return resp.status_code == 200
    except Exception as e:
        print(f"[telegram] Error: {e}")
        return False


def send_telegram_document(file_path: str, caption: str = "") -> bool:
    """Sends a file (e.g. a PDF report) to the configured Telegram chat."""
    if not BOT_TOKEN or not CHAT_ID:
        print("[telegram] Skipped: TELEGRAM_BOT_TOKEN / TELEGRAM_CHAT_ID not set.")
        return False
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendDocument"
    try:
        with open(file_path, "rb") as f:
            files = {"document": f}
            data = {"chat_id": CHAT_ID, "caption": caption[:1024]}  # Telegram caption limit
            resp = requests.post(url, data=data, files=files, timeout=30)
        if resp.status_code != 200:
            print(f"[telegram] sendDocument failed: {resp.status_code} {resp.text}")
        return resp.status_code == 200
    except Exception as e:
        print(f"[telegram] Error sending document: {e}")
        return False


def format_signal_message(sig: dict) -> str:
    icon = "🟢" if sig["signal"] == "BUY" else ("🔴" if sig["signal"] == "SHORT" else "⚪")
    lines = [
        f"{icon} <b>{sig['symbol']}</b> — {sig['signal']}",
        f"Price: {sig['price']} ({sig['price_change_pct']:+.2f}%)",
    ]

    if sig.get("exit_rule") == "next_bar_close":
        # Direction-prediction style signal (e.g. PCJEWELLER strategy) —
        # no price target/SL, exits at the next bar's close instead.
        confidence = sig.get("confidence", "unspecified")
        lines.append(f"Predicted direction: {sig.get('predicted_direction', '?')} (confidence: {confidence})")
        lines.append("Exit: at next hourly bar's close")
        if sig.get("reasons"):
            lines.append("Reason: " + sig["reasons"][-1])
    else:
        lines.append(f"Candle: {sig['candle']} ({sig['candle_strength']})")
        lines.append(f"Near level: {sig['near_level']} | Volume confirmed: {sig['volume_confirmed']}")
        lines.append(f"SL: {sig['sl_price']} | Target: {sig['tgt_price']}")

    lines.append(f"Source: {sig['source']}")
    return "\n".join(lines)


def send_signals(signals: list):
    for sig in signals:
        if sig["signal"] in ("BUY", "SHORT"):  # only alert on actionable signals
            send_telegram_message(format_signal_message(sig))
