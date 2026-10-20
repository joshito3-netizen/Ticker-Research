"""Microsoft Project 1 finance engine.

The engine reads traceable inputs from ``data/model_inputs.json``, builds a
five-year three-statement forecast, values enterprise FCFF, and returns only
structured results. The interface never owns finance logic.

USD millions except per-share data. Standard library only.
"""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass, replace
from datetime import datetime, timezone
import json
import math
from pathlib import Path
from typing import Any, Iterable


ROOT = Path(__file__).resolve().parent
INPUT_PATH = ROOT / "data" / "model_inputs.json"
OUTPUT_JSON = ROOT / "outputs" / "visible_output.json"
OUTPUT_MD = ROOT / "outputs" / "visible_output.md"
YEARS = tuple(range(2027, 2032))
TOLERANCE = 1e-6


@dataclass(frozen=True)
class Drivers:
    productivity_growth: tuple[float, ...]
    cloud_growth: tuple[float, ...]
    personal_growth: tuple[float, ...]
    ebitda_margin: tuple[float, ...]
    cash_capex_ratio: tuple[float, ...]
    finance_lease_addition_ratio: tuple[float, ...]
    depreciation_rate: float
    amortization: tuple[float, ...]
    tax_rate: float
    stock_compensation_ratio: float
    finance_lease_principal_rate: float
    finance_lease_interest_rate: float
    debt_interest_rate: float
    cash_yield: float
    dividend_growth: float
    operating_cash_ratio: float
    investment_recovery: float
    wacc: float
    terminal_growth: float


def load_inputs(path: Path = INPUT_PATH) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def drivers_from_dict(values: dict[str, Any]) -> Drivers:
    tuple_fields = {
        "productivity_growth", "cloud_growth", "personal_growth",
        "ebitda_margin", "cash_capex_ratio", "finance_lease_addition_ratio",
        "amortization",
    }
    cooked = {
        key: tuple(value) if key in tuple_fields else value
        for key, value in values.items()
    }
    return Drivers(**cooked)


def shifted(values: Iterable[float], amount: float) -> tuple[float, ...]:
    return tuple(value + amount for value in values)


def validate_drivers(d: Drivers) -> None:
    schedules = (
        d.productivity_growth, d.cloud_growth, d.personal_growth,
        d.ebitda_margin, d.cash_capex_ratio,
        d.finance_lease_addition_ratio, d.amortization,
    )
    if any(len(schedule) != len(YEARS) for schedule in schedules):
        raise ValueError("Every forecast schedule must contain exactly five years")
    if any(not math.isfinite(value) for schedule in schedules for value in schedule):
        raise ValueError("Forecast schedules must contain only finite values")
    if any(growth <= -1 for schedule in schedules[:3] for growth in schedule):
        raise ValueError("Revenue growth cannot be -100% or lower")
    if any(not 0 <= margin <= 1 for margin in d.ebitda_margin):
        raise ValueError("EBITDA margin must stay between 0% and 100%")
    if any(value < 0 for value in d.cash_capex_ratio + d.finance_lease_addition_ratio):
        raise ValueError("Capital-investment ratios cannot be negative")
    if not 0 <= d.tax_rate < 1:
        raise ValueError("Tax rate must be at least 0% and below 100%")
    if not 0 < d.depreciation_rate <= 1:
        raise ValueError("Depreciation rate must be above 0% and at most 100%")
    if not -1 < d.terminal_growth < d.wacc:
        raise ValueError("Terminal growth must be below WACC")
    if d.wacc <= -1:
        raise ValueError("WACC must exceed -100%")


