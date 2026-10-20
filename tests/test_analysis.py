"""Small, decision-relevant validation suite for the Microsoft model."""

from __future__ import annotations

from dataclasses import replace
import unittest

import analysis


class MicrosoftModelTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.inputs = analysis.load_inputs()
        cls.h = cls.inputs["historical"]
        cls.base = analysis.drivers_from_dict(cls.inputs["base_drivers"])
        cls.forecast = analysis.project(cls.h, cls.base)
        cls.value = analysis.value_forecast(cls.h, cls.base, cls.forecast)

    def test_training_case_known_answer(self) -> None:
        def training_value(wacc: float, growth: float) -> float:
            fcff = 100.0
            path = []
            for rate in (0.08, 0.06, 0.05, 0.04, 0.03):
                fcff *= 1 + rate
                path.append(fcff)
            explicit = sum(value / (1 + wacc) ** year for year, value in enumerate(path, 1))
            terminal = path[-1] * (1 + growth) / (wacc - growth) / (1 + wacc) ** 5
            return (explicit + terminal + 50.0 - 300.0) / 50.0

        expected = (
            (28.60, 32.94, 39.02),
            (24.36, 27.50, 31.69),
            (21.06, 23.41, 26.44),
        )
        for row, wacc in zip(expected, (0.09, 0.10, 0.11)):
            for answer, growth in zip(row, (0.02, 0.03, 0.04)):
                self.assertEqual(round(training_value(wacc, growth), 2), answer)

    def test_base_year_and_statements_articulate(self) -> None:
        opening = analysis.historical_row(self.h)
        self.assertAlmostEqual(opening["total_assets"], 758376.0)
        self.assertAlmostEqual(opening["total_liabilities"], 315989.0)
        self.assertAlmostEqual(opening["balance_gap"], 0.0)
        for row in self.forecast:
            self.assertAlmostEqual(row["balance_gap"], 0.0)
            self.assertAlmostEqual(row["checks"]["cash_tie"], 0.0)
            self.assertAlmostEqual(row["checks"]["fcff_reconciliation"], 0.0)

    def test_bridge_identity(self) -> None:
        value = self.value
        expected = (
            value["enterprise_value"] + value["excess_cash"] + value["investment_value"]
            - value["debt"] - value["finance_leases"]
        )
        self.assertAlmostEqual(value["equity_value"], expected)
        self.assertAlmostEqual(value["per_share"], expected / self.h["diluted_shares"])

    def test_wacc_and_terminal_growth_directions(self) -> None:
        lower_wacc = analysis.value_forecast(self.h, replace(self.base, wacc=0.085), self.forecast)["per_share"]
        higher_wacc = analysis.value_forecast(self.h, replace(self.base, wacc=0.105), self.forecast)["per_share"]
        lower_growth = analysis.value_forecast(self.h, replace(self.base, terminal_growth=0.02), self.forecast)["per_share"]
        higher_growth = analysis.value_forecast(self.h, replace(self.base, terminal_growth=0.04), self.forecast)["per_share"]
        self.assertGreater(lower_wacc, self.value["per_share"])
        self.assertLess(higher_wacc, self.value["per_share"])
        self.assertLess(lower_growth, self.value["per_share"])
        self.assertGreater(higher_growth, self.value["per_share"])

    def test_directional_changed_inputs(self) -> None:
        higher_cloud = replace(self.base, cloud_growth=analysis.shifted(self.base.cloud_growth, 0.01))
        higher_capex = replace(self.base, cash_capex_ratio=analysis.shifted(self.base.cash_capex_ratio, 0.01))
        cloud_value = analysis.value_forecast(self.h, higher_cloud, analysis.project(self.h, higher_cloud))["per_share"]
        capex_value = analysis.value_forecast(self.h, higher_capex, analysis.project(self.h, higher_capex))["per_share"]
        self.assertGreater(cloud_value, self.value["per_share"])
        self.assertLess(capex_value, self.value["per_share"])

    def test_highest_risk_finance_lease_omission(self) -> None:
        no_new_leases = replace(self.base, finance_lease_addition_ratio=(0.0,) * 5)
        omitted_value = analysis.value_forecast(
            self.h, no_new_leases, analysis.project(self.h, no_new_leases)
        )["per_share"]
        self.assertGreater(omitted_value, self.value["per_share"])

    def test_invalid_terminal_boundary_fails_loudly(self) -> None:
        with self.assertRaisesRegex(ValueError, "Terminal growth must be below WACC"):
            analysis.project(self.h, replace(self.base, wacc=0.03, terminal_growth=0.03))

    def test_comparable_definitions(self) -> None:
        result = analysis.comparable_analysis(self.inputs["comparables"])
        self.assertEqual(len(result["admitted_peers"]), 1)
        peer = result["admitted_peers"][0]
        self.assertAlmostEqual(peer["pe"], 244.16 / 7.80)
        crm_ev = 244.16 * 956.0 + 14439.0 - 9565.0
        self.assertAlmostEqual(peer["ev_revenue"], crm_ev / 41525.0)
        self.assertEqual(result["excluded_candidates"][0]["ticker"], "ORCL")


if __name__ == "__main__":
    unittest.main()
