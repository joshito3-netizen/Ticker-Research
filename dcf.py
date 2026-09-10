"""Five-year FCFF DCF model for Microsoft (USD millions, except per-share value)."""

# Editable inputs — Microsoft, FY ended June 30, 2026
starting_fcff = 68196.0  # CFO + after-tax cash interest − capex; USD millions
growth_rates = [0.20, 0.16, 0.13, 0.10, 0.07]  # estimates, Years 1–5
wacc = 0.095  # estimate
terminal_growth = 0.03  # estimate
non_operating_cash = 76843.0  # USD millions
debt = 40294.0  # USD millions
diluted_shares = 7453.0  # millions

# Sensitivity and reverse-DCF controls
wacc_values = [0.085, 0.095, 0.105]
terminal_growth_values = [0.02, 0.03, 0.04]
target_share_price = 491.65  # MSFT close, September 9, 2026
reverse_lower_bound = -0.05
reverse_upper_bound = 0.30  # widened after the required +10% starter bracket had no solution


def dcf_value_per_share(starting, growths, discount_rate, perpetuity_growth, cash, total_debt, shares):
    """Return annual FCFF and the DCF outputs used in the twelve printed lines."""
    if perpetuity_growth >= discount_rate:
        raise ValueError("terminal growth must be less than WACC")
    fcff_by_year, fcff = [], starting
    for growth in growths:
        fcff *= 1 + growth
        fcff_by_year.append(fcff)
    pv_explicit = sum(fcff / (1 + discount_rate) ** year for year, fcff in enumerate(fcff_by_year, 1))
    terminal_value = fcff_by_year[-1] * (1 + perpetuity_growth) / (discount_rate - perpetuity_growth)
    pv_terminal = terminal_value / (1 + discount_rate) ** len(growths)
    enterprise_value = pv_explicit + pv_terminal
    equity_value = enterprise_value + cash - total_debt
    return (fcff_by_year, pv_explicit, terminal_value, pv_terminal, enterprise_value,
            equity_value, equity_value / shares, pv_terminal / enterprise_value)


def print_twelve_lines():
    values = dcf_value_per_share(starting_fcff, growth_rates, wacc, terminal_growth,
                                 non_operating_cash, debt, diluted_shares)
    fcff_by_year, pv_explicit, terminal_value, pv_terminal, ev, equity, per_share, terminal_share = values
    for year, fcff in enumerate(fcff_by_year, 1):
        print(f"FCFF Year {year}: {fcff:.4f}")
    print(f"Present Value of Explicit FCFF: {pv_explicit:.4f}")
    print(f"Terminal Value at Year 5: {terminal_value:.4f}")
    print(f"Present Value of Terminal Value: {pv_terminal:.4f}")
    print(f"Enterprise Value: {ev:.4f}")
    print(f"Equity Value: {equity:.4f}")
    print(f"Value per Diluted Share: {per_share:.4f}")
    print(f"PV of Terminal Value as Share of Enterprise Value: {terminal_share:.4f}")


def value_with_rates(discount_rate, perpetuity_growth):
    return dcf_value_per_share(starting_fcff, growth_rates, discount_rate, perpetuity_growth,
                               non_operating_cash, debt, diluted_shares)[6]


def print_sensitivity_grid():
    print("\nSensitivity grid — value per diluted share ($)")
    print("WACC \\ terminal growth | " + " | ".join(f"{g:.1%}" for g in terminal_growth_values))
    print("-" * (25 + 10 * len(terminal_growth_values)))
    for discount_rate in wacc_values:
        cells = ["invalid" if perpetuity_growth >= discount_rate else f"{value_with_rates(discount_rate, perpetuity_growth):.2f}"
                 for perpetuity_growth in terminal_growth_values]
        print(f"{discount_rate:.1%}".ljust(23) + " | " + " | ".join(cells))


def reverse_dcf_shift():
    """Bisection solve for a uniform shift to all five explicit growth rates."""
    if min(g + reverse_lower_bound for g in growth_rates) <= -1 or min(g + reverse_upper_bound for g in growth_rates) <= -1:
        raise ValueError("a reverse-DCF bound pushes an annual growth rate to -100% or below")

    def value_at(shift):
        return dcf_value_per_share(starting_fcff, [g + shift for g in growth_rates], wacc,
                                   terminal_growth, non_operating_cash, debt, diluted_shares)[6]

    low, high = reverse_lower_bound, reverse_upper_bound
    if not value_at(low) <= target_share_price <= value_at(high):
        return None
    for _ in range(100):
        midpoint = (low + high) / 2
        if value_at(midpoint) < target_share_price:
            low = midpoint
        else:
            high = midpoint
    return (low + high) / 2


def print_reverse_dcf():
    shift = reverse_dcf_shift()
    print("\nReverse DCF")
    print(f"Target share price: ${target_share_price:.2f}")
    if shift is None:
        print(f"No solution in the selected bracket [{reverse_lower_bound:+.1%}, {reverse_upper_bound:+.1%}].")
    else:
        print(f"Solved uniform shift to Years 1–5 growth: {shift:+.2%}")
    print("Held fixed: starting FCFF, WACC, terminal growth, non-operating cash, debt, diluted shares, and the five-year forecast horizon.")


def verify_training_case():
    """Silent regression check for the supplied training grid."""
    expected = [[28.60, 32.94, 39.02], [24.36, 27.50, 31.69], [21.06, 23.41, 26.44]]
    for row, rate in zip(expected, [0.09, 0.10, 0.11]):
        for answer, terminal in zip(row, [0.02, 0.03, 0.04]):
            actual = dcf_value_per_share(100.0, [0.08, 0.06, 0.05, 0.04, 0.03], rate,
                                         terminal, 50.0, 300.0, 50.0)[6]
            assert round(actual, 2) == answer, (actual, answer)


def main():
    verify_training_case()
    print_twelve_lines()
    print_sensitivity_grid()
    print_reverse_dcf()


if __name__ == "__main__":
    main()


# AI-use disclosure: AI was used to help generate and revise this file. Review all
# inputs, sources, assumptions, and outputs before submission.
