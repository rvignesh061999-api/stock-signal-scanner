# Infosys (INFY.NS) — Hourly Candle Statistical Analysis
### Data: 2,964 hourly bars, 2024‑09‑10 to 2026‑09‑09 | Source: Yahoo Finance (as provided)

---

## PART 1 — DATA VALIDATION

| Check | Result |
|---|---|
| Total valid bars | 2,964 (matches header claim exactly) |
| Earliest bar | 2024‑09‑10 12:15 IST |
| Latest bar | 2026‑09‑09 15:15 IST |
| Trading dates covered | 494 |
| UP bars | 1,433 (48.3%) |
| DOWN bars | 1,506 (50.8%) |
| FLAT bars | **25 (0.8%) — by far the fewest of any of the eight stocks analyzed in this series** |
| Bars per time slot | 09:15 → 16, 10:15 → 491, 11:15 → 491, 12:15 → 492, 13:15 → 493, 14:15 → 494, 15:15 → 480 |
| Pattern counts | Bearish Candle 808, Bullish Candle 716, Doji 363, Strong Bearish 213, Strong Bullish 196, Bullish Engulfing 179, Evening Star 156, Bearish Engulfing 152, Morning Star 149, Shooting Star 25, Hammer 7 |
| Duplicate records | **0** (no duplicate Date+Time rows, no duplicate full rows) |
| High < Low | **0 occurrences** |
| Close outside High/Low | **0 occurrences** |
| Open outside High/Low | **0 occurrences** |
| Direction vs Close‑Open sign | **0 mismatches** in the entire dataset |
| Missing calendar dates | None beyond normal weekends/holidays |
| Bars per day | 457 days have exactly 6, 22 have 7 (extra 09:15 print), 12 days have 5, and 3 days have very short sessions (4, 2, 2 bars) — consistent with holiday/first/last‑day sessions |

**Things worth flagging (observations, not corrections):**

1. **This stock is fundamentally different from the seven small/mid‑cap names analyzed so far.** Infosys is a large‑cap, highly liquid, closely‑followed stock, and it shows it: only 25 FLAT bars in the entire two‑year, 2,964‑bar sample (0.8%), versus 4–13% in every other stock analyzed. A high‑value, high‑liquidity share almost never prints a bar with zero net change.
2. **Frozen bars (O=H=L=C) are essentially absent — just 1 of 2,964.** No illiquidity clustering of any kind, unlike the small‑cap names.
3. **Doji is, once again, not synonymous with FLAT**, but here it's much closer to a genuine three‑way split (171 DOWN, 168 UP, only 24 FLAT out of 363) — a further sign that even Infosys's smallest‑bodied bars rarely represent true "no movement."

**Conclusion of Part 1: the dataset is internally clean** — no fabricated OHLC, no impossible bars, no label/direction mismatches. The main takeaway from Part 1 is qualitative: this is a much more "efficient," actively‑traded stock than any analyzed previously in this series.

---

## PART 2 — DERIVED VARIABLES

Same full set computed from Open/High/Low/Close/Volume/Date/Time as in the seven prior reports: Range, Range %, Body size/%, Bar % change, upper/lower wick (absolute + % of range), body‑to‑range ratio, gap and gap % vs. previous close, close‑position tercile, BodyDir (cross‑checked, zero mismatches), volume vs. previous bar and vs. trailing 20‑bar rolling average, range/body change vs. previous bar, streak type/length, previous 2‑/3‑bar sequences, day‑of‑week, HH/HL/LH/LL flags, Close‑vs‑previous‑Close.

**Not calculated:** VWAP, RSI, MACD, tick/order‑book data, sector/index correlation — none derivable from the given columns.

---

## PARTS 3–11 — SEARCH FOR AN EDGE

**Same non‑circular methodology as the seven prior reports:** single‑candle pattern labels equal that bar's own Direction by definition (0 exceptions verified), so every result targets **NextDirection** using only information available once the current bar closes (or, for gaps, as soon as the next bar opens).

**Chronological split:** Train = 2024‑09‑10 → 2025‑12‑26 (1,926 rows), Validation = 2025‑12‑26 → 2026‑04‑20 (445 rows), Test = 2026‑04‑20 → 2026‑09‑09 (593 rows). No shuffling.