def historical_row(h: dict[str, float]) -> dict[str, float]:
    row = deepcopy(h)
    row.update(
        productivity=h["productivity_revenue"],
        cloud=h["cloud_revenue"],
        personal=h["personal_revenue"],
        short_investments=h["short_investments"],
        other_current_assets=h["other_current_assets"],
        operating_rou=h["operating_rou"],
        investments=h["equity_investments"],
        other_long_assets=h["other_long_assets"],
        compensation=h["accrued_compensation"],
        unearned=h["short_unearned"] + h["long_unearned"],
        operating_payables=h["accounts_payable"],
        other_current_liabilities=h["other_current_liabilities_residual"],
        tax_liabilities=h["short_term_taxes"] + h["long_term_taxes"] + h["deferred_taxes"],
        operating_leases=h["operating_lease_current"] + h["operating_lease_long"],
        finance_leases=h["finance_lease_current"] + h["finance_lease_long"],
        other_long_liabilities=h["other_long_liabilities_residual"],
        debt=h["debt_current"] + h["debt_long"],
    )
    compute_totals(row)
    return row


ASSET_KEYS = (
    "cash", "short_investments", "receivables", "inventory",
    "other_current_assets", "ppe", "operating_rou", "investments",
    "goodwill", "intangibles", "other_long_assets",
)
LIABILITY_KEYS = (
    "operating_payables", "compensation", "unearned",
    "other_current_liabilities", "tax_liabilities", "operating_leases",
    "other_long_liabilities", "debt", "finance_leases",
)
WC_ASSETS = ("receivables", "inventory", "other_current_assets")
WC_LIABILITIES = ("operating_payables", "compensation", "unearned")


def compute_totals(row: dict[str, float]) -> None:
    row["total_assets"] = sum(row[key] for key in ASSET_KEYS)
    row["total_liabilities"] = sum(row[key] for key in LIABILITY_KEYS)
    row["liabilities_and_equity"] = row["total_liabilities"] + row["equity"]
    row["balance_gap"] = row["total_assets"] - row["liabilities_and_equity"]


def net_working_capital(row: dict[str, float]) -> float:
    return sum(row[key] for key in WC_ASSETS) - sum(row[key] for key in WC_LIABILITIES)


def require_near_zero(value: float, label: str) -> None:
    if not math.isfinite(value) or abs(value) > TOLERANCE:
        raise ValueError(f"{label}: gap {value:.9f} USD millions")


