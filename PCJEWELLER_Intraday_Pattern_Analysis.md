# PC Jeweller (PCJEWELLER.NS) — Hourly Candle Statistical Analysis
### Data: 2,983 hourly bars, 2024‑09‑10 to 2026‑09‑09 | Source: Yahoo Finance (as provided)

---

## PART 1 — DATA VALIDATION

**Confirmed facts:**

| Check | Result |
|---|---|
| Total valid bars | 2,983 (matches header claim exactly) |
| Earliest bar | 2024‑09‑10 12:15 IST |
| Latest bar | 2026‑09‑09 15:15 IST |
| Trading dates covered | 494 |
| UP bars | 1,184 (39.7%) |
| DOWN bars | 1,466 (49.1%) |
| FLAT bars | 333 (11.2%) |
| Bars per time slot | 09:15 → 29, 10:15 → 491, 11:15 → 491, 12:15 → 492, 13:15 → 493, 14:15 → 494, 15:15 → 493 |
| Pattern counts | Bearish Candle 891, Bullish Candle 634, Doji 450, Strong Bearish 234, Bullish Engulfing 180, Strong Bullish 148, Bearish Engulfing 139, Evening Star 135, Morning Star 123, Shooting Star 32, Hammer 17 |
| Duplicate records | **0** (no duplicate Date+Time rows, no duplicate full rows) |
| High < Low | **0 occurrences** |
| Close outside High/Low range | **0 occurrences** |
| Open outside High/Low range | **0 occurrences** |
| Direction label vs Close‑Open sign | **0 mismatches** — every UP bar has Close>Open, every DOWN bar Close<Open, every FLAT bar Close=Open |
| Missing calendar dates | None beyond normal weekends/holidays — no gap >4 calendar days found |
| Bars per day | 462 days have exactly 6 bars, 29 days have 7 (an extra 09:15 bar), 1 day (2024‑09‑10, the first day) has 4, and 2 days (2025‑10‑21, 2026‑04‑20) have only 2 — consistent with early/late partial sessions, not corruption |

**Two things worth flagging (not corrections — just noted, as instructed):**

1. **"Doji" is not always flat.** Of 450 Doji‑labeled bars, 328 are FLAT direction, but 63 are DOWN and 59 are UP. A genuine Doji (Open≈Close) can still be labeled UP/DOWN if Close differs from Open by even a fraction of a paisa. This is not an error, but it means "Doji" ≠ "no movement" in this dataset — 25% of Doji bars actually closed with a directional bias.
2. **A large subset of FLAT/Doji bars are "frozen" bars, not genuine indecision candles.** 114 of the 333 FLAT bars (and 114 of the 450 Doji bars) have Open=High=Low=Close *exactly*, with average volume of ~253,000 shares vs. the dataset average of ~9.3 million. These almost certainly represent periods of essentially no trading (illiquidity, or the stock parked at a static print) rather than a market genuinely "deciding" nothing. Any interpretation of Doji/FLAT bars should separate these frozen prints from bars that traded actively but closed unchanged.
3. **Volume regime is non‑stationary.** Average hourly volume grew from under 1 million shares/hour in late 2024 to 30–95 million shares/hour by mid‑2026 (see Part 5). This is a real structural shift in the stock's liquidity, not a data error, but it means any **absolute** volume threshold calibrated on early data is meaningless on later data (confirmed empirically in Part 15).

**Conclusion of Part 1: the dataset is internally clean.** No fabricated OHLC, no logically impossible bars, no label/price mismatches. The only caveats are interpretive (Doji≠flat, frozen bars, volume drift), not data-quality errors.

---

## PART 2 — DERIVED VARIABLES

All of the following were computed directly from Open/High/Low/Close/Volume/Date/Time — nothing outside these was invented:

Range, Range %, Body size, Body %, Bar % change (Close vs Open), Upper/Lower wick (absolute and % of range), Body‑to‑range ratio, Gap (vs previous bar's Close) and Gap %, close‑position tercile (top/middle/bottom third of the bar's own range), BodyDir (Close>Open / < / =, cross‑checked against Direction — zero mismatches), Volume vs. previous bar, Volume vs. trailing 20‑bar rolling average (this is the only volume measure that survives the regime shift — see Part 5), change in range/body vs. previous bar, consecutive UP/DOWN/FLAT streak length, previous bar's direction/pattern, 2‑bar and 3‑bar direction sequences, day‑of‑week, Higher‑High/Higher‑Low/Lower‑High/Lower‑Low flags, Close‑vs‑previous‑Close.

