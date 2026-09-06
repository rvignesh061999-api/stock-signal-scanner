"""
data_fetch.py
Fetches daily OHLCV candle data for a symbol.
Primary source: Yahoo Finance chart API (direct HTTP, browser-like headers)
Fallback source: Twelve Data API (needs TD_API_KEY env var)

Supports selectable duration: 6, 12, 24, or 48 months.

Returns a list of dicts, newest first:
[{"date": "2026-09-05", "open":.., "high":.., "low":.., "close":.., "volume":..}, ...]
or None if both sources fail.
"""

import os
import requests

TD_API_KEY = os.environ.get("TD_API_KEY", "")

SESSION = requests.Session()
SESSION.headers.update({
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/124.0 Safari/537.36",
    "Accept": "application/json",
    "Accept-Language": "en-US,en;q=0.9",
})

# Maps a duration-in-months option to the Yahoo range string and an
# approximate Twelve Data outputsize (trading days, ~21/month).
DURATION_OPTIONS = {
    6: {"yahoo_range": "6mo", "td_outputsize": 130},
    12: {"yahoo_range": "1y", "td_outputsize": 260},
    24: {"yahoo_range": "2y", "td_outputsize": 500},   # Twelve Data free tier caps outputsize; may return less
    48: {"yahoo_range": "5y", "td_outputsize": 1000},  # closest Yahoo range above 4y; TD capped by plan
}
DEFAULT_DURATION_MONTHS = 6


def _resolve_duration(months: int):
    if months not in DURATION_OPTIONS:
        # snap to nearest supported option instead of failing
        months = min(DURATION_OPTIONS.keys(), key=lambda m: abs(m - months))
    return DURATION_OPTIONS[months]


def fetch_from_yahoo(symbol: str, yahoo_range="6mo"):
    """Direct call to Yahoo's chart API. Returns list of OHLCV dicts or None."""
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?interval=1d&range={yahoo_range}"
    try:
        resp = SESSION.get(url, timeout=10)
        if resp.status_code != 200:
            print(f"[yahoo] {symbol}: HTTP {resp.status_code}")
            return None
        data = resp.json()
        result = data.get("chart", {}).get("result")
        if not result:
            return None
        result = result[0]
        timestamps = result.get("timestamp", [])
        quote = result["indicators"]["quote"][0]
        rows = []
        for i, ts in enumerate(timestamps):
            close = quote["close"][i]
            volume = quote["volume"][i]
            if close is None or not volume:
                continue  # skip holiday/no-trade rows
            rows.append({
                "date": _ts_to_date(ts),
                "open": round(quote["open"][i] or close, 2),
                "high": round(quote["high"][i] or close, 2),
                "low": round(quote["low"][i] or close, 2),
                "close": round(close, 2),
                "volume": int(volume),
            })
        rows.reverse()  # newest first
        return rows if len(rows) >= 5 else None
    except Exception as e:
        print(f"[yahoo] {symbol}: error {e}")
        return None


def fetch_from_twelvedata(symbol: str, outputsize=100):
    """Fallback: Twelve Data time_series endpoint. Returns list of OHLCV dicts or None."""
    if not TD_API_KEY:
        print("[twelvedata] No TD_API_KEY set, skipping fallback")
        return None
    url = (
        f"https://api.twelvedata.com/time_series?symbol={symbol}"
        f"&interval=1day&outputsize={outputsize}&apikey={TD_API_KEY}"
    )
    try:
        resp = SESSION.get(url, timeout=10)
        data = resp.json()
        values = data.get("values")
        if not values:
            print(f"[twelvedata] {symbol}: {data.get('message', 'no data')}")
            return None
        rows = []
        for v in values:
            try:
                vol = int(float(v.get("volume", 0)))
            except (TypeError, ValueError):
                vol = 0
            close = float(v["close"])
            if vol == 0 or close <= 0:
                continue
            rows.append({
                "date": v["datetime"],
                "open": round(float(v["open"]), 2),
                "high": round(float(v["high"]), 2),
                "low": round(float(v["low"]), 2),
                "close": round(close, 2),
                "volume": vol,
            })
        return rows if len(rows) >= 5 else None
    except Exception as e:
        print(f"[twelvedata] {symbol}: error {e}")
        return None


def fetch_daily_candles(symbol: str, twelvedata_symbol: str = None, duration_months: int = DEFAULT_DURATION_MONTHS):
    """
    Try Yahoo first, then Twelve Data as fallback.
    twelvedata_symbol: use a different symbol format for Twelve Data if needed
                        (e.g. "RELIANCE" instead of "RELIANCE.NS").
    duration_months: how far back to fetch — 6, 12, 24, or 48 (snapped to
                      nearest supported option if a different number is passed).
    Returns (rows, source) where source is "yahoo" or "twelve_data", or (None, None).
    """
    opts = _resolve_duration(duration_months)

    rows = fetch_from_yahoo(symbol, yahoo_range=opts["yahoo_range"])
    if rows:
        return rows, "yahoo"

    td_symbol = twelvedata_symbol or symbol.replace(".NS", "")
    rows = fetch_from_twelvedata(td_symbol, outputsize=opts["td_outputsize"])
    if rows:
        return rows, "twelve_data"

    return None, None


def _ts_to_date(ts: int) -> str:
    from datetime import datetime, timezone
    return datetime.fromtimestamp(ts, tz=timezone.utc).strftime("%Y-%m-%d")
