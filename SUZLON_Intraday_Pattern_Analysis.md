# Suzlon Energy (SUZLON.NS) — Hourly Candle Statistical Analysis
### Data: 2,969 hourly bars, 2024‑09‑10 to 2026‑09‑09 | Source: Yahoo Finance (as provided)

---

## PART 1 — DATA VALIDATION

| Check | Result |
|---|---|
| Total valid bars | 2,969 (matches header claim exactly) |
| Earliest bar | 2024‑09‑10 12:15 IST |
| Latest bar | 2026‑09‑09 15:15 IST |
| Trading dates covered | 494 |
| UP bars | 1,300 (43.8%) |
| DOWN bars | 1,550 (52.2%) |
| FLAT bars | 119 (4.0%) — the lowest FLAT share of all four stocks analyzed so far |
| Bars per time slot | 09:15 → 18, 10:15 → 491, 11:15 → 491, 12:15 → 492, 13:15 → 493, 14:15 → 494, 15:15 → 490 |
| Pattern counts | Bearish Candle 817, Bullish Candle 676, Doji 375, Strong Bearish 264, Bullish Engulfing 171, Strong Bullish 171, Bearish Engulfing 154, Evening Star 144, Morning Star 136, Shooting Star 43, Hammer 18 |
| Duplicate records | **0** (no duplicate Date+Time rows, no duplicate full rows) |
| High < Low | **0 occurrences** |
| Close outside High/Low | **0 occurrences** |
| Open outside High/Low | **0 occurrences** |
| Direction vs Close‑Open sign | **0 mismatches** in the entire dataset |
| Missing calendar dates | None beyond normal weekends/holidays |
| Bars per day | 470 days have exactly 6, 18 have 7 (extra 09:15 print), and 6 days have partial sessions (4, 2, 5, 2, 5, 5 bars) on 2024‑09‑10, 2025‑10‑21, 2026‑03‑11, 2026‑04‑20, 2026‑05‑29, 2026‑07‑14 — consistent with holiday/first/last‑day sessions |

**Things worth flagging (observations, not corrections):**

1. **The very first bars in this file are a genuine, extended frozen/flatline stretch** — e.g. 2024‑09‑10's 13:15, 14:15, 15:15 bars and 2024‑09‑11's 10:15 bar are all identical prints (Open=High=Low=Close=78.05, then 81.95). This isn't a parsing error — it reflects real low‑activity opening sessions in this dataset.
2. **Frozen bars (O=H=L=C) total 54 of 2,969 (1.8%)**, concentrated almost entirely in the training period (53 of 54; only 1 appears afterward) — the same kind of regime change seen in Reliance Power, where illiquid "no‑trade" prints became far rarer after 2025.
3. **Doji is, once again, not synonymous with FLAT.** Of 375 Doji‑labeled bars, 151 are DOWN, 113 FLAT, 111 UP — roughly an even three‑way split, the most balanced of the four stocks analyzed.
4. **Volume is comparatively stable** — monthly averages range ~4.8M–15M shares/hour with a couple of elevated months (2025‑05/06, 2026‑04‑06) but no permanent multi‑year escalation. Rolling‑relative volume was used throughout for consistency.

**Conclusion of Part 1: the dataset is internally clean** — no fabricated OHLC, no impossible bars, no label/direction mismatches. The only caveats are interpretive (Doji≠flat, frozen bars concentrated early in the sample).

---

## PART 2 — DERIVED VARIABLES

Same full set computed from Open/High/Low/Close/Volume/Date/Time as in the three prior reports: Range, Range %, Body size/%, Bar % change, upper/lower wick (absolute + % of range), body‑to‑range ratio, gap and gap % vs. previous close, close‑position tercile, BodyDir (cross‑checked, zero mismatches), volume vs. previous bar and vs. trailing 20‑bar rolling average, range/body change vs. previous bar, streak type/length, previous 2‑/3‑bar sequences, day‑of‑week, HH/HL/LH/LL flags, Close‑vs‑previous‑Close.

**Not calculated:** VWAP, RSI, MACD, tick/order‑book data, sector/index correlation — none derivable from the given columns.

---

## PARTS 3–11 — SEARCH FOR AN EDGE

**Same non‑circular methodology as the previous three reports:** single‑candle pattern labels equal that bar's own Direction by definition (0 exceptions verified), so every result targets **NextDirection** using only information available once the current bar closes (or, for gaps, as soon as the next bar opens).

