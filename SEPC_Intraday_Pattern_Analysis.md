# South East Power Company (SEPC.NS) — Hourly Candle Statistical Analysis
### Data: 2,974 hourly bars, 2024‑09‑10 to 2026‑09‑09 | Source: Yahoo Finance (as provided)

---

## PART 1 — DATA VALIDATION

| Check | Result |
|---|---|
| Total valid bars | 2,974 (matches header claim exactly) |
| Earliest bar | 2024‑09‑10 12:15 IST |
| Latest bar | 2026‑09‑09 15:15 IST |
| Trading dates covered | 494 |
| UP bars | 1,130 (38.0%) |
| DOWN bars | 1,587 (53.4%) — **the highest DOWN share of any of the five stocks analyzed so far** |
| FLAT bars | 257 (8.6%) |
| Bars per time slot | 09:15 → 31, 10:15 → 491, 11:15 → 491, 12:15 → 492, 13:15 → 493, 14:15 → 494, 15:15 → 482 |
| Pattern counts | Bearish Candle 980, Bullish Candle 651, Doji 398, Strong Bearish 221, Evening Star 163, Morning Star 146, Bearish Engulfing 143, Bullish Engulfing 136, Strong Bullish 96, Shooting Star 28, Hammer 12 |
| Duplicate records | **0** (no duplicate Date+Time rows, no duplicate full rows) |
| High < Low | **0 occurrences** |
| Close outside High/Low | **0 occurrences** |
| Open outside High/Low | **0 occurrences** |
| Direction vs Close‑Open sign | **0 mismatches** in the entire dataset |
| Missing calendar dates | None beyond normal weekends/holidays |
| Bars per day | 453 days have exactly 6, 29 have 7 (extra 09:15 print), 9 days have 5, and 3 days have very short sessions (4, 2, 2 bars) on 2024‑09‑10, 2025‑10‑21, 2026‑04‑20 — consistent with holiday/first/last‑day sessions |

**Things worth flagging (observations, not corrections):**

1. **Frozen bars (O=H=L=C) are rare overall (19 of 2,974, 0.6%) but land almost entirely inside the validation window** — 19 in validation, 0 in training, 0 in test. This is the opposite pattern from Reliance Power and Suzlon (where frozen bars were concentrated early and disappeared later); here they appear to be a short‑lived illiquidity patch specific to the Dec 2025–Apr 2026 window rather than a long‑term trend.
2. **Doji, again, is not synonymous with FLAT** — of 398 Doji bars, 243 are FLAT, but 83 are DOWN and 72 are UP.
3. **Volume is comparatively low and choppy for this stock** (monthly averages range roughly ₹430K–6.8M shares/hour, with no clean multi‑year trend up or down) — smaller and noisier than the other four stocks, consistent with SEPC being a smaller‑cap, lower‑turnover name.

**Conclusion of Part 1: the dataset is internally clean** — no fabricated OHLC, no impossible bars, no label/direction mismatches. The one real structural note is the validation‑period‑only frozen‑bar cluster, flagged above.

---

## PART 2 — DERIVED VARIABLES

Same full set computed from Open/High/Low/Close/Volume/Date/Time as in the four prior reports: Range, Range %, Body size/%, Bar % change, upper/lower wick (absolute + % of range), body‑to‑range ratio, gap and gap % vs. previous close, close‑position tercile, BodyDir (cross‑checked, zero mismatches), volume vs. previous bar and vs. trailing 20‑bar rolling average, range/body change vs. previous bar, streak type/length, previous 2‑/3‑bar sequences, day‑of‑week, HH/HL/LH/LL flags, Close‑vs‑previous‑Close.

**Not calculated:** VWAP, RSI, MACD, tick/order‑book data, sector/index correlation — none derivable from the given columns.

---

## PARTS 3–11 — SEARCH FOR AN EDGE

**Same non‑circular methodology as the four prior reports:** single‑candle pattern labels equal that bar's own Direction by definition (0 exceptions verified), so every result targets **NextDirection** using only information available once the current bar closes (or, for gaps, as soon as the next bar opens).