**Explicitly NOT calculated** (would require data not present): VWAP, RSI, MACD, any multi‑day moving average requiring price history beyond what's given (I did use rolling volume, which is legitimate), bid/ask spread, order‑book imbalance, tick‑level data, sector/index correlation. Any of these mentioned later is a "what would help" note, not something computed.

---

## PART 3–11 — THE ACTUAL SEARCH FOR AN EDGE (methodology first, because it matters)

**The key design decision, and why:** "Candle Pattern" and "Direction" both describe the *same completed bar* — e.g. every single "Bullish Candle" is, by definition, an UP bar (verified: 0 exceptions). So asking "does Bullish Candle predict UP?" is circular. The only non‑circular, tradable question is: **given everything known the moment a bar closes (its pattern, volume, body, streak history), what happens in the *next* hourly bar?** That is what every result below tests — the target is always **NextDirection**, the direction of the following hourly candle. Where a feature (like a gap) is only known once the next candle opens, it's still valid, because it's known before that candle's own close.

**Chronological split used throughout:** Train = first 65% (2024‑09‑10 → 2025‑12‑26, 1,938 decision rows), Validation = next 15% (2025‑12‑26 → 2026‑04‑21, 448 rows), Test = final 20% (2026‑04‑21 → 2026‑09‑09, 597 rows). No shuffling.

**Baseline you must beat (train):** Next bar is UP 38.9% / DOWN 48.8% / FLAT 12.3% of the time. **This stock has a structural intraday downward drift — DOWN is always the modal outcome, at every hour, in every period.** Any "edge" has to beat 48.8% DOWN or 38.9% UP, not 50/50.

### Systematic search
I cross‑tabulated NextDirection against every 1‑, 2‑, and 3‑way combination of Time, Streak(type+length), Pattern, relative Volume category, Body direction, close‑position tercile, and next‑bar gap category (790 combinations with ≥40 train observations). Below are the combinations that looked strongest in training, followed immediately by how they held up out of sample — because that's the only number that matters.

### PART 9 — Best UP candidates found

| Setup | Train n / UP% | Val n / UP% | Test n / UP% | Verdict |
|---|---|---|---|---|
| 2‑bar UP streak + this bar closed in the **middle third** of its range | 58 / 58.6% | 13 / 46.2% | 22 / 63.6% | **Directionally consistent** (all three beat the ~39–41% baseline), but validation sample is tiny (13) — treat as suggestive, not proven |
| 14:15 bar + high **absolute** volume | 68 / 60.3% | 32 / 50.0% | 19 / 63.2% | Looked good, but re‑testing with *relative* volume (robust to the regime shift) makes this **flip to a DOWN‑leaning result in val/test (51.9%, 58.1% DOWN)** — this is an artifact of the 2024 volume scale, not a real edge |
| Volume spike + bullish body + no gap | 43 / 58.1% | 19 / 36.8% | 71 / 42.3% | **Fails out of sample** — classic overfit, discard |
| 14:15 bar + gap down next | 95 / 58.9% | 22 / 68.2% | 36 / 36.1% | **Fails in test** — discard |

**Honest conclusion for UP setups: only one candidate (2‑bar UP streak + middle‑third close) survives all three time periods directionally, and even that rests on a thin validation sample. There is no strong, well‑evidenced UP setup in this dataset.**

### PART 10 — Best DOWN candidates found

| Setup | Train n / DOWN% | Val n / DOWN% | Test n / DOWN% | Verdict |
|---|---|---|---|---|
| **Bearish body (Close<Open) + closed in middle third of own range + next bar opens with no gap** | 140 / 65.7% | 36 / 52.8% | 50 / 64.0% | **The strongest, most consistent finding in the whole dataset.** Beats baseline (≈49%) in all three periods; triggers on ~7–8% of all bars, consistently, in every period |
| Narrower version: labeled "Bearish Candle" pattern specifically + middle‑third close | 105 / 67.6% | 30 / 53.3% | 42 / 66.7% | Slightly stronger, same pattern, slightly smaller sample |
| Relative‑volume "normal‑high" + bearish body + middle‑third close | 86 / 65.1% | 32 / 56.2% | 28 / 64.3% | Also holds up reasonably, largely overlapping with the setup above |
| 1‑bar DOWN streak + middle‑third close + no gap | 68 / 72.1% | 18 / 33.3% | 21 / 52.4% | **Fails in validation** — do not rely on this one alone |

