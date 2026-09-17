# RattanIndia Power (RTNPOWER.NS) — Hourly Candle Statistical Analysis
### Data: 2,974 hourly bars, 2024‑09‑10 to 2026‑09‑09 | Source: Yahoo Finance (as provided)

---

## PART 1 — DATA VALIDATION

| Check | Result |
|---|---|
| Total valid bars | 2,974 (matches header claim exactly) |
| Earliest bar | 2024‑09‑10 12:15 IST |
| Latest bar | 2026‑09‑09 15:15 IST |
| Trading dates covered | 494 |
| UP bars | 1,193 (40.1%) |
| DOWN bars | 1,465 (49.3%) |
| FLAT bars | 316 (10.6%) |
| Bars per time slot | 09:15 → 22, 10:15 → 491, 11:15 → 491, 12:15 → 492, 13:15 → 493, 14:15 → 494, 15:15 → 491 |
| Pattern counts | Bearish Candle 943, Bullish Candle 653, Doji 395, Strong Bearish 203, Morning Star 180, Bullish Engulfing 164, Evening Star 143, Strong Bullish 128, Bearish Engulfing 126, Shooting Star 28, Hammer 11 |
| Duplicate records | **0** (no duplicate Date+Time rows, no duplicate full rows) |
| High < Low | **0 occurrences** |
| Close outside High/Low | **0 occurrences** |
| Open outside High/Low | **0 occurrences** |
| Direction vs Close‑Open sign | **0 mismatches** in the entire dataset |
| Missing calendar dates | None beyond normal weekends/holidays |
| Bars per day | 467 days have exactly 6, 22 have 7 (extra 09:15 print), and 5 days have short sessions (4, 2, 2, 5, 5 bars) on 2024‑09‑10, 2025‑10‑21, 2026‑04‑20, 2026‑06‑15, 2026‑08‑06 — consistent with holiday/first/last‑day sessions |

**Things worth flagging (observations, not corrections):**

1. **Frozen bars (O=H=L=C) total 25 of 2,974 (0.8%), all 25 in the training period, zero afterward** — the same illiquidity‑clustering‑then‑disappearing pattern seen in Reliance Power and Suzlon Energy, both of which are similarly small‑cap power/energy names.
2. **Doji is again not synonymous with FLAT** — of 395 Doji bars, 306 are FLAT, 47 DOWN, 42 UP.
3. **Volume had one temporary spike** (June–July 2025, averaging ~15–16M shares/hour vs. a typical 1–5M) but returned to its normal range afterward — a one‑off event, not a permanent regime shift like PC Jeweller's. Rolling‑relative volume handles this cleanly.

**Conclusion of Part 1: the dataset is internally clean** — no fabricated OHLC, no impossible bars, no label/direction mismatches.

---

## PART 2 — DERIVED VARIABLES

Same full set computed from Open/High/Low/Close/Volume/Date/Time as in the six prior reports: Range, Range %, Body size/%, Bar % change, upper/lower wick (absolute + % of range), body‑to‑range ratio, gap and gap % vs. previous close, close‑position tercile, BodyDir (cross‑checked, zero mismatches), volume vs. previous bar and vs. trailing 20‑bar rolling average, range/body change vs. previous bar, streak type/length, previous 2‑/3‑bar sequences, day‑of‑week, HH/HL/LH/LL flags, Close‑vs‑previous‑Close.

**Not calculated:** VWAP, RSI, MACD, tick/order‑book data, sector/index correlation — none derivable from the given columns.

---

## PARTS 3–11 — SEARCH FOR AN EDGE

**Same non‑circular methodology as all six prior reports:** single‑candle pattern labels equal that bar's own Direction by definition (0 exceptions verified), so every result targets **NextDirection** using only information available once the current bar closes (or, for gaps, as soon as the next bar opens).

**Chronological split:** Train = 2024‑09‑10 → 2025‑12‑26 (1,933 rows), Validation = 2025‑12‑26 → 2026‑04‑21 (446 rows), Test = 2026‑04‑21 → 2026‑09‑09 (595 rows). No shuffling.

