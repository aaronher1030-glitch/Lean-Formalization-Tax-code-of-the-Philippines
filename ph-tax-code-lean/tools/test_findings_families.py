# -*- coding: utf-8 -*-
import re
import sys
import unittest
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import findings_families as fam

EXPECTED = {
    "equivalence_certT": 32,
    "equivalence_cert8": 96,
    "divergence": 56,
    "boundary": 16,
    "cliff": 18,
    "crossover": 20,
    "monotone": 20,
    "gap": 16,
}
KINDS = {"equivalence", "divergence", "boundary", "incentive", "identity", "gap"}


class FamilyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows = fam.all_findings()

    def test_counts(self):
        counts = Counter(r["family"] for r in self.rows)
        self.assertEqual(dict(counts), EXPECTED)
        self.assertEqual(len(self.rows), 274)
        self.assertEqual(fam.FAMILY_COUNTS, EXPECTED)

    def test_ids_and_names(self):
        ids = [r["id"] for r in self.rows]
        self.assertEqual(ids, [f"F{n:03d}" for n in range(1, 275)])
        names = [r["theorem"] for r in self.rows]
        self.assertEqual(len(set(names)), 274)
        for n in names:
            self.assertRegex(n, r"^[a-z][a-z0-9_]*$")

    def test_schema_and_kinds(self):
        keys = {"id", "family", "kind", "theorem", "prop", "tactic", "witness",
                "value", "source", "note"}
        for r in self.rows:
            self.assertEqual(set(r), keys)
            self.assertIn(r["kind"], KINDS)
            self.assertIn(r["tactic"], ("rfl", "decide"))
            self.assertTrue(r["witness"])
            self.assertNotIn("sorry", r["prop"])
            self.assertNotIn("\n", r["note"])

    def test_divergence_covers_seven_engines(self):
        engines = {r["witness"].split()[0] for r in self.rows if r["family"] == "divergence"}
        self.assertEqual(engines, {"G1_eight_on_income", "G2_no_exempt_floor",
                                   "G3_ineligible_eight", "G4_pct_double",
                                   "G5_missing_pct", "G6_rate10",
                                   "G7_penalty_wrong_base"})

    def test_crossover_is_two_sided(self):
        cr = [r for r in self.rows if r["family"] == "crossover"]
        self.assertEqual(len(cr), 20)
        ups = [r for r in cr if not r["prop"].startswith("¬")]
        lows = [r for r in cr if r["prop"].startswith("¬")]
        self.assertEqual(len(ups), 10)
        self.assertEqual(len(lows), 10)
        self.assertIn("tax8 300000000 ≤ bracketTax 91000000 + pctTax 300000000",
                      [r["prop"] for r in ups])


if __name__ == "__main__":
    unittest.main()
