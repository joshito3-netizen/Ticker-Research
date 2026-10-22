"""Meridian portfolio risk engine and historical-price estimator."""

from __future__ import annotations

from itertools import combinations
from math import isclose, sqrt
from pathlib import Path
from typing import Mapping, Sequence


# Course-authored training inputs, expressed in decimal units.
ASSETS = (
    "Treasury bills",
    "Treasury 10-year note",
    "Investment-grade bond fund",
    "Global equity index fund",
)
EXPECTED_RETURNS = {
    "Treasury bills": 0.035,
    "Treasury 10-year note": 0.043,
    "Investment-grade bond fund": 0.050,
    "Global equity index fund": 0.080,
}
VOLATILITIES = {
    "Treasury bills": 0.005,
    "Treasury 10-year note": 0.070,
    "Investment-grade bond fund": 0.060,
    "Global equity index fund": 0.160,
}
CORRELATIONS = {
    "Treasury bills": {
        "Treasury bills": 1.00,
        "Treasury 10-year note": 0.10,
        "Investment-grade bond fund": 0.05,
        "Global equity index fund": 0.00,
    },
    "Treasury 10-year note": {
        "Treasury bills": 0.10,
        "Treasury 10-year note": 1.00,
        "Investment-grade bond fund": 0.80,
        "Global equity index fund": -0.10,
    },
    "Investment-grade bond fund": {
        "Treasury bills": 0.05,
        "Treasury 10-year note": 0.80,
        "Investment-grade bond fund": 1.00,
        "Global equity index fund": 0.25,
    },
    "Global equity index fund": {
        "Treasury bills": 0.00,
        "Treasury 10-year note": -0.10,
        "Investment-grade bond fund": 0.25,
        "Global equity index fund": 1.00,
    },
}
OBJECTIVE_RETURN = 0.065  # CPI estimate 2.5% + 4.0%
RESERVE_ELIGIBLE = ("Treasury bills", "Treasury 10-year note")


def validate_correlations(
    assets: Sequence[str], correlations: Mapping[str, Mapping[str, float]]
) -> None:
    """Refuse out-of-range, incomplete, nonsymmetric correlation tables."""

    expected_assets = set(assets)
    if set(correlations) != expected_assets:
        raise ValueError("Correlation rows must match the asset list exactly.")
    for asset in assets:
        if set(correlations[asset]) != expected_assets:
            raise ValueError(
                f"Correlation columns in the {asset!r} row must match the asset list."
            )
        for other_asset in assets:
            correlation = correlations[asset][other_asset]
            if not -1.0 <= correlation <= 1.0:
                raise ValueError(
                    f"Correlation for {asset!r} and {other_asset!r} is {correlation}; "
                    "every correlation must be between -1 and 1."
                )
            reverse = correlations[other_asset][asset]
            if not isclose(correlation, reverse, abs_tol=1e-12):
                raise ValueError(
                    f"Correlation table is not symmetric for {asset!r} and "
                    f"{other_asset!r}: {correlation} does not equal {reverse}."
                )
        if not isclose(correlations[asset][asset], 1.0, abs_tol=1e-12):
            raise ValueError(f"The self-correlation for {asset!r} must equal 1.0.")


def build_covariance_matrix(
    assets: Sequence[str],
    volatilities: Mapping[str, float],
    correlations: Mapping[str, Mapping[str, float]],
) -> dict[str, dict[str, float]]:
    """Build covariance as correlation x first volatility x second volatility."""

    validate_correlations(assets, correlations)
    return {
        asset: {
            other_asset: (
                correlations[asset][other_asset]
                * volatilities[asset]
                * volatilities[other_asset]
            )
            for other_asset in assets
        }
        for asset in assets
    }


def validate_weights(assets: Sequence[str], weights: Mapping[str, float]) -> None:
    """Require one long-only weight per asset and a 100% total."""

    if set(weights) != set(assets):
        raise ValueError("Portfolio weights must include every asset exactly once.")
    if any(weight < 0.0 for weight in weights.values()):
        raise ValueError("Portfolio weights must be long-only (zero or greater).")
    if not isclose(sum(weights.values()), 1.0, abs_tol=1e-12):
        raise ValueError("Portfolio weights must sum to 100%.")


def calculate_expected_return(
    assets: Sequence[str],
    weights: Mapping[str, float],
    expected_returns: Mapping[str, float],
) -> float:
    """Calculate the weighted-average expected return."""

    validate_weights(assets, weights)
    return sum(weights[asset] * expected_returns[asset] for asset in assets)


def calculate_portfolio_variance(
    assets: Sequence[str],
    weights: Mapping[str, float],
    covariance: Mapping[str, Mapping[str, float]],
) -> float:
    """Calculate w'Cov(w), including every cross-asset covariance term."""

    validate_weights(assets, weights)
    return sum(
        weights[asset]
        * weights[other_asset]
        * covariance[asset][other_asset]
        for asset in assets
        for other_asset in assets
    )


