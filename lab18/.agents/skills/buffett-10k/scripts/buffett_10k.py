#!/usr/bin/env python3
"""Deterministic five-year Buffett screen using SEC EDGAR company facts."""

from __future__ import annotations

import argparse
import json
import os
import ssl
import sys
import urllib.error
import urllib.request
from dataclasses import asdict, dataclass
from datetime import date
from pathlib import Path
from typing import Any, Iterable


TICKERS_URL = "https://www.sec.gov/files/company_tickers.json"
FACTS_URL = "https://data.sec.gov/api/xbrl/companyfacts/CIK{cik:010d}.json"
FLOW_MIN_DAYS = 300
FLOW_MAX_DAYS = 400

TAG_RULES = {
    "revenue": (
        "RevenueFromContractWithCustomerExcludingAssessedTax",
        "Revenues",
    ),
    "net_income": ("NetIncomeLoss",),
    "operating_cash_flow": ("NetCashProvidedByUsedInOperatingActivities",),
    "capital_spending": (
        "PaymentsToAcquirePropertyPlantAndEquipment",
        "PaymentsToAcquireProductiveAssets",
    ),
    "equity": ("StockholdersEquity",),
}


@dataclass(frozen=True)
class SelectedFact:
    value: float
    tag: str
    filed: str
    accession: str


@dataclass
class YearRow:
    fiscal_year_end: str
    revenue: float | None
    revenue_tag: str
    net_income: float | None
    net_income_tag: str
    operating_cash_flow: float | None
    operating_cash_flow_tag: str
    capital_spending: float | None
    capital_spending_tag: str
    equity: float | None
    equity_tag: str
    roe_percent: float | None
    roe_tag: str
    owner_earnings: float | None
    owner_earnings_tag: str


def _ssl_context() -> ssl.SSLContext:
    """Use Python defaults, with the macOS system CA bundle as a fallback."""
    for ca_file in ("/etc/ssl/cert.pem", "/private/etc/ssl/cert.pem"):
        if Path(ca_file).is_file():
            return ssl.create_default_context(cafile=ca_file)
    return ssl.create_default_context()


def _fetch_json(url: str, user_agent: str) -> dict[str, Any]:
    request = urllib.request.Request(
        url,
        headers={"User-Agent": user_agent, "Accept": "application/json"},
    )
    try:
        with urllib.request.urlopen(request, timeout=30, context=_ssl_context()) as response:
            return json.load(response)
    except urllib.error.HTTPError as exc:
        raise RuntimeError(f"SEC request failed: HTTP {exc.code} for {url}") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"SEC request failed for {url}: {exc.reason}") from exc


def _validated_user_agent(value: str | None = None) -> str:
    user_agent = (value or os.environ.get("SEC_USER_AGENT", "")).strip()
    if not user_agent or "@" not in user_agent:
        raise ValueError(
            "Set SEC_USER_AGENT to your real name and email, for example: "
            "export SEC_USER_AGENT='Your Name your.email@example.edu'"
        )
    return user_agent


def resolve_cik(ticker: str, user_agent: str) -> tuple[int, str]:
    target = ticker.upper().strip()
    mapping = _fetch_json(TICKERS_URL, user_agent)
    for item in mapping.values():
        if str(item.get("ticker", "")).upper() == target:
            return int(item["cik_str"]), str(item.get("title", target))
    raise ValueError(f"Ticker not found in SEC company_tickers.json: {target}")


def _duration_days(item: dict[str, Any]) -> int | None:
    try:
        return (date.fromisoformat(item["end"]) - date.fromisoformat(item["start"])).days
    except (KeyError, TypeError, ValueError):
        return None


def _is_one_year_flow(item: dict[str, Any]) -> bool:
    duration = _duration_days(item)
    return duration is not None and FLOW_MIN_DAYS <= duration <= FLOW_MAX_DAYS


def _usd_items(company_facts: dict[str, Any], tag: str) -> list[dict[str, Any]]:
    fact = company_facts.get("facts", {}).get("us-gaap", {}).get(tag, {})
    return list(fact.get("units", {}).get("USD", []))


