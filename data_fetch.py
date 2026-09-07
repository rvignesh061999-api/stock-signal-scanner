"""
data_fetch.py
Fetches OHLCV candle data for a symbol, at a chosen interval.
Primary source: Yahoo Finance chart API (direct HTTP, browser-like headers)
Fallback source: Twelve Data API (needs TD_API_KEY env var)

Two fetch modes:
- fetch_daily_candles(): daily bars, selectable duration (6/12/24/48 months).
  Used for the original swing-trading scan and backtest.
- fetch_intraday_candles(): hourly or 15-min bars. Yahoo limits how far back
  these go — roughly 2 years for 1h bars, ~60 days for 15m bars. Used for
  intraday-style backtesting and (once validated) faster live scans.

Returns a list of dicts, newest first:
[{"date": "2026-09-05" or "2026-09-05 14:30:00", "open":.., "high":.., "low":.., "close":.., "volume":..}, ...]
or None if both sources fail.
"""

import os
import requests
from datetime import datetime, timezone

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

# Intraday intervals: how far back Yahoo actually allows data for each.
# These are real platform limits, not something we can configure around.
INTRADAY_OPTIONS = {
    "1h": {"yahoo_range": "2y", "yahoo_interval": "60m", "td_interval": "1h", "td_outputsize": 5000},
    "15m": {"yahoo_range": "60d", "yahoo_interval": "15m", "td_interval": "15min", "td_outputsize": 2000},
}


def _resolve_duration(months: int):
    if months not in DURATION_OPTIONS:
        # snap to nearest supported option instead of failing
        months = min(DURATION_OPTIONS.keys(), key=lambda m: abs(m - months))
    return DURATION_OPTIONS[months]


def fetch_from_yahoo(symbol: str, yahoo_range="6mo", yahoo_interval="1d"):
    """Direct call to Yahoo's chart API. Returns list of OHLCV dicts or None."""
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?interval={yahoo_interval}&range={yahoo_range}"
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
        is_intraday = yahoo_interval != "1d"
        rows = []
        for i, ts in enumerate(timestamps):
            close = quote["close"][i]
            volume = quote["volume"][i]
            if close is None or not volume:
                continue  # skip holiday/no-trade/no-volume rows
            rows.append({
                "date": _ts_to_datetime(ts) if is_intraday else _ts_to_date(ts),
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


def fetch_from_twelvedata(symbol: str, outputsize=100, interval="1day"):
    """Fallback: Twelve Data time_series endpoint. Returns list of OHLCV dicts or None."""
    if not TD_API_KEY:
        print("[twelvedata] No TD_API_KEY set, skipping fallback")
        return None
    url = (
        f"https://api.twelvedata.com/time_series?symbol={symbol}"
        f"&interval={interval}&outputsize={outputsize}&apikey={TD_API_KEY}"
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
    Try Yahoo first, then Twelve Data as fallback. Daily bars only.
    twelvedata_symbol: use a different symbol format for Twelve Data if needed
                        (e.g. "RELIANCE" instead of "RELIANCE.NS").
    duration_months: how far back to fetch — 6, 12, 24, or 48 (snapped to
                      nearest supported option if a different number is passed).
    Returns (rows, source) where source is "yahoo" or "twelve_data", or (None, None).
    """
    opts = _resolve_duration(duration_months)

    rows = fetch_from_yahoo(symbol, yahoo_range=opts["yahoo_range"], yahoo_interval="1d")
    if rows:
        return rows, "yahoo"

    td_symbol = twelvedata_symbol or symbol.replace(".NS", "")
    rows = fetch_from_twelvedata(td_symbol, outputsize=opts["td_outputsize"], interval="1day")
    if rows:
        return rows, "twelve_data"

    return None, None


def fetch_intraday_candles(symbol: str, twelvedata_symbol: str = None, interval: str = "1h"):
    """
    Fetches intraday bars: interval="1h" (up to ~2 years back) or
    interval="15m" (up to ~60 days back) — these history limits are set
    by Yahoo/Twelve Data's platforms, not configurable.

    Returns (rows, source) where source is "yahoo" or "twelve_data", or (None, None).
    """
    if interval not in INTRADAY_OPTIONS:
        raise ValueError(f"Unsupported intraday interval: {interval}. Use one of {list(INTRADAY_OPTIONS)}")
    opts = INTRADAY_OPTIONS[interval]

    rows = fetch_from_yahoo(symbol, yahoo_range=opts["yahoo_range"], yahoo_interval=opts["yahoo_interval"])
    if rows:
        return rows, "yahoo"

    td_symbol = twelvedata_symbol or symbol.replace(".NS", "")
    rows = fetch_from_twelvedata(td_symbol, outputsize=opts["td_outputsize"], interval=opts["td_interval"])
    if rows:
        return rows, "twelve_data"

    return None, None


def _ts_to_date(ts: int) -> str:
    return datetime.fromtimestamp(ts, tz=timezone.utc).strftime("%Y-%m-%d")


def _ts_to_datetime(ts: int) -> str:
    return datetime.fromtimestamp(ts, tz=timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