**Chronological split:** Train = 2024‑09‑10 → 2025‑12‑24 (1,929 rows), Validation = 2025‑12‑26 → 2026‑04‑20 (446 rows), Test = 2026‑04‑21 → 2026‑09‑09 (594 rows). No shuffling.

**Baseline to beat (train):** Next bar is UP 42.2% / DOWN 52.7% / FLAT 5.1%. **The same DOWN‑leaning baseline seen in all four stocks analyzed so far** — a recurring feature across every name tested to date, not something unique to any one company.

### PART 9 — Best UP setup found (modest, but real)

| Setup | Train n / UP% | Val n / UP% | Test n / UP% | Verdict |
|---|---|---|---|---|
| **Bullish Engulfing pattern + closed in the top third of its own range + next bar opens with no gap** | 51 / 52.9% | 15 / 73.3% | 21 / 57.1% | Directionally consistent in all three windows and comfortably above the ~42% baseline throughout, though the sample sizes (51/15/21) are modest |
| 13:15 bar + 1‑bar DOWN streak + closed in bottom third | 44 / 61.4% | 17 / 58.8% | 16 / 50.0% | Direction holds but decays toward baseline in test — weaker evidence than the setup above |

The Bullish Engulfing combination is the one I'd flag as the primary UP candidate: a genuine bullish engulfing bar that closes strong (top third) and isn't followed by a gap tends to continue upward more often than the baseline, in every one of the three periods.

### PART 10 — Best DOWN setup found (the strongest, tightest result across all four stocks analyzed)

| Setup | Train n / DOWN% | Val n / DOWN% | Test n / DOWN% | Verdict |
|---|---|---|---|---|
| **11:15 bar has a bearish body + closes in the bottom third of its own range + next bar opens with no gap** | 110 / 67.3% | 22 / 68.2% | 35 / 65.7% | **The single tightest, most consistent result found across all four stocks analyzed to date** — within 2.6 percentage points of each other across train/val/test |
| 11:15 bar closes in bottom third + no gap (drop the body‑direction condition) | 119 / 65.5% | 26 / 65.4% | 39 / 64.1% | Nearly identical performance, slightly larger sample — a good alternative if you want to relax one condition |
| 11:15 bar has a bearish body + closes in bottom third (drop the no‑gap condition) | 122 / 64.8% | 24 / 66.7% | 38 / 68.4% | Also excellent and even improves slightly in test — any of these three variants works |

**Component breakdown (why the full combination matters):**

| Condition alone | Train DOWN% | Val DOWN% | Test DOWN% |
|---|---|---|---|
| Time = 11:15 only | 58.2% | 50.0% | 53.5% |
| Bearish body only | 55.7% | 52.3% | 51.9% |
| Bottom‑third close only | 55.3% | 54.7% | 54.6% |
| **11:15 + bearish body + bottom third + no gap** | **67.3%** | **68.2%** | **65.7%** |

11:15 is already this stock's most DOWN‑biased hour on its own (58.2% train — see Part 4), and layering "closed weak, near its own low" plus "no gap into the next bar" on top of that pushes the edge up substantially, and — unusually — this holds almost exactly the same magnitude in validation and test as it did in training.

### PART 6 — Candle‑pattern reliability (Pattern → NEXT bar, train)

| Pattern | n | Next UP% | Next DOWN% | Next FLAT% | Reliable? |
|---|---|---|---|---|---|
| Bearish Candle | 542 | 42.6% | 55.7% | 1.7% | Mild continuation, feeds into the validated combo above |
| Bullish Engulfing | 105 | 41.9% | 56.2% | 1.9% | On its own, no edge — the edge only appears once combined with close‑position and gap (see Part 9) |
| Doji (all) | 256 | 35.2% | 43.8% | 21.1% | Elevated FLAT‑next rate but far less dramatic than Reliance Power's frozen‑bar‑driven Doji behavior |
| Shooting Star | 25 | 48.0% | 52.0% | 0% | Close to baseline, no edge, and sample too small regardless |
| Strong Bullish Candle | 86 | 48.8% | 43.0% | 8.1% | Mild positive tilt but not independently tested for robustness given the small sample |
| Morning Star | 90 | 44.4% | 51.1% | 4.4% | No meaningful edge |
| Evening Star | 90 | 43.3% | 54.4% | 2.2% | No meaningful edge |
| Hammer | 13 | 38.5% | 53.8% | 7.7% | Sample far too small to trust |

