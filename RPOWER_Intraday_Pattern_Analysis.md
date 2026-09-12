# Reliance Power (RPOWER.NS) — Hourly Candle Statistical Analysis
### Data: 2,988 hourly bars, 2024‑09‑10 to 2026‑09‑09 | Source: Yahoo Finance (as provided)

---

## PART 1 — DATA VALIDATION

| Check | Result |
|---|---|
| Total valid bars | 2,988 (matches header claim exactly) |
| Earliest bar | 2024‑09‑10 12:15 IST |
| Latest bar | 2026‑09‑09 15:15 IST |
| Trading dates covered | 494 |
| UP bars | 1,183 (39.6%) |
| DOWN bars | 1,504 (50.3%) |
| FLAT bars | 301 (10.1%) |
| Bars per time slot | 09:15 → 35, 10:15 → 491, 11:15 → 491, 12:15 → 492, 13:15 → 493, 14:15 → 494, 15:15 → 492 |
| Pattern counts | Bearish Candle 884, Bullish Candle 614, Doji 500, Strong Bearish 250, Strong Bullish 157, Bearish Engulfing 143, Bullish Engulfing 141, Morning Star 133, Evening Star 119, Shooting Star 31, Hammer 16 |
| Duplicate records | **0** (no duplicate Date+Time rows, no duplicate full rows) |
| High < Low | **0 occurrences** |
| Close outside High/Low | **0 occurrences** |
| Open outside High/Low | **0 occurrences** |
| Direction vs Close‑Open sign | **0 mismatches** in the entire dataset |
| Missing calendar dates | None beyond normal weekends/holidays |
| Bars per day | 455 days have exactly 6, 35 have 7 (extra 09:15 print), and 4 days have partial sessions (4, 2, 2, 5 bars) on 2024‑09‑10, 2025‑10‑21, 2026‑04‑20, 2026‑08‑06 — consistent with holiday/first/last‑day sessions |

**Things worth flagging (observations, not corrections):**

1. **Frozen bars (O=H=L=C) are common here — 210 of 2,988 bars (7.0%)**, closer to PC Jeweller's illiquidity profile than YES Bank's. Average volume on frozen bars is ~634K vs. the dataset average of ~4.9M.
2. **Frozen bars are entirely a 2024–2025 phenomenon.** All 210 frozen bars fall in the training window (10.8% of training bars); **zero** occur in either the validation or test window. This is a real, dramatic change in the stock's trading behavior over time — RPOWER stopped printing "no‑trade" bars after roughly late 2025 — and it means any no‑trade rule built on frozen‑bar persistence from the early data should **not** be assumed to still apply going forward.
3. **Doji is once again not synonymous with "no movement."** Of 500 Doji‑labeled bars, roughly 40% are FLAT, the rest split between DOWN/UP.
4. **Volume did not undergo the extreme multi‑year escalation seen in PC Jeweller** — monthly averages ranged roughly ₹1.4M–15M shares/hour, with two elevated months (2025‑05/06) rather than a permanent 50x structural shift. Still used the rolling‑relative volume measure throughout for consistency.

**Conclusion of Part 1: the dataset is internally clean** — no fabricated OHLC, no impossible bars, no label/direction mismatches. The only real caveat is that the stock's "quiet/frozen" behavior essentially disappeared after the training period — a genuine regime change, not a data error.

---

## PART 2 — DERIVED VARIABLES

Same full set computed from Open/High/Low/Close/Volume/Date/Time as in the two prior reports: Range, Range %, Body size/%, Bar % change, upper/lower wick (absolute + % of range), body‑to‑range ratio, gap and gap % vs. previous close, close‑position tercile, BodyDir (cross‑checked, zero mismatches), volume vs. previous bar and vs. trailing 20‑bar rolling average, range/body change vs. previous bar, streak type/length, previous 2‑/3‑bar sequences, day‑of‑week, HH/HL/LH/LL flags, Close‑vs‑previous‑Close.

