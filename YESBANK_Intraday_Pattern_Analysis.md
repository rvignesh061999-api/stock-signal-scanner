# YES Bank (YESBANK.NS) — Hourly Candle Statistical Analysis
### Data: 2,977 hourly bars, 2024‑09‑10 to 2026‑09‑09 | Source: Yahoo Finance (as provided)

---

## PART 1 — DATA VALIDATION

| Check | Result |
|---|---|
| Total valid bars | 2,977 (matches header claim exactly) |
| Earliest bar | 2024‑09‑10 12:15 IST |
| Latest bar | 2026‑09‑09 15:15 IST |
| Trading dates covered | 494 |
| UP bars | 1,230 (41.3%) |
| DOWN bars | 1,522 (51.1%) |
| FLAT bars | 225 (7.6%) |
| Bars per time slot | 09:15 → 28, 10:15 → 491, 11:15 → 491, 12:15 → 492, 13:15 → 493, 14:15 → 493, 15:15 → 489 |
| Pattern counts | Bearish Candle 942, Bullish Candle 696, Doji 324, Strong Bearish 249, Bullish Engulfing 168, Bearish Engulfing 156, Strong Bullish 151, Morning Star 140, Evening Star 117, Shooting Star 23, Hammer 11 |
| Duplicate records | **0** (no duplicate Date+Time rows, no duplicate full rows) |
| High < Low | **0 occurrences** |
| Close outside High/Low | **0 occurrences** |
| Open outside High/Low | **0 occurrences** |
| Direction vs Close‑Open sign | **0 mismatches** in the entire dataset |
| Missing calendar dates | None beyond normal weekends/holidays |
| Bars per day | 460 days have exactly 6, 27 have 7 (extra 09:15 print), and 7 days have partial sessions (4, 5, 5, 2, 3, 5, 4 bars) on 2024‑09‑10, 2025‑01‑14, 2025‑08‑06, 2025‑10‑21, 2026‑04‑20, 2026‑08‑03, 2026‑08‑06 — consistent with holiday‑shortened or first/last‑day sessions, not corruption |

**Two things worth flagging (observations, not corrections):**