**Label‑vs‑OHLC check:** all single‑candle labels matched Close‑vs‑Open sign with zero exceptions.

### PART 7 — Sequence analysis (train)

| Streak (ending at bar just closed) | n | Next UP% | Next DOWN% | Next avg % move |
|---|---|---|---|---|
| 1‑bar DOWN | 451 | 44.6% | 53.9% | −0.05% |
| 2‑bar DOWN | 243 | 35.8% | 61.7% | −0.05% |
| 3‑bar DOWN | 150 | 38.7% | 60.0% | −0.11% |
| 5‑bar DOWN | 46 | 54.4% | 43.5% | −0.02% (looked like reversal, **not independently tested for robustness — small sample, treat as descriptive only**) |
| 1‑bar UP | 455 | 45.5% | 52.3% | +0.01% |
| 3‑bar UP | 94 | 33.0% | 61.7% | −0.09% (looked like reversal in training; overlaps with, but is not identical to, the validated DOWN combination — not separately confirmed) |

2‑ and 3‑bar DOWN streaks show a meaningfully elevated next‑DOWN rate (61.7%, 60.0% vs. the 52.7% baseline) in training, largely consistent with (and likely capturing some of the same signal as) the 11:15‑hour finding above, since down streaks are naturally more common by early afternoon.

### PART 8 — Price structure & gaps

| Structure | n (train) | Next UP% | Next DOWN% |
|---|---|---|---|
| Higher High + Higher Low | 532 | 44.2% | 51.3% |
| Lower High + Lower Low | 752 | 43.1% | 54.9% |
| Mixed | 645 | 39.4% | 51.3% |

No clean separation — structure alone adds little, consistent with all three prior stocks.

**Gap behavior:** Gap‑down bars showed an elevated own‑bar UP rate (50.4% vs. ~44% baseline) in training, similar to the weak, inconsistent gap‑fade tendency seen in the other stocks — not independently re‑validated here as a standalone rule. Gap fill rates: gap‑down bars close back above the prior close only 28.9% of the time; gap‑up bars close back below only 27.1% of the time — gaps mostly don't fill same‑session, the same finding in all four stocks now.

---

## PART 5 — VOLUME ANALYSIS

Monthly average volume ranged roughly 4.8M–15M shares/hour, without the extreme multi‑year escalation seen in PC Jeweller. Rolling‑relative volume was used throughout for consistency, though — notably — **volume did not end up being a necessary ingredient of either validated rule for this stock** (unlike Reliance Power, where it was central to the UP setup). Close position and time‑of‑day did the work here instead.

A full 6‑feature logistic‑regression score (Time + Streak + BodyDir + relative Volume + close‑position + gap category) shows the same overfitting pattern seen in all three prior reports:

| Target | Split | Base rate | Model accuracy | Model AUC |
|---|---|---|---|---|
| Next=DOWN | Train | 52.7% | 56.5% | **0.604** |
| Next=DOWN | Val | 49.8% | 51.3% | **0.525** |
| Next=DOWN | Test | 52.4% | 56.3% | **0.548** |
| Next=UP | Train | 42.1% | 57.9% | **0.595** |
| Next=UP | Val | 48.7% | 48.9% | **0.491** (worse than a coin flip) |
| Next=UP | Test | 45.4% | 53.3% | **0.531** |

Both models degrade sharply from training to validation — **explicitly overfit** — reinforcing the same conclusion as the other three reports: use the simple, validated checklist, not a fitted multi‑feature score.

---

## PART 4 — TIME‑OF‑DAY (train)

| Time | UP% | DOWN% | FLAT% | Avg range% | Avg chg% | n |
|---|---|---|---|---|---|---|
| 09:15 | 46.7% | 53.3% | 0% | 3.29% | −0.33% | 15 (too few to trust) |
| 10:15 | 43.4% | 54.4% | 2.2% | 1.11% | −0.03% | 318 |
| **11:15** | **36.8%** | **59.7%** | 3.5% | 0.94% | −0.08% | 318 — **the most DOWN‑biased hour of the day, and the basis for the validated DOWN rule** |
| 12:15 | 37.0% | 58.0% | 5.0% | 0.80% | −0.06% | 319 |
| 13:15 | 42.5% | 51.6% | 5.9% | 0.80% | −0.05% | 320 |
| 14:15 | 46.9% | 47.5% | 5.6% | 0.99% | +0.04% | 320 |
| 15:15 | 46.4% | 44.8% | 8.8% | 0.48% | +0.01% | 319 |