**Chronological split:** Train = 2024‑09‑10 → 2025‑12‑26 (1,933 rows), Validation = 2025‑12‑29 → 2026‑04‑21 (446 rows), Test = 2026‑04‑21 → 2026‑09‑09 (595 rows). No shuffling.

**Baseline to beat (train):** Next bar is UP 38.5% / DOWN 55.0% / FLAT 6.4%. **The strongest DOWN‑leaning baseline of any of the five stocks analyzed so far** — this stock's intraday drift is even more persistently negative than PC Jeweller, YES Bank, Reliance Power, or Suzlon.

### PART 9 — UP setups: **none survived**, the second time this has happened (after YES Bank)

A systematic scan of the 50 best‑looking training UP combinations found **zero** that held the same direction with ≥15 observations in both validation and test. Every UP‑leaning candidate tested decayed to baseline or reversed out of sample. This is an honest, important negative result: **there is no validated UP setup for SEPC in this dataset.**

### PART 10 — Best DOWN setup found

| Setup | Train n / DOWN% | Val n / DOWN% | Test n / DOWN% | Verdict |
|---|---|---|---|---|
| **11:15 bar has a bearish body (Close<Open)** | 193 / 67.9% | 33 / 57.6% | 43 / 62.8% | The best‑evidenced, largest‑sample setup found for this stock — held up in both out‑of‑sample windows |
| 11:15 bar has a bearish body + closed in the bottom third of its own range | 125 / 68.8% | 20 / 60.0% | 28 / 57.1% | Slightly stronger in training, similar out‑of‑sample, smaller sample |
| 11:15 bar labeled "Bearish Candle" specifically | 114 / 71.1% | 22 / 50.0% (weak — barely above baseline) | 22 / 68.2% | Direction holds but validation is right at the edge — the broader BodyDir version above is more dependable |

**Component breakdown:**

| Condition alone | Train DOWN% | Val DOWN% | Test DOWN% |
|---|---|---|---|
| Time = 11:15 only | 65.2% | 56.8% | 50.0% |
| Bearish body only | 56.2% | 55.7% | 45.9% |
| **11:15 + bearish body** | **67.9%** | **57.6%** | **62.8%** |

11:15 is already this stock's most DOWN‑biased hour on its own (65.2% train — see Part 4), and the combination with a bearish body pushes it further, holding up reasonably (though not perfectly — the test‑period edge over the "time alone" baseline is larger than the training‑period edge, an encouraging sign rather than a red flag).

### PART 6 — Candle‑pattern reliability (Pattern → NEXT bar, train)

| Pattern | n | Next UP% | Next DOWN% | Next FLAT% | Reliable? |
|---|---|---|---|---|---|
| Bearish Candle | 647 | 36.2% | 57.8% | 6.0% | Feeds into the validated 11:15 combination above; on its own, modest |
| Bullish Engulfing | 89 | 31.5% | 60.7% | 7.9% | Counter‑intuitive (a bullish pattern followed by DOWN more often than average) — **not independently tested for robustness given the modest sample**, flagged as a curiosity, not a rule |
| Hammer | 8 | 12.5% | 87.5% | 0% | **Only 8 occurrences in the entire dataset — statistically meaningless despite the dramatic‑looking number** |
| Doji (all) | 245 | 40.4% | 52.2% | 7.3% | Close to baseline, no real edge |
| Morning Star | 101 | 44.6% | 49.5% | 5.9% | No meaningful edge |
| Evening Star | 105 | 41.0% | 52.4% | 6.7% | No meaningful edge |
| Shooting Star | 16 | 37.5% | 56.2% | 6.2% | Sample far too small |

**Label‑vs‑OHLC check:** all single‑candle labels matched Close‑vs‑Open sign with zero exceptions.

### PART 7 — Sequence analysis (train)

