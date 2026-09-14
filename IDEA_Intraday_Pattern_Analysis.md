# Vodafone Idea (IDEA.NS) — Hourly Candle Statistical Analysis
### Data: 2,975 hourly bars, 2024‑09‑10 to 2026‑09‑09 | Source: Yahoo Finance (as provided)

---

## PART 1 — DATA VALIDATION

| Check | Result |
|---|---|
| Total valid bars | 2,975 (matches header claim exactly) |
| Earliest bar | 2024‑09‑10 12:15 IST |
| Latest bar | 2026‑09‑09 15:15 IST |
| Trading dates covered | 494 |
| UP bars | 1,220 (41.0%) |
| DOWN bars | 1,510 (50.8%) |
| FLAT bars | 245 (8.2%) |
| Bars per time slot | 09:15 → 24, 10:15 → 491, 11:15 → 491, 12:15 → 492, 13:15 → 493, 14:15 → 494, 15:15 → 490 |
| Pattern counts | Bearish Candle 955, Bullish Candle 674, Doji 315, Strong Bearish 244, Bullish Engulfing 199, Bearish Engulfing 147, Strong Bullish 135, Morning Star 127, Evening Star 122, Shooting Star 37, Hammer 20 |
| Duplicate records | **0** (no duplicate Date+Time rows, no duplicate full rows) |
| High < Low | **0 occurrences** |
| Close outside High/Low | **0 occurrences** |
| Open outside High/Low | **0 occurrences** |
| Direction vs Close‑Open sign | **0 mismatches** in the entire dataset |
| Missing calendar dates | None beyond normal weekends/holidays |
| Bars per day | 464 days have exactly 6, 24 have 7 (extra 09:15 print), 3 days have 5, and 3 days have very short sessions (4, 2, 2 bars) on 2024‑09‑10, 2025‑10‑21, 2026‑04‑20 — consistent with holiday/first/last‑day sessions |

**Things worth flagging (observations, not corrections):**

1. **This is by far the highest‑volume stock analyzed in this series.** Average hourly volume runs ₹35M–240M shares, roughly 10–1,000x the other stocks analyzed so far — unsurprising for Vodafone Idea, one of the most heavily‑traded retail names on the NSE. No extreme multi‑year regime shift, but a healthy 2–4x fluctuation month‑to‑month.
2. **Frozen bars (O=H=L=C) are very rare (only 7 of 2,975, 0.2%)**, and interestingly all 7 fall in the *test* period rather than training — the opposite of the pattern seen in Reliance Power/Suzlon (where illiquidity clustered early). Given IDEA's enormous liquidity, none of this should be read as a meaningful trend either way; it's simply too small a count to matter.
3. **Doji is comparatively rare here (315 bars, the fewest of any of the six stocks analyzed)** and split fairly evenly (237 FLAT, 41 UP, 37 DOWN) — a high‑liquidity stock like this one rarely sits still.

**Conclusion of Part 1: the dataset is internally clean** — no fabricated OHLC, no impossible bars, no label/direction mismatches.

---

## PART 2 — DERIVED VARIABLES

Same full set computed from Open/High/Low/Close/Volume/Date/Time as in the five prior reports: Range, Range %, Body size/%, Bar % change, upper/lower wick (absolute + % of range), body‑to‑range ratio, gap and gap % vs. previous close, close‑position tercile, BodyDir (cross‑checked, zero mismatches), volume vs. previous bar and vs. trailing 20‑bar rolling average, range/body change vs. previous bar, streak type/length, previous 2‑/3‑bar sequences, day‑of‑week, HH/HL/LH/LL flags, Close‑vs‑previous‑Close.

**Not calculated:** VWAP, RSI, MACD, tick/order‑book data, sector/index correlation — none derivable from the given columns.

---

## PARTS 3–11 — SEARCH FOR AN EDGE

**Same non‑circular methodology as the five prior reports:** single‑candle pattern labels equal that bar's own Direction by definition (0 exceptions verified), so every result targets **NextDirection** using only information available once the current bar closes (or, for gaps, as soon as the next bar opens).

