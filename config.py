"""
config.py
Shared configuration for the scan and backtest scripts.
"""

# Full watchlist — used for daily-candle swing scanning (scan_and_alert.py)
# and as the default for daily-interval backtests.
WATCHLIST = {
    "US": ["AAPL", "MSFT", "TSLA", "NVDA", "AMZN"],
    "IN": [
        "RELIANCE.NS", "TCS.NS", "INFY.NS", "HDFCBANK.NS", "ICICIBANK.NS",
        "IDEA.NS", "RPOWER.NS", "YESBANK.NS", "SUZLON.NS",
        "PCJEWELLER.NS", "RTNPOWER.NS", "SEPC.NS", "GTLINFRA.NS",
    ],
}

# Intraday watchlist — filtered down from a full hourly backtest
# (19,912 signals, 2yr history, 10-hour holding). Only stocks that
# cleared 35%+ win rate (vs. the ~33.3% breakeven line for the current
# 2:1 reward-risk setup) are kept. Every US large-cap and Indian
# large-cap bank/Reliance fell at or below breakeven on hourly candles
# and was excluded — this list is deliberately short.
#
# IMPORTANT: this list was chosen BECAUSE it scored well on this one
# backtest — that carries real overfitting risk (finding patterns in
# past noise rather than a repeatable edge). Treat this as a hypothesis
# to keep validating on fresh data, not a settled conclusion. Re-run
# the backtest periodically and drop any symbol whose win rate drifts
# back toward or below breakeven.
INTRADAY_WATCHLIST = {
    "IN": [
        "PCJEWELLER.NS",  # 40.3% win rate on last backtest
        "YESBANK.NS",     # 38.1%
        "RPOWER.NS",      # 37.8%
        "SUZLON.NS",      # 37.5%
        "SEPC.NS",        # 36.6%
        "IDEA.NS",        # 36.5%
        "RTNPOWER.NS",    # 36.5%
        "INFY.NS",        # 35.6%
    ],
}

DEFAULT_CAPITAL = 10000