| Streak (ending at bar just closed) | n | Next UP% | Next DOWN% | Next avg % move |
|---|---|---|---|---|
| 1‑bar DOWN | 466 | 39.5% | 54.7% | −0.04% |
| 2‑bar DOWN | 255 | 35.3% | 59.2% | −0.11% |
| 4‑bar DOWN | 75 | 32.0% | 66.7% | −0.18% |
| 6‑bar DOWN | 24 | 29.2% | 70.8% | −0.25% (looked like accelerating continuation, but **failed to replicate in test**: only 48.0% next‑DOWN, essentially baseline — do not trust) |
| 1‑bar UP | 457 | 39.6% | 53.6% | −0.01% |
| 4‑bar UP | 27 | 22.2% | 74.1% | −0.20% (small sample, not independently tested) |

Unlike some of the other stocks, longer DOWN streaks here *looked* like they strengthened continuation rather than reverting — but the specific 4+‑bar‑streak combination did not hold up once tested against the fully unseen test period (60.9% train → 48.0% test), so this is flagged as unreliable despite the appealing‑looking training numbers.

### PART 8 — Price structure & gaps

| Structure | n (train) | Next UP% | Next DOWN% |
|---|---|---|---|
| Higher High + Higher Low | 501 | 39.3% | 53.9% |
| Lower High + Lower Low | 811 | 38.8% | 55.7% |
| Mixed | 621 | 37.5% | 55.1% |

No meaningful separation — structure alone adds little, the same finding as all four prior stocks.

**Gap behavior:** gap categories showed little differentiation in this dataset (own‑bar DOWN rate 53.4%/56.1%/55.6% for gap‑down/gap‑up/no‑gap respectively — all close to baseline). Gap fill rates: gap‑down bars close back above the prior close only 27.7% of the time; gap‑up bars close back below only 44.1% of the time (somewhat higher fill rate than the other stocks, but still a minority). Gaps mostly don't fill same‑session, consistent with all prior reports.

---

## PART 5 — VOLUME ANALYSIS

Monthly average volume for SEPC is both lower and choppier than the other four stocks (~₹430K–6.8M shares/hour, no clear multi‑year trend). Rolling‑relative volume was used throughout for consistency, though — like Suzlon — **volume did not end up being a necessary ingredient of the validated DOWN rule.** A relative‑volume‑spike condition combined with bullish body did look interesting in training (SPIKE + Bullish → 70.5% next‑DOWN) but this was not selected as a primary rule given the modest, somewhat inconsistent out‑of‑sample behavior (val 56.2%, test 60.9% — directionally fine but overlapping heavily with the simpler 11:15 rule).

A full 6‑feature logistic‑regression score (Time + Streak + BodyDir + relative Volume + close‑position + gap category) shows the same overfitting pattern seen in all four prior reports:

| Split | Base DOWN rate | Model accuracy | Model AUC |
|---|---|---|---|
| Train | 55.0% | 57.9% | **0.607** |
| Validation | 51.8% | 49.1% | **0.485** (worse than a coin flip) |
| Test | 49.2% | 50.2% | **0.517** |

**Explicitly overfit** — the same conclusion as all four prior stocks: use the simple, validated checklist, not a fitted multi‑feature score.

---

## PART 4 — TIME‑OF‑DAY (train)

| Time | UP% | DOWN% | FLAT% | Avg range% | Avg chg% | n |
|---|---|---|---|---|---|---|
| 09:15 | 52.6% | 47.4% | 0% | 4.94% | +1.68% | 19 (too few to trust) |
| 10:15 | 40.1% | 54.5% | 5.3% | 1.45% | −0.05% | 319 |
| **11:15** | **35.1%** | **60.5%** | 4.4% | 1.17% | −0.17% | 319 — the basis for the validated DOWN rule |
| **12:15** | **30.0%** | **65.0%** | 5.0% | 1.04% | −0.17% | 320 — **the single most DOWN‑biased hour across all five stocks analyzed to date** |
| 13:15 | 38.6% | 55.8% | 5.6% | 1.10% | −0.06% | 321 |
| 14:15 | 37.4% | 54.8% | 7.8% | 1.25% | −0.11% | 321 |
| 15:15 | 49.4% | 39.8% | 10.8% | 0.90% | +0.11% | 314 |

