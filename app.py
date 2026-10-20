"""Bounded Microsoft pro-forma workbench for the investment committee."""

from __future__ import annotations

import streamlit as st

from analysis import run_analysis


st.set_page_config(page_title="Microsoft Pro-Forma Workbench", layout="wide")
st.title("Microsoft Pro-Forma Workbench")
st.caption("FIN 43900 Project 1 · USD millions except per-share values · evidence cutoff September 9, 2026")


UI_DEFAULTS = {
    "cloud_growth_shift": 0.0,
    "productivity_growth_shift": 0.0,
    "ebitda_margin_shift": 0.0,
    "cash_capex_ratio_shift": 0.0,
    "finance_lease_addition_ratio_shift": 0.0,
    "wacc": 9.5,
    "terminal_growth": 3.0,
}


def reset() -> None:
    for key, value in UI_DEFAULTS.items():
        st.session_state[key] = value


with st.sidebar:
    st.header("Bounded driver panel")
    st.button("Reset to base", on_click=reset, width="stretch")
    st.slider(
        "Cloud growth shift", -8.0, 5.0, UI_DEFAULTS["cloud_growth_shift"], 0.5,
        key="cloud_growth_shift", format="%.1f%%",
        help="Shift applied to all five Intelligent Cloud growth rates. Bounds bracket the downside/upside cases and sharper saturation risk.",
    )
    st.slider(
        "Productivity growth shift", -5.0, 3.0, UI_DEFAULTS["productivity_growth_shift"], 0.5,
        key="productivity_growth_shift", format="%.1f%%",
        help="Shift applied to all five Productivity and Business Processes growth rates.",
    )
    st.slider(
        "EBITDA margin shift", -4.0, 2.0, UI_DEFAULTS["ebitda_margin_shift"], 0.5,
        key="ebitda_margin_shift", format="%.1f%%",
        help="Shift applied to EBITDA margin after stock compensation; depreciation remains linked to investment.",
    )
    st.slider(
        "Cash capex / revenue shift", -3.0, 5.0, UI_DEFAULTS["cash_capex_ratio_shift"], 0.5,
        key="cash_capex_ratio_shift", format="%.1f%%",
        help="Cash additions to PP&E. Bounds retain a heavy AI-infrastructure build while testing normalization or persistence.",
    )
    st.slider(
        "Finance-lease additions / revenue shift", -2.0, 2.0, UI_DEFAULTS["finance_lease_addition_ratio_shift"], 0.5,
        key="finance_lease_addition_ratio_shift", format="%.1f%%",
        help="Noncash leased PP&E is treated as economic reinvestment and creates a lease liability.",
    )
    st.slider("WACC", 8.0, 12.0, UI_DEFAULTS["wacc"], 0.5, key="wacc", format="%.1f%%")
    st.slider(
        "Terminal growth", 1.5, 4.0, UI_DEFAULTS["terminal_growth"], 0.5,
        key="terminal_growth", format="%.1f%%",
    )
    failure_demo = st.checkbox(
        "Demonstrate loud failure (temporarily set terminal growth = WACC)",
        value=False,
        help="This deliberately violates the DCF boundary for the required recorded check demonstration. Uncheck to recover.",
    )
    st.caption("Accounting, filing facts, source lineage, share basis, and checks are locked.")


overrides = {
    key: st.session_state.get(key, value) / 100.0
    for key, value in UI_DEFAULTS.items()
}
if failure_demo:
    overrides["terminal_growth"] = overrides["wacc"]
try:
    result = run_analysis(overrides)
except ValueError as exc:
    st.error(f"MODEL CHECK FAILED: {exc}")
    st.stop()

low, high = result["valuation_range"]
valuation = result["valuation"]
market = result["meta"]["market_price"]

st.subheader(f"Committee action: {result['recommendation']}")
c1, c2, c3, c4 = st.columns(4)
c1.metric("Market close", f"${market:,.2f}")
c2.metric("Selected-driver DCF", f"${valuation['per_share']:,.2f}", f"{valuation['per_share'] / market - 1:.1%} vs market")
c3.metric("Causal case range", f"${low:,.0f}–${high:,.0f}")
c4.metric("Terminal-value share", f"{valuation['terminal_share']:.1%}")

st.info(
    "Base conclusion: defer because the dated market price is above even the causal upside DCF. "
    "Re-underwrite if price enters the supported range or operating evidence supports materially "
    "higher cloud cash returns without persistent cash and lease investment."
)

tab_summary, tab_statements, tab_sensitivity, tab_evidence = st.tabs(
    ["Decision", "Three statements", "Sensitivity", "Evidence & checks"]
)

