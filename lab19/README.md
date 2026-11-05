# Lab 19 — Legend Panel

Question: When three investors' skills read the same 10-K facts, where do they agree, where do they split — and would you trust the panel?

The app and `panel_10k.py` preserve Lab 18 and add Graham and Burry screens over the same SEC EDGAR facts. Every check is computed in code. Missing facts remain `not found`; dependent ratios and checks remain `not known`. The memo guard checks all three memos together.

## Run

```bash
export SEC_USER_AGENT='Your Name your.email@example.edu'
python3 panel_10k.py COST
streamlit run app.py
```

## Validation

COST reproduces the known answer: Buffett 3 of 3; Graham 2 of 3, with latest current ratio 1.06 failing the retained 2.0 threshold; Burry 2 of 2, with latest liabilities/equity 1.49. The required 1.0 probe changes Graham's liquidity check and verdict to pass. I retain 2.0 because changing a threshold after observing COST would tailor the rule to the answer.

NVDA is used as the largest operating-company holding assumption for SPGM in the Project 2 universe recorded in Lab 15. Its panel is Buffett 3 of 3, Graham 3 of 3, and Burry 1 of 2. Burry splits because operating cash flow is not at least net income every year.

**Bull case:** Buffett and Graham both pass NVDA on strong returns, growing earnings, positive owner earnings, and liquidity. Low latest liabilities/equity also supports balance-sheet resilience.

**Bear case:** Burry's cash-conversion check fails because reported net income outruns operating cash flow in multiple years. The panel uses historical accounting thresholds and cannot establish valuation or durability.

**Decision:** I would let the panel screen Project 2 companies only as a first-pass filter, conditioned on preserving unknowns and requiring separate valuation and qualitative review before any investment decision.

## Learn and reflect

A panel of AI agents applies multiple explicit decision rules to one shared evidence set. The personas disagree because each weights different features and thresholds, not because they receive different facts. On NVDA, the panel agrees on earnings strength and low leverage but splits on cash conversion. The COST threshold probe shows that a screen's verdict can change when a designer moves one cutoff, so thresholds must be chosen and documented before judging the company.

Sources: [FAskills](https://github.com/CinderZhang/FAskills), [Codex skills](https://developers.openai.com/codex/skills), [SEC EDGAR APIs](https://www.sec.gov/edgar/sec-api-documentation), [Streamlit](https://docs.streamlit.io/).