def project(h: dict[str, float], d: Drivers) -> list[dict[str, float]]:
    """Roll five articulated statements without a balance-sheet plug."""
    validate_drivers(d)
    opening = historical_row(h)
    require_near_zero(opening["balance_gap"], "FY2026 base-year balance-sheet reconciliation")
    if abs(opening["total_assets"] - h["total_assets"]) > TOLERANCE:
        raise ValueError("FY2026 assets do not reconcile to the filing")
    if abs(opening["total_liabilities"] - h["total_liabilities"]) > TOLERANCE:
        raise ValueError("FY2026 liabilities do not reconcile to the filing")

    ratios = {key: opening[key] / opening["revenue"] for key in WC_ASSETS + WC_LIABILITIES}
    results: list[dict[str, float]] = []
    for index, year in enumerate(YEARS):
        row = opening.copy()
        row["year"] = year
        row["productivity"] = opening["productivity"] * (1 + d.productivity_growth[index])
        row["cloud"] = opening["cloud"] * (1 + d.cloud_growth[index])
        row["personal"] = opening["personal"] * (1 + d.personal_growth[index])
        row["revenue"] = row["productivity"] + row["cloud"] + row["personal"]
        row["growth"] = row["revenue"] / opening["revenue"] - 1

        row["cash_capex"] = row["revenue"] * d.cash_capex_ratio[index]
        row["finance_lease_additions"] = row["revenue"] * d.finance_lease_addition_ratio[index]
        row["total_capex"] = row["cash_capex"] + row["finance_lease_additions"]
        row["depreciation"] = min(
            opening["ppe"] + row["total_capex"],
            d.depreciation_rate * (opening["ppe"] + 0.5 * row["total_capex"]),
        )
        row["amortization"] = min(opening["intangibles"], d.amortization[index])
        row["da"] = row["depreciation"] + row["amortization"]
        row["ppe"] = opening["ppe"] + row["total_capex"] - row["depreciation"]
        row["intangibles"] = opening["intangibles"] - row["amortization"]

        row["ebitda"] = row["revenue"] * d.ebitda_margin[index]
        row["cash_operating_costs"] = row["revenue"] - row["ebitda"]
        row["ebit"] = row["ebitda"] - row["da"]
        row["ebit_margin"] = row["ebit"] / row["revenue"]
        row["stock_compensation"] = row["revenue"] * d.stock_compensation_ratio
        row["interest_income"] = (opening["cash"] + opening["short_investments"]) * d.cash_yield
        row["debt_interest"] = opening["debt"] * d.debt_interest_rate
        row["lease_interest"] = opening["finance_leases"] * d.finance_lease_interest_rate
        row["interest_expense"] = row["debt_interest"] + row["lease_interest"]
        row["other_income"] = row["interest_income"] - row["interest_expense"]
        row["pretax_income"] = row["ebit"] + row["other_income"]
        row["tax"] = max(0.0, row["pretax_income"]) * d.tax_rate
        row["net_income"] = row["pretax_income"] - row["tax"]
        row["eps"] = row["net_income"] / h["diluted_shares"]

        for key in WC_ASSETS + WC_LIABILITIES:
            row[key] = ratios[key] * row["revenue"]
        row["nwc"] = net_working_capital(row)
        row["delta_nwc"] = row["nwc"] - net_working_capital(opening)

        row["debt_repayment"] = 0.0
        row["debt_issuance"] = 0.0
        row["finance_lease_principal"] = opening["finance_leases"] * d.finance_lease_principal_rate
        row["finance_leases"] = (
            opening["finance_leases"] + row["finance_lease_additions"]
            - row["finance_lease_principal"]
        )
        row["dividends"] = h["dividends"] * (1 + d.dividend_growth) ** (index + 1)
        row["buybacks"] = row["stock_compensation"]

        row["cfo"] = row["net_income"] + row["da"] + row["stock_compensation"] - row["delta_nwc"]
        row["cfi"] = -row["cash_capex"]
        row["cff"] = -row["finance_lease_principal"] - row["dividends"] - row["buybacks"]
        row["opening_cash"] = opening["cash"]
        row["change_cash"] = row["cfo"] + row["cfi"] + row["cff"]
        row["cash"] = opening["cash"] + row["change_cash"]
        row["equity"] = (
            opening["equity"] + row["net_income"] + row["stock_compensation"]
            - row["dividends"] - row["buybacks"]
        )

        row["nopat"] = row["ebit"] - max(0.0, row["ebit"]) * d.tax_rate
        row["fcff"] = (
            row["nopat"] + row["da"] - row["cash_capex"]
            - row["finance_lease_additions"] - row["delta_nwc"]
        )
        operating_tax = max(0.0, row["ebit"]) * d.tax_rate
        row["fcff_from_cash"] = (
            row["cfo"] - row["stock_compensation"] - row["interest_income"]
            + row["interest_expense"] + row["tax"] - operating_tax
            - row["cash_capex"] - row["finance_lease_additions"]
        )
        compute_totals(row)

        checks = {
            "balance_sheet": row["balance_gap"],
            "cash_tie": row["cash"] - opening["cash"] - row["cfo"] - row["cfi"] - row["cff"],
            "ppe_roll": row["ppe"] - opening["ppe"] - row["total_capex"] + row["depreciation"],
            "lease_roll": row["finance_leases"] - opening["finance_leases"] - row["finance_lease_additions"] + row["finance_lease_principal"],
            "equity_roll": row["equity"] - opening["equity"] - row["net_income"] - row["stock_compensation"] + row["dividends"] + row["buybacks"],
            "fcff_reconciliation": row["fcff"] - row["fcff_from_cash"],
        }
        for name, gap in checks.items():
            require_near_zero(gap, f"FY{year} {name}")
        if row["cash"] < -TOLERANCE:
            raise ValueError(f"FY{year}: cash becomes negative; financing policy is incomplete")
        if any(row[key] < -TOLERANCE for key in ASSET_KEYS + LIABILITY_KEYS):
            raise ValueError(f"FY{year}: an asset or liability becomes negative")
        row["checks"] = checks
        results.append(row)
        opening = row
    return results