with tab_summary:
    st.subheader("Low / base / high cases")
    st.dataframe(
        [
            {
                "Case": name,
                "Value/share": round(data["per_share"], 2),
                "FY2031 revenue": round(data["fy2031_revenue"], 1),
                "FY2031 EBIT": round(data["fy2031_ebit"], 1),
                "FY2031 FCFF": round(data["fy2031_fcff"], 1),
                "WACC": data["wacc"],
                "Terminal growth": data["terminal_growth"],
            }
            for name, data in result["scenarios"].items()
        ],
        width="stretch",
        hide_index=True,
    )
    st.subheader("Enterprise-to-equity bridge")
    st.dataframe(
        [
            {"Item": "Enterprise value", "USD millions": valuation["enterprise_value"]},
            {"Item": "Add: excess cash and short investments", "USD millions": valuation["excess_cash"]},
            {"Item": "Add: 50% equity-investment recovery", "USD millions": valuation["investment_value"]},
            {"Item": "Less: term debt", "USD millions": -valuation["debt"]},
            {"Item": "Less: finance-lease liabilities", "USD millions": -valuation["finance_leases"]},
            {"Item": "Equity value", "USD millions": valuation["equity_value"]},
        ],
        width="stretch",
        hide_index=True,
    )
    reverse = result["reverse_dcf"]
    st.subheader("Market-implied expectation")
    if reverse["solved"]:
        st.write(
            f"To reach ${reverse['target_price']:,.2f}, all three segment-growth paths require a "
            f"uniform **+{reverse['uniform_growth_shift']:.1%}** shift, holding margins, reinvestment, "
            "WACC, terminal growth, bridge balances, share count, and horizon fixed. This is one "
            "assumption set consistent with price—not proof of mispricing."
        )
    else:
        st.warning("The selected reverse-DCF bracket does not reach the market price.")

with tab_statements:
    forecast = result["forecast"]
    st.subheader("Income statement")
    st.dataframe(
        [
            {
                "FY": row["year"], "Productivity revenue": row["productivity"],
                "Cloud revenue": row["cloud"], "Personal revenue": row["personal"],
                "Revenue": row["revenue"], "EBITDA": row["ebitda"],
                "D&A": row["da"], "Operating income": row["ebit"],
                "Pretax income": row["pretax_income"], "Tax": row["tax"],
                "Net income": row["net_income"], "Diluted EPS": row["eps"],
            }
            for row in forecast
        ],
        width="stretch",
        hide_index=True,
    )
    st.subheader("Balance sheet")
    st.dataframe(
        [
            {
                "FY": row["year"], "Cash": row["cash"], "Receivables": row["receivables"],
                "PP&E": row["ppe"], "Total assets": row["total_assets"],
                "Debt": row["debt"], "Finance leases": row["finance_leases"],
                "Total liabilities": row["total_liabilities"], "Equity": row["equity"],
                "Balance gap": row["balance_gap"],
            }
            for row in forecast
        ],
        width="stretch",
        hide_index=True,
    )
    st.subheader("Cash flow and FCFF")
    st.dataframe(
        [
            {
                "FY": row["year"], "CFO": row["cfo"], "Cash capex": -row["cash_capex"],
                "Financing cash flow": row["cff"], "Change in cash": row["change_cash"],
                "Ending cash": row["cash"], "New finance leases (noncash)": row["finance_lease_additions"],
                "Economic FCFF": row["fcff"],
            }
            for row in forecast
        ],
        width="stretch",
        hide_index=True,
    )

with tab_sensitivity:
    st.subheader("One-at-a-time operating sensitivity")
    st.caption("Each run starts from the same selected-driver base and changes only the named driver.")
    ranking = [
        {
            "Rank": rank,
            "Driver": row["driver"],
            "Value/share span": row["per_share_span"],
            "FY2031 EBIT span": row["ebit_span"],
            "FY2031 FCFF span": row["fcff_span"],
        }
        for rank, row in enumerate(result["operating_sensitivity"], 1)
    ]
    st.dataframe(ranking, width="stretch", hide_index=True)
    st.subheader("WACC × terminal-growth grid")
    grid = result["sensitivity_grid"]
    st.dataframe(
        [
            {
                "WACC": wacc,
                **{
                    f"g={growth:.1%}": next(
                        cell["per_share"] for cell in grid
                        if cell["wacc"] == wacc and cell["terminal_growth"] == growth
                    )
                    for growth in (0.02, 0.03, 0.04)
                },
            }
            for wacc in (0.085, 0.095, 0.105)
        ],
        width="stretch",
        hide_index=True,
    )
    st.subheader("Comparable-company references")
    peers = result["comparables"]["admitted_peers"]
    st.dataframe(
        [
            {
                "Peer": peer["ticker"], "Policy": peer["decision"],
                "P/E": peer["pe"], "MSFT from P/E": peer["implied_target_price_pe"],
                "EV/Revenue": peer["ev_revenue"],
                "MSFT from EV/Revenue": peer["implied_target_price_ev_revenue"],
            }
            for peer in peers
        ],
        width="stretch",
        hide_index=True,
    )
    st.caption("The single qualified peer is a reference, not a range. The two multiples and DCF are not averaged.")

with tab_evidence:
    st.subheader("Checks that can fail loudly")
    for name, passed in result["checks"].items():
        (st.success if passed else st.error)(f"{'PASS' if passed else 'FAIL'} — {name.replace('_', ' ')}")
    st.subheader("Base-year normalization")
    h = result["historical"]
    st.write(
        f"FY2026 reported net income was ${h['reported_net_income']:,.0f} million. The base removes "
        f"the ${h['openai_after_tax_gain']:,.0f} million after-tax OpenAI investment gain, producing "
        f"normalized net income of ${h['normalized_net_income']:,.0f} million and normalized diluted EPS of "
        f"${h['normalized_diluted_eps']:.2f}. Forecast other income includes cash yield and financing cost, "
        "but no recurring investment gain."
    )
    st.subheader("Source ledger")
    st.dataframe(result["sources"], width="stretch", hide_index=True)
    st.warning(
        "Highest-risk claim: the model treats both cash PP&E additions and new finance-lease assets as "
        "economic reinvestment. Removing lease additions raises value mechanically and fails the economic "
        "completeness test even if the accounting statements still balance."
    )
