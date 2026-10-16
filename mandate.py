"""Check candidate portfolios against Meridian's machine-checkable rules."""

# Editable inputs
HOLDINGS = {
    "Cash": {
        "issuer": "none",
        "business_days_to_redeem": 0,
        "reserve_eligible": True,
    },
    "Treasury bills": {
        "issuer": "U.S. Treasury",
        "business_days_to_redeem": 1,
        "reserve_eligible": True,
    },
    "Treasury 10-year note": {
        "issuer": "U.S. Treasury",
        "business_days_to_redeem": 1,
        "reserve_eligible": True,
    },
    "Global equity index fund": {
        "issuer": "diversified fund",
        "business_days_to_redeem": 2,
        "reserve_eligible": False,
    },
    "Investment-grade bond fund": {
        "issuer": "diversified fund",
        "business_days_to_redeem": 3,
        "reserve_eligible": False,
    },
    "Private real estate fund": {
        "issuer": "diversified fund",
        "business_days_to_redeem": 90,
        "reserve_eligible": False,
    },
    "Acme Corp bonds": {
        "issuer": "Acme Corp",
        "business_days_to_redeem": 4,
        "reserve_eligible": False,
    },
    "Acme Corp stock": {
        "issuer": "Acme Corp",
        "business_days_to_redeem": 1,
        "reserve_eligible": False,
    },
}

CANDIDATES = {
    "A": {
        "Cash": 2,
        "Treasury bills": 2,
        "Treasury 10-year note": 10,
        "Global equity index fund": 60,
        "Investment-grade bond fund": 26,
        "Private real estate fund": 0,
        "Acme Corp bonds": 0,
        "Acme Corp stock": 0,
    },
    "B": {
        "Cash": 1,
        "Treasury bills": 0,
        "Treasury 10-year note": 0,
        "Global equity index fund": 55,
        "Investment-grade bond fund": 20,
        "Private real estate fund": 15,
        "Acme Corp bonds": 5,
        "Acme Corp stock": 4,
    },
    "C": {
        "Cash": 1,
        "Treasury bills": 1,
        "Treasury 10-year note": 0,
        "Global equity index fund": 70,
        "Investment-grade bond fund": 20,
        "Private real estate fund": 0,
        "Acme Corp bonds": 0,
        "Acme Corp stock": 8,
    },
    # Attack portfolio: feasible for the checker, but likely unsuitable for S2.
    "D": {
        "Cash": 3,
        "Treasury bills": 97,
        "Treasury 10-year note": 0,
        "Global equity index fund": 0,
        "Investment-grade bond fund": 0,
        "Private real estate fund": 0,
        "Acme Corp bonds": 0,
        "Acme Corp stock": 0,
    },
}

RESERVE_SIZE_USD_MILLIONS = 100
QUARTERLY_DISTRIBUTION_USD_MILLIONS = 0.75
QUARTERS_TO_COVER = 4
LIQUIDITY_WINDOW_BUSINESS_DAYS = 5
MINIMUM_LIQUID_SHARE_PERCENT = 90
ISSUER_LIMIT_PERCENT = 8
ISSUER_LIMIT_EXEMPTIONS = {"none", "U.S. Treasury", "diversified fund"}


def status(passes):
    """Return the required display label for a Boolean result."""
    return "pass" if passes else "FAIL"


def check_candidate(name, weights, reserve_minimum_percent):
    """Calculate and print every checkable rule for one candidate."""
    total_weight = sum(weights.values())
    lowest_weight = min(weights.values())
    reserve_weight = sum(
        weights[holding]
        for holding, details in HOLDINGS.items()
        if details["reserve_eligible"]
    )
    liquid_weight = sum(
        weights[holding]
        for holding, details in HOLDINGS.items()
        if details["business_days_to_redeem"]
        <= LIQUIDITY_WINDOW_BUSINESS_DAYS
    )

    company_weights = {}
    for holding, details in HOLDINGS.items():
        issuer = details["issuer"]
        if issuer not in ISSUER_LIMIT_EXEMPTIONS:
            company_weights[issuer] = company_weights.get(issuer, 0) + weights[holding]
    largest_company_weight = max(company_weights.values(), default=0)

    results = [
        ("Weights sum to 100", total_weight, abs(total_weight - 100) < 1e-9),
        ("Long-only (lowest weight)", lowest_weight, lowest_weight >= 0),
        (
            f"Reserve >= {reserve_minimum_percent:.1f}%",
            reserve_weight,
            reserve_weight >= reserve_minimum_percent,
        ),
        (
            f"Redeemable in {LIQUIDITY_WINDOW_BUSINESS_DAYS} days "
            f">= {MINIMUM_LIQUID_SHARE_PERCENT:.0f}%",
            liquid_weight,
            liquid_weight >= MINIMUM_LIQUID_SHARE_PERCENT,
        ),
        (
            f"Largest single company <= {ISSUER_LIMIT_PERCENT:.0f}%",
            largest_company_weight,
            largest_company_weight <= ISSUER_LIMIT_PERCENT,
        ),
    ]

    print(f"\nCandidate {name}")
    for label, measured_value, passes in results:
        print(f"  {label}: {measured_value:.1f} {status(passes)}")
    print("  Calendar-year loss: requires CIO clarification")

    failure_count = sum(not passes for _, _, passes in results)
    if failure_count == 0:
        print("  Verdict: passes every checkable rule")
    else:
        print(f"  Verdict: fails {failure_count} rule(s)")


def main():
    reserve_minimum_percent = (
        QUARTERS_TO_COVER
        * QUARTERLY_DISTRIBUTION_USD_MILLIONS
        / RESERVE_SIZE_USD_MILLIONS
        * 100
    )
    print(f"Reserve minimum: {reserve_minimum_percent:.1f}% of the portfolio")

    for name, weights in CANDIDATES.items():
        check_candidate(name, weights, reserve_minimum_percent)


if __name__ == "__main__":
    main()