def value_forecast(h: dict[str, float], d: Drivers, forecast: list[dict[str, float]]) -> dict[str, float]:
    validate_drivers(d)
    if len(forecast) != 5:
        raise ValueError("Valuation requires exactly five forecast years")
    pv_explicit = sum(row["fcff"] / (1 + d.wacc) ** period for period, row in enumerate(forecast, 1))
    terminal_fcff = forecast[-1]["fcff"] * (1 + d.terminal_growth)
    terminal_value = terminal_fcff / (d.wacc - d.terminal_growth)
    pv_terminal = terminal_value / (1 + d.wacc) ** 5
    enterprise_value = pv_explicit + pv_terminal
    required_operating_cash = h["revenue"] * d.operating_cash_ratio
    excess_cash = max(0.0, h["cash"] + h["short_investments"] - required_operating_cash)
    investment_value = h["equity_investments"] * d.investment_recovery
    debt = h["debt_current"] + h["debt_long"]
    finance_leases = h["finance_lease_current"] + h["finance_lease_long"]
    equity_value = enterprise_value + excess_cash + investment_value - debt - finance_leases
    return {
        "pv_explicit": pv_explicit,
        "terminal_fcff": terminal_fcff,
        "terminal_value": terminal_value,
        "pv_terminal": pv_terminal,
        "enterprise_value": enterprise_value,
        "required_operating_cash": required_operating_cash,
        "excess_cash": excess_cash,
        "investment_value": investment_value,
        "debt": debt,
        "finance_leases": finance_leases,
        "equity_value": equity_value,
        "per_share": equity_value / h["diluted_shares"],
        "terminal_share": pv_terminal / enterprise_value,
    }


def case_drivers(base: Drivers) -> dict[str, Drivers]:
    return {
        "Downside": replace(
            base,
            productivity_growth=shifted(base.productivity_growth, -0.04),
            cloud_growth=shifted(base.cloud_growth, -0.07),
            personal_growth=shifted(base.personal_growth, -0.03),
            ebitda_margin=shifted(base.ebitda_margin, -0.02),
            cash_capex_ratio=shifted(base.cash_capex_ratio, 0.03),
            finance_lease_addition_ratio=shifted(base.finance_lease_addition_ratio, 0.01),
            wacc=0.105,
            terminal_growth=0.025,
        ),
        "Base": base,
        "Upside": replace(
            base,
            productivity_growth=shifted(base.productivity_growth, 0.02),
            cloud_growth=shifted(base.cloud_growth, 0.03),
            personal_growth=shifted(base.personal_growth, 0.01),
            ebitda_margin=shifted(base.ebitda_margin, 0.01),
            cash_capex_ratio=shifted(base.cash_capex_ratio, -0.02),
            finance_lease_addition_ratio=shifted(base.finance_lease_addition_ratio, -0.005),
            wacc=0.088,
            terminal_growth=0.035,
        ),
    }


def sensitivity_grid(h: dict[str, float], base: Drivers) -> list[dict[str, float]]:
    forecast = project(h, base)
    cells = []
    for wacc in (0.085, 0.095, 0.105):
        for growth in (0.02, 0.03, 0.04):
            value = value_forecast(h, replace(base, wacc=wacc, terminal_growth=growth), forecast)
            cells.append({"wacc": wacc, "terminal_growth": growth, "per_share": value["per_share"]})
    return cells


