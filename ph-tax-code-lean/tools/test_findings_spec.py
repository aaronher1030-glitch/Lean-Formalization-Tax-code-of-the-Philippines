# -*- coding: utf-8 -*-
import csv
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import findings_spec as spec

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"


class SpecTests(unittest.TestCase):
    def test_benchmark8_truth_on_all_64_rows(self):
        rows = list(csv.DictReader((DATA / "benchmark8_cases.csv").open(encoding="utf-8")))
        self.assertEqual(len(rows), 64)
        for r in rows:
            got = spec.cert8_total(
                int(r["gross_sales_centavos"]), int(r["income_centavos"]),
                int(r["days_late"]), r["elected"].lower() == "true")
            self.assertEqual(got, int(r["total_due"]), r["case_id"])

    def test_loophole_cases_reproduce(self):
        rows = list(csv.DictReader((DATA / "loophole_cases.csv").open(encoding="utf-8")))
        self.assertEqual(len(rows), 11)
        for r in rows:
            if r["checker"] == "checkT":
                got = spec.cert_t_total(
                    int(r["gross_sales"]), int(r["income"]), int(r["days_late"]))
            else:
                got = spec.cert8_total(
                    int(r["gross_sales"]), int(r["income"]),
                    int(r["days_late"]), r["elected"].lower() == "true")
            self.assertEqual(got, int(r["total_centavos"]), r["label"])

    def test_crossover_at_three_million(self):
        self.assertEqual(spec.crossover(300_000_000), 91_000_000)
        self.assertLess(
            spec.bracket_tax(90_999_999) + spec.pct_tax(300_000_000),
            spec.tax8(300_000_000))

    def test_tier_boundaries(self):
        self.assertEqual(spec.classify(299_999_999), "micro")
        self.assertEqual(spec.classify(300_000_000), "small")
        self.assertEqual(spec.classify(2_000_000_000), "medium")
        self.assertEqual(spec.classify(100_000_000_000), "large")

    def test_rates(self):
        self.assertEqual(spec.rates("micro"), (10, 6))
        self.assertEqual(spec.rates("small"), (10, 6))
        self.assertEqual(spec.rates("medium"), (25, 12))
        self.assertEqual(spec.rates("large"), (25, 12))


if __name__ == "__main__":
    unittest.main()
