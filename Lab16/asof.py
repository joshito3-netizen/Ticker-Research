"""Build a point-in-time panel and compare it with a naive latest-vintage view."""

from __future__ import annotations

import csv
import io
from datetime import date


# Editable inputs
DECISION_DATE = "2026-03-31"

TABLE = """row,ticker,month_measured,published_on,index
1,AAA,2026-01,2026-02-10,101.0
2,AAA,2026-02,2026-03-10,104.0
3,AAA,2026-03,2026-04-10,109.0
4,AAA,2026-02,2026-03-25,103.0
5,BBB,2026-01,2026-02-10,98.0
6,BBB,2026-02,2026-03-10,97.0
7,BBB,2026-02,2026-03-10,97.0
8,BBB,2026-03,2026-04-10,92.0
9,CCC,2026-01,2026-02-10,110.0
10,CCC,2026-02,2026-04-05,112.0
11,,2026-02,2026-03-10,99.0
12,CCC,2026-02,2026-03-10,111.0
"""


def parse_inputs(table: str) -> list[dict]:
    """Parse the editable CSV text and give values useful Python types."""

    rows = []
    for raw_row in csv.DictReader(io.StringIO(table.strip())):
        rows.append(
            {
                "row": int(raw_row["row"]),
                "ticker": raw_row["ticker"].strip(),
                "month_measured": raw_row["month_measured"],
                "published_on": date.fromisoformat(raw_row["published_on"]),
                "index": float(raw_row["index"]),
            }
        )
    return rows


def remove_missing_tickers(rows: list[dict]) -> tuple[list[dict], list[dict]]:
    """Rule 1: quarantine rows whose ticker is blank."""

    removed = [row for row in rows if not row["ticker"]]
    kept = [row for row in rows if row["ticker"]]
    return kept, removed


def remove_exact_duplicates(rows: list[dict]) -> tuple[list[dict], list[dict]]:
    """Rule 2: keep the first copy of each exact observation."""

    seen = set()
    kept = []
    removed = []
    for row in rows:
        # The source row number identifies the copy, not the observation itself.
        observation = (
            row["ticker"],
            row["month_measured"],
            row["published_on"],
            row["index"],
        )
        if observation in seen:
            removed.append(row)
        else:
            seen.add(observation)
            kept.append(row)
    return kept, removed


def remove_future_publications(
    rows: list[dict], decision_date: date
) -> tuple[list[dict], list[dict]]:
    """Rule 3: exclude observations unavailable on the decision date."""

    removed = [row for row in rows if row["published_on"] > decision_date]
    kept = [row for row in rows if row["published_on"] <= decision_date]
    return kept, removed


def keep_latest_vintage(rows: list[dict]) -> tuple[list[dict], list[dict]]:
    """Rule 4: retain the latest publication for each ticker-month pair."""

    latest = {}
    for row in rows:
        key = (row["ticker"], row["month_measured"])
        current = latest.get(key)
        if current is None or (row["published_on"], row["row"]) > (
            current["published_on"],
            current["row"],
        ):
            latest[key] = row

    kept_row_numbers = {row["row"] for row in latest.values()}
    kept = [row for row in rows if row["row"] in kept_row_numbers]
    removed = [row for row in rows if row["row"] not in kept_row_numbers]
    return kept, removed


def build_asof_panel(
    all_rows: list[dict], decision_date: date
) -> tuple[list[dict], list[tuple[str, list[dict]]], list[dict]]:
    """Apply the four rules in order and return the panel, funnel, and clean rows."""

    rows, quarantined = remove_missing_tickers(all_rows)
    rows, duplicates = remove_exact_duplicates(rows)
    clean_rows = rows.copy()  # Rules 1-2 also define the naive comparison universe.
    rows, future = remove_future_publications(rows, decision_date)
    rows, old_vintages = keep_latest_vintage(rows)
    funnel = [
        ("Quarantined: no ticker", quarantined),
        ("Exact duplicate", duplicates),
        (f"Published after {decision_date:%d %B}", future),
        ("Older vintage replaced by a revision", old_vintages),
    ]
    return rows, funnel, clean_rows


def calculate_signals(
    rows: list[dict], revision_source_rows: list[dict] | None = None
) -> dict[str, dict]:
    """Calculate each ticker's latest month-over-month index change."""

    if revision_source_rows is None:
        revision_source_rows = rows
    vintage_counts = {}
    for row in revision_source_rows:
        key = (row["ticker"], row["month_measured"])
        vintage_counts[key] = vintage_counts.get(key, 0) + 1

    by_ticker = {}
    for row in rows:
        by_ticker.setdefault(row["ticker"], []).append(row)

    signals = {}
    for ticker, ticker_rows in sorted(by_ticker.items()):
        ordered = sorted(ticker_rows, key=lambda row: row["month_measured"])
        if len(ordered) < 2:
            signals[ticker] = None
            continue
        previous, latest = ordered[-2:]
        signals[ticker] = {
            "change": (latest["index"] / previous["index"] - 1.0) * 100.0,
            "month": latest["month_measured"],
            "revised": vintage_counts[
                (latest["ticker"], latest["month_measured"])
            ]
            > 1,
        }
    return signals


def month_name(year_month: str) -> str:
    """Turn YYYY-MM into a readable month name."""

    return date.fromisoformat(f"{year_month}-01").strftime("%B")


def row_numbers(rows: list[dict]) -> str:
    """Format source row numbers for the funnel."""

    return ", ".join(str(row["row"]) for row in rows) or "none"


def print_panel(rows: list[dict]) -> None:
    """Print the surviving point-in-time rows as a compact table."""

    print("\nAs-of panel")
    print(f"{'Row':>3}  {'Ticker':<6}  {'Month':<7}  {'Published':<10}  {'Index':>6}")
    for row in sorted(rows, key=lambda item: item["row"]):
        print(
            f"{row['row']:>3}  {row['ticker']:<6}  {row['month_measured']:<7}  "
            f"{row['published_on'].isoformat():<10}  {row['index']:>6.1f}"
        )


def print_signals(heading: str, signals: dict[str, dict]) -> None:
    """Print signals with signs, two decimals, and the latest measured month."""

    print(f"\n{heading}")
    for ticker, signal in signals.items():
        if signal is None:
            print(f"{ticker}: unavailable (fewer than two months)")
        else:
            revision_note = ", revised" if signal["revised"] else ""
            print(
                f"{ticker}: {signal['change']:+.2f}% "
                f"({month_name(signal['month'])}{revision_note})"
            )


def run(table: str = TABLE, decision_date_text: str = DECISION_DATE) -> None:
    """Run the point-in-time and naive calculations from editable inputs."""

    decision_date = date.fromisoformat(decision_date_text)
    all_rows = parse_inputs(table)
    asof_panel, funnel, clean_rows = build_asof_panel(all_rows, decision_date)

    # For the naive comparison, ignore the date cutoff but still choose the latest
    # publication for each ticker-month so revisions do not become extra months.
    naive_panel, _ = keep_latest_vintage(clean_rows)

    print(f"Decision date: {decision_date.isoformat()}")
    print("\nRow funnel")
    for label, removed in funnel:
        print(f"{label}: removed {len(removed)} row(s) [{row_numbers(removed)}]")
    print(f"As-of panel: {len(asof_panel)} row(s) [{row_numbers(asof_panel)}]")

    print_panel(asof_panel)
    print_signals("As-of signals", calculate_signals(asof_panel))
    print_signals(
        "Naive signals (publication date ignored)",
        calculate_signals(naive_panel, clean_rows),
    )


if __name__ == "__main__":
    run()