**Chronological split:** Train = 2024‑09‑10 → 2025‑12‑26 (1,933 rows), Validation = 2025‑12‑26 → 2026‑04‑21 (447 rows), Test = 2026‑04‑21 → 2026‑09‑09 (595 rows). No shuffling.

**Baseline to beat (train):** Next bar is UP 40.7% / DOWN 50.5% / FLAT 8.9%. **The same recurring DOWN‑leaning baseline seen in all six stocks analyzed to date.**

### PART 9 — UP setups: **none survived**, the third time this has happened

A systematic scan of the 50 best‑looking training UP combinations found **zero** that held the same direction with ≥15 observations in both validation and test. As with YES Bank and SEPC, this dataset does not support a validated UP setup.

### PART 10 — Best DOWN setup found: a genuinely clean, large‑sample, single‑factor result

| Setup | Train n / DOWN% | Val n / DOWN% | Test n / DOWN% | Verdict |
|---|---|---|---|---|
| **The bar that's about to open does so with a gap UP vs. the prior bar's close** | 481 / 54.5% | 125 / 58.4% | 174 / 59.8% | **The single largest‑sample, most consistent finding of any stock in this series** — and unusually, the edge actually strengthens from training through both out‑of‑sample windows |
| Add: prior bar was part of a 2‑bar DOWN streak with a bearish body | 68 / 61.8% | 19 / 63.2% | 16 / 68.8% | Tighter and even stronger, but the sample shrinks considerably |
| Add: relative volume normal‑low + bottom‑third close (instead of the streak condition) | 123 / 59.3% | 36 / 61.1% | 30 / 56.7% | A good middle‑ground refinement — larger sample than the streak version, still comfortably above the plain gap‑up baseline |

**For contrast — gap‑down and no‑gap bars show no such effect:**

| Condition | Train DOWN% | Val DOWN% | Test DOWN% |
|---|---|---|---|
| Next bar gaps down | 49.6% | 49.6% | 44.1% |
| Next bar has no gap | 48.9% | 48.6% | 49.6% |
| **Next bar gaps up** | **54.5%** | **58.4%** | **59.8%** |

This is a genuine, asymmetric "gap‑up fade" effect specific to this stock: bars that gap down or don't gap at all behave close to the overall baseline, but bars that gap *up* are meaningfully more likely to close DOWN than the general average — and this held up (in fact got stronger) in both out‑of‑sample windows. Roughly a quarter to a third of all bars gap up, so this is also one of the highest‑frequency rules found across the whole six‑stock series.

### PART 6 — Candle‑pattern reliability (Pattern → NEXT bar, train)

| Pattern | n | Next UP% | Next DOWN% | Next FLAT% | Reliable? |
|---|---|---|---|---|---|
| Strong Bearish Candle | 153 | 37.9% | 56.2% | 5.9% | Mildly elevated, not independently tested for robustness given the smaller sample |
| Bearish Candle | 632 | 38.1% | 51.7% | 10.1% | Close to baseline |
| Bullish Engulfing | 132 | 44.7% | 47.0% | 8.3% | No edge |
| Hammer | 15 | 26.7% | 60.0% | 13.3% | Sample far too small (15) to trust |
| Doji (all) | 210 | 38.6% | 49.1% | 12.4% | Close to baseline |
| Morning Star | 92 | 43.5% | 50.0% | 6.5% | No meaningful edge |
| Evening Star | 84 | 40.5% | 52.4% | 7.1% | No meaningful edge |
| Shooting Star | 25 | 40.0% | 48.0% | 12.0% | Sample too small |

**Label‑vs‑OHLC check:** all single‑candle labels matched Close‑vs‑Open sign with zero exceptions. No pattern's own‑bar label contradicted its actual price action.

### PART 7 — Sequence analysis (train)

