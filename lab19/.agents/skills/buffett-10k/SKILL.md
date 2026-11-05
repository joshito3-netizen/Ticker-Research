---
name: buffett-10k
description: Screen a company with Buffett-style ROE and owner-earnings checks computed from five SEC EDGAR 10-K fiscal years. Use as the Buffett member of the Lab 19 panel.
---

# Buffett 10-K

Run `python panel_10k.py TICKER` with a compliant `SEC_USER_AGENT`. Use only printed facts and code-computed checks. Preserve `not found` and `not known`; do not add price data, forecasts, estimates, or prose arithmetic.

Code computes: ROE at least 15% every year; positive owner earnings every year; owner-earnings growth from first year to last.

Write `memos/TICKER_buffett_memo.md` with a `pass`, `watch`, or `fail` verdict based only on printed evidence. State that this is a five-year 10-K screen rather than investment advice. Use `watch` when decisive evidence is missing.

Sources: [FAskills](https://github.com/CinderZhang/FAskills), [SEC EDGAR](https://www.sec.gov/edgar/sec-api-documentation).