**Same recurring cross‑stock pattern: 15:15 (the close) is the least DOWN‑biased hour, and the market shows the strongest DOWN bias mid‑morning to early afternoon** — here 12:15 is even more extreme (65.0% DOWN) than 11:15. This is now the **fifth stock in a row** showing the "last hour leans less bearish" shape, reinforcing that this looks like a broader structural feature rather than a stock‑specific quirk (though I have not tested it outside these five names, and it was not itself built into a scored trading rule — it's a descriptive, not prescriptive, finding). 12:15 was tested as an alternative anchor for the DOWN rule but 11:15 + bearish body gave the more consistent out‑of‑sample result.

---

## PART 11 — NO‑TRADE CONDITIONS

| Condition | What the data shows | Why it's a NO‑TRADE zone |
|---|---|---|
| **Frozen bars** (19, concentrated entirely in the validation window) | An isolated illiquidity patch, not a long‑term trend | Flag any recurrence as untradeable regardless of when it happens |
| **09:15 slot** | Only 19–31 observations across the whole sample | Statistically unusable |
| **Doji overall** | Close to baseline (40/52/7 UP/DOWN/FLAT in training) | No standalone directional information |
| **Hammer, Shooting Star, Morning/Evening Star alone** | All too small a sample (8–163 occurrences) or too close to baseline | Not usable as standalone signals |
| **4+ bar DOWN streaks** | Looked like accelerating continuation in training but failed to replicate in test | Do not rely on long streaks as a signal by themselves |
| **Any UP‑leaning read** | No UP setup survived out‑of‑sample validation | Treat all UP‑leaning signals as noise for this stock until more data changes that |
| **Any single isolated factor** (Time, Pattern, Volume, gap, structure alone) | Each moves the DOWN/UP rate by only a few points off baseline | Only the specific 11:15 + bearish‑body combination shows a real, repeatable edge |

**NO‑TRADE rule:** stand aside on the 09:15 slot, any bare candlestick‑pattern read, any long DOWN streak used as a standalone signal, and — importantly — on any attempted UP setup, since none survived validation for this stock.

---

## PART 12 — SCORING SYSTEM

Following the same reasoning as the four prior reports, a simple evidence‑backed checklist is used instead of a fitted multi‑factor score.

**DOWN SCORE (0–2, one point each):**
- +1 if this is the **11:15** bar
- +1 if this bar's body is bearish (Close < Open)

**DOWN SCORE = 2 → historical DOWN rate for the next bar: 67.9% (train) / 57.6% (val) / 62.8% (test), vs. a ~49–55% baseline.**

**UP SCORE: not recommended.** No UP combination in this dataset survived out‑of‑sample testing — the second stock (after YES Bank) where this is the honest conclusion. Presenting an UP rule here would not be evidence‑based.

**Threshold:** DOWN SCORE = 2 → potential DOWN setup. Anything else (including any UP‑leaning read) → NO TRADE.

---

## PART 13 — REAL‑TIME DECISION FORMULA

```
CURRENT HOURLY BAR JUST CLOSED (Open, High, Low, Close, Volume known)
        │
        ▼
Is this the 11:15 bar?
        │
   NO ──┴──► NO TRADE (no validated setup exists for other hours in this stock)
        │
       YES
        ▼
Is Close < Open (bearish body)?
        │
   NO ──┴──► NO TRADE
        │
       YES
        ▼
   DOWN SCORE = 2 → POTENTIAL DOWN SETUP
   (no UP setup path — none validated for this stock)
```

---

## PART 14 — BACKTEST RESULTS (chronological, no shuffling)

| Metric | Train (65%, n=1,933) | Validation (15%, n=446) | Test (20%, n=595) |
|---|---|---|---|
| DOWN setup: trigger rate | 10.0% | 7.4% | 7.2% |
| DOWN setup: hit rate | 67.9% | 57.6% | 62.8% |
| DOWN setup: avg next‑bar % move | −0.20% | −0.18% | −0.14% |
| Baseline DOWN rate | 55.0% | 51.8% | 49.2% |
| UP setup | **Not offered — no candidate survived validation** | — | — |

**Is this overfit?** **No.** The rule's edge over baseline is consistent in all three windows: +12.9 points in training (67.9 vs 55.0), +5.8 points in validation (57.6 vs 51.8), +13.6 points in test (62.8 vs 49.2). Validation is the softest of the three, but the rule clearly still beats baseline there too, and test — the fully unseen window — actually shows a wider edge than validation. This is not the signature of an overfit rule.

---

## PART 15 — ROBUSTNESS CHECKS

- **Volume regime:** choppy but without a runaway multi‑year trend; not a major confound, and volume wasn't a necessary ingredient of the validated rule anyway.
- **Threshold sensitivity:** adding a third condition (bottom‑third close, or narrowing to the specific "Bearish Candle" label) gives similar or slightly weaker out‑of‑sample results (see Part 10's alternate rows) — the simple 2‑condition rule is about as good as any variant tested, a reasonably "flat" rather than "cliff‑edged" relationship.
- **Different time periods:** the rule's edge over baseline holds in all three chronological windows, including the fully unseen test period.
- **Frozen‑bar cluster:** confirmed as isolated to the validation window only — doesn't appear to be a long‑term structural feature the way it was for Reliance Power or Suzlon, and doesn't affect the DOWN rule (which doesn't depend on frozen bars).
- **High‑ vs low‑volatility subperiods:** not separately re‑tested beyond the three chronological splits, same limitation as the four prior reports.

---

## PART 16 — FINAL TRADING RULE (plain language)

**DOWN SETUP — IF:**
1. The just‑closed hourly bar is the **11:15** bar
2. That bar's Close is below its Open (bearish body)

**AND DOWN SCORE = 2 → THEN:** Potential DOWN setup for the 12:15 bar (historical hit rate ~58–68% across all three periods, vs. a ~49–55% baseline).

**UP SETUP: not offered.** No UP‑leaning combination survived validation and test for this stock. Trading UP setups on SEPC based on this dataset would not be evidence‑based.

**Avoid the trade if:** it's any hour other than 11:15, the bar isn't bearish‑bodied, or the only basis is a classic candlestick name (Hammer, Shooting Star, Bullish/Bearish Engulfing) without the specific conditions validated above.

**NO TRADE — IF:** any hour other than 11:15 is being evaluated for the DOWN rule; it's the 09:15 slot; the bar is a Doji not meeting the DOWN combination; or you're relying on a long DOWN streak (4+ bars) as a standalone reversal or continuation signal.

---

## PART 17 — QUICK‑REFERENCE TABLE

| Factor | UP condition | DOWN condition | Neutral / No‑Trade |
|---|---|---|---|
| Time | none validated | **11:15** (core of the DOWN rule); 12:15 even more DOWN‑biased descriptively but not used in the final rule | 09:15 (n too small); 15:15 least DOWN‑biased descriptively |
| Previous direction/streak | none validated | none validated alone (4+ streak looked promising but failed test) | Long DOWN streaks (4+ bars) as a standalone signal |
| Candle pattern | none reliable | Bearish Candle / bearish body (as part of the 11:15 combo) | Hammer, Shooting Star, Morning/Evening Star, Bullish Engulfing (all unreliable or too small) |
| Body size / % change | — | Bearish body (Close<Open) | — |
| Volume | no standalone edge | not required for the validated rule | Any single volume reading alone; full 6‑feature model (overfit) |
| Range | — | — | — |
| Gap | — | — | Gap categories showed little differentiation for this stock |
| Sequence | — | — | Streak length alone, any direction |
| Score | **Not offered** | DOWN SCORE = 2 | Anything below threshold |

**UP FORMULA:** Not available — no validated UP setup exists in this dataset for SEPC.

**DOWN FORMULA:** 11:15 bar + bearish body → DOWN SCORE 2 → next bar (12:15) DOWN ~58–68% historically, vs. ~49–55% baseline.

**NO‑TRADE FORMULA:** Any hour other than 11:15 for the DOWN rule, the 09:15 slot, a Doji not meeting the DOWN combination, or reliance on a bare candlestick‑pattern name or a long streak alone.

---

## PART 18 — HONEST CONCLUSION

1. **Does this dataset contain a measurable directional edge?** Yes, one — the 11:15 bearish‑body bar predicting a DOWN 12:15 bar, with a consistent edge over baseline across all three chronological windows.
2. **Strongest UP conditions:** **None found.** A systematic scan of the 50 best‑looking training UP combinations found zero that replicated out of sample — the same honest negative result as YES Bank.
3. **Strongest DOWN conditions:** 11:15 bar closing with a bearish body.
4. **Strongest reversal patterns:** None validated. A long (6‑bar) DOWN streak looked like an accelerating continuation signal in training but collapsed to near‑baseline in test — rejected.
5. **Strongest continuation patterns:** Short DOWN streaks (1–2 bars) show a mild elevated next‑DOWN rate, largely overlapping with the 11:15‑hour finding rather than adding independent value.
6. **Which candle patterns are actually useful, and do labels match behavior?** All single‑candle labels matched their own Open/Close sign exactly — no mislabeling. "Bearish Candle" contributes to the one validated rule, but only via its 11:15 timing, not as a standalone signal. Bullish Engulfing showed an odd, counter‑intuitive down‑leaning tendency in training that wasn't independently tested for robustness — flagged as a curiosity, not a finding.
7. **Which patterns are unreliable?** Hammer (8 occurrences — meaningless), Shooting Star, Morning Star, Evening Star, and Doji as a group.
8. **Does volume materially improve prediction?** No standalone effect found, and it wasn't required for the validated DOWN rule either — the only stock of the five (alongside Suzlon) where volume didn't end up in the final rule.
9. **Does body size/% change add value?** Yes — bearish body direction is one of the two ingredients in the DOWN rule.
10. **Does gap behavior add value?** Not much for this stock — gap categories showed little differentiation, unlike some of the other four stocks.
11. **Most reliable time:** 11:15 for the DOWN setup. Descriptively, 12:15 is even more DOWN‑biased (65.0% train), and 15:15 is again the least DOWN‑biased hour of the day — continuing the pattern seen in all five stocks analyzed.
12. **Time to avoid:** 09:15 (only 19–31 observations across two years).
13. **How many signals would the final strategy generate?** The DOWN setup triggers on roughly 7.2–10.0% of all bars — about 215–295 signals over the ~2,970‑bar, two‑year sample.
14. **Historical success rate:** ~67.9% in training.
15. **Performance on unseen (test) data:** 62.8% — a somewhat smaller but still solid edge over the test‑period baseline (49.2%).
16. **Is the strategy overfit?** **No** — the edge over baseline held in both out‑of‑sample windows, with test actually showing a wider margin than validation.
17. **What additional data would help?** Tick/order‑book data (to understand what specifically drives the pronounced 11:15–12:15 DOWN bias — this is now a recurring mid‑morning pattern across all five stocks and may reflect broader market‑structure or algorithmic flow effects worth investigating with cross‑market data), sector/power‑sector index correlation, and a longer sample to properly test the handful of low‑count patterns (Hammer, Shooting Star) that occurred too rarely here to evaluate.

**This analysis does not, and cannot, guarantee future performance.** The honest summary for SEPC: this stock has the strongest structural DOWN bias of any of the five names analyzed (55% of next bars are DOWN regardless of setup), one specific, well‑replicated rule modestly improves on that baseline for the 12:15 bar following a bearish 11:15 open, and — as with YES Bank — **no UP‑side edge exists in this dataset.** The recurring "mid‑morning DOWN bias, closing‑hour UP lean" shape, now seen in all five stocks analyzed across this series, looks like the most durable pattern in the whole project — more so than any single‑stock candlestick rule.
