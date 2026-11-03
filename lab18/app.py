"""Streamlit interface for the Lab 18 Buffett 10-K skill."""

from __future__ import annotations

import os
import sys
from pathlib import Path

import pandas as pd
import streamlit as st

from memo_guard import find_unprinted_numbers


PROJECT_DIR = Path(__file__).resolve().parent
SKILL_SCRIPTS = PROJECT_DIR / ".agents" / "skills" / "buffett-10k" / "scripts"
sys.path.insert(0, str(SKILL_SCRIPTS))

from buffett_10k import analyze_ticker, render_report  # noqa: E402


def money(value: float | None) -> str:
    if value is None:
        return "not found"
    if abs(value - round(value)) < 0.000001:
        return f"{round(value):,.0f}"
    return f"{value:,.1f}"


def percent(value: float | None) -> str:
    return "not known" if value is None else f"{value:.1f}%"


@st.cache_data(ttl=3600, show_spinner=False)
def load_analysis(ticker: str, user_agent: str) -> dict:
    return analyze_ticker(ticker, user_agent)


def main() -> None:
    st.set_page_config(page_title="Buffett 10-K Skill", layout="wide")
    st.title("Buffett 10-K Skill")
    st.caption(
        "Data from SEC EDGAR; built with AI help, a learning demonstration, "
        "not investment advice."
    )

    ticker = st.text_input("Ticker", value="COST", max_chars=10).upper().strip()
    user_agent = os.environ.get("SEC_USER_AGENT", "").strip()
    if not user_agent or "@" not in user_agent:
        st.error(
            "Set SEC_USER_AGENT in the terminal to your real name and email, then restart "
            "Streamlit. The value is not stored by this app."
        )
        st.code("export SEC_USER_AGENT='Your Name your.email@example.edu'")
        st.stop()

    try:
        with st.spinner("Reading SEC EDGAR company facts..."):
            analysis = load_analysis(ticker, user_agent)
    except (ValueError, RuntimeError) as exc:
        st.error(str(exc))
        st.stop()

    rows = analysis["rows"]
    st.subheader(f"{analysis['ticker']} — {analysis['company']}")

    chart_data = pd.DataFrame(
        {
            "Fiscal year end": [row["fiscal_year_end"] for row in rows],
            "Owner earnings": [row["owner_earnings"] for row in rows],
            "Net income": [row["net_income"] for row in rows],
        }
    ).set_index("Fiscal year end")
    st.subheader("Owner earnings and net income (USD millions)")
    st.line_chart(chart_data)

    st.subheader("Five fiscal years (USD millions except ROE)")
    display_rows = []
    for row in rows:
        display_rows.append(
            {
                "FY end": row["fiscal_year_end"],
                "Revenue": money(row["revenue"]),
                "Net income": money(row["net_income"]),
                "Operating cash flow": money(row["operating_cash_flow"]),
                "Capital spending": money(row["capital_spending"]),
                "Equity": money(row["equity"]),
                "ROE": percent(row["roe_percent"]),
                "Owner earnings": money(row["owner_earnings"]),
            }
        )
    st.dataframe(pd.DataFrame(display_rows), hide_index=True, width="stretch")

    with st.expander("XBRL tags used", expanded=False):
        tag_rows = []
        for row in rows:
            tag_rows.append(
                {
                    "FY end": row["fiscal_year_end"],
                    "Revenue": row["revenue_tag"],
                    "Net income": row["net_income_tag"],
                    "Operating cash flow": row["operating_cash_flow_tag"],
                    "Capital spending": row["capital_spending_tag"],
                    "Equity": row["equity_tag"],
                    "ROE formula": row["roe_tag"],
                    "Owner earnings formula": row["owner_earnings_tag"],
                }
            )
        st.dataframe(pd.DataFrame(tag_rows), hide_index=True, width="stretch")

    st.subheader("Buffett checks")
    st.dataframe(
        pd.DataFrame(
            [
                {"Check": check, "Result": result}
                for check, result in analysis["checks"].items()
            ]
        ),
        hide_index=True,
        width="stretch",
    )

    memo_path = PROJECT_DIR / "memos" / f"{ticker}_buffett_memo.md"
    memo = memo_path.read_text(encoding="utf-8") if memo_path.exists() else "Memo not found."
    st.subheader("Buffett-style memo")
    edited_memo = st.text_area(
        "Edit the memo to probe its numbers",
        value=memo,
        height=300,
        key=f"memo-{ticker}",
    )

    flagged = find_unprinted_numbers(edited_memo, render_report(analysis))
    if flagged:
        st.error("Numbers not printed by the script: " + ", ".join(flagged))
    else:
        st.success("Every number in the memo was printed by the script.")


if __name__ == "__main__":
    main()