**Baseline to beat (train):** Next bar is UP 50.0% / DOWN 49.4% / FLAT 0.6%. **This is the headline finding of Part 3–11 all by itself: unlike every other stock analyzed in this series (which all showed a persistent 48–55% DOWN‑leaning baseline), Infosys is essentially a coin flip.** This is consistent with Infosys being a large, heavily‑covered, efficiently‑priced stock rather than a thinly‑traded small‑cap where retail order flow can create a persistent directional drift.

### PART 9 & 10 — Best setups found: both centered on the 14:15 hour, and genuinely mirror‑image of each other

| Setup | Train n / Rate | Val n / Rate | Test n / Rate | Verdict |
|---|---|---|---|---|
| **DOWN: 14:15 bar closed in the top third of its own range** | 107 / 66.4% DOWN | 31 / 61.3% DOWN | 26 / 65.4% DOWN | **The single most consistent finding for this stock** — a strong 14:15 close (near its own high) tends to be followed by a DOWN 15:15 bar |
| **UP: 14:15 bar has a bearish body (Close<Open)** | 162 / 61.1% UP | 33 / 48.5% UP (weak — barely above baseline) | 57 / 64.9% UP | Direction holds in training and test but dips close to baseline in validation — treat with somewhat lower confidence than the DOWN rule |
| UP (alternate framing): 14:15 bar closed in the bottom third of its own range | 107 / 61.7% UP | 25 / 44.0% UP (below baseline — inconsistent) | 46 / 76.1% UP | Striking in test, but the validation‑period reversal means this specific framing is not fully reliable — the "bearish body" version above is the safer choice |

**Component breakdown for the DOWN rule (why the combination matters):**

| Condition alone | Train DOWN% | Val DOWN% | Test DOWN% |
|---|---|---|---|
| Time = 14:15 only | 50.6% | 52.0% | 37.4% (!) |
| Closed in top third only (any time) | 50.5% | 55.5% | 61.8% |
| **14:15 + top‑third close** | **66.4%** | **61.3%** | **65.4%** |

This is a genuine mean‑reversion signal specific to the second‑to‑last hour of the trading day: a 14:15 bar that closes strong (near its own high) tends to give some of that back in the final 15:15 hour, and a 14:15 bar that closes weak (bearish body, or near its own low) tends to bounce back somewhat in the final hour. Both directions of this same underlying pattern show up, though the DOWN framing (top‑third close) is the more consistently‑replicating of the two.

### PART 6 — Candle‑pattern reliability (Pattern → NEXT bar, train)

| Pattern | n | Next UP% | Next DOWN% | Reliable? |
|---|---|---|---|---|
| Strong Bearish Candle | 123 | 53.7% | 46.3% | Close to baseline — this stock's near‑50/50 nature means even "strong" candles carry little forward information |
| Evening Star | 101 | 52.5% | 47.5% | No meaningful edge |
| Bullish Engulfing | 118 | 44.9% | 53.4% | Mild, not independently stress‑tested |
| Hammer | 5 | 20.0% | 80.0% | **Only 5 occurrences — statistically meaningless** |
| Doji (all) | 231 | 49.8% | 49.8% | Perfectly balanced — no signal whatsoever |
| Morning Star | 89 | 48.3% | 51.7% | No meaningful edge |
| Shooting Star | 17 | 52.9% | 47.1% | Sample too small |

**Label‑vs‑OHLC check:** all single‑candle labels matched Close‑vs‑Open sign with zero exceptions. **None of the classic candlestick patterns showed a meaningful edge for this stock** — every single one, including "Strong" variants, landed within a few points of the 49–50% coin‑flip baseline. This is a notably cleaner (i.e., more efficient) picture than any of the seven prior stocks.

### PART 7 — Sequence analysis (train)

| Streak (ending at bar just closed) | n | Next UP% | Next DOWN% |
|---|---|---|---|
| 1‑bar DOWN | 491 | 51.3% | 47.9% |
| 3‑bar DOWN | 119 | 52.1% | 47.9% |
| 5‑bar DOWN | 26 | 61.5% | 38.5% (small sample) |
| 1‑bar UP | 495 | 49.9% | 49.1% |
| 4‑bar UP | 56 | 42.9% | 57.1% (small sample) |