def one_at_a_time_sensitivity(h: dict[str, float], base: Drivers) -> list[dict[str, Any]]:
    """Change one operating driver at a time and rank by per-share span."""
    specifications = (
        ("Cloud growth", "cloud_growth", -0.03, 0.03, "percentage-point shift in all five years"),
        ("Productivity growth", "productivity_growth", -0.02, 0.02, "percentage-point shift in all five years"),
        ("EBITDA margin", "ebitda_margin", -0.01, 0.01, "percentage-point shift in all five years"),
        ("Cash capex / revenue", "cash_capex_ratio", -0.02, 0.02, "percentage-point shift in all five years"),
        ("Finance-lease additions / revenue", "finance_lease_addition_ratio", -0.01, 0.01, "percentage-point shift in all five years"),
    )
    records: list[dict[str, Any]] = []
    for label, field, low_shift, high_shift, unit in specifications:
        runs = []
        for level, change in (("Lower", low_shift), ("Base", 0.0), ("Higher", high_shift)):
            candidate = replace(base, **{field: shifted(getattr(base, field), change)})
            forecast = project(h, candidate)
            valuation = value_forecast(h, candidate, forecast)
            runs.append({
                "level": level,
                "shift": change,
                "fy2031_ebit": forecast[-1]["ebit"],
                "fy2031_fcff": forecast[-1]["fcff"],
                "per_share": valuation["per_share"],
            })
        records.append({
            "driver": label,
            "field": field,
            "unit": unit,
            "runs": runs,
            "ebit_span": max(run["fy2031_ebit"] for run in runs) - min(run["fy2031_ebit"] for run in runs),
            "fcff_span": max(run["fy2031_fcff"] for run in runs) - min(run["fy2031_fcff"] for run in runs),
            "per_share_span": max(run["per_share"] for run in runs) - min(run["per_share"] for run in runs),
        })
    return sorted(records, key=lambda record: record["per_share_span"], reverse=True)


def comparable_analysis(comparables: dict[str, Any]) -> dict[str, Any]:
    """Calculate one consistent equity and enterprise-value peer multiple."""
    target = comparables["target"]
    admitted = [row for row in comparables["candidates"] if row["decision"] in {"use", "qualify"}]
    if not admitted:
        raise ValueError("Comparable analysis has no admitted peer")
    if any(row["earnings_published"] > "2026-09-09" for row in [target, *admitted]):
        raise ValueError("Comparable earnings were not public by the comparison date")

    peers = []
    for row in admitted:
        equity_value = row["price"] * row["diluted_shares"]
        enterprise_value = (
            equity_value + row["term_debt"] + row.get("finance_leases", 0.0)
            - row["cash_and_securities"]
        )
        pe = row["price"] / row["diluted_eps"]
        ev_revenue = enterprise_value / row["revenue"]
        implied_equity_price = pe * target["diluted_eps"]
        implied_target_ev = ev_revenue * target["revenue"]
        implied_target_equity = (
            implied_target_ev + target["cash_and_securities"] - target["term_debt"]
            - target["finance_leases"]
        )
        peers.append({
            "ticker": row["ticker"],
            "decision": row["decision"],
            "reason": row["reason"],
            "pe": pe,
            "ev_revenue": ev_revenue,
            "implied_target_price_pe": implied_equity_price,
            "implied_target_price_ev_revenue": implied_target_equity / target["diluted_shares"],
        })
    return {
        "policy": comparables["policy"],
        "comparison_date": "2026-09-09",
        "target": target,
        "admitted_peers": peers,
        "excluded_candidates": [
            {"ticker": row["ticker"], "reason": row["reason"]}
            for row in comparables["candidates"] if row["decision"] == "exclude"
        ],
        "definition_check": (
            "P/E bridges no cash or debt. EV/Revenue uses dated price × annual diluted shares "
            "+ term debt + finance leases − cash and marketable securities, then applies the peer "
            "multiple to target revenue and completes the target enterprise-to-equity bridge."
        ),
        "limitation": (
            "One qualified peer supplies reference estimates, not a statistical range; annual diluted "
            "shares proxy for point-in-time shares and fiscal windows differ."
        ),
    }


