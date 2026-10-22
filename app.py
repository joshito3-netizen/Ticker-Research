"""Streamlit interface for the Lab 15 portfolio stability decision."""

from __future__ import annotations

from pathlib import Path
import sys

import streamlit as st


# Keep the Lab 15 app separate from the existing Project 1 app while importing
# the one shared engine at the repository root.
REPOSITORY_ROOT = Path(__file__).resolve().parent.parent
if str(REPOSITORY_ROOT) not in sys.path:
    sys.path.insert(0, str(REPOSITORY_ROOT))

from portfolio import (  # noqa: E402
    ASSETS,
    CORRELATIONS,
    EXPECTED_RETURNS,
    OBJECTIVE_RETURN,
    RESERVE_ELIGIBLE,
    VOLATILITIES,
    estimate_from_prices_csv,
    search_lowest_risk_mix,
)


st.set_page_config(page_title="Portfolio Stability Decision", layout="wide")
st.title("Portfolio Stability Decision")
st.caption("Built with AI help, a learning demonstration, not investment advice.")


def run_search(
    assets,
    expected_returns,
    volatilities,
    correlations,
    objective,
    reserve_eligible,
    reserve_minimum,
):
    """Call the shared engine with the app's current controls."""

    return search_lowest_risk_mix(
        assets,
        expected_returns,
        volatilities,
        correlations,
        objective,
        reserve_eligible,
        reserve_minimum,
    )


def show_answer(container, heading, answer, assets):
    """Display one engine result without duplicating portfolio math."""

    with container:
        st.subheader(heading)
        if answer is None:
            st.warning("No mix meets the objective.")
            return
        rows = [
            {"Asset": asset, "Weight": f"{answer['weights'][asset]:.2%}"}
            for asset in assets
        ]
        st.dataframe(rows, hide_index=True, use_container_width=True)
        first, second, third = st.columns(3)
        first.metric("Expected return", f"{answer['expected_return']:.2%}")
        second.metric("Volatility", f"{answer['volatility']:.2%}")
        third.metric("Reserve-eligible", f"{answer['reserve_weight']:.2%}")


with st.sidebar:
    st.header("Mandate controls")
    objective_percent = st.number_input(
        "Objective expected return (%)",
        min_value=-100.0,
        max_value=100.0,
        value=OBJECTIVE_RETURN * 100.0,
        step=0.1,
        format="%.1f",
    )
    reserve_minimum_percent = st.number_input(
        "Minimum reserve-eligible weight (%)",
        min_value=0.0,
        max_value=100.0,
        value=3.0,
        step=1.0,
        format="%.1f",
    )
    uploaded_file = st.file_uploader("Upload prices.csv", type="csv")
    last_36_months = st.checkbox(
        "Use only the last 36 monthly returns", value=False
    )

objective = objective_percent / 100.0
reserve_minimum = reserve_minimum_percent / 100.0

try:
    if uploaded_file is None:
        source_label = "Meridian training inputs"
        assets = ASSETS
        loaded_expected_returns = dict(EXPECTED_RETURNS)
        loaded_volatilities = dict(VOLATILITIES)
        loaded_correlations = CORRELATIONS
        current_volatilities = loaded_volatilities
        current_correlations = loaded_correlations
        estimate_note = "Course-authored training inputs; not market estimates."
    else:
        source_label = uploaded_file.name
        uploaded_file.seek(0)
        all_months = estimate_from_prices_csv(uploaded_file, last_36_months=False)
        uploaded_file.seek(0)
        current_estimate = estimate_from_prices_csv(
            uploaded_file, last_36_months=last_36_months
        )
        assets = all_months["assets"]
        loaded_expected_returns = all_months["expected_returns"]
        loaded_volatilities = all_months["volatilities"]
        loaded_correlations = all_months["correlations"]
        current_volatilities = current_estimate["volatilities"]
        current_correlations = current_estimate["correlations"]
        estimate_note = (
            "Historical annualized estimates from monthly adjusted-close prices; "
            "they are not forecasts. "
            f"Current risk window uses {current_estimate['months_used']} monthly returns."
        )
except ValueError as error:
    st.error(f"PRICE FILE ERROR — {error}")
    st.stop()

st.write(f"**Inputs:** {source_label}")
st.caption(estimate_note)
st.subheader("Expected return estimates")
st.caption("Edit any box to test whether the allocation survives a changed estimate.")

current_expected_returns = {}
return_columns = st.columns(min(len(assets), 3))
for index, asset in enumerate(assets):
    with return_columns[index % len(return_columns)]:
        current_expected_returns[asset] = st.number_input(
            asset,
            min_value=-100.0,
            max_value=100.0,
            value=float(
                (
                    current_estimate["expected_returns"][asset]
                    if uploaded_file is not None
                    else loaded_expected_returns[asset]
                )
                * 100.0
            ),
            step=0.1,
            format="%.2f",
            key=f"return_{source_label}_{last_36_months}_{asset}",
        ) / 100.0

st.subheader("Reserve eligibility")
reserve_columns = st.columns(min(len(assets), 3))
selected_reserve_assets = []
for index, asset in enumerate(assets):
    with reserve_columns[index % len(reserve_columns)]:
        default_checked = uploaded_file is None and asset in RESERVE_ELIGIBLE
        if st.checkbox(
            asset,
            value=default_checked,
            key=f"reserve_{source_label}_{asset}",
        ):
            selected_reserve_assets.append(asset)

try:
    current_answer = run_search(
        assets,
        current_expected_returns,
        current_volatilities,
        current_correlations,
        objective,
        selected_reserve_assets,
        reserve_minimum,
    )
    loaded_answer = run_search(
        assets,
        loaded_expected_returns,
        loaded_volatilities,
        loaded_correlations,
        objective,
        selected_reserve_assets,
        reserve_minimum,
    )
except ValueError as error:
    st.error(f"INPUT ERROR — portfolio engine refused to run: {error}")
    st.stop()

current_column, loaded_column = st.columns(2)
show_answer(current_column, "Current answer", current_answer, assets)
show_answer(loaded_column, "As-loaded answer", loaded_answer, assets)

if current_answer is not None and loaded_answer is not None:
    changes = {
        asset: abs(
            current_answer["weights"][asset] - loaded_answer["weights"][asset]
        )
        for asset in assets
    }
    largest_asset = max(changes, key=changes.get)
    st.info(
        f"Largest weight change: {changes[largest_asset] * 100:.0f} percentage points "
        f"({largest_asset})."
    )
else:
    st.info("Largest weight change is unavailable because one run has no feasible mix.")