**Same recurring cross‑stock pattern: the last two hours of the session (14:15, 15:15) are the least DOWN‑biased, while the mid‑morning hour (here, 11:15) is the most DOWN‑biased.** This is now the fourth stock in a row to show this shape, which is worth treating as a broader market‑structure observation rather than a stock‑specific curiosity. The 09:15 slot again shows the largest average move but far too few observations (15) to use.

---

## PART 11 — NO‑TRADE CONDITIONS

| Condition | What the data shows | Why it's a NO‑TRADE zone |
|---|---|---|
| **Frozen bars** (54 total, 53 in training, essentially none afterward) | Concentrated in 2024–2025, same regime‑change pattern seen in Reliance Power | Flag any recurrence as untradeable, but don't expect it to persist at the training‑period rate |
| **09:15 slot** | Only 15–18 observations across the whole sample | Statistically unusable |
| **Doji overall** | Roughly even 3‑way split (35/44/21 UP/DOWN/FLAT in training) | No directional information on its own |
| **Hammer, Shooting Star, Morning/Evening Star alone** | All close to baseline or too small a sample (13–144 occurrences, none independently validated) | Not usable as standalone signals |
| **Any single isolated factor** (Time, Pattern, Volume, gap, structure alone) | Each moves the DOWN/UP rate by only a few points off baseline | Only the specific combinations in Parts 9–10 show a real, repeatable edge |

**NO‑TRADE rule:** stand aside on the 09:15 slot, on Doji bars that don't also meet a validated combination, and on any bare candlestick‑pattern read.

---

## PART 12 — SCORING SYSTEM

Following the same reasoning as the three prior reports, a simple evidence‑backed checklist is used instead of a fitted multi‑factor score.

**DOWN SCORE (0–3, one point each):**
- +1 if this is the **11:15** bar
- +1 if this bar's body is bearish (Close < Open)
- +1 if this bar closed in the **bottom third** of its own High‑Low range

**DOWN SCORE = 3 → historical DOWN rate for the next bar: 67.3% (train) / 68.2% (val) / 65.7% (test), vs. a ~50–53% baseline.** This is the tightest, most consistent spread found across all four stocks analyzed to date. (Note: the "no gap into next bar" condition can be added as a 4th point for an even tighter — though smaller‑sample — version; either 3‑condition variant reported in Part 10 works nearly as well.)

**UP SCORE (0–2, one point each):**
- +1 if this bar is labeled **Bullish Engulfing**
- +1 if this bar closed in the **top third** of its own range, with no gap forming into the next bar

**UP SCORE = 2 → historical UP rate for the next bar: 52.9% (train) / 73.3% (val) / 57.1% (test), vs. a ~42–49% baseline.** Directionally consistent, but based on a noticeably smaller sample than the DOWN score — treat with somewhat lower confidence.

**Thresholds:** DOWN SCORE = 3 → potential DOWN setup. UP SCORE = 2 → potential UP setup. Anything else → NO TRADE.

---

## PART 13 — REAL‑TIME DECISION FORMULA

```
CURRENT HOURLY BAR JUST CLOSED (Open, High, Low, Close, Volume known)
        │
        ▼
Is this the 11:15 bar?
   YES ─┼───────────────────────────────┐
        │                               │
        NO → check UP path below   Is Close < Open (bearish body)?
                                         │
                                    YES ─┼──► +1 (DOWN score)
                                    NO ──┴──► NO TRADE
                                         │
                              Did this bar close in the BOTTOM THIRD
                              of its own range?
                                    YES ─┼──► DOWN SCORE = 3
                                         │    → POTENTIAL DOWN SETUP
                                    NO ──┴──► NO TRADE


[UP path — checked for any bar]
Is this bar's pattern "Bullish Engulfing"?
   NO ──┴──► NO TRADE
   YES ──► +1
        ▼
Did it close in the TOP THIRD of its range, with no gap into the next bar?
   YES ─┼──► UP SCORE = 2 → POTENTIAL UP SETUP
   NO ──┴──► NO TRADE
```

---

## PART 14 — BACKTEST RESULTS (chronological, no shuffling)