def _eligible_items(
    company_facts: dict[str, Any], tag: str, *, flow: bool
) -> Iterable[dict[str, Any]]:
    for item in _usd_items(company_facts, tag):
        if item.get("form") != "10-K":
            continue
        if flow and not _is_one_year_flow(item):
            continue
        if not flow and item.get("start"):
            continue
        if item.get("end") and item.get("val") is not None:
            yield item


def _candidate_fiscal_year_ends(company_facts: dict[str, Any]) -> list[str]:
    ends: set[str] = set()
    for key in ("revenue", "net_income", "operating_cash_flow"):
        for tag in TAG_RULES[key]:
            ends.update(item["end"] for item in _eligible_items(company_facts, tag, flow=True))
    return sorted(ends)[-5:]


def _select_fact(
    company_facts: dict[str, Any],
    tags: tuple[str, ...],
    fiscal_year_end: str,
    *,
    flow: bool,
) -> SelectedFact | None:
    for tag in tags:
        candidates = [
            item
            for item in _eligible_items(company_facts, tag, flow=flow)
            if item["end"] == fiscal_year_end
        ]
        if candidates:
            latest = max(
                candidates,
                key=lambda item: (item.get("filed", ""), item.get("accn", "")),
            )
            return SelectedFact(
                value=float(latest["val"]) / 1_000_000,
                tag=tag,
                filed=str(latest.get("filed", "")),
                accession=str(latest.get("accn", "")),
            )
    return None


def _fact_parts(fact: SelectedFact | None) -> tuple[float | None, str]:
    if fact is None:
        return None, "not found"
    return fact.value, fact.tag


def build_year_row(company_facts: dict[str, Any], fiscal_year_end: str) -> YearRow:
    """Turn EDGAR facts into one fiscal-year row using only the lab rules."""
    revenue = _select_fact(company_facts, TAG_RULES["revenue"], fiscal_year_end, flow=True)
    net_income = _select_fact(
        company_facts, TAG_RULES["net_income"], fiscal_year_end, flow=True
    )
    operating_cash_flow = _select_fact(
        company_facts, TAG_RULES["operating_cash_flow"], fiscal_year_end, flow=True
    )
    capital_spending = _select_fact(
        company_facts, TAG_RULES["capital_spending"], fiscal_year_end, flow=True
    )
    equity = _select_fact(company_facts, TAG_RULES["equity"], fiscal_year_end, flow=False)

    revenue_value, revenue_tag = _fact_parts(revenue)
    net_income_value, net_income_tag = _fact_parts(net_income)
    operating_cash_flow_value, operating_cash_flow_tag = _fact_parts(operating_cash_flow)
    capital_spending_value, capital_spending_tag = _fact_parts(capital_spending)
    equity_value, equity_tag = _fact_parts(equity)

    roe: float | None = None
    if net_income_value is not None and equity_value is not None and equity_value > 0:
        roe = 100 * net_income_value / equity_value

    owner_earnings: float | None = None
    if operating_cash_flow_value is not None and capital_spending_value is not None:
        owner_earnings = operating_cash_flow_value - capital_spending_value

    roe_tag = f"{net_income_tag} / {equity_tag}" if roe is not None else "not known"
    owner_earnings_tag = (
        f"{operating_cash_flow_tag} - {capital_spending_tag}"
        if owner_earnings is not None
        else "not known"
    )

    return YearRow(
        fiscal_year_end=fiscal_year_end,
        revenue=revenue_value,
        revenue_tag=revenue_tag,
        net_income=net_income_value,
        net_income_tag=net_income_tag,
        operating_cash_flow=operating_cash_flow_value,
        operating_cash_flow_tag=operating_cash_flow_tag,
        capital_spending=capital_spending_value,
        capital_spending_tag=capital_spending_tag,
        equity=equity_value,
        equity_tag=equity_tag,
        roe_percent=roe,
        roe_tag=roe_tag,
        owner_earnings=owner_earnings,
        owner_earnings_tag=owner_earnings_tag,
    )


def _all_or_unknown(values: list[float | None], predicate: Any) -> str:
    if any(value is None for value in values):
        return "not known"
    return "pass" if all(predicate(value) for value in values) else "fail"