**Not calculated:** VWAP, RSI, MACD, tick/order‑book data, sector/index correlation — none derivable from the given columns.

---

## PARTS 3–11 — SEARCH FOR AN EDGE

**Same non‑circular methodology as before:** single‑candle pattern labels equal that bar's own Direction by definition (0 exceptions verified), so every result targets **NextDirection** — the direction of the following hourly bar, using only information known once the current bar closes (or, for gaps, known as soon as the next bar opens).

**Chronological split:** Train = 2024‑09‑10 → 2025‑12‑26 (1,942 rows), Validation = 2025‑12‑26 → 2026‑04‑21 (448 rows), Test = 2026‑04‑21 → 2026‑09‑09 (598 rows). No shuffling.

**Baseline to beat (train):** Next bar is UP 38.7% / DOWN 48.5% / FLAT 12.9%. **Same structural DOWN‑leaning pattern seen in the other two stocks** — this appears to be a general feature of Indian small/mid‑cap intraday data across all three names analyzed so far, not something specific to any one company.

### PART 9 — Best UP setup found (this one held up unusually well)

| Setup | Train n / UP% | Val n / UP% | Test n / UP% | Verdict |
|---|---|---|---|---|
| **14:15 bar + relative volume in the 1.5–2.5x‑of‑normal ("HIGH") band** | 58 / 51.7% | 22 / 68.2% | 28 / 64.3% | **Strong and directionally consistent — the edge actually strengthens out of sample rather than decaying**, the best UP setup found across all three stocks analyzed to date |
| 4+ consecutive DOWN bars + relative volume in the 0.5–1x ("normal‑low") band | 62 / 50.0% | 16 / 50.0% | 18 / 61.1% | A secondary, weaker mean‑reversion‑after‑exhaustion signal — smaller sample, still directionally consistent |

**Component breakdown (why volume matters here, unlike in PC Jeweller/YES Bank):**

| Condition alone | Train UP% | Val UP% | Test UP% |
|---|---|---|---|
| Time = 14:15 only | 38.4% | 60.0% | 60.6% |
| Relative volume "HIGH" only | 40.4% | 50.0% | 45.5% |
| **14:15 + relative volume HIGH** | **51.7%** | **68.2%** | **64.3%** |

Interesting nuance: the 14:15 hour alone already shows a strong late‑period UP lean (60%+ in val/test) — this may partly reflect the same "closing‑hours‑lean‑up" pattern seen across all three stocks (see Part 4). Adding the volume condition sharpens it further and gives the strongest, most stable signal found in any of the three reports so far.

### PART 10 — Best DOWN setup found

| Setup | Train n / DOWN% | Val n / DOWN% | Test n / DOWN% | Verdict |
|---|---|---|---|---|
| **10:15 bar has a bearish body (Close<Open) + next bar opens with no gap** | 111 / 59.5% | 33 / 60.6% | 54 / 59.3% | **Remarkably stable — within 1.3 points of each other across all three periods, with a healthy sample size in every window** |
| 3‑bar DOWN streak + labeled "Bearish Candle" (no time restriction — generalizes across the whole day) | 83 / 61.4% | 24 / 54.2% | 28 / 53.6% | Also holds up, slightly weaker in the later periods, but useful because it doesn't depend on a specific hour |

**Component breakdown for the primary DOWN rule:**

| Condition alone | Train DOWN% | Val DOWN% | Test DOWN% |
|---|---|---|---|
| Time = 10:15 only | 53.9% | 54.1% | 65.3% |
| Bearish body only | 52.7% | 56.5% | 51.7% |
| No gap only | 45.8% | 54.4% | 51.7% |
| 10:15 + bearish body | 56.7% | 59.6% | 59.7% |
| **10:15 + bearish body + no gap** | **59.5%** | **60.6%** | **59.3%** |

Same story as the other two stocks: each factor alone gives a modest lift, but the full combination is both stronger and — this time — unusually *stable* rather than decaying from train to test.