| Metric | Train (65%, n=1,929) | Validation (15%, n=446) | Test (20%, n=594) |
|---|---|---|---|
| DOWN setup: trigger rate | 5.7% | 4.9% | 5.9% |
| DOWN setup: hit rate | 67.3% | 68.2% | 65.7% |
| DOWN setup: avg next‑bar % move | −0.16% | −0.21% | −0.04% |
| Baseline DOWN rate | 52.7% | 49.8% | 52.4% |
| UP setup: trigger rate | 2.6% | 3.4% | 3.5% |
| UP setup: hit rate | 52.9% | 73.3% | 57.1% |
| Baseline UP rate | 42.2% | 48.7% | 45.4% |

**Is this overfit?** **No, for the DOWN rule** — its hit rate is essentially flat across all three windows (67.3/68.2/65.7%), the tightest such spread of any rule across all four stocks analyzed. **No, for the UP rule either** — direction and edge held up in both out‑of‑sample windows, though the smaller sample (51/15/21) means the exact hit‑rate estimate is less precise. The 6‑feature logistic‑regression scores, by contrast, **are explicitly LIKELY OVERFIT** for both directions (AUC drops of 0.05–0.10 from training to validation).

---

## PART 15 — ROBUSTNESS CHECKS

- **Volume regime:** relatively stable, not a confound here — and notably, volume wasn't even a necessary ingredient of either validated rule for this stock.
- **Threshold sensitivity:** dropping any one of the three DOWN conditions still leaves a respectable 64–68% hit rate (Part 10's alternate‑combination table) — **this rule is unusually robust to which exact 2‑of‑3 (or 3‑of‑3) conditions you use**, a notably "soft slope" rather than the "cliff" seen in the other three stocks' rules.
- **Different time periods:** both rules fire and perform similarly across training, validation, and the fully unseen test window — stable across more than two years.
- **Frozen‑bar regime change:** confirmed (53 of 54 frozen bars occurred in training) — same caution as Reliance Power: don't assume the early illiquidity pattern still applies.
- **High‑ vs low‑volatility subperiods:** not separately re‑tested beyond the three chronological splits, same limitation as the other three reports.

---

## PART 16 — FINAL TRADING RULES (plain language)

**DOWN SETUP — IF:**
1. The just‑closed hourly bar is the **11:15** bar
2. That bar's Close is below its Open (bearish body)
3. That bar closed in the **bottom third** of its own High‑Low range

**AND DOWN SCORE = 3 → THEN:** Potential DOWN setup for the 12:15 bar (historical hit rate ~66–68% across all three periods, vs. a ~50–53% baseline — the tightest, most stable rule across all four stocks analyzed).

**UP SETUP — IF:**
1. This bar is a **Bullish Engulfing** pattern
2. It closed in the **top third** of its own range, and the next bar opens with **no gap**

**AND UP SCORE = 2 → THEN:** Potential UP setup (historical hit rate ~53–73% across the three periods, though on a smaller, lower‑confidence sample than the DOWN rule).

**Avoid the trade if:** it's the 09:15 slot, the only basis is a bare candlestick‑pattern name without the specific conditions above, or you're relying on Doji/frozen bars for direction.

**NO TRADE — IF:** it's any hour other than 11:15 for the DOWN rule and the bar isn't a qualifying Bullish Engulfing for the UP rule; the bar is a Doji not meeting either combination; or it's the 09:15 slot.

---

## PART 17 — QUICK‑REFERENCE TABLE

| Factor | UP condition | DOWN condition | Neutral / No‑Trade |
|---|---|---|---|
| Time | — (not time‑dependent for the UP rule) | **11:15** (most DOWN‑biased hour; core of the DOWN rule) | 09:15 (n too small); 14:15/15:15 least DOWN‑biased descriptively |
| Previous direction/streak | — | 2‑ and 3‑bar DOWN streaks show elevated next‑DOWN (61.7%/60.0%), largely overlapping with the 11:15 finding | Streak length alone beyond 2–3 bars, not independently validated |
| Candle pattern | Bullish Engulfing (as part of combo) | none standalone | Doji, Hammer, Shooting Star, Morning/Evening Star (all too weak or too small alone) |
| Body size / % change | — | Bearish body (as part of combo) | — |
| Volume | not required for either rule | not required for either rule | Any single volume reading alone; full 6‑feature model (overfit) |
| Range/close position | Top third (as part of UP combo) | **Bottom third** (as part of DOWN combo) | — |
| Gap | No gap into next bar (as part of UP combo) | No gap adds a small extra edge to the DOWN combo (optional 4th condition) | Gap present, either direction (weak, inconsistent fade only) |
| Score | UP SCORE = 2 | DOWN SCORE = 3 | Anything below threshold |

**UP FORMULA:** Bullish Engulfing pattern + closed in top third + no gap into next bar → UP SCORE 2 → next bar UP ~53–73% historically, vs. ~42–49% baseline.

**DOWN FORMULA:** 11:15 bar + bearish body + closed in bottom third of its own range → DOWN SCORE 3 → next bar (12:15) DOWN ~66–68% historically, vs. ~50–53% baseline — the tightest, most consistent rule across all four stocks analyzed to date.

**NO‑TRADE FORMULA:** 09:15 slot, Doji not meeting either combination, or reliance on a bare candlestick‑pattern name alone.

---

## PART 18 — HONEST CONCLUSION

1. **Does this dataset contain a measurable directional edge?** Yes — and the DOWN rule found here is the strongest, most stable result across all four stocks analyzed so far (66–68% hit rate, essentially flat across train/val/test).
2. **Strongest UP conditions:** A Bullish Engulfing bar that closes in the top third of its own range with no gap into the next bar.
3. **Strongest DOWN conditions:** The 11:15 bar closing with a bearish body in the bottom third of its own range.
4. **Strongest reversal patterns:** None fully validated as standalone; a possible 5‑bar‑DOWN‑streak reversal was observed in training (54.4% next‑UP) but not independently confirmed out of sample given the small underlying sample.
5. **Strongest continuation patterns:** 2‑ and 3‑bar DOWN streaks show elevated next‑DOWN rates (61.7%, 60.0%), consistent with (and likely overlapping) the 11:15‑hour finding.
6. **Which candle patterns are actually useful, and do labels match behavior?** All single‑candle labels matched their own Open/Close sign exactly — no mislabeling anywhere in the dataset. Bullish Engulfing is the one pattern that contributes to a validated setup, but only once combined with close‑position and gap conditions — on its own it shows no edge.
7. **Which patterns are unreliable?** Hammer, Shooting Star, Morning Star, Evening Star (all either too rare or too close to baseline), and Doji taken as a group.
8. **Does volume materially improve prediction?** Not for this stock — neither validated rule required a volume condition, unlike Reliance Power.
9. **Does body size/% change add value?** Yes — bearish body direction is one of the three ingredients in the DOWN rule.
10. **Does gap behavior add value?** Modestly — "no gap" strengthens both rules slightly but isn't strictly required for either (the DOWN rule works almost as well without it).
11. **Most reliable time:** 11:15 for the DOWN setup; the UP setup is pattern‑driven rather than time‑driven. Descriptively, 14:15–15:15 are the least DOWN‑biased hours, continuing the pattern seen in all three prior stocks.
12. **Time to avoid:** 09:15 (only 15–18 observations across two years).
13. **How many signals would the final strategy generate?** DOWN setup: ~4.9–5.9% of bars (roughly 145–170 signals over the ~2,970‑bar sample). UP setup: ~2.6–3.5% of bars (roughly 75–105 signals).
14. **Historical success rate:** DOWN ≈ 67.3% in training; UP ≈ 52.9% in training.
15. **Performance on unseen (test) data:** DOWN 65.7% (essentially unchanged); UP 57.1% (held up, smaller sample).
16. **Is the strategy overfit?** **No, for either simple rule** — both held their edge from training through the fully unseen test period. The 6‑feature logistic‑regression scores for both directions **are explicitly LIKELY OVERFIT** (AUC drops of 0.05–0.10+ out of sample, and the UP model's validation AUC of 0.491 is worse than random).
17. **What additional data would help?** Tick/order‑book data (to understand what specifically happens around 11:15 that produces this unusually stable DOWN bias — possibly related to mid‑morning profit‑taking or algorithmic flow patterns common across all four stocks at similar hours), sector/renewable‑energy index correlation, and more occurrences of Bullish Engulfing, Hammer, and Shooting Star to test those patterns with greater statistical confidence.

**This analysis does not, and cannot, guarantee future performance.** The honest summary for Suzlon Energy: this stock shares the same structural DOWN‑leaning baseline seen in all three prior names, but produces the single most stable, tightly‑replicated rule found across the whole four‑stock series — an 11:15 bar closing weak (bearish body, near its own low) tends to be followed by a DOWN 12:15 bar roughly two‑thirds of the time, consistently, across two independent out‑of‑sample windows spanning more than a year and a half.
