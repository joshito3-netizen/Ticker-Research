"""Streamlit app for the Lab 19 legend panel."""
import os
from pathlib import Path
import pandas as pd
import streamlit as st
from memo_guard import find_unprinted_numbers
from panel_10k import analyze_ticker, render_report

ROOT = Path(__file__).resolve().parent
INVESTORS = ("Buffett", "Graham", "Burry")

def money(value):
    if value is None: return "not found"
    return f"{value:,.0f}" if abs(value-round(value)) < .000001 else f"{value:,.1f}"

def ratio(value): return "not known" if value is None else f"{value:.2f}"

@st.cache_data(ttl=3600, show_spinner=False)
def load(ticker, agent): return analyze_ticker(ticker, agent)

def read_memos(ticker):
    return {name: (ROOT / "memos" / f"{ticker}_{name.lower()}_memo.md").read_text(encoding="utf-8")
            if (ROOT / "memos" / f"{ticker}_{name.lower()}_memo.md").exists() else "Memo not found."
            for name in INVESTORS}

def main():
    st.set_page_config(page_title="Lab 19 — Legend Panel", layout="wide")
    st.title("Lab 19 — Legend Panel")
    st.caption("One SEC 10-K fact set, three deterministic investor screens. Learning demonstration; not investment advice.")
    ticker = st.text_input("Ticker", "COST", max_chars=10).upper().strip()
    agent = os.environ.get("SEC_USER_AGENT", "").strip()
    if not agent or "@" not in agent:
        st.error("Set SEC_USER_AGENT to your real name and email, then restart Streamlit.")
        st.code("export SEC_USER_AGENT='Your Name your.email@example.edu'"); st.stop()
    try:
        with st.spinner("Reading SEC EDGAR company facts..."): analysis = load(ticker, agent)
    except (ValueError, RuntimeError) as exc:
        st.error(str(exc)); st.stop()

    st.subheader(f"{analysis['ticker']} — {analysis['company']}")
    rows = analysis["rows"]
    st.dataframe(pd.DataFrame([{"FY end": r["fiscal_year_end"], "Net income": money(r["net_income"]),
        "Operating cash flow": money(r["operating_cash_flow"]), "Equity": money(r["equity"]),
        "Liabilities": money(r["liabilities"]), "Current assets": money(r["current_assets"]),
        "Current liabilities": money(r["current_liabilities"]), "Current ratio": ratio(r["current_ratio"]),
        "Liabilities / equity": ratio(r["liabilities_to_equity"])} for r in rows]), hide_index=True, width="stretch")

    st.subheader("Panel table")
    panel = []
    for investor, checks in analysis["checks"].items():
        for check, result in checks.items():
            panel.append({"Investor": investor, "Check": check, "Result": result, "Verdict": analysis["verdicts"][investor]})
    st.dataframe(pd.DataFrame(panel), hide_index=True, width="stretch")

    st.subheader("Three memos")
    memos = read_memos(ticker)
    edited = {}
    for column, investor in zip(st.columns(3), INVESTORS):
        with column:
            st.markdown(f"### {investor} — {analysis['verdicts'][investor]}")
            edited[investor] = st.text_area(investor, memos[investor], height=360, label_visibility="collapsed", key=f"{ticker}-{investor}")
    flagged = find_unprinted_numbers(edited, render_report(analysis))
    problems = [f"{name}: {', '.join(values)}" for name, values in flagged.items() if values]
    if problems: st.error("Unprinted memo numbers — " + " | ".join(problems))
    else: st.success("Every number across all three memos was printed by the panel script.")

    with st.expander("Full deterministic report"):
        st.code(render_report(analysis))

if __name__ == "__main__": main()
