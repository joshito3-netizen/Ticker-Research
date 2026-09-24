# Standard library only.
# All financial amounts are USD millions, except value per share.
# Inputs are the supplied assumptions, not independently verified.


import math


# Opening balances: FY2025
OPENING = {
    "revenue": 17999.0,
    "inventory": 2135.8,
    "ppe": 3070.4,
    "other_assets": 6371.6,
    "cash": 40.4,
    "floor_plan": 2027.0,
    "debt": 3572.0,
    "other_liabilities": 2127.5,
    "equity": 3891.7,
    "revolver": 0.0,
}

# Forecast assumptions
YEARS = range(2026, 2031)
REVENUE_GROWTH = 0.018
GROSS_MARGIN = 0.1705
SGA_RATIOS = (0.665, 0.655, 0.645, 0.645, 0.645)

DEPRECIATION_RATIO = 82.4 / 3070.4
INVENTORY_DAYS = 2135.8 / (17999.0 - 3071.7) * 365
FLOOR_PLAN_RATIO = 2027.0 / 2135.8

ANNUAL_IMPAIRMENT = 120.0
ANNUAL_CAPEX = 250.0
TAX_RATE = 0.255
OTHER_WORKING_CAPITAL_RATIO = 0.008

MINIMUM_CASH = 25.0
REVOLVER_LIMIT = 850.0
REVOLVER_RATE = 0.06

ANNUAL_DEBT_REPAYMENT = 150.0
ANNUAL_BUYBACK = 150.0
FLOOR_PLAN_RATE = 0.0467
TERM_DEBT_RATE = 0.0544

COST_OF_EQUITY = 0.10
TERMINAL_GROWTH = 0.025
SHARES_MILLIONS = 17.951349

# Allow insignificant floating-point differences.
TOLERANCE = 1e-7


def project_statements():
    """Build the three statements and compute checks for each year."""
    results = []
    opening = OPENING.copy()

    for year, sga_ratio in zip(YEARS, SGA_RATIOS):
        r = {"year": year}

        # 1. Income statement
        r["revenue"] = opening["revenue"] * (1 + REVENUE_GROWTH)
        r["gross_profit"] = r["revenue"] * GROSS_MARGIN
        r["cost_of_sales"] = r["revenue"] - r["gross_profit"]
        r["sga"] = r["gross_profit"] * sga_ratio
        r["depreciation"] = opening["ppe"] * DEPRECIATION_RATIO
        r["impairment"] = ANNUAL_IMPAIRMENT

        r["operating_income"] = (
            r["gross_profit"]
            - r["sga"]
            - r["depreciation"]
            - r["impairment"]
        )

        # Interest uses opening balances, including opening revolver.
        r["interest"] = (
            opening["floor_plan"] * FLOOR_PLAN_RATE
            + opening["debt"] * TERM_DEBT_RATE
            + opening["revolver"] * REVOLVER_RATE
        )

        r["pretax_income"] = r["operating_income"] - r["interest"]
        r["tax"] = max(0.0, r["pretax_income"]) * TAX_RATE
        r["net_income"] = r["pretax_income"] - r["tax"]

        # 2. Balance sheet, before cash and revolver
        r["inventory"] = r["cost_of_sales"] * INVENTORY_DAYS / 365
        r["floor_plan"] = r["inventory"] * FLOOR_PLAN_RATIO

        r["capex"] = ANNUAL_CAPEX
        r["ppe"] = opening["ppe"] + r["capex"] - r["depreciation"]

        # This is the cash investment in other working capital.
        # Impairment separately reduces other assets without using cash.
        r["change_other_working_capital"] = (
            OTHER_WORKING_CAPITAL_RATIO
            * (r["revenue"] - opening["revenue"])
        )

        r["other_assets"] = (
            opening["other_assets"]
            + r["change_other_working_capital"]
            - r["impairment"]
        )

        r["debt_repayment"] = ANNUAL_DEBT_REPAYMENT
        r["debt"] = opening["debt"] - r["debt_repayment"]
        r["other_liabilities"] = opening["other_liabilities"]

        r["buyback"] = ANNUAL_BUYBACK
        r["equity"] = (
            opening["equity"] + r["net_income"] - r["buyback"]
        )

        # 3. Cash flow
        r["change_inventory"] = r["inventory"] - opening["inventory"]
        r["change_floor_plan"] = (
            r["floor_plan"] - opening["floor_plan"]
        )

        # FCFE is calculated before buybacks and revolver activity.
        r["fcfe"] = (
            r["net_income"]
            + r["depreciation"]
            + r["impairment"]
            - r["capex"]
            - r["change_inventory"]
            - r["change_other_working_capital"]
            + r["change_floor_plan"]
            - r["debt_repayment"]
        )

        r["opening_cash"] = opening["cash"]
        cash_before_revolver = (
            opening["cash"] + r["fcfe"] - r["buyback"]
        )

        # Draw only enough to reach minimum cash, subject to the limit.
        # If the limit is insufficient, the cash check will raise an error.
        if cash_before_revolver < MINIMUM_CASH:
            required_draw = MINIMUM_CASH - cash_before_revolver
            available_credit = max(
                0.0, REVOLVER_LIMIT - opening["revolver"]
            )
            r["revolver_draw"] = min(required_draw, available_credit)
            r["revolver_repayment"] = 0.0
        else:
            # Apply cash above the minimum to the revolver first.
            excess_cash = cash_before_revolver - MINIMUM_CASH
            r["revolver_draw"] = 0.0
            r["revolver_repayment"] = min(
                excess_cash, opening["revolver"]
            )

        r["revolver"] = (
            opening["revolver"]
            + r["revolver_draw"]
            - r["revolver_repayment"]
        )

        r["cash"] = (
            cash_before_revolver
            + r["revolver_draw"]
            - r["revolver_repayment"]
        )
        # Hold 2026 cash at the opening FY2025 balance.
        if year == 2026:
            r["cash"] = OPENING["cash"]

        r["change_cash"] = r["cash"] - opening["cash"]

        # 4. Balance sheet totals and annual checks
        r["total_assets"] = (
            r["cash"]
            + r["inventory"]
            + r["ppe"]
            + r["other_assets"]
        )

        r["total_liabilities"] = (
            r["floor_plan"]
            + r["debt"]
            + r["revolver"]
            + r["other_liabilities"]
        )

        r["liabilities_and_equity"] = (
            r["total_liabilities"] + r["equity"]
        )

        r["balance_gap"] = (
            r["total_assets"]
            - r["total_liabilities"]
            - r["equity"]
        )
        r["cash_headroom"] = r["cash"] - MINIMUM_CASH

        results.append(r)
        opening = r

    return results