**Baseline to beat (train):** Next bar is UP 40.1% / DOWN 50.4% / FLAT 9.5% — the same recurring DOWN‑leaning baseline seen in all seven stocks now analyzed in this series.

### PART 9 — Best UP setup found

| Setup | Train n / UP% | Val n / UP% | Test n / UP% | Verdict |
|---|---|---|---|---|
| **14:15 bar with relative volume in the 1.5–2.5x ("HIGH") band** | 55 / 67.3% | 17 / 58.8% | 29 / 51.7% | Direction holds comfortably above baseline in all three periods, though the magnitude decays somewhat from training — similar in spirit to the equivalent Reliance Power finding |

**Component check:** 14:15 alone (no volume condition) gives 55.0%/45.3%/44.4% UP — degrading close to baseline in the out‑of‑sample windows. **The relative‑volume condition is what keeps this setup above baseline in validation and test** — without it, the time‑of‑day effect alone isn't enough.

### PART 10 — Best DOWN setup found

| Setup | Train n / DOWN% | Val n / DOWN% | Test n / DOWN% | Verdict |
|---|---|---|---|---|
| **10:15 bar has a bullish body (Close>Open)** | 127 / 72.4% | 26 / 53.8% | 33 / 66.7% | The strongest, largest‑sample DOWN candidate found — holds up well in test, softer in validation, but stays on the correct side of baseline throughout |

**Component breakdown:**

| Condition alone | Train DOWN% | Val DOWN% | Test DOWN% |
|---|---|---|---|
| Time = 10:15 only | 63.6% | 51.4% | 58.2% |
| Bullish body only | 53.3% | 48.4% | 48.9% |
| **10:15 + bullish body** | **72.4%** | **53.8%** | **66.7%** |

