# Lab 16 — Provenance Gate

## Decision question

On the day I would have traded, what did this data actually say—and how much of what I see now came later?

## Event time and publication time

The month measured is the period the value describes. The publication date is the day the value became available to a trader. A March observation published on April 10 belongs to March economically, but it cannot inform a March 31 decision.

## Known-answer validation

Decision date: **March 31, 2026**.

| Funnel step | Rows removed |
|---|---|
| Quarantined: no ticker | 11 |
| Exact duplicate | 7 |
| Published after March 31 | 3, 8, 10 |
| Older vintage replaced by a revision | 2 |
| **As-of panel** | **1, 4, 5, 6, 9, 12** |

| Ticker | As-of signal | Naive signal |
|---|---:|---:|
| AAA | +1.98% (February) | +5.83% (March) |
| BBB | -1.02% (February) | -5.15% (March) |
| CCC | +0.91% (February) | +1.82% (February, revised) |

Changing the decision date to April 15, 2026 makes every as-of signal equal its naive signal because every publication in the training table is knowable by then.

## Rule 4 explained

`keep_latest_vintage` uses `(ticker, month_measured)` as a key, so publications that describe the same observation compete with one another. It compares their publication dates and keeps the later one. Because Rule 3 has already removed publications after the decision date, “later” here means the latest vintage that was actually knowable at that time. The source row number breaks a tie deterministically if two non-duplicate rows have the same publication date.

## Learn and reflect

**What is look-ahead bias?** Look-ahead bias occurs when a historical decision or backtest uses information that was not available at the time of the decision.

**How does it work here?** Event time identifies the month being measured, publication time identifies when a trader could know the value, and a revision can replace an earlier value after its first release. A valid as-of panel respects all three.

**AAA example.** On March 31, AAA's newest knowable month was February, using the March 25 revision from 104 to 103. Its knowable change was therefore 101 to 103, or +1.98%. The +5.83% naive result uses March's 109, which was not published until April 10, so it looks stronger only because it imports future information.

**Row that mattered most.** Rule 3 removed the rows published after the decision date. For AAA, removing row 3 prevents the unavailable March value from entering the signal. Rule 4 also matters because it replaces row 2 with its knowable revision, row 4; keeping row 2 would incorrectly report +2.97%.

**What a naive backtest would claim.** It would claim that the strategy traded on later releases and revisions as though they were already known. That would overstate AAA's contemporaneous momentum and misstate the signals for BBB and CCC.

## Run

From the repository root:

```bash
python Lab16/asof.py
```