def reverse_dcf_growth_shift(h: dict[str, float], base: Drivers, target_price: float) -> dict[str, Any]:
    """Solve for one uniform shift to the three segment-growth schedules."""
    def price_at(shift: float) -> float:
        candidate = replace(
            base,
            productivity_growth=shifted(base.productivity_growth, shift),
            cloud_growth=shifted(base.cloud_growth, shift),
            personal_growth=shifted(base.personal_growth, shift),
        )
        return value_forecast(h, candidate, project(h, candidate))["per_share"]

    low, high = -0.10, 0.30
    low_price, high_price = price_at(low), price_at(high)
    if not low_price <= target_price <= high_price:
        return {
            "solved": False, "lower_shift": low, "upper_shift": high,
            "lower_price": low_price, "upper_price": high_price,
            "target_price": target_price,
        }
    for _ in range(100):
        midpoint = (low + high) / 2
        if price_at(midpoint) < target_price:
            low = midpoint
        else:
            high = midpoint
    solution = (low + high) / 2
    return {
        "solved": True,
        "uniform_growth_shift": solution,
        "target_price": target_price,
        "implied_price": price_at(solution),
        "held_fixed": [
            "EBITDA margins", "cash and finance-lease investment ratios", "tax rate",
            "WACC", "terminal growth", "bridge balances", "diluted shares", "five-year horizon",
        ],
    }


def run_analysis(overrides: dict[str, Any] | None = None) -> dict[str, Any]:
    inputs = load_inputs()
    h = inputs["historical"]
    base = drivers_from_dict(inputs["base_drivers"])
    overrides = overrides or {}
    for field, value in overrides.items():
        if field.endswith("_shift"):
            target = field.removesuffix("_shift")
            base = replace(base, **{target: shifted(getattr(base, target), float(value))})
        elif field in Drivers.__dataclass_fields__:
            base = replace(base, **{field: float(value)})
        else:
            raise ValueError(f"Unknown driver override: {field}")

    forecast = project(h, base)
    valuation = value_forecast(h, base, forecast)
    scenarios: dict[str, Any] = {}
    for name, drivers in case_drivers(base).items():
        case_forecast = project(h, drivers)
        scenarios[name] = {
            "per_share": value_forecast(h, drivers, case_forecast)["per_share"],
            "fy2031_revenue": case_forecast[-1]["revenue"],
            "fy2031_ebit": case_forecast[-1]["ebit"],
            "fy2031_fcff": case_forecast[-1]["fcff"],
            "wacc": drivers.wacc,
            "terminal_growth": drivers.terminal_growth,
        }

    market_price = inputs["meta"]["market_price"]
    high_value = scenarios["Upside"]["per_share"]
    recommendation = "WATCH / DEFER" if high_value < market_price else "CONDITIONAL INITIATE"
    checks = {
        "base_year_reconciles": True,
        "balance_sheet_balances_all_years": all(abs(row["checks"]["balance_sheet"]) <= TOLERANCE for row in forecast),
        "cash_ties_all_years": all(abs(row["checks"]["cash_tie"]) <= TOLERANCE for row in forecast),
        "fcff_reconciles_all_years": all(abs(row["checks"]["fcff_reconciliation"]) <= TOLERANCE for row in forecast),
    }
    return {
        "meta": inputs["meta"],
        "drivers": {key: getattr(base, key) for key in Drivers.__dataclass_fields__},
        "driver_bounds": inputs["driver_bounds"],
        "historical": h,
        "forecast": forecast,
        "valuation": valuation,
        "scenarios": scenarios,
        "valuation_range": [scenarios["Downside"]["per_share"], scenarios["Upside"]["per_share"]],
        "sensitivity_grid": sensitivity_grid(h, base),
        "operating_sensitivity": one_at_a_time_sensitivity(h, base),
        "comparables": comparable_analysis(inputs["comparables"]),
        "reverse_dcf": reverse_dcf_growth_shift(h, base, market_price),
        "checks": checks,
        "recommendation": recommendation,
        "sources": inputs["sources"],
    }


def _money(value: float) -> str:
    return f"${value:,.2f}"