### PART 6 — Candle‑pattern reliability (Pattern → NEXT bar, train)

| Pattern | n | Next UP% | Next DOWN% | Next FLAT% | Reliable? |
|---|---|---|---|---|---|
| Bearish Candle | 543 | 42.9% | 53.8% | 3.3% | Mild continuation, part of the validated combo above |
| Doji (all) | 398 | 22.6% | 32.4% | **45.0%** | Strongly FLAT‑leaning in training — but this is driven by the frozen‑bar cluster (see Part 1) that vanished after training; **do not expect this in current data** |
| Shooting Star | 17 | 29.4% | 70.6% | 0% | **The only textbook reversal pattern that held its direction across all three periods** (train 70.6% DOWN, val 57.1% DOWN, test 57.1% DOWN) — genuinely the pattern behaving as its name suggests, but the sample (17/7/7) is too small to trade with confidence; a promising lead for a longer dataset, not yet a rule |
| Morning Star | 83 | 33.7% | 62.7% | 3.6% | Looked strongly bearish in training (counter to the textbook bullish‑reversal story) but **completely reversed in validation** (80% UP) — reject |
| Evening Star | 77 | 46.8% | 53.3% | 0% | Close to baseline, no real edge |
| Hammer | 10 | 60.0% | 30.0% | 10.0% | Sample far too small (10 total) |

**Label‑vs‑OHLC check:** all single‑candle labels matched Close‑vs‑Open sign with zero exceptions.

### PART 7 — Sequence analysis (train)

| Streak (ending at bar just closed) | n | Next UP% | Next DOWN% | Next avg % move |
|---|---|---|---|---|
| 1‑bar DOWN | 446 | 44.4% | 51.6% | +0.05% |
| 2‑bar DOWN | 230 | 41.7% | 55.2% | +0.17% |
| 3‑bar DOWN | 127 | 40.2% | 54.3% | −0.04% |
| 5‑bar DOWN | 38 | 47.4% | 52.6% | −0.09% |
| 1‑bar UP | 440 | 40.7% | 55.0% | 0.00% |
| 2‑bar UP | 179 | 40.2% | 55.9% | −0.05% |
| **1‑bar FLAT** | 72 | 26.4% | 27.8% | +0.08% (45.8% stayed FLAT — **but this collapses almost entirely to near‑baseline directional outcomes in val/test**, see Part 11) |

No streak length on its own produces a clean, tradeable edge beyond what's already captured in the validated combinations above.

### PART 8 — Price structure & gaps

| Structure | n (train) | Next UP% | Next DOWN% |
|---|---|---|---|
| Higher High + Higher Low | 470 | 39.6% | 53.6% |
| Lower High + Lower Low | 700 | 43.6% | 51.7% |
| Mixed | 772 | 33.7% | 42.4% |

No clean separation — structure alone adds little, consistent with the other two stocks.

**Gap fill rates (train):** gap‑down bars closed back above the prior close only 28.7% of the time; gap‑up bars closed back below only 34.5% of the time — gaps mostly don't fill same‑session, matching PC Jeweller and YES Bank.

---

## PART 5 — VOLUME ANALYSIS

Monthly average volume ranged ~1.4M–15M shares/hour with two elevated months, but no permanent multi‑year escalation like PC Jeweller. Rolling‑relative volume was used throughout for consistency and comparability across the three reports.

**This is the one stock of the three where volume genuinely contributes to a validated setup** — the 14:15 + "HIGH relative volume" combination is the strongest UP signal found across all three analyses, and it held up (in fact strengthened) out of sample. That said, a full 6‑feature logistic‑regression score built from Time + Streak + BodyDir + relative Volume + close‑position + gap category shows the same overfitting pattern as the other two stocks:

| Target | Split | Base rate | Model accuracy | Model AUC |
|---|---|---|---|---|
| Next=DOWN | Train | 48.5% | 59.4% | **0.630** |
| Next=DOWN | Val | 53.6% | 54.2% | **0.526** |
| Next=DOWN | Test | 53.9% | 57.1% | **0.590** |
| Next=UP | Train | 38.7% | 61.8% | **0.610** |
| Next=UP | Val | 42.9% | 52.5% | **0.506** |
| Next=UP | Test | 40.2% | 58.0% | **0.516** |

Both full models degrade sharply out of sample (AUC drops of ~0.10–0.13) — **explicitly overfit**, and not recommended. The simple, hand‑picked combinations above (which happened to include volume for the UP case) are the better‑evidenced approach.

---

## PART 4 — TIME‑OF‑DAY (train)

| Time | UP% | DOWN% | FLAT% | Avg range% | Avg chg% | n |
|---|---|---|---|---|---|---|
| 09:15 | 55.6% | 40.7% | 3.7% | 4.78% | +1.35% | 27 (too few to trust) |
| 10:15 | 42.9% | 49.2% | 7.8% | 1.65% | +0.03% | 319 |
| 11:15 | 37.1% | 54.1% | 8.8% | 1.30% | −0.01% | 318 |
| 12:15 | 39.5% | 49.5% | 11.0% | 1.23% | +0.03% | 319 |
| 13:15 | 37.5% | 49.4% | 13.1% | 1.11% | +0.01% | 320 |
| 14:15 | 35.0% | 49.7% | 15.3% | 1.22% | −0.07% | 320 |
| 15:15 | 38.2% | 39.8% | 21.9% | 0.61% | +0.01% | 319 |

**Same cross‑stock pattern as PC Jeweller and YES Bank: 15:15 (the closing hour) has the lowest DOWN percentage of the day, and 11:15 is the most DOWN‑biased mid‑session hour.** This consistent "last hour leans less bearish" signature across three unrelated stocks is itself worth noting as a broader market‑structure observation, though I have not tested whether it holds beyond these three names. 09:15 again shows by far the largest range/move but far too few observations (27) to use.

---

## PART 11 — NO‑TRADE CONDITIONS

| Condition | What the data shows | Why it's a NO‑TRADE zone |
|---|---|---|
| **Frozen bars** (210 in training, 0 in val/test) | Persisted heavily in 2024–2025, then vanished | Flag any frozen bar as untradeable if it recurs, but don't rely on the training‑period FLAT‑streak persistence statistics (below) as a forward‑looking rule — the regime that produced them appears to be over |
| **FLAT streak ≥2 bars** | Train: 73–89% chance of staying FLAT (looked like a strong, exploitable no‑trade signal) | **Failed to replicate**: val/test FLAT‑streak samples are almost nonexistent (0–2 observations) because frozen bars stopped occurring — treat the training‑period persistence rate as descriptive history, not a current rule |
| **Doji overall** | 45% FLAT in training, driven by the frozen‑bar cluster | Same caveat as above — expect this to be less true going forward |
| **09:15 slot** | Only 27–35 observations across the whole sample | Statistically unusable |
| **Morning Star, Evening Star, Hammer alone** | Morning Star reversed sign between train/val; Evening Star showed no edge; Hammer has only 16 total occurrences | Not usable as standalone signals |
| **Any single isolated factor** (Time, Pattern, Volume, gap, structure alone) | Each moves the DOWN/UP rate by only a few points off baseline | Only the specific combinations in Parts 9–10 show a real, repeatable edge |

**NO‑TRADE rule:** stand aside on Doji bars that don't also meet a validated combination, the 09:15 slot, any bare candlestick‑pattern read (including Shooting Star, despite its promising‑looking consistency — the sample is still only 17/7/7), and don't assume the old FLAT‑persistence behavior still applies.

---

## PART 12 — SCORING SYSTEM

Following the same reasoning as the two prior reports (the full logistic‑regression model overfits), a simple evidence‑backed checklist is used instead of a weighted formula.