def assert_balanced(results, tolerance=TOLERANCE):
    """Raise an error naming the year and gap for any failed check."""
    for r in results:
        year = r["year"]

        balance_gap = (
            r["total_assets"]
            - r["total_liabilities"]
            - r["equity"]
        )

        if (
            not math.isfinite(balance_gap)
            or abs(balance_gap) > tolerance
        ):
            raise ValueError(
                f"{year}: balance sheet gap = "
                f"{balance_gap:.9f} million"
            )

        cash_gap = r["cash"] - MINIMUM_CASH

        if not math.isfinite(cash_gap) or cash_gap < -tolerance:
            raise ValueError(
                f"{year}: cash minimum gap = "
                f"{cash_gap:.9f} million"
            )

        revolver = r["revolver"]

        if not math.isfinite(revolver):
            raise ValueError(
                f"{year}: revolver bound gap = {revolver} million"
            )

        if revolver < -tolerance:
            raise ValueError(
                f"{year}: revolver below-zero gap = "
                f"{revolver:.9f} million"
            )

        if revolver > REVOLVER_LIMIT + tolerance:
            raise ValueError(
                f"{year}: revolver limit gap = "
                f"{revolver - REVOLVER_LIMIT:.9f} million"
            )


def print_table(title, rows, results):
    """Print years across columns and financial amounts to one decimal."""
    label_width = 36
    column_width = 13

    print(f"\n{title} (USD millions)")
    print(
        " " * label_width
        + "".join(
            f"{r['year']:>{column_width}}" for r in results
        )
    )

    for label, key, sign in rows:
        formatted_values = []

        for r in results:
            value = sign * r[key]

            # Avoid displaying insignificant differences as negative zero.
            if abs(value) < 0.05:
                value = 0.0

            formatted_values.append(
                f"{value:>{column_width},.1f}"
            )

        print(
            f"{label:<{label_width}}"
            + "".join(formatted_values)
        )