Every streak bucket sits within a few points of the 50/50 baseline — **streak length carries essentially no forward‑looking information for this stock**, a further sign of relative market efficiency compared to the small‑cap names in this series.

### PART 8 — Price structure & gaps

| Structure | n (train) | Next UP% | Next DOWN% |
|---|---|---|---|
| Higher High + Higher Low | 708 | 48.9% | 50.6% |
| Lower High + Lower Low | 704 | 51.1% | 48.2% |
| Mixed | 514 | 50.0% | 49.6% |

No meaningful separation whatsoever — essentially a coin flip in every structural category.

**Gap behavior — the one place this stock differs qualitatively from all seven prior stocks:** gap‑up bars showed a mildly elevated own‑bar UP rate (52.0% vs. 46.4% for gap‑down bars) — a **gap‑continuation** tendency rather than the gap‑fade tendency seen in most of the other stocks (though the effect is modest and wasn't independently re‑tested for robustness as a standalone rule). Gap fill rates are strikingly low here: only 7.1% of gap‑down bars and 7.2% of gap‑up bars close back through the prior close — **gaps essentially never fill same‑session for Infosys**, a far more pronounced version of the "gaps mostly don't fill" finding seen (to a lesser degree) in every other stock in this series.

---

## PART 5 — VOLUME ANALYSIS

Infosys's volume is modest and comparatively stable (roughly 700K–2M shares/hour across most of the sample, with a gradual step‑up in early‑to‑mid 2026), without the dramatic multi‑year escalation seen in PC Jeweller. Volume was tested as part of the systematic search but **did not end up being a necessary ingredient of either validated rule** — the close‑position and body‑direction conditions at the 14:15 hour did all the work.

A full 6‑feature logistic‑regression score (Time + Streak + BodyDir + relative Volume + close‑position + gap category) shows the same overfitting pattern seen in all seven prior reports — though here, given how close the underlying baseline already is to 50/50, the model has essentially nothing to work with:

| Split | Base DOWN rate | Model accuracy | Model AUC |
|---|---|---|---|
| Train | 49.4% | 52.5% | **0.542** |
| Validation | 52.6% | 49.9% | **0.504** (essentially random) |
| Test | 54.1% | 50.5% | **0.506** (essentially random) |

The model barely beats a coin flip even in training, and collapses to pure noise out of sample — **explicitly overfit and, in this case, barely informative even before testing it out of sample.**

---

## PART 4 — TIME‑OF‑DAY (train)

| Time | UP% | DOWN% | FLAT% | Avg range% | Avg chg% | n |
|---|---|---|---|---|---|---|
| 09:15 | 43.8% | 56.2% | 0% | 1.74% | +0.01% | 16 (too few to trust) |
| 10:15 | 49.2% | 50.2% | 0.6% | 0.68% | +0.01% | 319 |
| 11:15 | 51.7% | 47.6% | 0.6% | 0.55% | +0.02% | 319 |
| 12:15 | 52.4% | 47.0% | 0.6% | 0.53% | +0.02% | 319 |
| 13:15 | 49.4% | 50.3% | 0.3% | 0.52% | 0.00% | 320 |
| 14:15 | 49.1% | 50.6% | 0.3% | 0.59% | +0.01% | 320 |
| 15:15 | 48.6% | 50.5% | 0.9% | 0.34% | 0.00% | 313 |

**This is a genuine break from the pattern seen in all seven prior stocks.** Every other stock in this series showed a pronounced "mid‑morning DOWN bias, closing‑hour UP lean" shape — for Infosys, the whole day is nearly flat, with 11:15–12:15 actually leaning very slightly UP rather than DOWN, and no hour deviating from 50/50 by more than about 3 points (excluding the unreliable 09:15 slot). Average intraday ranges are also far smaller here (0.3–0.7% vs. 0.6–4.8% for the small‑cap names) — consistent with a much more heavily‑traded, efficiently‑priced stock. **The mid‑morning‑DOWN/closing‑hour‑UP shape does not appear to be universal — it shows up in small‑ and mid‑cap names with concentrated retail flow, but not (at least not here) in a heavily‑covered large‑cap.**

---

## PART 11 — NO‑TRADE CONDITIONS

| Condition | What the data shows | Why it's a NO‑TRADE zone |
|---|---|---|
| **09:15 slot** | Only 16 observations across the whole sample | Statistically unusable |
| **Any candlestick pattern alone** (Bearish/Bullish Candle, Strong variants, Engulfing, Star patterns) | Every single one landed within a few points of the 49–50% baseline | No standalone directional information anywhere in this dataset |
| **Streak length, any direction** | Every bucket sits within a few points of baseline | No standalone edge |
| **Structure (HH/HL/LH/LL)** | No separation from baseline in any category | No standalone edge |
| **Any hour other than 14:15** | No time slot other than 14:15 (combined with close position or body direction) produced a validated setup | Treat the rest of the day as no‑edge for this stock |
| **The "bottom‑third close" framing of the UP setup on its own** | Reversed in validation (44.0% UP, below baseline) | Use the "bearish body" framing instead, and treat even that with some caution given its own validation softness |

**NO‑TRADE rule:** for this stock specifically, the default should be NO TRADE for almost the entire trading day — only the 14:15 hour, combined with either a strong (top‑third) or weak (bearish‑bodied) close, showed any repeatable signal at all.

---

## PART 12 — SCORING SYSTEM

Following the same reasoning as the seven prior reports, a simple evidence‑backed checklist is used instead of a fitted multi‑factor score. For this stock, the checklist is unusually narrow — nearly the whole day carries no information, so the "score" is really a single time‑and‑shape condition.

**DOWN SCORE (0–1):**
- +1 if this is the **14:15** bar **and** it closed in the **top third** of its own range

**DOWN SCORE = 1 → historical DOWN rate for the 15:15 bar: 66.4% (train) / 61.3% (val) / 65.4% (test), vs. a ~49–54% baseline.**

**UP SCORE (0–1, lower confidence):**
- +1 if this is the **14:15** bar **and** it has a **bearish body** (Close < Open)

**UP SCORE = 1 → historical UP rate for the 15:15 bar: 61.1% (train) / 48.5% (val — weak) / 64.9% (test), vs. a ~46–50% baseline.**

**Thresholds:** DOWN SCORE = 1 → potential DOWN setup (higher confidence). UP SCORE = 1 → potential UP setup (lower confidence, given the validation‑period softness). Anything else → NO TRADE.

---

## PART 13 — REAL‑TIME DECISION FORMULA

```
CURRENT HOURLY BAR JUST CLOSED (Open, High, Low, Close, Volume known)
        │
        ▼
Is this the 14:15 bar?
        │
   NO ──┴──► NO TRADE (no validated setup exists for any other hour in this stock)
        │
       YES
        ▼
Did it close in the TOP THIRD of its own range?
   YES ─┼──► DOWN SCORE = 1 → POTENTIAL DOWN SETUP (for the 15:15 bar)
        │
   NO ──┴──► Does it have a BEARISH body (Close < Open)?
              YES ─┼──► UP SCORE = 1 → POTENTIAL UP SETUP (lower confidence)
              NO ──┴──► NO TRADE
```

---

## PART 14 — BACKTEST RESULTS (chronological, no shuffling)

| Metric | Train (65%, n=1,926) | Validation (15%, n=445) | Test (20%, n=593) |
|---|---|---|---|
| DOWN setup: trigger rate | 5.6% | 7.0% | 4.4% |
| DOWN setup: hit rate | 66.4% | 61.3% | 65.4% |
| Baseline DOWN rate | 49.4% | 52.6% | 54.1% |
| UP setup: trigger rate | 8.4% | 7.4% | 9.6% |
| UP setup: hit rate | 61.1% | 48.5% | 64.9% |
| Baseline UP rate | 50.0% | 47.4%* | 45.9%* |

*implied from the split's own DOWN/FLAT rates.

**Is this overfit?** **No, for the DOWN rule** — its hit rate is tight and consistent across all three windows (66.4/61.3/65.4%), comfortably above baseline throughout. **Mixed evidence for the UP rule** — it holds up well in training and test (61.1%, 64.9%) but sits almost exactly at baseline in validation (48.5%), which is a softer result than any of the primary rules found for the seven prior stocks. I'm presenting it as a real but lower‑confidence finding rather than rejecting it outright, since two of the three windows show a clear, consistent edge. The 6‑feature logistic‑regression score, by contrast, **is explicitly LIKELY OVERFIT and barely informative even in training** (AUC 0.542, collapsing to ~0.50 out of sample).

---

## PART 15 — ROBUSTNESS CHECKS

- **Volume regime:** modest, gradually increasing but no extreme multi‑year shift; not a confound, and volume wasn't needed for either rule.
- **Threshold sensitivity:** the DOWN rule's edge is entirely dependent on the specific 14:15 + top‑third combination — neither the time nor the close‑position condition alone comes close to matching it (component table, Part 9/10) — this is a genuine "cliff," meaning the combination, not a general tendency, is what's doing the work.
- **Different time periods:** the DOWN rule replicated cleanly across all three windows. The UP rule showed one weak window (validation) sandwiched between two strong ones (training, test) — worth monitoring rather than fully trusting.
- **Frozen‑bar/illiquidity concerns:** essentially none for this stock (1 frozen bar total).
- **High‑ vs low‑volatility subperiods:** not separately re‑tested beyond the three chronological splits, same limitation as all seven prior reports.

---

## PART 16 — FINAL TRADING RULES (plain language)

**DOWN SETUP — IF:**
1. The just‑closed hourly bar is the **14:15** bar
2. That bar closed in the **top third** of its own High‑Low range

**AND DOWN SCORE = 1 → THEN:** Potential DOWN setup for the 15:15 (final) bar (historical hit rate ~61–66% across all three periods, vs. a ~49–54% baseline).

**UP SETUP (lower confidence) — IF:**
1. The just‑closed hourly bar is the **14:15** bar
2. That bar's body is bearish (Close < Open)

**AND UP SCORE = 1 → THEN:** Potential UP setup for the 15:15 bar (historical hit rate ~49–65% — solid in training and test, weak in validation; treat with more caution than the DOWN rule).

**Avoid the trade if:** it's any hour other than 14:15, or the only basis is a bare candlestick‑pattern name or a streak — none of these carried any signal for this stock.

**NO TRADE — IF:** it's any hour other than 14:15 (this is the default state for nearly the entire trading day for this stock); it's the 09:15 slot; or you're relying on a candlestick pattern, streak, or structural (HH/HL) reading alone.

---

## PART 17 — QUICK‑REFERENCE TABLE

| Factor | UP condition | DOWN condition | Neutral / No‑Trade |
|---|---|---|---|
| Time | **14:15** (with bearish body) | **14:15** (with top‑third close) | Every other hour of the day — no edge found anywhere else |
| Previous direction/streak | none validated | none validated | Streak length alone, any direction — no signal at all for this stock |
| Candle pattern | none reliable | none reliable | **Every classic pattern** (Bullish/Bearish Candle, Strong variants, Engulfing, Star patterns) — all within a few points of 50/50 |
| Body size / % change | Bearish body at 14:15 (as part of combo) | — | — |
| Volume | not required | not required | Any single volume reading alone; full 6‑feature model (overfit and barely informative even in training) |
| Range/close position | — | Top‑third close at 14:15 (as part of combo) | — |
| Gap | — | — | Gap‑up shows a mild continuation tendency (opposite of the fade seen elsewhere), not independently validated as a rule; gaps essentially never fill same‑session (only ~7%) |
| Sequence | — | — | No edge anywhere |
| Score | UP SCORE = 1 (lower confidence) | DOWN SCORE = 1 | Anything outside the 14:15 hour |

**UP FORMULA:** 14:15 bar with a bearish body → UP SCORE 1 → 15:15 bar UP ~49–65% historically (solid in two of three windows), vs. ~46–50% baseline.

**DOWN FORMULA:** 14:15 bar closed in the top third of its own range → DOWN SCORE 1 → 15:15 bar DOWN ~61–66% historically, vs. ~49–54% baseline — the most consistent finding for this stock.

**NO‑TRADE FORMULA:** Any hour other than 14:15, the 09:15 slot, or reliance on a candlestick pattern, streak, or structural reading alone.

---

## PART 18 — HONEST CONCLUSION

1. **Does this dataset contain a measurable directional edge?** A narrow one — confined almost entirely to the 14:15 hour, in a stock whose overall baseline is otherwise essentially a 50/50 coin flip.
2. **Strongest UP conditions:** A 14:15 bar with a bearish body → next bar (15:15) UP more often than baseline, though the effect softened noticeably in the validation window.
3. **Strongest DOWN conditions:** A 14:15 bar closing in the top third of its own range → next bar (15:15) DOWN more often than baseline — the single most consistent finding for this stock.
4. **Strongest reversal patterns:** The 14:15‑hour findings themselves are best understood as a short‑term mean‑reversion effect in the final trading hour, rather than a classic multi‑candle reversal pattern.
5. **Strongest continuation patterns:** None found — streak length carried essentially no information anywhere in this dataset.
6. **Which candle patterns are actually useful, and do labels match behavior?** All single‑candle labels matched their own Open/Close sign exactly — no mislabeling. **Uniquely among the eight stocks in this series, not a single classic candlestick pattern (including "Strong" variants) showed a meaningful edge** — every one landed within a few points of 50/50.
7. **Which patterns are unreliable?** All of them, for this stock — Bullish/Bearish Candle, Strong Bullish/Bearish, Engulfing, Morning/Evening Star, Hammer, Shooting Star, Doji all showed essentially coin‑flip next‑bar behavior.
8. **Does volume materially improve prediction?** No standalone effect found, and it wasn't required for either of the two 14:15‑hour rules.
9. **Does body size/% change add value?** Yes — bearish body direction at 14:15 is the key ingredient of the (lower‑confidence) UP rule.
10. **Does gap behavior add value?** Not independently validated as a standalone rule, though a mild gap‑continuation tendency (rather than the gap‑fade seen in most other stocks) was observed, and gaps essentially never fill same‑session for this stock (~7% fill rate, the lowest in the series).
11. **Most reliable time:** 14:15, and only 14:15 — no other hour showed any edge in either direction.
12. **Time to avoid:** Every hour except 14:15 should be treated as a no‑edge zone for this stock; 09:15 additionally suffers from too few observations (16) to trust regardless.
13. **How many signals would the final strategy generate?** DOWN setup: ~4.4–7.0% of bars (roughly 130–210 signals over the ~2,960‑bar sample). UP setup: ~7.4–9.6% of bars (roughly 220–285 signals), though with the caveat that its validation‑period performance was weak.
14. **Historical success rate:** DOWN ≈ 66.4% in training; UP ≈ 61.1% in training.
15. **Performance on unseen (test) data:** DOWN 65.4% (essentially unchanged from training); UP 64.9% (also strong, despite the weak validation reading).
16. **Is the strategy overfit?** **No, for the DOWN rule** — consistent across all three windows. **Uncertain for the UP rule** — strong in training and test but weak in validation; I'm not calling this "likely overfit" outright since two of three windows show a clear edge, but it deserves more scrutiny than the DOWN rule before being relied upon. The 6‑feature logistic‑regression score **is explicitly overfit and barely informative even in training** given how close to 50/50 this stock's baseline already is.
17. **What additional data would help?** Tick/order‑book data (to understand what specifically drives the 14:15‑hour mean‑reversion effect — this could reflect pre‑close institutional rebalancing or algorithmic flow patterns common in large, heavily‑covered stocks), Nifty/IT‑sector index correlation (Infosys is a bellwether IT stock, and its near‑50/50 baseline may partly reflect broader index efficiency rather than anything stock‑specific), and continued monitoring of the UP rule's validation‑period softness with more data.

**This analysis does not, and cannot, guarantee future performance.** The honest summary for Infosys: this is a qualitatively different stock from the seven small‑ and mid‑caps analyzed earlier in this series — its overall next‑bar direction is close to a coin flip, none of the classic candlestick patterns carry any edge, and the mid‑morning‑DOWN/closing‑hour‑UP shape seen in every other stock analyzed does not appear here. The one real, repeatable finding is a narrow mean‑reversion effect specific to the 14:15 hour — a genuinely modest edge in an otherwise efficiently‑priced stock, which is itself a useful and honest finding: not every stock has a strong intraday drift to exploit.