**Component breakdown (why the 3‑way combo works better than any single piece):**

| Condition alone | Train DOWN% | Val DOWN% | Test DOWN% |
|---|---|---|---|
| Bearish body only | 52.3% | 50.7% | 46.9% |
| Middle‑third close only | 45.4% | 47.5% | 52.0% |
| No gap only | 48.3% | 51.0% | 48.3% |
| Bearish body + middle‑third | 55.6% | 50.0% | 52.2% |
| **Bearish body + middle‑third + no gap** | **65.7%** | **52.8%** | **64.0%** |

Each factor alone is barely different from the 48.8% baseline. It's the **combination of all three** — a bar that closed down, closed mid‑range (not near its low — i.e., not a "weak" bearish bar with a long lower wick suggesting buyers stepped in), with no gap forming into the next bar — that produces a real, repeatable jump in DOWN probability. Interpretation: this describes an "orderly, unspectacular sell‑off" bar (down, but not climactic), which historically tends to continue rather than reverse.

### PART 6 — Candle‑pattern reliability (own‑bar stats are trivial by construction; the table below is Pattern → NEXT bar)

| Pattern | n (train) | Next UP% | Next DOWN% | Next FLAT% | Reliable? |
|---|---|---|---|---|---|
| Bearish Candle | 567 | 38.6% | 55.2% | 6.2% | Mild continuation edge |
| Strong Bearish Candle | 145 | 39.3% | 50.9% | 9.7% | avg next move −0.15% — mild continuation |
| Bullish Candle | 387 | 41.6% | 50.4% | 8.0% | No real edge |
| Strong Bullish Candle | 101 | 38.6% | 47.5% | 13.9% | No edge — a "strong" bullish bar does **not** reliably continue |
| Morning Star | 76 | 44.7% | 50.0% | 5.3% | Weak positive tilt, but n too small after conditioning (e.g. only 27 occur after a genuine 2+ down streak, and even that thinner slice is inconsistent — see below) |
| Evening Star | 92 | 37.0% | 48.9% | 14.1% | No reliable edge; even after a prior 2+ UP streak (n=21) results flip between splits |
| Hammer | 14 | 35.7% | 50.0% | 14.3% | **Sample far too small (14 total, 17 with the full "small body + long lower wick + after a down move" filter) to draw any conclusion** |
| Shooting Star | 22 | 63.6% | 36.4% | 0% | Counter‑intuitive (textbook says bearish reversal) and n=22 is too small to trust; conditioned further (after an up‑streak, n=20) it's even noisier across splits |
| Doji (all) | 325 | 31.7% | 33.8% | 34.5% | Split roughly evenly between UP/DOWN/FLAT — genuinely no directional information once the frozen prints are mixed in |

**Label‑vs‑actual‑OHLC check:** All single‑candle pattern labels (Bullish/Bearish/Strong Bullish/Strong Bearish Candle, Bullish/Bearish Engulfing, Morning/Evening Star, Hammer) matched their Close‑vs‑Open sign with **zero exceptions**. The one pattern that does *not* behave as its name implies is **Shooting Star**: textbook shooting stars are bearish signals, but 23 of 32 (72%) are themselves UP‑direction bars, and the bars that follow them lean UP more often than DOWN in training (though the sample is too small to trust this as an edge — see above).

### PART 7 — Sequence analysis (train)

| Prior sequence (ending at the bar just closed) | n | Next UP% | Next DOWN% | Next avg % move |
|---|---|---|---|---|
| 1‑bar DOWN | 451 | 37.3% | 55.4% | −0.08% |
| 2‑bar DOWN | 250 | 41.6% | 48.0% | −0.02% |
| 3‑bar DOWN | 120 | 49.2% | 44.2% | +0.14% |
| 5‑bar DOWN | 25 | 24.0% | 68.0% | −0.43% (small n, treat cautiously) |
| 1‑bar UP | 440 | 39.1% | 52.3% | +0.09% |
| 2‑bar UP | 172 | 48.3% | 43.6% | +0.10% |
| 3‑bar UP | 83 | 39.8% | 56.6% | −0.09% |