def calculate_portfolio_volatility(
    assets: Sequence[str],
    weights: Mapping[str, float],
    covariance: Mapping[str, Mapping[str, float]],
) -> float:
    """Calculate volatility as the square root of portfolio variance."""

    return sqrt(max(calculate_portfolio_variance(assets, weights, covariance), 0.0))


def calculate_reserve_weight(
    weights: Mapping[str, float], reserve_eligible: Sequence[str]
) -> float:
    """Add the weights of the reserve-eligible sleeves."""

    return sum(weights[asset] for asset in reserve_eligible)


def meets_objective(expected_return: float, objective_return: float) -> bool:
    """Report whether the portfolio reaches the mandate's return objective."""

    return expected_return >= objective_return


def calculate_inverse_volatility_weights(
    assets: Sequence[str], volatilities: Mapping[str, float]
) -> dict[str, float]:
    """Set each weight proportional to 1 / volatility, scaled to total 100%."""

    if any(volatilities[asset] <= 0.0 for asset in assets):
        raise ValueError("Inverse-volatility weights require positive volatilities.")
    inverse_volatilities = {
        asset: 1.0 / volatilities[asset] for asset in assets
    }
    total = sum(inverse_volatilities.values())
    return {
        asset: inverse_volatilities[asset] / total for asset in assets
    }


def define_portfolios(
    assets: Sequence[str], volatilities: Mapping[str, float]
) -> dict[str, dict[str, float]]:
    """Create the benchmark, equal-weight, and inverse-volatility baselines."""

    return {
        "Benchmark": {
            "Treasury bills": 0.00,
            "Treasury 10-year note": 0.00,
            "Investment-grade bond fund": 0.40,
            "Global equity index fund": 0.60,
        },
        "Equal weight": {asset: 1.0 / len(assets) for asset in assets},
        "Inverse volatility": calculate_inverse_volatility_weights(
            assets, volatilities
        ),
    }


def price_portfolio(
    assets: Sequence[str],
    weights: Mapping[str, float],
    expected_returns: Mapping[str, float],
    covariance: Mapping[str, Mapping[str, float]],
    reserve_eligible: Sequence[str],
    objective_return: float,
) -> dict[str, object]:
    """Return all displayed measures for one portfolio from the shared inputs."""

    expected_return = calculate_expected_return(assets, weights, expected_returns)
    return {
        "weights": dict(weights),
        "expected_return": expected_return,
        "volatility": calculate_portfolio_volatility(assets, weights, covariance),
        "reserve_weight": calculate_reserve_weight(weights, reserve_eligible),
        "meets_objective": meets_objective(expected_return, objective_return),
    }


def calculate_all_portfolios() -> dict[str, dict[str, object]]:
    """Validate the inputs and price all three Meridian baseline portfolios."""

    covariance = build_covariance_matrix(ASSETS, VOLATILITIES, CORRELATIONS)
    return {
        name: price_portfolio(
            ASSETS,
            weights,
            EXPECTED_RETURNS,
            covariance,
            RESERVE_ELIGIBLE,
            OBJECTIVE_RETURN,
        )
        for name, weights in define_portfolios(ASSETS, VOLATILITIES).items()
    }


def search_lowest_risk_mix(
    assets: Sequence[str],
    expected_returns: Mapping[str, float],
    volatilities: Mapping[str, float],
    correlations: Mapping[str, Mapping[str, float]],
    objective_return: float,
    reserve_eligible: Sequence[str],
    minimum_reserve_weight: float,
    step: float = 0.05,
) -> dict[str, object] | None:
    """Return the lowest-volatility feasible long-only mix on a fixed grid."""

    if not assets:
        raise ValueError("The search requires at least one asset.")
    if set(expected_returns) != set(assets) or set(volatilities) != set(assets):
        raise ValueError("Returns and volatilities must match the asset list exactly.")
    if not 0.0 <= minimum_reserve_weight <= 1.0:
        raise ValueError("The reserve minimum must be between 0% and 100%.")
    if any(asset not in assets for asset in reserve_eligible):
        raise ValueError("Every reserve-eligible asset must be in the asset list.")

    units = round(1.0 / step)
    if step <= 0.0 or not isclose(units * step, 1.0, abs_tol=1e-12):
        raise ValueError("The step must divide 100% into equal whole units.")

    covariance = build_covariance_matrix(assets, volatilities, correlations)
    best: dict[str, object] | None = None

    # Choosing divider locations enumerates every integer composition of
    # ``units`` across the assets exactly once, including zero weights.
    for dividers in combinations(range(units + len(assets) - 1), len(assets) - 1):
        boundaries = (-1, *dividers, units + len(assets) - 1)
        counts = [
            boundaries[index + 1] - boundaries[index] - 1
            for index in range(len(assets))
        ]
        weights = {
            asset: count / units for asset, count in zip(assets, counts)
        }
        portfolio_return = calculate_expected_return(
            assets, weights, expected_returns
        )
        reserve_weight = calculate_reserve_weight(weights, reserve_eligible)
        if portfolio_return + 1e-12 < objective_return:
            continue
        if reserve_weight + 1e-12 < minimum_reserve_weight:
            continue

        volatility = calculate_portfolio_volatility(assets, weights, covariance)
        if best is None or volatility < best["volatility"] - 1e-15:
            best = {
                "weights": weights,
                "expected_return": portfolio_return,
                "volatility": volatility,
                "reserve_weight": reserve_weight,
                "meets_objective": True,
            }

    return best


