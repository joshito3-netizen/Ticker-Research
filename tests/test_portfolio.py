"""Known-answer and validation tests for the Lab 14 portfolio engine."""

from __future__ import annotations

from copy import deepcopy
from io import StringIO
import unittest

from mandate import CANDIDATE_E, check_candidate
from portfolio import (
    ASSETS,
    CORRELATIONS,
    EXPECTED_RETURNS,
    OBJECTIVE_RETURN,
    RESERVE_ELIGIBLE,
    VOLATILITIES,
    build_covariance_matrix,
    calculate_all_portfolios,
    estimate_from_prices_csv,
    price_portfolio,
    search_lowest_risk_mix,
    validate_correlations,
)


class PortfolioKnownAnswerTests(unittest.TestCase):
    def test_three_published_known_answers(self):
        results = calculate_all_portfolios()
        expected = {
            "Benchmark": ([0.0, 0.0, 0.4, 0.6], "6.80%", "10.46%", "0.0%", True),
            "Equal weight": ([0.25] * 4, "5.20%", "5.21%", "50.0%", False),
            "Inverse volatility": (
                [0.843, 0.060, 0.070, 0.026],
                "3.77%",
                "1.05%",
                "90.3%",
                False,
            ),
        }
        for name, (weights, portfolio_return, volatility, reserve, meets) in expected.items():
            result = results[name]
            actual_weights = list(result["weights"].values())
            for actual, target in zip(actual_weights, weights):
                self.assertAlmostEqual(actual, target, places=3)
            self.assertEqual(f"{result['expected_return']:.2%}", portfolio_return)
            self.assertEqual(f"{result['volatility']:.2%}", volatility)
            self.assertEqual(f"{result['reserve_weight']:.1%}", reserve)
            self.assertEqual(result["meets_objective"], meets)

    def test_changed_ig_equity_correlation_raises_benchmark_volatility(self):
        correlations = deepcopy(CORRELATIONS)
        correlations["Investment-grade bond fund"]["Global equity index fund"] = 0.50
        correlations["Global equity index fund"]["Investment-grade bond fund"] = 0.50
        covariance = build_covariance_matrix(ASSETS, VOLATILITIES, correlations)
        result = price_portfolio(
            ASSETS,
            CANDIDATE_E,
            EXPECTED_RETURNS,
            covariance,
            RESERVE_ELIGIBLE,
            OBJECTIVE_RETURN,
        )
        self.assertEqual(f"{result['volatility']:.2%}", "11.00%")

    def test_out_of_range_correlation_is_refused(self):
        correlations = deepcopy(CORRELATIONS)
        correlations["Investment-grade bond fund"]["Global equity index fund"] = 1.30
        correlations["Global equity index fund"]["Investment-grade bond fund"] = 1.30
        with self.assertRaisesRegex(ValueError, "between -1 and 1"):
            validate_correlations(ASSETS, correlations)

    def test_asymmetric_correlation_is_refused(self):
        correlations = deepcopy(CORRELATIONS)
        correlations["Investment-grade bond fund"]["Global equity index fund"] = 0.50
        with self.assertRaisesRegex(ValueError, "not symmetric"):
            validate_correlations(ASSETS, correlations)

    def test_candidate_e_fails_the_reserve_rule(self):
        result = check_candidate(CANDIDATE_E)
        self.assertTrue(result["passes_return"])
        self.assertEqual(result["reserve_weight"], 0.0)
        self.assertFalse(result["passes_reserve"])
        self.assertFalse(result["passes_mandate"])

    def test_lab15_meridian_known_answer_and_one_point_stress(self):
        baseline = search_lowest_risk_mix(
            ASSETS,
            EXPECTED_RETURNS,
            VOLATILITIES,
            CORRELATIONS,
            OBJECTIVE_RETURN,
            RESERVE_ELIGIBLE,
            0.03,
        )
        self.assertIsNotNone(baseline)
        self.assertEqual(
            [baseline["weights"][asset] for asset in ASSETS],
            [0.0, 0.20, 0.25, 0.55],
        )
        self.assertEqual(f"{baseline['expected_return']:.2%}", "6.51%")
        self.assertEqual(f"{baseline['volatility']:.2%}", "9.44%")

        stressed_returns = dict(EXPECTED_RETURNS)
        stressed_returns["Global equity index fund"] = 0.07
        stressed = search_lowest_risk_mix(
            ASSETS,
            stressed_returns,
            VOLATILITIES,
            CORRELATIONS,
            OBJECTIVE_RETURN,
            RESERVE_ELIGIBLE,
            0.03,
        )
        self.assertIsNotNone(stressed)
        self.assertEqual(
            [stressed["weights"][asset] for asset in ASSETS],
            [0.0, 0.10, 0.10, 0.80],
        )
        self.assertEqual(f"{stressed['expected_return']:.2%}", "6.53%")
        self.assertEqual(f"{stressed['volatility']:.2%}", "12.94%")
        largest_change = max(
            abs(stressed["weights"][asset] - baseline["weights"][asset])
            for asset in ASSETS
        )
        self.assertEqual(f"{largest_change:.0%}", "25%")

    def test_price_csv_estimates_monthly_returns_then_annualizes(self):
        price_csv = StringIO(
            "Date,FUND_A,FUND_B\n"
            "2026-01-31,100,100\n"
            "2026-02-28,101,99\n"
            "2026-03-31,103,100\n"
            "2026-04-30,102,102\n"
        )
        estimate = estimate_from_prices_csv(price_csv)
        self.assertEqual(estimate["assets"], ("FUND_A", "FUND_B"))
        self.assertEqual(estimate["months_used"], 3)
        self.assertEqual(set(estimate["expected_returns"]), {"FUND_A", "FUND_B"})
        self.assertEqual(set(estimate["volatilities"]), {"FUND_A", "FUND_B"})
        self.assertEqual(set(estimate["correlations"]), {"FUND_A", "FUND_B"})


if __name__ == "__main__":
    unittest.main()
