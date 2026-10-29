"""Streamlit point-in-time audit for FRED and ALFRED series."""

from __future__ import annotations

from datetime import date
from io import StringIO
import re

import pandas as pd
import requests
import streamlit as st


FRED_CSV_URL = "https://fred.stlouisfed.org/graph/fredgraph.csv"
ALFRED_CSV_URL = "https://alfred.stlouisfed.org/graph/alfredgraph.csv"

SERIES_NAMES = {
    "BAA": "Moody's Baa corporate bond yield",
    "FEDFUNDS": "Federal funds rate",
    "DGS10": "10-year Treasury yield",
    "MORTGAGE30US": "30-year mortgage rate",
}


def _parse_fred_csv(csv_text: str, series_id: str) -> pd.DataFrame:
    """Return a standard date/value frame and reject non-series responses."""

    frame = pd.read_csv(StringIO(csv_text), na_values=["."])
    value_columns = [
        column
        for column in frame.columns
        if column == series_id or column.startswith(f"{series_id}_")
    ]
    if "observation_date" not in frame.columns or len(value_columns) != 1:
        raise ValueError(f"FRED did not return data for series {series_id}.")

    frame = frame.rename(columns={value_columns[0]: "value"})[
        ["observation_date", "value"]
    ]
    frame["observation_date"] = pd.to_datetime(
        frame["observation_date"], errors="coerce"
    )
    frame["value"] = pd.to_numeric(frame["value"], errors="coerce")
    return frame.dropna().sort_values("observation_date").reset_index(drop=True)


@st.cache_data(ttl=3600, show_spinner=False)
def download_today(series_id: str) -> pd.DataFrame:
    """Download the values displayed by FRED today in one request."""

    response = requests.get(
        FRED_CSV_URL,
        params={"id": series_id},
        timeout=30,
    )
    response.raise_for_status()
    return _parse_fred_csv(response.text, series_id)


@st.cache_data(ttl=3600, show_spinner=False)
def download_as_known(series_id: str, vintage_date: date) -> pd.DataFrame:
    """Download the values ALFRED showed on one historical date in one request."""

    response = requests.get(
        ALFRED_CSV_URL,
        params={"id": series_id, "vintage_date": vintage_date.isoformat()},
        timeout=30,
    )
    response.raise_for_status()
    return _parse_fred_csv(response.text, series_id)


def clean_series_id(raw_series_id: str) -> str:
    """Normalize a typed FRED ID and reject characters that cannot be in an ID."""

    series_id = raw_series_id.strip().upper()
    if series_id and not re.fullmatch(r"[A-Z0-9_.-]+", series_id):
        raise ValueError("A FRED series ID may contain only letters, numbers, _, -, or .")
    return series_id


def audit_series(today: pd.DataFrame, as_known: pd.DataFrame) -> dict:
    """Compare one historical vintage with today's observations."""

    if today.empty:
        raise ValueError("FRED returned no numeric observations.")
    if as_known.empty:
        last_known_date = pd.NaT
        last_known_value = None
        later_count = len(today)
        revised_count = 0
    else:
        last_known = as_known.iloc[-1]
        last_known_date = last_known["observation_date"]
        last_known_value = float(last_known["value"])
        later_count = int((today["observation_date"] > last_known_date).sum())

        common = today.merge(
            as_known,
            on="observation_date",
            how="inner",
            suffixes=("_today", "_then"),
        )
        revised_count = int(
            (~common["value_today"].eq(common["value_then"])).sum()
        )

    latest_today = today.iloc[-1]
    return {
        "last_known_date": last_known_date,
        "last_known_value": last_known_value,
        "last_today_date": latest_today["observation_date"],
        "last_today_value": float(latest_today["value"]),
        "later_count": later_count,
        "revised_count": revised_count,
    }


def format_value(value: float | None) -> str:
    """Show rates with two decimals and large whole-number series with commas."""

    if value is None:
        return "—"
    if float(value).is_integer() and abs(value) >= 1000:
        return f"{value:,.0f}"
    return f"{value:,.2f}"


