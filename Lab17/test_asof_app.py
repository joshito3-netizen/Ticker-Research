"""Small live validation for the Lab 17 point-in-time calculations."""

from datetime import date
import unittest

from Lab17.asof_app import audit_series, download_as_known, download_today


class PointInTimeKnownAnswerTests(unittest.TestCase):
    def test_october_2026_known_answer(self):
        vintage_date = date(2026, 10, 5)
        expected = {
            "BAA": (date(2026, 9, 1), 6.47),
            "FEDFUNDS": (date(2026, 9, 1), 3.75),
            "DGS10": (date(2026, 10, 2), 5.28),
            "MORTGAGE30US": (date(2026, 10, 1), 7.28),
        }

        for series_id, (expected_date, expected_value) in expected.items():
            with self.subTest(series_id=series_id):
                frame = download_as_known(series_id, vintage_date)
                latest = frame.iloc[-1]
                self.assertEqual(latest["observation_date"].date(), expected_date)
                self.assertAlmostEqual(float(latest["value"]), expected_value)

    def test_payems_revision_probe(self):
        vintage = download_as_known("PAYEMS", date(2025, 1, 15))
        current = download_today("PAYEMS")
        audit = audit_series(current, vintage)

        latest = vintage.iloc[-1]
        self.assertEqual(latest["observation_date"].date(), date(2024, 12, 1))
        self.assertEqual(float(latest["value"]), 159_536)
        current_december = current.loc[
            current["observation_date"].eq("2024-12-01"), "value"
        ].iloc[0]
        self.assertLess(float(current_december), 159_536)
        self.assertGreater(audit["revised_count"], 0)


if __name__ == "__main__":
    unittest.main()