**DOWN SCORE (0–3, one point each):**
- +1 if this is the **10:15** bar
- +1 if this bar's body is bearish (Close < Open)
- +1 if the *next* bar opens with **no gap** vs. this bar's close

**DOWN SCORE = 3 → historical DOWN rate for the next bar: 59.5% (train) / 60.6% (val) / 59.3% (test), vs. a ~48–54% baseline.** The tightest, most stable spread of the three stocks analyzed.

**UP SCORE (0–2, one point each):**
- +1 if this is the **14:15** bar
- +1 if this bar's volume is roughly **1.5–2.5x** its own trailing 20‑bar average ("high but not spike" relative volume)

**UP SCORE = 2 → historical UP rate for the next bar: 51.7% (train) / 68.2% (val) / 64.3% (test), vs. a ~38–43% baseline.** This is the strongest UP signal found across all three stocks analyzed — it didn't just hold up, it strengthened out of sample.

**Thresholds:** DOWN SCORE = 3 → potential DOWN setup. UP SCORE = 2 → potential UP setup. Anything else → NO TRADE.

---

## PART 13 — REAL‑TIME DECISION FORMULA

```
CURRENT HOURLY BAR JUST CLOSED (Open, High, Low, Close, Volume known)
        │
        ▼
Is this bar frozen (O=H=L=C)? → YES: NO TRADE (no information)
        │ NO
        ▼
Is this the 10:15 bar?
   YES ─┼─────────────────────────────┐            Is this the 14:15 bar?
        │                             │                    │
        NO                    Is Close < Open?        YES ─┼──────────────┐
   (check UP path →)                 │                     │              │
                              YES ──┼──► +1 (DOWN score)   NO         Is volume 1.5-2.5x
                              NO ───┴──► NO TRADE           │         its 20-bar average?
                                     │                (NO TRADE)          │
                              Does next bar open                    YES ─┼──► UP SCORE = 2
                              with NO GAP?                                │   → POTENTIAL UP SETUP
                              YES ─┼──► DOWN SCORE = 3                    │
                                   │    → POTENTIAL DOWN SETUP       NO ──┴──► NO TRADE
                              NO ──┴──► NO TRADE
```

---

## PART 14 — BACKTEST RESULTS (chronological, no shuffling)

| Metric | Train (65%, n=1,942) | Validation (15%, n=448) | Test (20%, n=598) |
|---|---|---|---|
| DOWN setup: trigger rate | 5.7% | 7.4% | 9.0% |
| DOWN setup: hit rate | 59.5% | 60.6% | 59.3% |
| DOWN setup: avg next‑bar % move | −0.12% | −0.35% | −0.07% |
| Baseline DOWN rate | 48.5% | 53.6% | 53.9% |
| UP setup: trigger rate | 3.0% | 4.9% | 4.7% |
| UP setup: hit rate | 51.7% | 68.2% | 64.3% |
| Baseline UP rate | 38.7% | 42.9% | 40.2% |

**Is this overfit?** **No, for either rule.** The DOWN rule's hit rate is essentially flat across all three windows (59.5/60.6/59.3%). The UP rule's hit rate actually *improves* from train to validation/test (51.7% → 68.2% → 64.3%) — the opposite of an overfitting signature, though it does mean the training‑period estimate may understate how well the rule has performed recently, and there's no guarantee that improvement continues. The 6‑feature logistic‑regression scores, in contrast, **are explicitly LIKELY OVERFIT** for both directions (AUC drops of 0.10+ from train to validation).

---

## PART 15 — ROBUSTNESS CHECKS