def format_observation_date(value: pd.Timestamp) -> str:
    """Format a measured date consistently for the audit table."""

    if pd.isna(value):
        return "—"
    return value.strftime("%Y-%m-%d")


def render_series_chart(
    series_id: str,
    today: pd.DataFrame,
    audit: dict,
    vintage_date: date,
    start_date: date,
) -> None:
    """Draw one current FRED history and identify its last knowable observation."""

    st.subheader(series_id)
    if series_id in SERIES_NAMES:
        st.caption(SERIES_NAMES[series_id])
    chart_data = today.loc[
        today["observation_date"] >= pd.Timestamp(start_date),
        ["observation_date", "value"],
    ].set_index("observation_date")
    if chart_data.empty:
        st.warning(f"No {series_id} observations occur on or after {start_date}.")
    else:
        st.line_chart(chart_data, y="value", use_container_width=True)

    st.caption(
        f"Last value known on {vintage_date:%Y-%m-%d}: "
        f"{format_observation_date(audit['last_known_date'])}, "
        f"{format_value(audit['last_known_value'])}."
    )


def main() -> None:
    """Render the point-in-time audit app."""

    st.set_page_config(page_title="Point-in-Time Rate Audit", layout="wide")
    st.title("Point-in-Time Rate Audit")
    st.caption(
        "Data from FRED and ALFRED, Federal Reserve Bank of St. Louis, "
        "downloaded today; built with AI help, a learning demonstration, "
        "not investment advice."
    )

    with st.sidebar:
        st.header("Audit controls")
        selected_ids = st.multiselect(
            "Rate series",
            options=list(SERIES_NAMES),
            default=list(SERIES_NAMES),
            format_func=lambda item: f"{item} — {SERIES_NAMES[item]}",
        )
        typed_id = st.text_input("Add another FRED series ID", placeholder="PAYEMS")
        start_date = st.date_input("Chart start date", value=date(2020, 1, 1))
        vintage_date = st.date_input("As known on", value=date.today())

    series_ids = list(selected_ids)
    try:
        extra_id = clean_series_id(typed_id)
    except ValueError as error:
        st.error(str(error))
        extra_id = ""
    if extra_id and extra_id not in series_ids:
        series_ids.append(extra_id)

    if not series_ids:
        st.info("Select or type at least one series ID.")
        return

    audit_rows = []
    for series_id in series_ids:
        try:
            with st.spinner(f"Downloading {series_id} from FRED and ALFRED…"):
                today = download_today(series_id)
                as_known = download_as_known(series_id, vintage_date)
            audit = audit_series(today, as_known)
            render_series_chart(
                series_id, today, audit, vintage_date, start_date
            )
            audit_rows.append(
                {
                    "Series": f"https://fred.stlouisfed.org/series/{series_id}",
                    "Last date known then": format_observation_date(
                        audit["last_known_date"]
                    ),
                    "Value known then": format_value(audit["last_known_value"]),
                    "Last date today": format_observation_date(
                        audit["last_today_date"]
                    ),
                    "Value today": format_value(audit["last_today_value"]),
                    "Values added later": audit["later_count"],
                    "Revised same-date values": audit["revised_count"],
                }
            )
        except (requests.RequestException, ValueError, pd.errors.ParserError) as error:
            st.error(f"{series_id}: could not load this series — {error}")

    st.subheader("Point-in-time audit table")
    if audit_rows:
        st.dataframe(
            pd.DataFrame(audit_rows),
            hide_index=True,
            use_container_width=True,
            column_config={
                "Series": st.column_config.LinkColumn(
                    "Series ID",
                    display_text=r"https://fred\.stlouisfed\.org/series/(.*)",
                )
            },
        )
    else:
        st.warning("No valid series were available for the audit table.")


if __name__ == "__main__":
    main()