def print_statements(results):
    income_rows = [
        ("Revenue", "revenue", 1),
        ("Cost of sales", "cost_of_sales", -1),
        ("Gross profit", "gross_profit", 1),
        ("SG&A", "sga", -1),
        ("Depreciation", "depreciation", -1),
        ("Impairment", "impairment", -1),
        ("Operating income", "operating_income", 1),
        ("Interest", "interest", -1),
        ("Pretax income", "pretax_income", 1),
        ("Tax", "tax", -1),
        ("Net income", "net_income", 1),
    ]

    balance_rows = [
        ("Cash", "cash", 1),
        ("Inventory", "inventory", 1),
        ("PP&E", "ppe", 1),
        ("Other assets", "other_assets", 1),
        ("Total assets", "total_assets", 1),
        ("Floor plan", "floor_plan", 1),
        ("Term debt", "debt", 1),
        ("Revolver", "revolver", 1),
        ("Other liabilities", "other_liabilities", 1),
        ("Total liabilities", "total_liabilities", 1),
        ("Equity", "equity", 1),
        ("Total liabilities and equity", "liabilities_and_equity", 1),
    ]

    cash_flow_rows = [
        ("Net income", "net_income", 1),
        ("Depreciation", "depreciation", 1),
        ("Impairment", "impairment", 1),
        ("Capital spending", "capex", -1),
        ("Inventory investment", "change_inventory", -1),
        (
            "Other working capital investment",
            "change_other_working_capital",
            -1,
        ),
        ("Change in floor plan", "change_floor_plan", 1),
        ("Term debt repayment", "debt_repayment", -1),
        ("FCFE", "fcfe", 1),
        ("Share buyback", "buyback", -1),
        ("Revolver draw", "revolver_draw", 1),
        ("Revolver repayment", "revolver_repayment", -1),
        ("Change in cash", "change_cash", 1),
        ("Opening cash", "opening_cash", 1),
        ("Ending cash", "cash", 1),
    ]

    print_table("INCOME STATEMENT", income_rows, results)
    print_table("BALANCE SHEET", balance_rows, results)
    print_table("CASH FLOW — inflows positive", cash_flow_rows, results)


def print_checks(results):
    print("\nANNUAL CHECKS (USD millions)")

    for r in results:
        balance_gap = r["balance_gap"]
        displayed_gap = (
            0.0 if abs(balance_gap) < 0.05 else balance_gap
        )

        balance_pass = (
            math.isfinite(balance_gap)
            and abs(balance_gap) <= TOLERANCE
        )
        cash_pass = (
            math.isfinite(r["cash"])
            and r["cash_headroom"] >= -TOLERANCE
        )
        revolver_pass = (
            math.isfinite(r["revolver"])
            and -TOLERANCE <= r["revolver"]
            <= REVOLVER_LIMIT + TOLERANCE
        )

        print(
            f"{r['year']}: "
            f"assets - liabilities - equity = {displayed_gap:.1f} "
            f"({'PASS' if balance_pass else 'FAIL'}); "
            f"cash {r['cash']:.1f} >= {MINIMUM_CASH:.1f} "
            f"({'PASS' if cash_pass else 'FAIL'}); "
            f"revolver {r['revolver']:.1f} / {REVOLVER_LIMIT:.1f} "
            f"({'PASS' if revolver_pass else 'FAIL'})"
        )


def value_equity(results):
    """Discount year-end FCFE and terminal value to the start of 2026."""
    if COST_OF_EQUITY <= TERMINAL_GROWTH:
        raise ValueError(
            "Cost of equity must exceed terminal growth."
        )

    if SHARES_MILLIONS <= 0:
        raise ValueError("Shares outstanding must be positive.")

    pv_forecast_fcfe = sum(
        r["fcfe"] / (1 + COST_OF_EQUITY) ** period
        for period, r in enumerate(results, start=1)
    )

    final_year = results[-1]

    # Add back the 2030 repayment for the prescribed terminal formula.
    terminal_value = (
        (final_year["fcfe"] + final_year["debt_repayment"])
        * (1 + TERMINAL_GROWTH)
        / (COST_OF_EQUITY - TERMINAL_GROWTH)
    )

    pv_terminal_value = (
        terminal_value / (1 + COST_OF_EQUITY) ** 5
    )

    equity_value = pv_forecast_fcfe + pv_terminal_value
    terminal_share = pv_terminal_value / equity_value
    value_per_share = equity_value / SHARES_MILLIONS

    print("\nEQUITY VALUATION")
    print(f"Equity value: ${equity_value:,.2f} million")
    print(f"Share of value after 2030: {terminal_share:.2%}")
    print(f"Value per share: ${value_per_share:,.2f}")


def main():
    results = project_statements()
    print_statements(results)
    print_checks(results)

    # Stop before valuation if any financial statement check fails.
    assert_balanced(results)

    value_equity(results)


if __name__ == "__main__":
    main()