- **Volume regime:** relatively stable (no extreme multi‑year drift), so the rolling‑relative volume measure and the UP rule built on it are on solid footing.
- **Threshold sensitivity:** loosening the DOWN rule to any 2 of its 3 conditions drops the hit rate to 51–57% (component table, Part 10) — again a "cliff," not a smooth "slope," but the full combination still replicated cleanly out of sample.
- **Different time periods:** both rules fire and perform similarly (DOWN) or improve (UP) across the training, validation, and fully unseen test windows — genuinely stable across more than two years for this stock.
- **Frozen‑bar regime change:** explicitly confirmed as a structural break (210 frozen bars in training, zero afterward) — any rule that implicitly depended on illiquidity clustering (like the FLAT‑streak persistence numbers) should not be trusted going forward, and neither of the two rules recommended here depends on it.
- **High‑ vs low‑volatility subperiods:** not separately re‑tested beyond the three chronological splits — same limitation noted in the other two reports.

---

## PART 16 — FINAL TRADING RULES (plain language)

**DOWN SETUP — IF:**
1. The just‑closed hourly bar is the **10:15** bar
2. That bar's Close is below its Open (bearish body)
3. The next bar opens with **no gap** vs. this bar's close

**AND DOWN SCORE = 3 → THEN:** Potential DOWN setup for the 11:15 bar (historical hit rate ~59–61% across all three periods, vs. a ~48–54% baseline).

**UP SETUP — IF:**
1. The just‑closed hourly bar is the **14:15** bar
2. That bar's volume is roughly **1.5–2.5 times** its own trailing 20‑bar average

**AND UP SCORE = 2 → THEN:** Potential UP setup for the 15:15 bar (historical hit rate 52–68% across the three periods — the strongest, most encouraging UP signal found across all three stocks analyzed, though based on a modest ~3–5% trigger rate).

**Avoid the trade if:** the bar is frozen/illiquid, it's outside the 10:15 (DOWN) or 14:15 (UP) hour for these specific rules, or you're relying on a bare candlestick‑pattern name (including Shooting Star, whose direction held up but on too small a sample to trust yet).

**NO TRADE — IF:** the bar is frozen; it's the 09:15 slot; it's a Doji not meeting the DOWN combination; or the only basis is a classic candlestick pattern (Morning Star, Evening Star, Hammer) without the specific conditions validated above.

---

## PART 17 — QUICK‑REFERENCE TABLE

| Factor | UP condition | DOWN condition | Neutral / No‑Trade |
|---|---|---|---|
| Time | 14:15 (as part of the UP combo); 15:15 descriptively least‑DOWN | 10:15 (as part of the DOWN combo); 11:15 most DOWN‑biased | 09:15 (n too small) |
| Previous direction/streak | 4+ bar DOWN streak + normal‑low volume (secondary, weaker) | 3‑bar DOWN streak + Bearish Candle (works without a time restriction) | Streak length alone, any direction |
| Candle pattern | none standalone | Bearish Candle (as part of combo) | Morning Star, Evening Star, Hammer (unreliable/too small); Shooting Star (promising but n too small) |
| Body size / % change | — | Bearish body (Close<Open) | — |
| Volume | Relative volume 1.5–2.5x of normal (key ingredient of the UP rule) | — | Any single volume reading alone; full 6‑feature model (overfit) |
| Range | — | — | — |
| Gap | — | No gap into next bar | Gap present, either direction (weak, inconsistent fade only) |
| Sequence | — | — | FLAT streaks (historical persistence broke down after training period — do not rely on it) |
| Score | UP SCORE = 2 | DOWN SCORE = 3 | Anything below threshold |

**UP FORMULA:** 14:15 bar + relative volume 1.5–2.5x its 20‑bar average → UP SCORE 2 → next bar (15:15) UP ~52–68% historically, vs. ~38–43% baseline.

**DOWN FORMULA:** 10:15 bar + bearish body + no gap into next bar → DOWN SCORE 3 → next bar (11:15) DOWN ~59–61% historically, vs. ~48–54% baseline.

**NO‑TRADE FORMULA:** Frozen bar, 09:15 slot, Doji not meeting the DOWN combination, or reliance on a bare candlestick‑pattern name alone.

---

## PART 18 — HONEST CONCLUSION

