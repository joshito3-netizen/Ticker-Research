"""Minimal Lab 13 mandate check for the newly added Lab 14 candidate E.

The earlier Lab 13 file was not present in this repository, so this file does
not invent candidates A--D. It checks only the required benchmark candidate E.
"""

from __future__ import annotations

from typing import Mapping

from portfolio import (
    ASSETS,
    EXPECTED_RETURNS,
    OBJECTIVE_RETURN,
    RESERVE_ELIGIBLE,
    calculate_expected_return,
    calculate_reserve_weight,
    define_portfolios,
    meets_objective,
    VOLATILITIES,
)


MINIMUM_RESERVE_WEIGHT = 0.03
CANDIDATE_E = define_portfolios(ASSETS, VOLATILITIES)["Benchmark"]


def check_candidate(
    weights: Mapping[str, float],
    objective_return: float = OBJECTIVE_RETURN,
    minimum_reserve_weight: float = MINIMUM_RESERVE_WEIGHT,
) -> dict[str, object]:
    """Check the candidate's return objective and hard reserve rule."""

    expected_return = calculate_expected_return(ASSETS, weights, EXPECTED_RETURNS)
    reserve_weight = calculate_reserve_weight(weights, RESERVE_ELIGIBLE)
    return {
        "expected_return": expected_return,
        "reserve_weight": reserve_weight,
        "passes_return": meets_objective(expected_return, objective_return),
        "passes_reserve": reserve_weight >= minimum_reserve_weight,
        "passes_mandate": (
            meets_objective(expected_return, objective_return)
            and reserve_weight >= minimum_reserve_weight
        ),
    }


def main() -> None:
    """Print candidate E's mandate verdict."""

    result = check_candidate(CANDIDATE_E)
    print("Candidate E — 40% IG bond fund / 60% global equity index fund")
    print(
        f"Return objective: {result['expected_return']:.2%} "
        f"({'pass' if result['passes_return'] else 'fail'})"
    )
    print(
        f"Reserve rule: {result['reserve_weight']:.1%} versus "
        f"{MINIMUM_RESERVE_WEIGHT:.1%} minimum "
        f"({'pass' if result['passes_reserve'] else 'fail'})"
    )
    print(f"Mandate verdict: {'PASS' if result['passes_mandate'] else 'FAIL'}")


if __name__ == "__main__":
    main()
