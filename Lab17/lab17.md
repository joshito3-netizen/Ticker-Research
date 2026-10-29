# Lab 17 — Point-in-Time Audit

## Decision question

Was each number in your series knowable on the day you would have traded on it — and may Project 2 use it?

## Series choice

I use **DGS10**, the 10-year Treasury yield, because changes in the benchmark Treasury rate directly affect the price and expected return of Project 2's intermediate-Treasury fund, SCHR, and also affect discount rates across the rest of the portfolio. No separate prework series ID was recorded in the repository, so DGS10 is the documented choice for this submission.

## Known-answer validation

The app downloaded the 5 October 2026 ALFRED vintage; these are calculated results, not values typed into the app.

| Series | Last date known on 5 October 2026 | Value |
|---|---|---:|
| BAA | September 2026 | 6.47 |
| FEDFUNDS | September 2026 | 3.75 |
| DGS10 | 2 October 2026 | 5.28 |
| MORTGAGE30US | 1 October 2026 | 7.28 |

The PAYEMS vintage downloaded for 15 January 2025 ended at December 2024 with **159,536 thousand jobs**. Today's December 2024 value is **158,316**, and the app finds **381** revised same-date observations across the common history, so the historical and current downloads are not the same data.

## DGS10 data card

| Field | Evidence |
|---|---|
| Source and link | Board of Governors of the Federal Reserve System (US), H.15 Selected Interest Rates, retrieved through [FRED series DGS10](https://fred.stlouisfed.org/series/DGS10) and its [public CSV](https://fred.stlouisfed.org/graph/fredgraph.csv?id=DGS10) |
| What it measures | Market yield on U.S. Treasury securities at 10-year constant maturity, quoted on an investment basis |
| Units | Percent per year, not seasonally adjusted |
| Frequency | Daily on business days |
| Publication lag | About one business day. The 29 October 2026 page showed the 27 October observation as updated on 28 October; the 30 September ALFRED vintage ended with the 29 September observation. |
| Revisions | None in the app's 30 September 2026 audit: **0** same-date values differed from today's file. Daily market rates can still be corrected, so each backtest must retain the vintage check. |
| Download date | 29 October 2026 |

### Three values checked by hand

I read these values on the [FRED DGS10 page](https://fred.stlouisfed.org/series/DGS10) and matched them to the app: **27 October 2026 = 4.99**, **26 October 2026 = 5.00**, and **23 October 2026 = 5.00**.

### Last-month audit

With **As known on = 30 September 2026**, the last knowable DGS10 observation was **29 September 2026 = 5.26**. Today's file contains **19** later observations through 27 October and **0** revisions on dates common to both files; the vanished observations were not yet published on 30 September.

## How the leak controls work

`download_as_known(series_id, vintage_date)` sends the series ID and decision date to ALFRED. ALFRED returns the historical vintage, `_parse_fred_csv` converts `.` to missing data and retains only dated numeric observations, and `audit_series` compares that vintage with today's FRED download by observation date. The vintage date prevents later publications from entering the signal; the last-known date exposes publication lag; the later-value count measures unavailable observations; and the same-date revision count exposes rewritten history.

A statement that data were “cleaned” is not a data card. Cleaning describes transformations, while a data card records meaning, source, units, timing, revisions, and retrieval date—the facts needed to decide whether a value was actually tradable.

## Partner attack

**Field challenged:** publication date.

The 30 September 2026 ALFRED view ended at 29 September = 5.26, so the app provides direct evidence of a one-business-day availability lag rather than same-day knowledge. The FRED page also showed 27 October = 4.99 as updated on 28 October, which independently supports that timing rule.

## My call

**Admit with an as-of rule.** Project 2 may use DGS10 only from the ALFRED vintage available on each decision date and must lag the observation by at least one business day; it may never substitute today's full FRED history. Quarantine it if the strategy needs a same-day rate before its release, or if a future vintage audit finds material revisions; evidence of a stable release time that precedes the trade would allow reconsidering the one-day lag.

## Learn and reflect

1. DGS10 is normally published about one business day after the observation. The app's “as known on” control proves this by removing observations unavailable on the selected decision date.
2. A backtest using today's values without an availability rule would overstate how current its rate signal was and could trade on the same day's yield before that yield had been published. For revision-heavy series such as PAYEMS, it would additionally replace the estimates traders saw with later revisions.

## Run and validate

From the repository root:

```bash
streamlit run Lab17/asof_app.py
python -m unittest Lab17.test_asof_app -v
```
