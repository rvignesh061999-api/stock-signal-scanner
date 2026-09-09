"""
calibrate_thresholds.py
For each stock in the intraday watchlist, grid-searches combinations of
target %, stop-loss %, volume factor, and level tolerance against that
STOCK'S OWN 2-year hourly history, and picks whichever combination
produced the best real win rate for that specific stock.

This replaces one flat threshold set (used for all 8 stocks) with a
per-stock calibrated profile — the same idea as the TIER3_TARGETS table
in the JS reference implementation reviewed earlier in this project.

IMPORTANT — this INCREASES overfitting risk, not decreases it: fitting
8 separate parameter sets to the same 2-year window gives the search
more freedom to find combinations that happened to work on that
specific historical stretch, without necessarily reflecting a durable
pattern. The live forward-validation system (scan_intraday.py +
forward_accuracy_report.py) becomes MORE important after this, not
less — it's the real check on whether per-stock tuning helped or just
overfit harder.

Only combinations with at least MIN_SIGNALS_FOR_CONSIDERATION signals
are considered, to avoid picking a combination that "won" purely from
having too few trades to be meaningful.

Sends a summary to Telegram and saves the resulting profiles to
per_stock_profiles.json (committed by the calibrate.yml workflow) —
this file is then read by scan_intraday.py and can be read by
backtest.py to apply the calibrated profile per symbol going forward.

Triggered manually via .github/workflows/calibrate.yml — this is
compute-intensive (many backtest runs per stock) and not meant to run
on a schedule.
"""

import json
import itertools

from config import INTRADAY_WATCHLIST
from backtest import backtest_symbol, summarize
from telegram_alert import send_telegram_message

HOLDING_BARS = 10
INTERVAL = "1h"
MIN_SIGNALS_FOR_CONSIDERATION = 150
OUTPUT_FILE = "per_stock_profiles.json"

# Grid search space. tgt_pct paired with sl_pct at a fixed 2:1 ratio,
# matching the existing minimum reward-risk convention used everywhere
# else in this project — we are NOT searching for a different R:R here,
# only for the right SIZE of move for each stock's typical volatility.
TGT_PCT_OPTIONS = [0.6, 0.8, 1.0, 1.2, 1.5, 2.0]
VOL_FACTOR_OPTIONS = [1.3, 1.6, 2.0]
LEVEL_TOLERANCE_OPTIONS = [0.005, 0.008, 0.012]


def grid_search_symbol(symbol: str):
    """
    Returns (best_profile_dict, best_stats_dict, all_results_list) for
    one symbol, or (None, None, []) if nothing met the minimum sample size.
    """
    results = []
    for tgt_pct, vol_factor, level_tolerance in itertools.product(
        TGT_PCT_OPTIONS, VOL_FACTOR_OPTIONS, LEVEL_TOLERANCE_OPTIONS
    ):
        profile_override = {
            "tgt_pct": tgt_pct,
            "sl_pct": round(tgt_pct / 2, 3),  # fixed 2:1 reward-risk
            "vol_factor": vol_factor,
            "level_tolerance": level_tolerance,
        }
        trades, err = backtest_symbol(
            symbol, holding_days=HOLDING_BARS, interval=INTERVAL, profile_override=profile_override
        )
        if err or not trades:
            continue
        stats = summarize(trades)["overall"]
        if stats["total_signals"] < MIN_SIGNALS_FOR_CONSIDERATION:
            continue
        results.append({"profile": profile_override, "stats": stats})

    if not results:
        return None, None, []

    # Pick the combination with the highest win rate among those with
    # enough signals to be meaningful. Ties broken by more signals
    # (slightly more evidence behind the number).
    best = max(results, key=lambda r: (r["stats"]["win_rate_pct"] or 0, r["stats"]["total_signals"]))
    return best["profile"], best["stats"], results


def main():
    symbols = []
    for market_list in INTRADAY_WATCHLIST.values():
        symbols.extend(market_list)

    send_telegram_message(
        f"Starting per-stock threshold calibration for {len(symbols)} stocks "
        f"({len(TGT_PCT_OPTIONS) * len(VOL_FACTOR_OPTIONS) * len(LEVEL_TOLERANCE_OPTIONS)} "
        f"combinations tested per stock). This will take a while — a summary follows when done."
    )

    profiles = {}
    summary_lines = ["📐 Per-Stock Calibration Results"]
    summary_lines.append(f"(2yr hourly, {HOLDING_BARS}-bar hold, min {MIN_SIGNALS_FOR_CONSIDERATION} signals to qualify)\n")

    for symbol in symbols:
        print(f"[calibrate] Grid-searching {symbol}...")
        best_profile, best_stats, all_results = grid_search_symbol(symbol)

        if best_profile is None:
            summary_lines.append(f"{symbol}: no combination met the minimum sample size — kept default profile")
            print(f"[calibrate] {symbol}: no qualifying combination found")
            continue

        profiles[symbol] = best_profile
        summary_lines.append(
            f"{symbol}: tgt {best_profile['tgt_pct']}% / sl {best_profile['sl_pct']}% / "
            f"vol {best_profile['vol_factor']}x / tol {best_profile['level_tolerance']} "
            f"→ {best_stats['win_rate_pct']}% win rate ({best_stats['total_signals']} signals)"
        )
        print(f"[calibrate] {symbol}: best = {best_profile}, win rate = {best_stats['win_rate_pct']}%")

    with open(OUTPUT_FILE, "w") as f:
        json.dump(profiles, f, indent=2)

    summary_lines.append(
        f"\n⚠️ These profiles were fit to the SAME 2yr window used to pick these 8 stocks — "
        f"real overfitting risk. Treat as a hypothesis; the forward accuracy report is the real test."
    )
    message = "\n".join(summary_lines)
    print(message)
    send_telegram_message(message)


if __name__ == "__main__":
    main()