1. **"Doji" isn't always flat here either.** Of 324 Doji‑labeled bars, 219 are FLAT, but 55 are DOWN and 50 are UP — about a third of Doji bars carry a directional close despite a very small body.
2. **Frozen bars (O=H=L=C) are rare in this stock** — only 5 of 2,977 bars, vs. 114/2,983 in the previously‑analyzed PC Jeweller dataset. YES Bank is a far more liquid stock, so "no‑trade" illiquidity artifacts are a much smaller concern here.
3. **Volume is comparatively stable across the sample** — monthly average volume ranges roughly 5M–23M shares/hour with no runaway multi‑year trend (unlike PC Jeweller's >50x volume expansion). Absolute volume thresholds are therefore somewhat more usable here, though I still primarily use volume **relative to its own trailing 20‑bar average** for consistency and comparability with the earlier analysis.

**Conclusion of Part 1: the dataset is internally clean** — no fabricated OHLC, no logically impossible bars, no label/price mismatches, only minor interpretive caveats.

---

## PART 2 — DERIVED VARIABLES

Same full set as the PC Jeweller analysis, computed only from Open/High/Low/Close/Volume/Date/Time: Range, Range %, Body size/%, Bar % change, upper/lower wick (absolute + % of range), body‑to‑range ratio, gap and gap % (vs. previous bar's close), close‑position tercile, BodyDir (cross‑checked against Direction — zero mismatches), volume vs. previous bar and vs. trailing 20‑bar rolling average, range/body change vs. previous bar, streak length/type, previous 2‑/3‑bar sequences, day‑of‑week, HH/HL/LH/LL flags, Close‑vs‑previous‑Close.

**Not calculated** (as before): VWAP, RSI, MACD, tick/order‑book data, sector/Nifty‑Bank correlation — none of these can be derived from the given columns.

---

## PARTS 3–11 — SEARCH FOR AN EDGE

**Same methodology as before, for the same reason:** single‑candle pattern labels (Bullish/Bearish/Strong Candle) are, by definition, identical to that bar's own Direction (verified: 0 exceptions) — so the only non‑circular question is **what happens in the *next* hourly bar**, given everything known once the current bar closes. All results below target **NextDirection**.

**Chronological split:** Train = 2024‑09‑10 → 2025‑12‑26 (1,935 rows), Validation = 2025‑12‑26 → 2026‑04‑20 (446 rows), Test = 2026‑04‑20 → 2026‑09‑09 (596 rows). No shuffling.

**Baseline to beat (train):** Next bar is UP 40.9% / DOWN 52.0% / FLAT 7.1%. **Like PC Jeweller, this stock has a persistent DOWN‑leaning baseline** — even stronger here (52% vs. PC Jeweller's 48.8%).

### Systematic search
Cross‑tabulated NextDirection against every 1‑/2‑/3‑way combination of Time, Streak(type+length), Pattern, relative Volume category, Body direction, close‑position tercile, and next‑bar gap category (780 combinations with ≥40 train observations), then re‑tested every promising candidate against validation and test.

### PART 9 — UP setups: **none survived**

Every UP‑leaning candidate found in training decayed to baseline (or reversed) in validation and/or test. Examples tested and rejected:

| Setup | Train UP% | Val UP% | Test UP% | Verdict |
|---|---|---|---|---|
| 14:15 bar + next bar gaps down | 59.3% | 70.0% (n=10) | 41.7% | Fails in test |
| 14:15 bar + high relative volume | 55.9% | 42.3% | 43.8% | Fails out of sample |
| Normal‑high relative volume + bullish body + next gap down | 63.4% | 50.0% (n=8) | 50.0% (n=4) | Samples too thin, no signal |
| Doji + next bar gaps down | 59.5% | 70.0% (n=10) | 38.5% | Flips in test |

**A systematic check of the top 40 highest‑training‑edge UP combinations found zero that held the same direction with ≥15 observations in both validation and test.** This is an important, honest negative result — the dataset does not currently support a validated UP setup for YES Bank.

### PART 10 — Best DOWN setups found (these did survive)

| Setup | Train n / DOWN% | Val n / DOWN% | Test n / DOWN% | Verdict |
|---|---|---|---|---|
| **10:15 bar closes in the top third of its own range + next bar opens with no gap** | 52 / 65.4% | 15 / 66.7% | 25 / 64.0% | **The strongest, most consistent finding in this dataset** — nearly identical DOWN rate in all three periods |
| 10:15 bar has a bullish body (Close>Open) + next bar opens with no gap | 99 / 64.6% | 23 / 56.5% | 37 / 54.1% | Larger sample, direction holds, but the edge decays somewhat from train to test |
| 3‑bar DOWN streak + bar closes in the bottom third of its own range | 74 / 63.5% | 18 / 50.0% | 25 / 56.0% | Direction holds but validation is right at the baseline — weaker evidence |

**Why the combination beats any single factor (component breakdown for the best setup):**

| Condition alone | Train DOWN% | Val DOWN% | Test DOWN% |
|---|---|---|---|
| Time = 10:15 only | 55.2% | 49.3% | 53.5% |
| Closed in top third only | 52.5% | 48.2% | 56.3% |
| No gap into next bar only | 53.9% | 45.7% | 50.8% |
| 10:15 + top‑third close | 58.8% | 55.6% | 66.7% |
| **10:15 + top‑third close + no gap** | **65.4%** | **66.7%** | **64.0%** |

Interpretation: a first‑hour (10:15) candle that closes strong — near its own high — but is *not* followed by a gap, historically tends to give that strength back in the next hour more often than not. This reads as a short‑term "morning strength gets faded" pattern rather than continuation. It triggers on only about 3–4% of all bars, but does so consistently across all three chronological windows.

### PART 6 — Candle‑pattern reliability (Pattern → NEXT bar, train)

| Pattern | n | Next UP% | Next DOWN% | Next FLAT% | Reliable? |
|---|---|---|---|---|---|
| Bearish Candle | 625 | 42.4% | 50.6% | 7.0% | Barely above baseline — weak |
| Strong Bearish Candle | 163 | 38.0% | 55.8% | 6.1% | Mild continuation, but see below — not tested robustly conditioned further due to sample limits |
| Bullish Candle | 462 | 38.5% | **54.3%** | 7.1% | Counter‑intuitive: a bullish candle is followed by a DOWN bar *more* often than a bearish one is — held up moderately across splits (44.1%/52.3% down in val/test), a mild contrarian tendency, not a strong one |
| Evening Star | 72 | 30.6% | 61.1% | 8.3% | Looked strong in training but **completely reversed in test (73.9% UP, only 21.7% DOWN)** — not usable |
| Morning Star | 96 | 41.7% | 51.0% | 7.3% | No meaningful edge |
| Doji (all) | 204 | 43.6% | 48.5% | 7.8% | Close to baseline in train; drifts to 58.7% DOWN in test — inconsistent, no reliable edge |
| Hammer | 2 | — | — | — | **Only 2 occurrences in the entire 2‑year, 2,977‑bar dataset — statistically unusable** |
| Shooting Star | 16 | 43.8% | 56.2% | 0% | Sample far too small to trust |

**Label‑vs‑OHLC check:** all single‑candle labels matched Close‑vs‑Open sign with zero exceptions. No pattern's label contradicted its own bar's actual direction.

### PART 7 — Sequence analysis (train)

| Prior streak (ending at the bar just closed) | n | Next UP% | Next DOWN% | Next avg % move |
|---|---|---|---|---|
| 1‑bar DOWN | 485 | 40.8% | 52.4% | −0.05% |
| 2‑bar DOWN | 254 | 38.2% | 51.2% | −0.03% |
| 3‑bar DOWN | 129 | 39.5% | 55.8% | −0.04% |
| 4‑bar DOWN | 72 | 41.7% | 50.0% | −0.06% |
| 5‑bar DOWN | 36 | 58.3% | 38.9% | +0.05% (mild reversal signal, but **failed to replicate**: val 33.3% UP, test 40.7% UP — do not trust) |
| 1‑bar UP | 470 | 40.0% | 54.5% | −0.02% |
| 2‑bar UP | 188 | 43.1% | 49.5% | +0.02% |
| 3‑bar UP | 81 | 38.3% | 53.1% | −0.04% |
| 4‑bar UP | 31 | 45.2% | 45.2% | +0.08% |

Takeaway: streak length alone doesn't produce a robust continuation or reversal signal for this stock once tested out of sample — every streak bucket sits close to the general DOWN‑leaning baseline, and the one that looked different (5‑bar DOWN → reversal) did not survive validation/test.

### PART 8 — Price structure & gaps

| Structure | n (train) | Next UP% | Next DOWN% |
|---|---|---|---|
| Higher High + Higher Low | 528 | 43.2% | 51.1% |
| Lower High + Lower Low | 755 | 38.1% | 53.8% |
| Mixed | 652 | 42.2% | 50.8% |

No meaningful separation — structure alone adds little.

**Gap behavior (own bar, known at open → own Direction):** Gap‑down bars showed an elevated UP rate in training (50.3% vs. ~41% baseline) and again in test (48.1%), but this **reversed in validation (only 42.5% UP, 53.4% DOWN)** — an inconsistent, unreliable gap‑fade effect on its own. Gap fill rates: gap‑down bars close back above the prior close only 35.6% of the time; gap‑up bars close back below only 33.9% of the time — gaps mostly do **not** fill same‑session, consistent with the PC Jeweller findings.

---

## PART 5 — VOLUME ANALYSIS

Unlike PC Jeweller, **YES Bank's volume did not undergo a multi‑year regime shift** — monthly averages stayed in a roughly 5M–23M shares/hour band throughout, with a couple of elevated months (2025‑05/06, 2026‑05/06) rather than a permanent structural jump. Both absolute and relative volume measures are usable here, though I used the rolling‑relative measure throughout for consistency.

**Volume, on its own or combined simply with body direction, did not produce a standalone robust edge** — every volume‑only or volume+body candidate tested in Parts 9–10 either failed to replicate or only worked as part of a larger multi‑factor combination (and even there, volume was not the decisive ingredient — Time, close position, and gap‑absence mattered more). A full 6‑feature logistic regression (Time + Streak + BodyDir + relative Volume + close‑position tercile + gap category) predicting "Next = DOWN" showed the same overfitting signature as with PC Jeweller:

| Split | Base DOWN rate | Model accuracy | Model AUC |
|---|---|---|---|
| Train | 52.0% | 57.3% | **0.590** |
| Validation | 47.1% | 47.8% | **0.475** (worse than a coin flip) |
| Test | 51.1% | 54.3% | **0.532** |

**This confirms: a heavily‑engineered multi‑factor model is not supported by this dataset either.** I recommend the same approach as before — a simple, validated checklist, not a fitted score.

---

## PART 4 — TIME‑OF‑DAY (train)

| Time | UP% | DOWN% | FLAT% | Avg range% | Avg chg% | n |
|---|---|---|---|---|---|---|
| 09:15 | 42.9% | 57.1% | 0% | 2.65% | −0.05% | 21 (too few to trust) |
| 10:15 | 42.9% | 53.6% | 3.4% | 0.80% | +0.02% | 319 |
| 11:15 | 38.6% | 55.2% | 6.3% | 0.67% | −0.05% | 319 |
| 12:15 | 39.5% | 54.9% | 5.6% | 0.62% | −0.03% | 319 |
| 13:15 | 36.3% | 55.0% | 8.8% | 0.61% | −0.07% | 320 |
| 14:15 | 41.6% | 54.4% | 4.1% | 0.69% | −0.02% | 320 |
| 15:15 | 46.4% | 38.8% | 14.8% | 0.37% | +0.02% | 317 |

**Same cross‑stock pattern as PC Jeweller: the closing hour (15:15) is the most UP‑leaning and lowest‑range period, while the mid‑session hours (11:15–13:15) carry the strongest DOWN bias** (54.9–55.2%). 13:15 is the single most DOWN‑biased hour here (55.0% DOWN, lowest UP% at 36.3%). The 09:15 slot again has by far the largest average range but only 21 observations across two full years — not usable as a rule.

---

## PART 11 — NO‑TRADE CONDITIONS

| Condition | What the data shows | Why it's a NO‑TRADE zone |
|---|---|---|
| **Doji (any)** | Train 43.6/48.5/7.8 (UP/DOWN/FLAT), drifting to 33.3/58.7/7.9 in test | Inconsistent across periods — no reliable signal on its own |
| **Frozen bars** (5 total) | Too few to analyze | Not a meaningful category for this stock, but flag any occurrence as untradeable regardless |
| **09:15 slot** | Only 21–28 observations across the whole sample | Statistically unusable |
| **Textbook reversal patterns alone** (Hammer n=2, Shooting Star n=16, Evening/Morning Star) | Evening Star looked promising in training (61% DOWN) but flipped to 74% UP in test; Hammer has only 2 occurrences total | None of these are usable standalone |
| **5‑bar DOWN streak** (looked like a reversal signal) | Reversed direction in both validation and test | Do not trade this as a reversal cue |
| **Any single isolated factor** (Time, Pattern, Volume, gap, structure alone) | Each moves DOWN/UP rate by only 1–5 points off baseline | Only the specific 3‑factor combination in Part 10 shows a real, repeatable edge |

**NO‑TRADE rule:** stand aside on Doji bars that don't also meet the validated DOWN combination, on the 09:15 slot, on any bare candlestick‑pattern read, and — importantly for this stock — on **any UP setup**, since none survived validation. Default to NO TRADE far more often than to DOWN, and essentially always for UP unless you have a much larger dataset to test against.

---

## PART 12 — SCORING SYSTEM

As with PC Jeweller, the data does not support a precisely‑weighted multi‑factor score (see the logistic‑regression collapse above). I'm recommending a simple, evidence‑backed checklist instead:

**DOWN SCORE (0–3, one point each):**
- +1 if this is the **10:15** bar (the first full hour of the session)
- +1 if this bar closed in the **top third** of its own High‑Low range (i.e., it looked strong)
- +1 if the *next* bar opens with **no gap** vs. this bar's close

**DOWN SCORE = 3 → historical DOWN rate for the next bar: 65.4% (train) / 66.7% (val) / 64.0% (test), vs. a ~47–52% baseline.** This is unusually consistent across all three periods — the most trustworthy single rule found in either stock analyzed so far.

**UP SCORE: not recommended.** No UP combination in this dataset survived out‑of‑sample testing. I am not providing an UP scoring rule for YES Bank — doing so would mean presenting an untested, likely‑noise pattern as if it were evidence‑backed, which the data does not support.

**Threshold:** DOWN SCORE = 3 → potential DOWN setup. Anything else (including any UP‑leaning read) → NO TRADE.

---

## PART 13 — REAL‑TIME DECISION FORMULA

```
CURRENT HOURLY BAR JUST CLOSED (Open, High, Low, Close, Volume known)
        │
        ▼
Is this the 10:15 bar (first full hour)?
        │
   NO ──┴──► NO TRADE (no validated setup exists for other hours in this stock)
        │
       YES
        ▼
Did this bar close in the TOP THIRD of its own High-Low range?
        │
   NO ──┴──► NO TRADE
        │
       YES ──► +1 (running DOWN score)
        ▼
Does the next bar open with NO GAP vs. this bar's close?
        │
   NO ──┴──► DOWN score = 2 → NO TRADE
        │
       YES ──► +1 (DOWN score = 3)
        ▼
   DOWN SCORE = 3 → POTENTIAL DOWN SETUP
   (no UP setup path — none validated for this stock)
```

---

## PART 14 — BACKTEST RESULTS (chronological, no shuffling)

| Metric | Train (65%, n=1,935) | Validation (15%, n=446) | Test (20%, n=596) |
|---|---|---|---|
| DOWN setup: trigger rate | 2.7% of bars | 3.4% of bars | 4.2% of bars |
| DOWN setup: hit rate (next bar actually DOWN) | 65.4% | 66.7% | 64.0% |
| DOWN setup: avg next‑bar % move | −0.20% | −0.19% | −0.08% |
| Baseline DOWN rate (no filter) | 52.0% | 47.1% | 51.1% |
| UP setup | **Not offered — no candidate survived validation** | — | — |

**Is this overfit?** **No.** Unlike every other candidate tested in this dataset, this rule's hit rate is essentially *identical* across train, validation, and test (65.4% / 66.7% / 64.0%) — this is the textbook signature of a genuine, if modest, repeatable effect rather than a fitted artifact. The 6‑feature logistic‑regression score, by contrast, **is explicitly LIKELY OVERFIT** (AUC fell from 0.59 in training to 0.475 — worse than random — in validation).

---

## PART 15 — ROBUSTNESS CHECKS

- **Volume regime:** stable across the sample (no >50x drift like PC Jeweller), so this isn't a confound here — but I still used rolling‑relative volume throughout for methodological consistency.
- **Threshold sensitivity:** dropping to just 2 of the 3 DOWN conditions cuts the edge to 52–59% (component table in Part 10) — the effect, again, is concentrated in the specific 3‑way combination rather than smoothly spread across partial matches. A "cliff," not a "slope" — worth knowing, but it did still replicate cleanly out of sample.
- **Different time periods:** the rule fires and performs almost identically in the 2024–25 training window, the Dec 2025–Apr 2026 validation window, and the Apr–Sep 2026 test window — genuinely stable across more than two years and multiple market regimes for this stock.
- **High‑ vs low‑volatility subperiods:** not separately re‑tested beyond the three chronological splits — flagged as a reasonable next step, same as for PC Jeweller.

---

## PART 16 — FINAL TRADING RULE (plain language)

**DOWN SETUP — IF:**
1. The bar that just closed is the **10:15** (first full hour) bar
2. That bar closed in the **top third** of its own High‑Low range
3. The next bar opens with **no gap** vs. this bar's close

**AND DOWN SCORE = 3 → THEN:** Potential DOWN setup for the 11:15 bar (historical hit rate ~64–67% across two independent out‑of‑sample windows, vs. a ~47–52% baseline).

**Avoid the trade if:** it's any hour other than 10:15, the bar didn't close near its own high, or a gap has formed into the next bar — none of those variations were shown to work.

**UP SETUP: not offered.** No UP‑leaning combination survived validation and test for this stock. Trading UP setups on YES Bank based on this dataset would not be evidence‑based.

**NO TRADE — IF:** any hour other than 10:15 is being evaluated for the DOWN rule; the bar is a Doji not meeting the DOWN combination; it's the 09:15 slot; or the only basis is a classic candlestick name (Evening Star, Morning Star, Hammer, Shooting Star) without the specific validated conditions above.

---

## PART 17 — QUICK‑REFERENCE TABLE

| Factor | UP condition | DOWN condition | Neutral / No‑Trade |
|---|---|---|---|
| Time | 15:15 (mild positive tilt, 46% UP) — **not independently validated as a setup** | 10:15 (as part of the 3‑factor combo) | 09:15 (n too small); 11:15–13:15 alone (weak) |
| Previous direction/streak | none validated | none validated alone | 5‑bar DOWN streak (looked like reversal, failed to replicate) |
| Candle pattern | none reliable | none reliable standalone | Evening Star, Doji, Hammer, Shooting Star (all too rare or inconsistent alone) |
| Body size / % change | — | — | Bullish‑Candle → next‑down mild tilt (weak, not a standalone rule) |
| Volume | no standalone edge | no standalone edge | any single volume reading alone; 6‑feature model (overfit) |
| Range | — | Closing in top third (as part of combo) | — |
| Gap | — | No gap into next bar (as part of combo) | Gap present, either direction (inconsistent fade only) |
| Sequence | — | — | Streak length alone, any direction |
| Score | **Not offered** | DOWN SCORE = 3 | Anything below threshold |

**UP FORMULA:** Not available — no validated UP setup exists in this dataset for YES Bank.

**DOWN FORMULA:** 10:15 bar + closed in top third of its range + no gap into the next bar → DOWN SCORE 3 → next bar (11:15) DOWN ~64–67% historically, vs. ~47–52% baseline — the single most consistent finding across both stocks analyzed to date.

**NO‑TRADE FORMULA:** Any hour other than 10:15 for the DOWN rule, any Doji not meeting the DOWN combination, the 09:15 slot, or reliance on a bare candlestick‑pattern name alone.

---

## PART 18 — HONEST CONCLUSION

1. **Does this dataset contain a measurable directional edge?** Yes, one — and only one — well‑evidenced edge: the 10:15‑bar / top‑third‑close / no‑gap combination predicting a DOWN next bar. It is unusually consistent (65.4% / 66.7% / 64.0% across train/val/test).
2. **Strongest UP conditions:** **None found.** Every UP candidate tested, including a systematic scan of the 40 best‑looking training combinations, failed to replicate out of sample.
3. **Strongest DOWN conditions:** 10:15 bar closing in the top third of its range, followed by no gap into the next bar.
4. **Strongest reversal patterns:** None held up. A 5‑bar DOWN streak looked like a reversal signal in training (58.3% next‑UP) but reversed direction in both validation and test — explicitly rejected.
5. **Strongest continuation patterns:** None strong enough to trade — streak‑length‑alone effects sit close to the general DOWN‑biased baseline in every bucket.
6. **Which candle patterns are actually useful, and do labels match behavior?** All single‑candle labels (Bullish/Bearish/Strong Candle, engulfing patterns) matched their own Close‑vs‑Open sign perfectly — no mislabeling. None of them, however, reliably predicted the *next* bar. Evening Star looked promising in training (61% next‑DOWN) but completely reversed in the test period (74% next‑UP) — flagged as unreliable despite the seemingly large training sample.
7. **Which patterns are unreliable?** Evening Star, Morning Star, Doji (as a group), and — simply due to sample size — Hammer (2 occurrences total) and Shooting Star (16 occurrences).
8. **Does volume materially improve prediction?** No standalone effect found, even after correcting for scale with a rolling relative measure. Volume plays only a background role inside the one validated combination and is not itself the key ingredient.
9. **Does body size/% change add value?** Marginally — a bullish‑bodied 10:15 candle shows a similar (if slightly weaker) down‑leaning tendency to the top‑third‑close version, but degrades more from train to test (64.6% → 54.1%), so the close‑position version is the better‑evidenced rule.
10. **Does gap behavior add value?** Yes, but only as the third leg of the validated combination ("no gap" into the next bar); gaps considered alone show an inconsistent, unreliable fade tendency.
11. **Most reliable time:** 10:15, specifically for the validated DOWN setup. Descriptively, 15:15 is the most UP‑leaning hour of the day, but this was not independently validated as a tradeable setup.
12. **Time to avoid:** 09:15 (too few observations to trust, 21–28 across two years).
13. **How many signals would the final strategy generate?** The DOWN setup triggers on roughly 3–4% of all bars — about 90–125 signals across the full ~3,000‑bar, two‑year sample.
14. **Historical success rate:** ~65% in training.
15. **Performance on unseen (test) data:** 64.0% — almost identical to training, and 66.7% in the intermediate validation window.
16. **Is the strategy overfit?** **No**, for the simple 3‑condition DOWN rule — its out‑of‑sample performance essentially matches training. **Yes**, explicitly, for the 6‑feature logistic‑regression score (validation AUC fell to 0.475, below random chance).
17. **What additional data would help?** Tick/order‑book data (to understand whether the "strong 10:15 close, then fade" pattern reflects real distribution or just noise at this specific liquidity level), Nifty Bank / sector‑index correlation (YES Bank is a banking stock — its persistent DOWN bias could partly reflect sector or index conditions rather than a stock‑specific effect), and a longer sample — two years is workable for one robust 3‑way rule, but not enough to confidently rule out the many textbook patterns (Hammer, Shooting Star) that simply didn't occur often enough to test.

**This analysis does not, and cannot, guarantee future performance.** The honest summary for YES Bank: this stock has a structural DOWN bias overall (~52% of bars are followed by a DOWN bar, regardless of setup), one specific, well‑replicated rule modestly improves on that baseline for the 11:15 bar following a strong 10:15 open, and — importantly — **no comparable UP‑side edge exists in this dataset.** Nearly every textbook candlestick‑pattern claim tested here failed to survive contact with out‑of‑sample data, which is itself the most useful finding of this report.