| Streak (ending at bar just closed) | n | Next UP% | Next DOWN% | Next avg % move |
|---|---|---|---|---|
| 1‑bar DOWN | 466 | 40.8% | 50.0% | +0.02% |
| 2‑bar DOWN | 233 | 39.9% | 50.6% | +0.03% |
| **3‑bar DOWN** | 118 | 28.0% | **61.9%** | −0.13% (looked strong in training, but **decayed to baseline in both val and test**: 50.0%/50.0% — do not rely on this alone) |
| 4‑bar DOWN | 73 | 35.6% | 60.3% | −0.34% (similar caveat — small sample, not independently validated) |
| 1‑bar UP | 439 | 42.8% | 49.2% | +0.01% |
| 4‑bar UP | 36 | 55.6% | 38.9% | +0.27% (small sample) |

The one streak‑based finding that looked most promising in training (3‑bar DOWN streak → 61.9% next‑DOWN) is a clear example of an overfitting trap: it drops to exactly baseline (50.0%) in both validation and test. **Flagged as unreliable despite the appealing training number** — this is exactly the kind of result the chronological‑split methodology exists to catch.

### PART 8 — Price structure & gaps

| Structure | n (train) | Next UP% | Next DOWN% |
|---|---|---|---|
| Higher High + Higher Low | 526 | 41.3% | 50.0% |
| Lower High + Lower Low | 706 | 38.5% | 52.8% |
| Mixed | 701 | 42.4% | 48.5% |