def estimate_from_prices_csv(
    csv_source: str | Path | object, last_36_months: bool = False
) -> dict[str, object]:
    """Estimate annual returns, volatilities, and correlations from monthly prices.

    The CSV must have an ascending date in its first column and one positive,
    complete adjusted-close price column per asset. Returns are historical
    estimates, not forecasts. The optional window keeps the latest 36 monthly
    returns after returns have been calculated from prices.
    """

    try:
        import pandas as pd
    except ModuleNotFoundError as error:
        raise ModuleNotFoundError(
            "Reading prices.csv requires pandas. Install it with "
            "'python3 -m pip install pandas'."
        ) from error

    prices = pd.read_csv(csv_source)
    if prices.shape[1] < 2:
        raise ValueError("The CSV needs a date column and at least one asset.")
    if prices.columns.duplicated().any():
        raise ValueError("Every CSV column name must be unique.")

    date_column = prices.columns[0]
    try:
        dates = pd.to_datetime(prices[date_column], errors="raise")
    except (TypeError, ValueError) as error:
        raise ValueError("The first CSV column must contain valid dates.") from error
    if dates.duplicated().any():
        raise ValueError("The CSV dates must be unique.")
    if not dates.is_monotonic_increasing:
        raise ValueError("The CSV must be ordered oldest month first.")

    asset_names = [str(column) for column in prices.columns[1:]]
    try:
        asset_prices = prices.iloc[:, 1:].apply(pd.to_numeric, errors="raise")
    except (TypeError, ValueError) as error:
        raise ValueError("Every asset price must be numeric.") from error
    asset_prices.columns = asset_names
    if asset_prices.isna().any().any():
        raise ValueError("Asset prices cannot be blank.")
    if (asset_prices <= 0.0).any().any():
        raise ValueError("Every asset price must be greater than zero.")

    monthly_returns = asset_prices.pct_change(fill_method=None).dropna(how="any")
    if last_36_months:
        monthly_returns = monthly_returns.tail(36)
    if len(monthly_returns) < 2:
        raise ValueError("At least three monthly price rows are required.")

    monthly_volatility = monthly_returns.std(ddof=1)
    if (monthly_volatility <= 0.0).any():
        zero_risk_assets = ", ".join(monthly_volatility[monthly_volatility <= 0.0].index)
        raise ValueError(f"Cannot estimate correlations for constant-price assets: {zero_risk_assets}.")

    annual_returns = monthly_returns.mean() * 12.0
    annual_volatilities = monthly_volatility * sqrt(12.0)
    correlation_frame = monthly_returns.corr()
    correlations = {
        asset: {
            other_asset: float(correlation_frame.loc[asset, other_asset])
            for other_asset in asset_names
        }
        for asset in asset_names
    }
    validate_correlations(asset_names, correlations)

    return {
        "assets": tuple(asset_names),
        "expected_returns": {
            asset: float(annual_returns[asset]) for asset in asset_names
        },
        "volatilities": {
            asset: float(annual_volatilities[asset]) for asset in asset_names
        },
        "correlations": correlations,
        "months_used": len(monthly_returns),
        "start_date": dates.iloc[monthly_returns.index[0]],
        "end_date": dates.iloc[monthly_returns.index[-1]],
    }


def print_results(results: Mapping[str, Mapping[str, object]]) -> None:
    """Print the checkout values with the requested percentage precision."""

    print("Meridian portfolio baselines")
    print(f"Objective: {OBJECTIVE_RETURN:.2%} (CPI 2.5% estimate + 4.0%)")
    for name, result in results.items():
        print(f"\n{name}")
        weights = result["weights"]
        print(
            "Weights (bills / 10-year / IG / equity): "
            + " / ".join(f"{weights[asset]:.1%}" for asset in ASSETS)
        )
        print(f"Expected return: {result['expected_return']:.2%}")
        print(f"Volatility: {result['volatility']:.2%}")
        print(f"Reserve-eligible weight: {result['reserve_weight']:.1%}")
        answer = "yes" if result["meets_objective"] else "no"
        print(f"Meets {OBJECTIVE_RETURN:.1%} objective? {answer}")


def main() -> None:
    """Run the checked engine and print the three baseline portfolios."""

    try:
        results = calculate_all_portfolios()
    except ValueError as error:
        raise SystemExit(f"INPUT ERROR — portfolio engine refused to run: {error}") from error
    print_results(results)


if __name__ == "__main__":
    main()