def visible_record(result: dict[str, Any]) -> dict[str, Any]:
    low, high = result["valuation_range"]
    market = result["meta"]["market_price"]
    return {
        "decision": "Should a buy-side committee with no position initiate MSFT?",
        "as_of": result["meta"]["valuation_date"],
        "financial_statement_date": result["meta"]["financial_statement_date"],
        "evidence_cutoff": result["meta"]["evidence_cutoff"],
        "currency": "USD",
        "units": "USD millions except per-share values",
        "share_basis": result["meta"]["share_basis"],
        "recommendation": result["recommendation"],
        "market_price": market,
        "dcf_base_per_share": result["valuation"]["per_share"],
        "dcf_scenario_range_per_share": [low, high],
        "terminal_value_share": result["valuation"]["terminal_share"],
        "reverse_dcf": result["reverse_dcf"],
        "scenario_values": {name: data["per_share"] for name, data in result["scenarios"].items()},
        "wacc_growth_sensitivity": result["sensitivity_grid"],
        "operating_sensitivity_ranking": [
            {
                "driver": row["driver"],
                "per_share_span": row["per_share_span"],
                "fy2031_ebit_span": row["ebit_span"],
                "fy2031_fcff_span": row["fcff_span"],
            }
            for row in result["operating_sensitivity"]
        ],
        "comparable_references": result["comparables"],
        "forecast_summary": [
            {
                "year": row["year"],
                "revenue": row["revenue"],
                "ebit": row["ebit"],
                "net_income": row["net_income"],
                "cfo": row["cfo"],
                "cash_capex": row["cash_capex"],
                "finance_lease_additions": row["finance_lease_additions"],
                "fcff": row["fcff"],
                "cash": row["cash"],
                "total_assets": row["total_assets"],
                "total_liabilities": row["total_liabilities"],
                "equity": row["equity"],
            }
            for row in result["forecast"]
        ],
        "reversal_trigger": (
            f"Re-underwrite for initiation if price enters the model's supported range ({_money(low)}–{_money(high)}) "
            "or sourced evidence supports materially higher cloud growth and cash returns without persistent lease/capex intensity."
        ),
        "monitoring_triggers": [
            "Intelligent Cloud growth versus cash capex plus new finance-lease assets",
            "EBIT margin after depreciation and finance-lease interest",
            "Commercial RPO conversion to revenue and cash",
            "Finance-lease liabilities and not-yet-commenced datacenter commitments",
        ],
        "checks": result["checks"],
        "bridge": result["valuation"],
        "limitations": [
            "Twelve-month committee action uses a long-duration DCF; no near-term price forecast is claimed.",
            "Forecast drivers are analyst estimates, not management guidance.",
            "All cash and short-term investments above a 2% operating-cash reserve are treated as excess.",
            "Half of equity-investment carrying value is recovered; operating leases remain in operating expense and are not separately deducted.",
            "A September 9 price is from a third-party historical table; filing facts are cross-checked to Microsoft investor relations.",
        ],
    }