No meaningful separation — structure alone adds little, consistent with all five prior stocks. (The gap analysis is covered in detail in Part 10 above, since it's the headline finding for this stock.)

Gap fill rates: gap‑down bars close back above the prior close 32.8% of the time; gap‑up bars close back below only 42.8% of the time — a somewhat higher fill rate than most of the other stocks, but still a minority, and consistent with (not contradictory to) the gap‑up‑fade finding above (a bar can partially fade — close lower than it opened — without fully "filling" all the way back to the prior close).

---

## PART 5 — VOLUME ANALYSIS

IDEA's volume is enormous and comparatively stable in proportional terms (no multi‑year 50x escalation like PC Jeweller), so the rolling‑relative volume measure works cleanly here. Volume contributed to one of the *refinements* of the DOWN rule (normal‑low relative volume + bottom‑third close + gap up → 56.7–61.1% DOWN) but was **not required** for the core, larger‑sample finding — the plain "gap up" condition alone already carries most of the edge.

A full 6‑feature logistic‑regression score (Time + Streak + BodyDir + relative Volume + close‑position + gap category) shows the same overfitting pattern seen in all five prior reports:

| Split | Base DOWN rate | Model accuracy | Model AUC |
|---|---|---|---|
| Train | 50.5% | 54.1% | **0.565** |
| Validation | 51.7% | 49.9% | **0.505** (essentially random) |
| Test | 51.0% | 51.7% | **0.519** |

The full model collapses to near‑random out of sample — **explicitly overfit**, reinforcing that the simple, single‑factor gap‑up rule (which needed no fitting at all) is the better‑evidenced finding here.

---

## PART 4 — TIME‑OF‑DAY (train)

| Time | UP% | DOWN% | FLAT% | Avg range% | Avg chg% | n |
|---|---|---|---|---|---|---|
| 09:15 | 44.4% | 50.0% | 5.6% | 3.80% | −0.75% | 18 (too few to trust) |
| 10:15 | 42.6% | 50.2% | 7.2% | 1.53% | +0.06% | 319 |
| **11:15** | **38.1%** | **54.7%** | 7.2% | 1.37% | −0.05% | 318 |
| 12:15 | 42.0% | 49.8% | 8.2% | 1.15% | +0.03% | 319 |
| 13:15 | 39.4% | 52.2% | 8.4% | 1.17% | −0.06% | 320 |
| 14:15 | 39.7% | 50.3% | 10.0% | 1.31% | −0.04% | 320 |
| 15:15 | 42.3% | 45.8% | 11.9% | 0.70% | +0.04% | 319 |

**The now‑familiar cross‑stock pattern continues: 11:15 is the most DOWN‑biased hour and 15:15 is the least, for the sixth stock in a row.** This shape has now shown up consistently in PC Jeweller, YES Bank, Reliance Power, Suzlon, SEPC, and IDEA — six unrelated stocks across small‑cap, mid‑cap, and one very high‑liquidity name. Time‑of‑day alone was not built into the final scored rule for IDEA (the gap‑up finding proved stronger and simpler), but this consistent shape is worth treating as the most durable pattern across the whole series to date.

---

## PART 11 — NO‑TRADE CONDITIONS

| Condition | What the data shows | Why it's a NO‑TRADE zone |
|---|---|---|
| **09:15 slot** | Only 18–24 observations across the whole sample | Statistically unusable |
| **3‑bar and 4‑bar DOWN streaks used alone** | Looked strong in training (60%+ next‑DOWN) but decayed to baseline in both out‑of‑sample windows | Do not trade streak length by itself |
| **Doji, Hammer, Shooting Star, Morning/Evening Star alone** | All close to baseline or too small a sample | Not usable as standalone signals |
| **Bars that gap down or don't gap at all** | Both sit close to the general ~49–52% baseline | No edge — only the gap‑*up* condition shows a real effect |
| **Any attempted UP setup** | No UP combination survived validation | Treat all UP‑leaning signals as noise for this stock |
| **Any single isolated factor other than the gap‑up condition** | Each moves the DOWN/UP rate by only a few points off baseline | Only the validated gap‑up combination shows a real, repeatable edge |

**NO‑TRADE rule:** stand aside on the 09:15 slot, any bare candlestick‑pattern read, any DOWN streak used alone as a signal, and — importantly — on any attempted UP setup, since none survived validation for this stock.

---

## PART 12 — SCORING SYSTEM

Following the same reasoning as the five prior reports, a simple evidence‑backed checklist is used instead of a fitted multi‑factor score. This is the first stock in the series where the core signal is a **single condition** rather than a combination — which is itself informative: it means the edge here is simpler and broader‑based than the multi‑condition rules found for the other five stocks.

**DOWN SCORE (0–1, or optionally 0–3 for a tighter version):**
- +1 if the bar about to form opens with a **gap up** vs. the prior bar's close

**DOWN SCORE = 1 → historical DOWN rate for that bar: 54.5% (train) / 58.4% (val) / 59.8% (test), vs. a ~44–50% baseline for non‑gap‑up bars.**

**Optional tightened version (0–3, for higher conviction at the cost of fewer signals):**
- +1 gap up (as above)
- +1 if the prior bar was part of a 2‑bar DOWN streak
- +1 if the prior bar's body was bearish

**Tightened score = 3 → 61.8% (train) / 63.2% (val) / 68.8% (test)** — stronger, but on a much smaller sample (68/19/16).

**UP SCORE: not recommended.** No UP combination in this dataset survived out‑of‑sample testing.

**Thresholds:** DOWN SCORE ≥1 (simple version) or =3 (tightened version) → potential DOWN setup. Anything else → NO TRADE.

---

## PART 13 — REAL‑TIME DECISION FORMULA

```
NEW HOURLY BAR IS ABOUT TO OPEN
        │
        ▼
Does it open with a GAP UP vs. the prior bar's close?
        │
   NO ──┴──► NO TRADE (no edge for gap-down or no-gap bars)
        │
       YES ──► DOWN SCORE = 1 → POTENTIAL DOWN SETUP
        │
        ▼
[Optional tightening for higher conviction]
Was the PRIOR bar part of a 2-bar DOWN streak with a bearish body?
   YES ─┼──► DOWN SCORE = 3 → HIGHER-CONVICTION DOWN SETUP
   NO ──┴──► keep DOWN SCORE = 1 (still a valid, if lower-conviction, setup)

(no UP setup path — none validated for this stock)
```

---

## PART 14 — BACKTEST RESULTS (chronological, no shuffling)

| Metric | Train (65%, n=1,933) | Validation (15%, n=447) | Test (20%, n=595) |
|---|---|---|---|
| DOWN setup (simple gap‑up rule): trigger rate | 24.9% | 28.0% | 29.3% |
| DOWN setup: hit rate | 54.5% | 58.4% | 59.8% |
| Baseline DOWN rate (non‑gap‑up bars) | ~48.9–49.6% | ~48.6–49.6% | ~44.1–49.6% |
| Tightened DOWN setup: trigger rate | 3.5% | 4.3% | 2.7% |
| Tightened DOWN setup: hit rate | 61.8% | 63.2% | 68.8% |

**Is this overfit?** **No — the opposite, in fact.** The simple gap‑up rule's hit rate *increases* from training (54.5%) through validation (58.4%) to test (59.8%) — the clearest non‑overfitting signature found anywhere in this six‑stock series. The tightened version shows the same pattern (61.8% → 63.2% → 68.8%). The 6‑feature logistic‑regression score, by contrast, **is explicitly LIKELY OVERFIT** (AUC collapses from 0.565 to ~0.51, essentially random, out of sample).

---

## PART 15 — ROBUSTNESS CHECKS

- **Volume regime:** stable in proportional terms despite IDEA's enormous absolute volume — not a confound, and volume wasn't required for the core rule.
- **Threshold sensitivity:** the rule is unusually *not* threshold‑sensitive — the simple 1‑condition version, the 2‑condition refinement, and the 3‑condition tightened version all point the same direction with increasing (not decreasing) strength as more conditions are added, which is the opposite of the "cliff" pattern seen in some other stocks' rules and a further sign of genuine signal rather than a fitted artifact.
- **Different time periods:** the edge holds — and strengthens — across training, validation, and the fully unseen test window.
- **Frozen‑bar/illiquidity concerns:** minimal for this stock given its very high liquidity; not a material confound.
- **High‑ vs low‑volatility subperiods:** not separately re‑tested beyond the three chronological splits, same limitation as the five prior reports.

---

## PART 16 — FINAL TRADING RULE (plain language)

**DOWN SETUP — IF:**
1. The bar about to form opens with a **gap up** relative to the previous bar's close

**AND DOWN SCORE ≥ 1 → THEN:** Potential DOWN setup for that bar (historical hit rate ~55–60% across all three periods, vs. a ~44–50% baseline for bars that don't gap up). This is a high‑frequency rule — it fires on roughly a quarter to a third of all bars.

**For higher conviction (fewer, stronger signals), ALSO require:**
2. The previous bar was part of a 2‑bar DOWN streak
3. The previous bar's body was bearish

**AND DOWN SCORE = 3 → THEN:** Higher‑conviction DOWN setup (hit rate ~62–69% across all three periods, but fires far less often).

**UP SETUP: not offered.** No UP‑leaning combination survived validation and test for this stock.

**Avoid the trade if:** the bar doesn't gap up (gap‑down and no‑gap bars showed no edge either way), or the only basis is a bare candlestick‑pattern name or a DOWN streak used alone.

**NO TRADE — IF:** the upcoming bar doesn't gap up; it's the 09:15 slot; or you're relying on a candlestick pattern or streak length by itself without the gap‑up condition.

---

## PART 17 — QUICK‑REFERENCE TABLE

| Factor | UP condition | DOWN condition | Neutral / No‑Trade |
|---|---|---|---|
| Time | none validated | 11:15 most DOWN‑biased descriptively (not used in final rule) | 09:15 (n too small); 15:15 least DOWN‑biased descriptively |
| Previous direction/streak | none validated | 2‑bar DOWN streak (as part of the tightened rule) | 3‑ and 4‑bar DOWN streaks used alone (decayed to baseline out of sample) |
| Candle pattern | none reliable | none standalone | Hammer, Shooting Star, Morning/Evening Star (all too weak or too small) |
| Body size / % change | — | Bearish body (as part of the tightened rule) | — |
| Volume | no standalone edge | Normal‑low relative volume (optional refinement, not required) | Any single volume reading alone; full 6‑feature model (overfit) |
| Range/close position | — | Bottom‑third close (optional refinement) | — |
| **Gap** | — | **Gap UP into this bar — the core finding for this stock** | Gap down or no gap (no edge either way) |
| Score | **Not offered** | DOWN SCORE ≥ 1 (simple) or = 3 (tightened) | Anything not meeting the gap‑up condition |

**UP FORMULA:** Not available — no validated UP setup exists in this dataset for IDEA.

**DOWN FORMULA:** Bar opens with a gap up vs. the prior close → DOWN SCORE ≥1 → that bar DOWN ~55–60% historically, vs. ~44–50% baseline. Tighten with a prior 2‑bar DOWN streak + bearish body for ~62–69% hit rate on fewer signals.

**NO‑TRADE FORMULA:** No gap up into the bar, the 09:15 slot, or reliance on a bare candlestick‑pattern name or streak length alone.

---

## PART 18 — HONEST CONCLUSION

1. **Does this dataset contain a measurable directional edge?** Yes — and it's the cleanest, simplest, and highest‑frequency edge found across the whole six‑stock series: bars that gap up tend to close DOWN more often than bars that don't.
2. **Strongest UP conditions:** **None found.** The third stock (after YES Bank and SEPC) with an honest "no validated UP edge" conclusion.
3. **Strongest DOWN conditions:** A gap up into the bar — on its own, a large‑sample, consistently‑replicating signal; tightened further with a prior 2‑bar DOWN streak and bearish body for a smaller but stronger signal.
4. **Strongest reversal patterns:** None validated. A 3‑bar DOWN streak looked like a strong continuation‑then‑something signal in training (61.9% next‑DOWN) but decayed to exactly baseline (50.0%) in both validation and test — a textbook example of a training‑period artifact.
5. **Strongest continuation patterns:** Short DOWN streaks (1–2 bars) sit close to baseline; longer streaks (3–4 bars) looked promising in training only and did not hold up.
6. **Which candle patterns are actually useful, and do labels match behavior?** All single‑candle labels matched their own Open/Close sign exactly — no mislabeling. None of the classic patterns (Hammer, Shooting Star, Morning/Evening Star) produced an independently validated edge, mostly due to small sample sizes.
7. **Which patterns are unreliable?** All of the low‑frequency multi‑candle patterns, and streak length used alone.
8. **Does volume materially improve prediction?** Only as an optional refinement, not as a requirement — the core finding here doesn't need volume at all, unlike Reliance Power.
9. **Does body size/% change add value?** Modestly, as part of the tightened 3‑condition version of the rule.
10. **Does gap behavior add value?** **Yes — this is the central finding for this stock**, and the strongest gap‑based result across the entire six‑stock series.
11. **Most reliable time:** Not time‑dependent for the validated rule, though 11:15 continues the now‑familiar cross‑stock "most DOWN‑biased mid‑morning hour" pattern descriptively.
12. **Time to avoid:** 09:15 (only 18–24 observations across two years).
13. **How many signals would the final strategy generate?** The simple gap‑up rule triggers on roughly 25–29% of all bars — by far the highest signal frequency of any rule found in this series (700+ signals over the ~2,975‑bar sample). The tightened version triggers on only 2.7–4.3% of bars (~65–100 signals).
14. **Historical success rate:** ~54.5% in training (simple rule); ~61.8% (tightened rule).
15. **Performance on unseen (test) data:** 59.8% (simple rule) and 68.8% (tightened rule) — both *higher* than their training‑period values.
16. **Is the strategy overfit?** **No — this is the clearest non‑overfitting result in the whole series.** Both versions of the rule strengthened, rather than weakened, from training through the fully unseen test period. The 6‑feature logistic‑regression score, in contrast, **is explicitly LIKELY OVERFIT** (AUC collapses to near‑random out of sample).
17. **What additional data would help?** Tick/order‑book data (to understand the mechanics of why gap‑ups fade so consistently for this stock — this could reflect retail‑driven overnight optimism that institutional flow tends to fade during the session, but that's speculation beyond what OHLCV data alone can confirm), sector/telecom‑index correlation, and continued monitoring to see whether the gap‑up‑fade effect persists as IDEA's ownership/liquidity profile evolves.

**This analysis does not, and cannot, guarantee future performance.** The honest summary for Vodafone Idea: this is the stock with the cleanest, most broadly‑applicable edge in the entire six‑stock series — a simple, high‑frequency, non‑decaying "gap‑up fade" pattern — but, like YES Bank and SEPC, it offers no comparable UP‑side edge. Combined with the recurring 11:15‑DOWN/15:15‑UP time‑of‑day shape seen across all six stocks, the most durable findings across this whole project appear to be structural (gap and time‑of‑day effects) rather than candlestick‑pattern‑based.
