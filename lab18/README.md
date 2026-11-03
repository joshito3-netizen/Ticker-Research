# Lab 18 — Legend Investor as Skill

The repo-scoped Codex skill is in `.agents/skills/buffett-10k`. Its Python script gets ticker and company-fact JSON directly from SEC EDGAR, selects five 10-K fiscal years, computes all metrics and checks, and leaves only the memo judgment to the model.

## Run

Set a compliant SEC User-Agent for the current terminal without adding it to a file:

```bash
export SEC_USER_AGENT='Your Name your.email@example.edu'
python3 -m venv .venv
.venv/bin/python -m pip install streamlit pandas
python3 .agents/skills/buffett-10k/scripts/buffett_10k.py COST
.venv/bin/streamlit run app.py
```

In Codex, invoke the skill with:

```text
Use $buffett-10k to analyze COST and save the memo.
```

For the number-guard probe, add `40.0%` in the memo text area. For the missing-data probe, enter `JPM`; capital spending and owner earnings should remain `not found`, and the two owner-earnings checks should be `not known`.

Sources: [Codex skills](https://developers.openai.com/codex/skills), [SEC EDGAR APIs](https://www.sec.gov/edgar/sec-api-documentation), [FAskills](https://github.com/CinderZhang/FAskills), and [Streamlit](https://docs.streamlit.io/develop/api-reference/charts/st.line_chart).