1. **Does this dataset contain a measurable directional edge?** Yes — and this is the richest of the three stocks analyzed so far, with **both** a validated DOWN rule and a validated UP rule, plus one that actually strengthened out of sample.
2. **Strongest UP conditions:** 14:15 bar with relative volume 1.5–2.5x its own 20‑bar average → next bar UP 52–68% across the three periods.
3. **Strongest DOWN conditions:** 10:15 bar with a bearish body and no gap into the next bar → next bar DOWN 59–61% across the three periods, the most stable finding of any rule in any of the three reports.
4. **Strongest reversal patterns:** None fully validated. Shooting Star showed a consistent DOWN‑leaning direction across all three periods (70.6%/57.1%/57.1%) — the only textbook multi‑candle reversal pattern across all three stocks analyzed that didn't flip sign — but with only 17/7/7 occurrences it's a lead, not yet a tradeable rule.
5. **Strongest continuation patterns:** 3‑bar DOWN streak + Bearish Candle label → next bar DOWN more often than baseline (61.4%/54.2%/53.6%), usable without a time restriction.
6. **Which candle patterns are actually useful, and do labels match behavior?** All single‑candle labels matched their own Open/Close sign exactly. Shooting Star's *next‑bar* behavior matched its bearish‑reversal reputation better here than in either PC Jeweller or YES Bank, though the sample remains too small to rely on. Morning Star's apparent bearish tilt in training reversed in validation — not usable.
7. **Which patterns are unreliable?** Morning Star, Evening Star, Hammer (too few occurrences), and Doji taken as a group (its training‑period FLAT‑heavy behavior was largely a frozen‑bar artifact that disappeared later).
8. **Does volume materially improve prediction?** **Yes, for this stock specifically** — volume is a load‑bearing part of the best UP rule found across all three analyses. It did not add standalone value on its own, only in combination with time‑of‑day.
9. **Does body size/% change add value?** Yes, as one of three ingredients in the DOWN rule.
10. **Does gap behavior add value?** Yes, modestly, as the third ingredient of the DOWN rule; gaps considered alone show a weak, inconsistent fade tendency, same as the other two stocks.
11. **Most reliable time:** 10:15 for the DOWN setup, 14:15 for the UP setup. Descriptively, 15:15 again has the lowest DOWN rate of the day — a pattern now seen consistently across all three stocks analyzed.
12. **Time to avoid:** 09:15 (only 27–35 observations across two years).
13. **How many signals would the final strategy generate?** DOWN setup: ~5.7–9.0% of bars (roughly 170–270 signals over the ~3,000‑bar sample). UP setup: ~3.0–4.9% of bars (roughly 90–150 signals).
14. **Historical success rate:** DOWN ≈ 59.5% in training; UP ≈ 51.7% in training.
15. **Performance on unseen (test) data:** DOWN 59.3% (essentially unchanged from training); UP 64.3% (better than training).
16. **Is the strategy overfit?** **No, for either simple rule** — both held their edge (or improved) from training through the fully unseen test period. The 6‑feature logistic‑regression scores for both directions **are explicitly LIKELY OVERFIT** (AUC drops of 0.10+ out of sample).
17. **What additional data would help?** Tick/order‑book data (to understand what specifically drove the 210 frozen bars in 2024–2025 and why they stopped — this looks like a genuine liquidity regime change worth understanding, possibly tied to corporate/regulatory events not present in this dataset), sector/power‑sector index correlation, and more history around the Shooting Star pattern specifically, since it's the one classic reversal signal across all three stocks that showed a consistent direction but didn't yet have enough occurrences to trust.

**This analysis does not, and cannot, guarantee future performance.** The honest summary for Reliance Power: this stock has the same structural DOWN‑leaning baseline seen in PC Jeweller and YES Bank, but — uniquely among the three — it offers **two** simple, well‑replicated rules (one DOWN, one UP) that both held up cleanly on fully unseen data, plus a real, documented change in the stock's liquidity behavior (frozen bars disappearing after 2025) that any forward‑looking use of this data should account for.