def render_markdown(record: dict[str, Any]) -> str:
    low, high = record["dcf_scenario_range_per_share"]
    lines = [
        "# Microsoft Project 1 — Visible Executed Output",
        "",
        f"**Decision:** {record['recommendation']} as of **{record['as_of']}**.",
        f"**Committee question:** {record['decision']}",
        f"**Market price:** {_money(record['market_price'])}; **DCF base:** {_money(record['dcf_base_per_share'])}; "
        f"**causal scenario range:** {_money(low)}–{_money(high)} per diluted share.",
        f"**Share basis:** {record['share_basis']}. Financial statements dated {record['financial_statement_date']}; evidence cutoff {record['evidence_cutoff']}.",
        "",
        "## Scenario output",
        "",
        "| Case | Value per diluted share |",
        "|---|---:|",
    ]
    lines.extend(f"| {name} | {_money(value)} |" for name, value in record["scenario_values"].items())
    lines.extend([
        "",
        f"Terminal value is {record['terminal_value_share']:.1%} of enterprise value.",
        "",
        "## Five-year forecast summary",
        "",
        "| FY | Revenue | EBIT | Net income | CFO | Cash capex | New finance leases | Economic FCFF | Ending cash |",
        "|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ])
    lines.extend(
        f"| {row['year']} | {row['revenue']:,.1f} | {row['ebit']:,.1f} | {row['net_income']:,.1f} | "
        f"{row['cfo']:,.1f} | {row['cash_capex']:,.1f} | {row['finance_lease_additions']:,.1f} | "
        f"{row['fcff']:,.1f} | {row['cash']:,.1f} |"
        for row in record["forecast_summary"]
    )
    lines.extend([
        "",
        "",
        "## Enterprise-to-equity bridge",
        "",
        "| Item | USD millions |",
        "|---|---:|",
        f"| Enterprise value | {record['bridge']['enterprise_value']:,.1f} |",
        f"| Add: excess cash and short-term investments | {record['bridge']['excess_cash']:,.1f} |",
        f"| Add: 50% recovery of equity investments | {record['bridge']['investment_value']:,.1f} |",
        f"| Less: term debt | ({record['bridge']['debt']:,.1f}) |",
        f"| Less: finance-lease liabilities | ({record['bridge']['finance_leases']:,.1f}) |",
        f"| Equity value | {record['bridge']['equity_value']:,.1f} |",
        "",
        "## Comparable references — kept separate from DCF",
        "",
        "| Qualified peer | P/E | MSFT implied price from P/E | EV/Revenue | MSFT implied price from EV/Revenue |",
        "|---|---:|---:|---:|---:|",
    ])
    lines.extend(
        f"| {peer['ticker']} | {peer['pe']:.2f}x | {_money(peer['implied_target_price_pe'])} | "
        f"{peer['ev_revenue']:.2f}x | {_money(peer['implied_target_price_ev_revenue'])} |"
        for peer in record["comparable_references"]["admitted_peers"]
    )
    lines.extend([
        "",
        record["comparable_references"]["limitation"],
        "",
        "The peer methods disagree because P/E transfers the market price of accounting earnings, while EV/Revenue "
        "also reflects the peer's margin, capital intensity, and enterprise-to-equity bridge. Neither is averaged with the DCF.",
        "",
        "## One-at-a-time operating sensitivity ranking",
        "",
        "| Rank | Driver | Value/share span | FY2031 EBIT span | FY2031 FCFF span |",
        "|---:|---|---:|---:|---:|",
    ])
    lines.extend(
        f"| {rank} | {row['driver']} | {_money(row['per_share_span'])} | "
        f"{row['fy2031_ebit_span']:,.1f} | {row['fy2031_fcff_span']:,.1f} |"
        for rank, row in enumerate(record["operating_sensitivity_ranking"], 1)
    )
    lines.extend([
        "",
        "## Recommendation conditions",
        "",
        record["reversal_trigger"],
        "",
        "Monitor:",
        "",
    ])
    lines.extend(f"- {item}" for item in record["monitoring_triggers"])
    lines.extend(["", "## Articulation checks", ""])
    lines.extend(f"- {name.replace('_', ' ').title()}: {'PASS' if passed else 'FAIL'}" for name, passed in record["checks"].items())
    lines.extend(["", "## Limitations", ""])
    lines.extend(f"- {item}" for item in record["limitations"])
    lines.append("")
    return "\n".join(lines)


def export_visible_output(result: dict[str, Any] | None = None) -> dict[str, Any]:
    result = result or run_analysis()
    record = visible_record(result)
    record["generated_at_utc"] = datetime.now(timezone.utc).isoformat()
    OUTPUT_JSON.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    OUTPUT_MD.write_text(render_markdown(record), encoding="utf-8")
    return record


def main() -> None:
    result = run_analysis()
    record = export_visible_output(result)
    print("Microsoft Project 1 finance engine")
    print(f"As of: {record['as_of']}")
    print(f"Recommendation: {record['recommendation']}")
    print(f"Market price: {_money(record['market_price'])}")
    print(f"DCF base: {_money(record['dcf_base_per_share'])}")
    low, high = record["dcf_scenario_range_per_share"]
    print(f"Causal scenario range: {_money(low)}–{_money(high)}")
    print(f"Terminal value share: {record['terminal_value_share']:.1%}")
    print("Checks: " + ", ".join(f"{name}={'PASS' if status else 'FAIL'}" for name, status in record["checks"].items()))
    print(f"Visible output: {OUTPUT_MD.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