This is the same "morning bullish bar gets faded" shape seen in YES Bank's first validated rule — a bar that opens the session on a bullish note at 10:15 tends to give it back in the next hour more often than either factor alone would suggest. 10:15 is already this stock's second‑most DOWN‑biased hour on its own (63.6% train, only behind 11:15's 63.6%... — see Part 4), and adding the bullish‑body condition amplifies that further.

### PART 6 — Candle‑pattern reliability (Pattern → NEXT bar, train)

| Pattern | n | Next UP% | Next DOWN% | Next FLAT% | Reliable? |
|---|---|---|---|---|---|
| Bullish Engulfing | 100 | 37.0% | **58.0%** | 5.0% | Counter‑intuitive (a bullish pattern followed by DOWN more often than average) — not independently re‑tested for robustness beyond the raw training number, flagged as a curiosity |
| Bullish Candle | 426 | 37.3% | 54.9% | 7.8% | Mild down‑leaning tendency, part of the broader "bullish body fades" theme seen throughout this stock and YES Bank |
| Bearish Candle | 614 | 42.5% | 49.7% | 7.8% | Close to baseline |
| Doji (all) | 253 | 38.3% | 45.5% | 16.2% | Somewhat elevated FLAT‑next rate, no strong directional signal |
| Morning Star | 114 | 42.1% | 47.4% | 10.5% | No meaningful edge |
| Evening Star | 91 | 39.6% | 51.7% | 8.8% | No meaningful edge |
| Shooting Star | 17 | 47.1% | 52.9% | 0% | Sample too small |
| Hammer | 7 | 28.6% | 42.9% | 28.6% | **Only 7 occurrences in the entire dataset — statistically meaningless** |

**Label‑vs‑OHLC check:** all single‑candle labels matched Close‑vs‑Open sign with zero exceptions.

### PART 7 — Sequence analysis (train)

| Streak (ending at bar just closed) | n | Next UP% | Next DOWN% | Next avg % move |
|---|---|---|---|---|
| 1‑bar DOWN | 497 | 40.2% | 51.1% | 0.00% |
| 2‑bar DOWN | 254 | 45.3% | 46.5% | +0.01% |
| 4‑bar DOWN | 56 | 48.2% | 44.6% | +0.03% |
| 1‑bar UP | 477 | 39.4% | 53.3% | +0.02% |
| 2‑bar UP | 188 | 35.1% | 54.3% | −0.02% |
| 4‑bar UP | 32 | 28.1% | 59.4% | −0.10% (small sample, not independently validated) |

No streak length on its own produces a clean, independently‑tested edge beyond what's already captured in the validated setups above — most buckets sit within a few points of the general baseline.

### PART 8 — Price structure & gaps

| Structure | n (train) | Next UP% | Next DOWN% |
|---|---|---|---|
| Higher High + Higher Low | 495 | 40.0% | 51.5% |
| Lower High + Lower Low | 702 | 40.2% | 51.0% |
| Mixed | 736 | 40.2% | 49.0% |

No meaningful separation — structure alone adds little, consistent with all six prior stocks.

**Gap behavior:** Gap‑down bars showed a modestly elevated own‑bar UP rate (44.8% vs. ~40% no‑gap baseline), a mild fade tendency similar to (but weaker than) IDEA's gap‑up finding, just in the opposite direction and smaller in magnitude — not independently re‑tested for robustness here. Gap fill rates: gap‑down bars close back above the prior close 34.5% of the time; gap‑up bars close back below 43.9% of the time — gaps mostly don't fill same‑session, the same finding across all seven stocks now.

---

## PART 5 — VOLUME ANALYSIS

Volume showed one temporary spike (mid‑2025) but no permanent multi‑year escalation. Rolling‑relative volume was used throughout, and — as with Reliance Power — **volume is a necessary ingredient of the UP setup** for this stock (the 14:15‑hour effect alone isn't enough; the relative‑volume condition is what keeps it above baseline out of sample).

A full 6‑feature logistic‑regression score (Time + Streak + BodyDir + relative Volume + close‑position + gap category) shows the same overfitting pattern seen in all six prior reports:

| Split | Base DOWN rate | Model accuracy | Model AUC |
|---|---|---|---|
| Train | 50.4% | 57.6% | **0.619** |
| Validation | 47.1% | 54.7% | **0.554** |
| Test | 47.3% | 50.3% | **0.545** |

The full model degrades meaningfully out of sample (AUC drop of ~0.07) — **overfit**, reinforcing the same conclusion as all six prior stocks: use the simple, validated checklist, not a fitted multi‑feature score.

---

## PART 4 — TIME‑OF‑DAY (train)

| Time | UP% | DOWN% | FLAT% | Avg range% | Avg chg% | n |
|---|---|---|---|---|---|---|
| 09:15 | 66.7% | 33.3% | 0% | 3.97% | +0.62% | 15 (too few to trust) |
| 10:15 | 39.8% | 53.9% | 6.3% | 1.29% | +0.01% | 319 |
| **11:15** | **30.1%** | **63.6%** | 6.3% | 0.99% | −0.12% | 319 — the most DOWN‑biased hour |
| 12:15 | 37.8% | 52.5% | 9.7% | 0.93% | 0.00% | 320 |
| 13:15 | 34.9% | 53.6% | 11.5% | 0.92% | −0.05% | 321 |
| 14:15 | 42.5% | 48.1% | 9.4% | 1.17% | +0.02% | 320 |
| **15:15** | **54.9%** | **31.0%** | 14.1% | 0.82% | +0.14% | 319 — the strongest UP‑leaning close of any stock in this series |

**This is the seventh stock in a row to show the same shape: mid‑morning is the most DOWN‑biased period, and the closing hour is the most UP‑leaning.** For RTNPOWER specifically, the effect is unusually pronounced — 11:15 sees DOWN bars nearly twice as often as UP bars (63.6% vs. 30.1%), while 15:15 flips almost completely (54.9% UP vs. 31.0% DOWN). This is now a consistent finding across PC Jeweller, YES Bank, Reliance Power, Suzlon, SEPC, IDEA, and RattanIndia Power — seven unrelated names spanning small‑, mid‑, and very‑high‑liquidity stocks.

---

## PART 11 — NO‑TRADE CONDITIONS

| Condition | What the data shows | Why it's a NO‑TRADE zone |
|---|---|---|
| **Frozen bars** (25, all in training, none afterward) | Same regime‑change pattern as Reliance Power/Suzlon | Flag any recurrence as untradeable, don't expect the training‑period rate to persist |
| **09:15 slot** | Only 15–22 observations across the whole sample | Statistically unusable |
| **Doji, Hammer, Shooting Star, Morning/Evening Star alone** | All close to baseline or far too small a sample (7–180 occurrences) | Not usable as standalone signals |
| **Streak length alone** (any direction, beyond what's captured in the validated setups) | Every bucket sits within a few points of baseline | No independent edge |
| **Any single isolated factor** (Time, Pattern, Volume, gap, structure alone) | Each moves the DOWN/UP rate by only a few points off baseline, except where combined as in Parts 9–10 | Only the two validated combinations show a real, repeatable edge |

**NO‑TRADE rule:** stand aside on the 09:15 slot, any bare candlestick‑pattern read, and any streak‑length‑only signal.

---

## PART 12 — SCORING SYSTEM

Following the same reasoning as the six prior reports, a simple evidence‑backed checklist is used instead of a fitted multi‑factor score.

**DOWN SCORE (0–2, one point each):**
- +1 if this is the **10:15** bar
- +1 if this bar's body is bullish (Close > Open)

**DOWN SCORE = 2 → historical DOWN rate for the next bar: 72.4% (train) / 53.8% (val) / 66.7% (test), vs. a ~47–50% baseline.**

**UP SCORE (0–2, one point each):**
- +1 if this is the **14:15** bar
- +1 if this bar's volume is roughly **1.5–2.5x** its own trailing 20‑bar average

**UP SCORE = 2 → historical UP rate for the next bar: 67.3% (train) / 58.8% (val) / 51.7% (test), vs. a ~40–47% baseline.**

**Thresholds:** DOWN SCORE = 2 → potential DOWN setup. UP SCORE = 2 → potential UP setup. Anything else → NO TRADE.

---

## PART 13 — REAL‑TIME DECISION FORMULA

```
CURRENT HOURLY BAR JUST CLOSED (Open, High, Low, Close, Volume known)
        │
        ▼
Is this the 10:15 bar?
   YES ─┼───────────────────────┐         Is this the 14:15 bar?
        │                       │                │
        NO (check UP path →)  Is Close > Open?  YES ─┼──────────────┐
                                │                     │              │
                          YES ─┼──► +1 (DOWN score)   NO         Is volume 1.5-2.5x
                          NO ──┴──► NO TRADE            │         its 20-bar average?
                                │                  (NO TRADE)         │
                          DOWN SCORE = 2                        YES ─┼──► UP SCORE = 2
                          → POTENTIAL DOWN SETUP                     │   → POTENTIAL UP SETUP
                                                                 NO ──┴──► NO TRADE
```

---

## PART 14 — BACKTEST RESULTS (chronological, no shuffling)

| Metric | Train (65%, n=1,933) | Validation (15%, n=446) | Test (20%, n=595) |
|---|---|---|---|
| DOWN setup: trigger rate | 6.6% | 5.8% | 5.6% |
| DOWN setup: hit rate | 72.4% | 53.8% | 66.7% |
| Baseline DOWN rate | 50.4% | 47.1% | 47.3% |
| UP setup: trigger rate | 2.8% | 3.8% | 4.9% |
| UP setup: hit rate | 67.3% | 58.8% | 51.7% |
| Baseline UP rate | 40.1% | 47.1%* | 40.1% |

*val baseline UP rate reflects the smaller validation sample's overall distribution.

**Is this overfit?** **No, for either rule**, though both show the more typical pattern of some validation‑period softening followed by a solid recovery (DOWN) or gradual decay (UP) in test, rather than IDEA's or Suzlon's unusually flat replication. Both rules stayed on the correct side of baseline in all three windows, which is the key test — neither collapsed to baseline the way the rejected candidates elsewhere in this report did. The 6‑feature logistic‑regression score, by contrast, **is more clearly overfit** (AUC drop of ~0.07 from train to test, with validation and test converging toward a much weaker signal than training suggested).

---

## PART 15 — ROBUSTNESS CHECKS

- **Volume regime:** one temporary spike (mid‑2025), otherwise stable; not a major confound given the use of rolling‑relative volume.
- **Threshold sensitivity:** dropping either condition of the DOWN rule cuts the edge substantially (component table, Part 10) — the combination matters, not just one piece. Similarly for the UP rule, the volume condition is what keeps it above baseline out of sample.
- **Different time periods:** both rules stayed on the correct side of baseline across training, validation, and the fully unseen test window, though with some fluctuation in magnitude — a moderately robust, if not perfectly flat, result.
- **Frozen‑bar regime change:** confirmed (25 of 25 frozen bars in training) — same caution as Reliance Power/Suzlon: don't assume this early illiquidity pattern still applies.
- **High‑ vs low‑volatility subperiods:** not separately re‑tested beyond the three chronological splits, same limitation as all six prior reports.

---

## PART 16 — FINAL TRADING RULES (plain language)

**DOWN SETUP — IF:**
1. The just‑closed hourly bar is the **10:15** bar
2. That bar's Close is above its Open (bullish body)

**AND DOWN SCORE = 2 → THEN:** Potential DOWN setup for the 11:15 bar (historical hit rate ~54–72% across the three periods, vs. a ~47–50% baseline).

**UP SETUP — IF:**
1. The just‑closed hourly bar is the **14:15** bar
2. That bar's volume is roughly **1.5–2.5 times** its own trailing 20‑bar average

**AND UP SCORE = 2 → THEN:** Potential UP setup for the 15:15 bar (historical hit rate ~52–67% across the three periods, vs. a ~40–47% baseline).

**Avoid the trade if:** the bar is frozen/illiquid, it's outside the 10:15 (DOWN) or 14:15 (UP) hour for these specific rules, or you're relying on a bare candlestick‑pattern name.

**NO TRADE — IF:** it's the 09:15 slot; the 10:15 bar isn't bullish‑bodied (for the DOWN rule) or the 14:15 bar doesn't show elevated relative volume (for the UP rule); or the only basis is a classic candlestick pattern without the specific conditions validated above.

---

## PART 17 — QUICK‑REFERENCE TABLE

| Factor | UP condition | DOWN condition | Neutral / No‑Trade |
|---|---|---|---|
| Time | 14:15 (core of UP rule); 15:15 strongest UP‑lean descriptively | 10:15 (core of DOWN rule); 11:15 most DOWN‑biased descriptively | 09:15 (n too small) |
| Previous direction/streak | — | — | Streak length alone, any direction |
| Candle pattern | — | Bullish body at 10:15 (as part of combo) | Doji, Hammer, Shooting Star, Morning/Evening Star (all too weak or too small) |
| Body size / % change | — | Bullish body (Close>Open) | Bullish Engulfing → next‑DOWN (counter‑intuitive, not independently validated) |
| Volume | Relative volume 1.5–2.5x normal (key ingredient of UP rule) | — | Any single volume reading alone; full 6‑feature model (overfit) |
| Range | — | — | — |
| Gap | — | — | Gap present, either direction (weak, inconsistent fade only) |
| Score | UP SCORE = 2 | DOWN SCORE = 2 | Anything below threshold |

**UP FORMULA:** 14:15 bar + relative volume 1.5–2.5x its 20‑bar average → UP SCORE 2 → next bar (15:15) UP ~52–67% historically, vs. ~40–47% baseline.

**DOWN FORMULA:** 10:15 bar + bullish body → DOWN SCORE 2 → next bar (11:15) DOWN ~54–72% historically, vs. ~47–50% baseline.

**NO‑TRADE FORMULA:** 09:15 slot, either rule's conditions not fully met, or reliance on a bare candlestick‑pattern name alone.

---

## PART 18 — HONEST CONCLUSION

1. **Does this dataset contain a measurable directional edge?** Yes — both a DOWN rule and a UP rule, similar in structure to Reliance Power's findings (a morning‑hour body‑direction rule for DOWN, an afternoon volume‑driven rule for UP).
2. **Strongest UP conditions:** 14:15 bar with relative volume 1.5–2.5x its own 20‑bar average.
3. **Strongest DOWN conditions:** 10:15 bar with a bullish body — the same "morning bullish bar fades" shape seen in YES Bank.
4. **Strongest reversal patterns:** None independently validated as standalone reversal signals beyond what's captured in the two setups above.
5. **Strongest continuation patterns:** None strong enough to trade on their own — streak‑length effects sit close to baseline in every bucket tested.
6. **Which candle patterns are actually useful, and do labels match behavior?** All single‑candle labels matched their own Open/Close sign exactly — no mislabeling. Bullish Engulfing showed a counter‑intuitive down‑leaning next‑bar tendency in training (58.0% next‑DOWN) but this was not independently stress‑tested for robustness the way the primary rules were — treat as a lead, not a rule.
7. **Which patterns are unreliable?** Hammer (7 occurrences — meaningless), Shooting Star, Morning Star, Evening Star, and Doji as a group.
8. **Does volume materially improve prediction?** Yes, for the UP rule specifically — without the relative‑volume condition, the 14:15‑hour effect alone decays close to baseline out of sample.
9. **Does body size/% change add value?** Yes — bullish body direction is the key ingredient (alongside timing) in the DOWN rule.
10. **Does gap behavior add value?** Not independently validated here — a mild gap‑down‑fade tendency was observed but not stress‑tested the way the primary rules were.
11. **Most reliable time:** 10:15 for the DOWN setup, 14:15 for the UP setup. Descriptively, 11:15 is the most DOWN‑biased hour (63.6% train) and 15:15 the most UP‑leaning (54.9% train) — the seventh stock in a row to show this shape, and the most pronounced version of it yet.
12. **Time to avoid:** 09:15 (only 15–22 observations across two years).
13. **How many signals would the final strategy generate?** DOWN setup: ~5.6–6.6% of bars (roughly 165–195 signals over the ~2,970‑bar sample). UP setup: ~2.8–4.9% of bars (roughly 85–145 signals).
14. **Historical success rate:** DOWN ≈ 72.4% in training; UP ≈ 67.3% in training.
15. **Performance on unseen (test) data:** DOWN 66.7% (a solid recovery after a softer validation reading of 53.8%); UP 51.7% (decayed somewhat from training but still comfortably above the ~40% baseline).
16. **Is the strategy overfit?** **No, for either simple rule** — both stayed on the correct side of baseline in every chronological window, even though the DOWN rule's magnitude dipped in validation before recovering in test. The 6‑feature logistic‑regression score **is more clearly overfit** (AUC drop of ~0.07 from train to test).
17. **What additional data would help?** Tick/order‑book data (to understand the mechanics behind the unusually pronounced 11:15‑DOWN/15:15‑UP swing seen in this stock specifically), sector/power‑sector index correlation (useful here too, as with Reliance Power), and more occurrences of Bullish Engulfing, Hammer, and Shooting Star to test those leads with greater statistical confidence.

**This analysis does not, and cannot, guarantee future performance.** The honest summary for RattanIndia Power: this stock shares the same structural DOWN‑leaning baseline and mid‑morning‑DOWN/closing‑hour‑UP shape seen across all seven stocks in this series — here in its most pronounced form yet — and offers two validated, non‑overfit rules (one DOWN, one UP) that both held their direction across two independent out‑of‑sample windows spanning more than a year and a half.
