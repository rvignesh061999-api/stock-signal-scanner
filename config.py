"""
config.py
Shared configuration for the scan and backtest scripts.
"""

WATCHLIST = {
    "US": ["AAPL", "MSFT", "TSLA", "NVDA", "AMZN"],
    "IN": [
        "RELIANCE.NS", "TCS.NS", "INFY.NS", "HDFCBANK.NS", "ICICIBANK.NS",
        "IDEA.NS", "RPOWER.NS", "YESBANK.NS", "SUZLON.NS",
        "PCJEWELLER.NS", "RTNPOWER.NS", "SEPC.NS", "GTLINFRA.NS",
    ],
}

DEFAULT_CAPITAL = 10000
