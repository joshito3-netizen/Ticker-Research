---
name: graham-10k
description: Screen a company with Graham-style liquidity and earnings checks computed from five SEC EDGAR 10-K fiscal years. Use for Lab 19 panel work where missing facts stay unknown and memo numbers come from code output.
---

# Graham 10-K

Run `python panel_10k.py TICKER` with `SEC_USER_AGENT` set to the user's real name and email. Use the shared report so all three investors read the same facts. Never calculate or add numbers in prose; preserve `not found` and `not known`.

Code computes: latest current ratio at least 2.0; positive net income every year; net-income growth from first year to last. The 2.0 threshold is retained after probing 1.0; label any change as a design choice.

Write `memos/TICKER_graham_memo.md` using only printed numbers and results. Give a `pass`, `watch`, or `fail` verdict, discuss liquidity and earnings, and state that this is a five-year 10-K screen rather than investment advice. Use `watch` when decisive evidence is missing.

Sources: [FAskills](https://github.com/CinderZhang/FAskills), [SEC EDGAR](https://www.sec.gov/edgar/sec-api-documentation).