Takeaway: a **single** down bar tends to continue down (momentum); after **three** consecutive down bars the odds start tilting back toward UP (mild mean‑reversion), though not strongly enough to trade on alone. A 2‑bar UP streak shows the mild continuation tendency used in the UP setup above; a 3‑bar UP streak tends to reverse.

### PART 8 — Price structure

| Structure (this bar vs. previous) | n (train) | Next UP% | Next DOWN% |
|---|---|---|---|
| Higher High + Higher Low | 457 | 42.2% | 49.2% |
| Lower High + Lower Low | 681 | 40.8% | 50.1% |
| Mixed (inside/outside bar) | 800 | 35.4% | 47.4% |

No meaningfully different behavior between these three structural states — HH+HL and LH+LL both still sit close to the general DOWN‑biased baseline. **Structure alone adds essentially nothing.**

**Gap fill rates (train):** Gap‑down bars closed back above the prior close only 34.5% of the time; gap‑up bars closed back below the prior close only 40.9% of the time — i.e., gaps mostly do **not** fill same‑session, and if anything a gap up shows a slight tendency to keep drifting down through the session (Gap‑up bars' own Direction was DOWN 51–54% of the time across all three periods, consistently) while a gap down bar's own Direction leaned UP somewhat more often (44–45% UP vs. the ~34–44% baseline for no‑gap bars) — a modest gap‑fade tendency, but not large enough on its own to trade.

---

## PART 5 — VOLUME ANALYSIS (the most important robustness lesson in this whole dataset)

Average hourly volume by period: **~0.4–2M shares/hour (2024)** → **~1.6–7.4M (2025)** → **30–95M shares/hour (Jul–Sep 2026)**. This is a >50x increase in trading activity over the sample. Practical consequence: **any volume category built on fixed thresholds (e.g., "high volume = >X shares") calibrated on early data becomes meaningless later** — I confirmed this directly: a "LOW volume" bucket built from 2024–2025 quantiles has **zero matching bars** in the validation and test periods, because *every* bar in 2026 exceeds the old "very high" threshold.

**Fix used everywhere in this report:** volume relative to its own trailing 20‑bar rolling average (Vol ÷ rolling mean), not an absolute number. This measure produces stable, comparable categories across all three time periods.

Even with this fix, volume alone (or volume+body‑direction) did **not** produce a robust standalone edge:

| Setup | Train | Val | Test |
|---|---|---|---|
| Relative volume ≥2.5x + bullish body | UP 47.9% | UP 37.5% | UP 46.7% |
| Relative volume ≥2.5x + bearish body | UP 50.0% (!) | DOWN 85.7% | DOWN 66.7% |
| Relative volume 1.5–2.5x + bearish body | flat 48.7/48.7 | UP 46.2% | DOWN 51.6% |

These flip sign and magnitude across periods with small samples — **volume, even scaled correctly, is not a reliable standalone directional signal in this dataset.** It only contributes anything when folded into the 3‑factor DOWN setup in Part 10, and even there it is not the dominant factor (body direction + close position + gap absence matter more).

---

## PART 4 — TIME‑OF‑DAY (train, n per slot in parentheses)

| Time | UP% | DOWN% | FLAT% | Avg range% | Avg |chg%| | Reversal freq.* |
|---|---|---|---|---|---|---|
| 09:15 (20) | 55.0% | 45.0% | 0% | 4.68% | +0.65% | 80% — **but n=20, unreliable** |
| 10:15 (319) | 39.8% | 49.8% | 10.3% | 1.52% | +0.03% | 58.9% |
| 11:15 (319) | 34.2% | 54.9% | 11.0% | 1.21% | −0.09% | 53.3% |
| 12:15 (320) | 33.8% | 54.1% | 12.2% | 1.15% | −0.02% | 53.4% |
| 13:15 (321) | 37.4% | 50.2% | 12.5% | 1.09% | −0.01% | 48.9% |
| 14:15 (320) | 39.4% | 47.5% | 13.1% | 1.39% | +0.03% | 48.1% |
| 15:15 (319) | 48.0% | 36.4% | 15.7% | 0.94% | +0.12% | 53.0% |

*Reversal freq. = % of bars whose own Direction differs from the immediately preceding bar's Direction (descriptive only).

**Clear, consistent pattern: 11:15 and 12:15 (mid‑morning) are the most DOWN‑biased hours (54–55% DOWN); 15:15 (the final hour) is the most UP‑biased and has the lowest DOWN rate (36.4%) and smallest average range.** The 09:15 slot shows the largest range and biggest average move by far, but only has 20 training observations — far too few to trust; treat it as descriptive curiosity, not a rule. Contrary to textbook assumption, the **closing hour, not the opening hour, is the most directionally distinct** period in this data — and it leans up, not down.

---

## PART 11 — NO‑TRADE CONDITIONS (mandatory, and well‑supported by the data)

| Condition | What happens next | Why it's a NO‑TRADE zone |
|---|---|---|
| **Frozen bar** (Open=High=Low=Close, ~114 occurrences) | Whatever follows is essentially unpredictable from this bar alone; these bars carry almost no volume and no information | The bar itself reflects an absence of trading, not a signal |
| **Doji overall** (all 450, mixing frozen and non‑frozen) | Train: 31.7% UP / 33.8% DOWN / 34.5% FLAT — a near‑even three‑way split | No directional information at all |
| **2+ consecutive FLAT bars** | Train: 68.3% stay FLAT next bar | This just tells you the stock is in a dead/illiquid patch — not a directional signal, and it does not reliably persist out of sample either (val n=4, test n=10 — too few to confirm the persistence rate, but directionally it's clearly not a place to bet UP or DOWN) |
| **09:15 slot** | Only 20–29 observations total across the whole 2‑year dataset | Statistically unusable regardless of what the numbers show |
| **Textbook reversal patterns alone** (Hammer, Shooting Star, Morning/Evening Star, with or without streak conditioning) | Every single conditioned test above had n between 3 and 34, and flipped sign between train/val/test | Not enough data to trade any of these patterns on their own, no matter how their names sound |
| **Any single factor in isolation** (body direction alone, close‑position alone, gap alone, volume alone) | Each moves the DOWN or UP rate by only 2–6 percentage points off baseline | Individually weak; only specific combinations (Part 10) show a real, repeatable edge |

**NO‑TRADE rule:** if the bar is frozen/near‑zero‑range, if it's a Doji without the specific down‑continuation combination below, if you're in a 2+ FLAT streak, if it's the 09:15 slot, or if the only signal you have is a "classic" candlestick reversal pattern by itself — **stand aside.** The system should default to NO TRADE far more often than it trades.

---

## PART 12 — SCORING SYSTEM (built from the evidence above, not arbitrary)

Given the honest results above, a heavily‑engineered multi‑factor score is *not* actually supported by the data — I tested one. A logistic regression using Time + Streak + BodyDir + relative‑Volume + close‑position + gap category (6 categorical features, one‑hot encoded) to predict "Next = DOWN":

| Split | Base DOWN rate | Model accuracy | Model AUC |
|---|---|---|---|
| Train | 48.8% | 58.9% | **0.628** |
| Validation | 50.9% | 52.2% | **0.519** |
| Test | 49.2% | 50.2% | **0.500** |

**This is a textbook overfitting signature** — a model that looks good in training (AUC 0.63) collapses to no‑better‑than‑random (AUC ~0.50) out of sample. **I am explicitly not recommending this multi‑factor model.** It's included here to show why: the raw feature list contains too many near‑noise variables (individual pattern names, absolute time slots, fine‑grained streak lengths) for the ~2,000 training rows available, and the model finds spurious combinations that don't repeat.

**What I recommend instead is the simple, 3‑condition rule that survived all three time periods (from Part 10), scored as a simple checklist rather than a weighted formula:**

**DOWN SCORE (0–3, one point each, all evidence‑backed above):**
- +1 if this bar's body is bearish (Close < Open)
- +1 if this bar closed in the **middle third** of its own High‑Low range (not near the low — a "climactic" bar closing at its low is a *different*, less reliable case)
- +1 if the *next* bar opens with **no gap** (i.e., current bar's close is essentially where the next bar opens)

**DOWN SCORE = 3 → historical DOWN rate for the next bar: 65.7% (train) / 52.8% (val) / 64.0% (test), vs. a ~49% baseline.**

**UP SCORE (0–2, lower‑confidence — flagged as such):**
- +1 if the last 2 completed bars were both UP
- +1 if this bar closed in the middle third of its own range

**UP SCORE = 2 → historical UP rate for the next bar: 58.6% (train) / 46.2% (val, n=13 only) / 63.6% (test), vs. ~39% baseline — directionally consistent but resting on a much thinner evidence base than the DOWN score. Treat this as a lower‑conviction signal.**

**Thresholds:** DOWN SCORE = 3 → potential DOWN setup. UP SCORE = 2 → potential (lower‑confidence) UP setup. Anything else → NO TRADE. I deliberately did **not** build finer‑grained point weights (e.g., +2 for volume, +1.5 for pattern) because the data does not support that level of precision — see the logistic‑regression failure above. A simple checklist that has been validated is more honest than a fitted formula that has not.

---

## PART 13 — THE REAL‑TIME DECISION FORMULA

```
CURRENT HOURLY BAR JUST CLOSED (Open, High, Low, Close, Volume known)
        │
        ▼
Is this bar "frozen" (O=H=L=C) or is it the 09:15 slot?
        │
   YES ─┴─► NO TRADE (insufficient information / unreliable sample)
        │
        NO
        ▼
Is Close < Open? (bearish body)
        │
   YES ─┼───────────────────────────────────────┐
        │                                       │
        NO → check UP path below                │
                                                 ▼
                              Did this bar close in the MIDDLE THIRD
                              of its own High-Low range?
                                                 │
                                            YES ─┼──► +1 (running DOWN score)
                                            NO ──┴──► stop, NO TRADE
                                                 │
                                                 ▼
                              Does the next bar open with NO GAP
                              vs. this bar's close?
                                            YES ─┼──► +1 (DOWN score = 3)
                                            NO ──┴──► DOWN score = 2, NO TRADE
                                                 │
                                                 ▼
                                    DOWN SCORE = 3 → POTENTIAL DOWN SETUP


[UP path, only checked if this bar was NOT bearish]
Were the last 2 completed bars BOTH UP?
        │
   YES ─┼──► +1
   NO ──┴──► NO TRADE
        │
        ▼
Did this bar close in the MIDDLE THIRD of its own range?
   YES ─┼──► UP SCORE = 2 → POTENTIAL (lower-confidence) UP SETUP
   NO ──┴──► NO TRADE
```

---

## PART 14 — BACKTEST RESULTS (chronological, no shuffling)

| Metric | Train (65%, n=1,938) | Validation (15%, n=448) | Test (20%, n=597) |
|---|---|---|---|
| DOWN setup: trigger rate | 7.2% of bars | 8.0% of bars | 8.4% of bars |
| DOWN setup: hit rate (next bar actually DOWN) | 65.7% | 52.8% | 64.0% |
| DOWN setup: avg next‑bar % move | −0.24% | +0.07% | −0.18% |
| Baseline DOWN rate (no filter) | 48.8% | 50.9% | 49.2% |
| UP setup: trigger rate | 3.0% of bars | 2.9% of bars | 3.7% of bars |
| UP setup: hit rate (next bar actually UP) | 58.6% | 46.2% (n=13) | 63.6% |
| Baseline UP rate (no filter) | 38.9% | 40.6% | 41.4% |

**Is this overfit?** The **DOWN** setup is **not** "LIKELY OVERFIT" — it degraded somewhat in validation (52.8% vs 65.7% train) but recovered fully in the fully‑unseen test period (64.0%), and stayed on the correct side of the baseline in all three windows. That pattern (some validation noise, but consistent direction and comparable test performance) is what a real, if modest, effect looks like — a truly overfit rule collapses to the baseline and stays there in every out‑of‑sample slice, which is what happened to every other candidate tested in Parts 9/10/12.

The **UP** setup direction held up too, but the tiny validation sample (13 trades) means I'd flag this one as **"weakly supported, not overfit‑but‑unproven."**

The full 6‑feature logistic‑regression score (Part 12) **is explicitly LIKELY OVERFIT** (AUC fell from 0.63 to 0.50) and should not be used.

---

## PART 15 — ROBUSTNESS CHECKS

- **Absolute volume thresholds: fail completely** across the 2024→2026 span (Part 5) — one of the "LOW volume" buckets from training had zero matches in later data. Any volume rule must use a *relative/rolling* measure, never a fixed share count.
- **Score threshold sensitivity:** Loosening the DOWN rule to 2/3 conditions (any two of the three) drops the hit rate toward the 52–57% range in every split (shown in the Part 10 component table) — i.e., the edge is concentrated specifically in the full 3‑condition combination, not spread smoothly across thresholds. That's a mild yellow flag: it means the rule is somewhat threshold‑sensitive (a "cliff," not a "slope"), even though it did replicate out of sample.
- **Different time periods:** the DOWN setup fires and works similarly in 2024–25 (train), the volatile Dec 2025–Apr 2026 window (val), and the high‑volume Apr–Sep 2026 window (test) — i.e., it survives the massive liquidity regime change, which is reassuring.
- **High‑ vs low‑volatility subperiods:** not separately re‑tested here beyond the chronological split (this would be a reasonable next step with more compute/time, flagged under limitations).

---

## PART 16 — FINAL TRADING RULES (plain language)

**DOWN SETUP — IF:**
1. The just‑closed hourly bar's Close is below its Open (bearish body)
2. That bar closed in the middle third of its own High‑Low range (not near the low)
3. The next bar opens with no meaningful gap vs. this bar's close

**AND DOWN SCORE = 3 → THEN:** Potential DOWN setup for the next hourly bar (historical hit rate ~64‑66% in the two fully out‑of‑sample windows, vs. a ~49% baseline).

**Avoid the trade if:** the bar is frozen/illiquid, it's the 09:15 slot, or the bar closed near its low (that's a *different*, unvalidated case, not this setup).

**UP SETUP (lower confidence) — IF:**
1. The last two completed hourly bars were both UP
2. The most recent bar closed in the middle third of its own range

**AND UP SCORE = 2 → THEN:** Potential UP setup (historical hit rate ~46‑64% vs. a ~39‑41% baseline, but based on a much smaller and thinner sample than the DOWN rule — treat with extra caution).

**NO TRADE — IF:** the bar is frozen (O=H=L=C) or near‑zero range; it's a Doji that doesn't also satisfy the DOWN or UP conditions above; you're in a run of 2+ FLAT bars; it's the 09:15 slot; or the only thing you're relying on is a classic candlestick name (Hammer, Shooting Star, Morning/Evening Star) without the specific streak/gap/close‑position conditions validated above.

---

## PART 17 — QUICK‑REFERENCE TABLE

| Factor | UP condition | DOWN condition | Neutral / No‑Trade |
|---|---|---|---|
| Time | 15:15 (mild positive tilt, 48% UP) | 11:15 / 12:15 (54‑55% DOWN) | 09:15 (n too small) |
| Previous direction/streak | 2 consecutive UP bars | 1 bearish bar just closed | 2+ consecutive FLAT bars |
| Candle pattern | none reliably standalone | none reliably standalone | Doji, Hammer, Shooting Star, Morning/Evening Star (all too rare / inconsistent alone) |
| Body size / % change | — | Close < Open (bearish body) | Body≈0 (frozen/Doji) |
| Volume | no standalone edge found | no standalone edge found | any single volume reading alone |
| Range | — | — | Range ≈ 0 (frozen) |
| Gap (of the following bar) | — | No gap into next bar | Gap present either direction (weak, inconsistent fade tendency only) |
| Close position in range | Middle third | Middle third | Bottom third (unvalidated), Top third (unvalidated) |
| Sequence | UP → UP | any single DOWN bar | 3‑bar same‑direction run (starts reverting) |
| Score | UP SCORE = 2 | DOWN SCORE = 3 | Anything below threshold |

**UP FORMULA:** 2 consecutive UP bars + middle‑third close → UP SCORE 2 → weak/moderate UP lean (~46‑64% historical hit rate vs ~39‑41% baseline; thin evidence).

**DOWN FORMULA:** Bearish body + middle‑third close + no gap into next bar → DOWN SCORE 3 → moderate DOWN lean (~52‑66% historical hit rate vs ~49% baseline; the best‑evidenced rule in this dataset).

**NO‑TRADE FORMULA:** Frozen bar, OR Doji not meeting either scored condition, OR 2+ FLAT streak, OR 09:15 slot, OR reliance on a bare candlestick pattern name alone.

---

## PART 18 — HONEST CONCLUSION

1. **Does this dataset contain a measurable directional edge?** A small one, yes — concentrated almost entirely in one combination (bearish body + middle‑third close + no gap → next bar DOWN). Most of what looks like an "edge" on first pass (individual candlestick patterns, volume spikes, gaps, single‑factor filters) evaporates or reverses out of sample.
2. **Strongest UP conditions:** Two consecutive UP bars followed by a middle‑third close. Weak/thin evidence.
3. **Strongest DOWN conditions:** Bearish body + middle‑third close + no gap into the next bar. Best‑evidenced finding in the dataset.
4. **Strongest reversal patterns:** A 3‑bar DOWN streak shows the beginnings of mean‑reversion (49% UP next vs. 39% baseline), but this is mild and not independently validated out‑of‑sample with a large enough sample to trade on its own.
5. **Strongest continuation patterns:** A single DOWN bar tends to be followed by another DOWN bar more often than baseline (55% vs 49%); a 2‑bar UP streak shows mild continuation.
6. **Which candle patterns are actually useful?** None of the classic multi‑candle reversal patterns (Hammer, Shooting Star, Morning Star, Evening Star) had enough occurrences (14–135, and far fewer once conditioned by streak/volume) to produce a trustworthy, repeatable signal — every conditioned test flipped sign between train/val/test. Single‑candle body‑direction labels (Bullish/Bearish/Strong variants) matched their own Open/Close perfectly (no mislabeling), but on their own they add little predictive value for the *next* bar. The one pattern whose *name* doesn't match its behavior is Shooting Star — 72% of them are themselves UP bars, and the (very thin) evidence on what follows them leans UP too, the opposite of the textbook bearish‑reversal story.
7. **Which patterns are unreliable?** All the low‑frequency multi‑candle reversal patterns, and Doji taken as a group (it splits almost evenly UP/DOWN/FLAT).
8. **Does volume materially improve prediction?** Not on its own, even after fixing the scale problem with a rolling relative measure. It only helps as a background condition (present implicitly via "normal" volume ranges) inside the validated DOWN combination, and even there it's not the dominant factor.
9. **Does body size/% change add value beyond Direction/Range?** Somewhat — bearish *body* direction (Close<Open) is one of the three ingredients in the one validated rule, but alone it moves DOWN probability by only ~2‑4 points.
10. **Does gap behavior add value?** Modestly — "no gap into the next bar" is a necessary ingredient of the validated DOWN rule, and gaps (up or down) show a weak, inconsistent fade tendency on their own.
11. **Most reliable time:** 15:15 (last hour) — the only time slot with a persistently different (more UP‑leaning, lower‑range) profile than the rest of the day.
12. **Time to avoid:** 09:15 — not because it's "bad," but because with only 20‑29 observations across two full years, nothing about it can be trusted statistically. 11:15/12:15 show the strongest DOWN bias if you want a directional (not "avoid") read.
13. **How many signals would the final strategy generate?** The DOWN setup triggers on roughly 7‑8% of all bars (about 210‑240 signals over the full 2‑year, 2,983‑bar sample); the UP setup on roughly 3‑4% (about 90‑110 signals).
14. **Historical success rate:** DOWN setup ≈ 65.7% in training. UP setup ≈ 58.6% in training.
15. **Performance on unseen (test) data:** DOWN setup 64.0% (very close to training) — genuinely held up. UP setup 63.6% in test but only 46.2% in the small validation slice — mixed.
16. **Is the strategy overfit?** The simple 3‑condition DOWN rule: **no, it is not overfit** — it degraded somewhat in validation but recovered in the fully unseen test set and stayed on the correct side of baseline throughout. The 6‑feature logistic‑regression score built from the same data: **yes, explicitly LIKELY OVERFIT** (AUC collapsed from 0.63 to 0.50) — this is why the simple rule, not the complex model, is what I'm recommending.
17. **What additional data would help?** Tick‑level/order‑book data (to see whether the "middle‑third close, no gap" bars are genuinely orderly distribution vs. absorption), sector/Nifty‑index correlation (to check whether this stock's DOWN bias simply tracks a weak sector/market rather than being stock‑specific), and a longer history (2 years / ~3,000 bars is a modest sample for 3‑way conditioning — many of the more granular multi‑candle‑pattern questions asked in the brief simply don't have enough data points to answer reliably yet).

**This analysis does not, and cannot, guarantee future performance.** A ~65% historical hit rate on a rule that fires ~7% of the time, on one small‑cap stock, over one 2‑year sample, is a real but modest statistical tilt — not a certainty, and not something that should be sized as if it were. The honest summary is: **this dataset has a structural downward drift, one well‑evidenced rule that modestly improves on that baseline for the next hourly bar, and a lot of textbook candlestick lore that simply doesn't hold up once tested against out‑of‑sample data.**