def compute_checks(rows: list[YearRow]) -> dict[str, str]:
    roe_values = [row.roe_percent for row in rows]
    owner_earnings = [row.owner_earnings for row in rows]
    growth = "not known"
    if rows and owner_earnings[0] is not None and owner_earnings[-1] is not None:
        growth = "pass" if owner_earnings[-1] > owner_earnings[0] else "fail"
    return {
        "ROE of 15% or more every year": _all_or_unknown(
            roe_values, lambda value: value >= 15
        ),
        "Owner earnings positive every year": _all_or_unknown(
            owner_earnings, lambda value: value > 0
        ),
        "Owner earnings grew, first year to last": growth,
    }


def analyze_ticker(ticker: str, user_agent: str | None = None) -> dict[str, Any]:
    normalized_ticker = ticker.upper().strip()
    if not normalized_ticker:
        raise ValueError("Ticker is required")
    validated_user_agent = _validated_user_agent(user_agent)
    cik, mapped_name = resolve_cik(normalized_ticker, validated_user_agent)
    company_facts = _fetch_json(FACTS_URL.format(cik=cik), validated_user_agent)
    fiscal_year_ends = _candidate_fiscal_year_ends(company_facts)
    if len(fiscal_year_ends) < 5:
        raise RuntimeError(
            f"SEC company facts contain only {len(fiscal_year_ends)} eligible fiscal years"
        )
    rows = [build_year_row(company_facts, end) for end in fiscal_year_ends]
    return {
        "ticker": normalized_ticker,
        "company": company_facts.get("entityName") or mapped_name,
        "cik": f"{cik:010d}",
        "units": "USD millions except ROE",
        "rows": [asdict(row) for row in rows],
        "checks": compute_checks(rows),
    }


def _format_money(value: float | None) -> str:
    if value is None:
        return "not found"
    if abs(value - round(value)) < 0.000001:
        return f"{round(value):,.0f}"
    return f"{value:,.1f}"


def _format_percent(value: float | None) -> str:
    if value is None:
        return "not known"
    return f"{value:.1f}%"


def render_report(analysis: dict[str, Any]) -> str:
    lines = [
        f"{analysis['ticker']} — {analysis['company']}",
        "Data source: SEC EDGAR company facts; 10-K only",
        "Amounts: USD millions",
        "",
    ]
    columns = (
        ("Revenue", "revenue", "revenue_tag", _format_money),
        ("Net income", "net_income", "net_income_tag", _format_money),
        (
            "Operating cash flow",
            "operating_cash_flow",
            "operating_cash_flow_tag",
            _format_money,
        ),
        ("Capital spending", "capital_spending", "capital_spending_tag", _format_money),
        ("Equity", "equity", "equity_tag", _format_money),
        ("ROE", "roe_percent", "roe_tag", _format_percent),
        ("Owner earnings", "owner_earnings", "owner_earnings_tag", _format_money),
    )
    for row in analysis["rows"]:
        lines.append(f"Fiscal year end: {row['fiscal_year_end']}")
        for label, value_key, tag_key, formatter in columns:
            lines.append(
                f"  {label}: {formatter(row[value_key])} | XBRL: {row[tag_key]}"
            )
        lines.append("")
    lines.append("Buffett checks")
    for label, result in analysis["checks"].items():
        lines.append(f"  {label}: {result}")
    return "\n".join(lines)


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Compute a five-year Buffett screen from SEC EDGAR 10-K facts."
    )
    parser.add_argument("ticker", help="U.S. public-company ticker, for example COST")
    parser.add_argument(
        "--json", action="store_true", help="Print machine-readable JSON instead of the report"
    )
    parser.add_argument(
        "--user-agent",
        help="SEC User-Agent containing your name and email; SEC_USER_AGENT is preferred",
    )
    return parser.parse_args()


def main() -> int:
    args = _parse_args()
    try:
        analysis = analyze_ticker(args.ticker, args.user_agent)
    except (ValueError, RuntimeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    if args.json:
        print(json.dumps(analysis, indent=2))
    else:
        print(render_report(analysis))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
