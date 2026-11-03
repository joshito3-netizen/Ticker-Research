---
name: buffett-10k
description: Analyze a public company from its last five 10-K fiscal years using SEC EDGAR facts, deterministic Buffett checks, and a short business-quality memo. Use for ticker-based Buffett screens where code must compute every number and the model must not use price data or invent missing values.
---

# Buffett 10-K

Keep calculation and judgment separate.

## Run the deterministic analysis

1. Require the user to set `SEC_USER_AGENT` to their real name and email. Do not write that value into a project file.
2. Run:

   ```bash
   python .agents/skills/buffett-10k/scripts/buffett_10k.py TICKER
   ```

   If the current project is elsewhere, use this skill directory's absolute script path.
3. Treat the script output as the complete numerical evidence. Never calculate, correct, estimate, or supplement a number in prose. A missing fact remains `not found`; a derived value or check with a missing or invalid input remains `not known`.

The script uses only SEC EDGAR company tickers and company facts. It selects 10-K facts, one-year periods for flow measures, the latest filing for a repeated period, and the last five fiscal-year-end dates. It prints each source XBRL tag and computes ROE, owner earnings, and all three checks in code.

## Write the memo

After a successful run, save `memos/TICKER_buffett_memo.md` in the current project. Use only facts and numbers printed by the script. Do not use price, valuation, forecasts, outside data, or arithmetic performed in prose.

Write no more than 180 words with these parts:

- `# TICKER — Buffett-style business memo`
- `Verdict: own the business`, `Verdict: watch it`, or `Verdict: pass`
- A short explanation of returns on equity, owner-earnings consistency and growth, and any missing evidence.
- `Limits:` stating that this is a five-year 10-K business-quality screen, not a price analysis or investment advice.

Use exact printed forms for every numeric value, including commas and percent signs. When either owner-earnings check is `not known`, explicitly say owner earnings cannot be judged from the required SEC tag set. Prefer `watch it` when decisive evidence is missing.

## Sources

- SEC EDGAR APIs: <https://www.sec.gov/edgar/sec-api-documentation>
- FAskills Buffett page, read for philosophy only: <https://github.com/CinderZhang/FAskills>
- Codex skills: <https://developers.openai.com/codex/skills>

This workflow is a learning demonstration, not investment advice.
