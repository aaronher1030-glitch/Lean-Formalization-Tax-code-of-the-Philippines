# -*- coding: utf-8 -*-
import csv
import io
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import findings_report as rep

FIXTURE = [
    {"id": "F001", "family": "equivalence_certT", "kind": "equivalence",
     "theorem": "f001_equivalence_certT_001", "prop": "p", "tactic": "rfl",
     "witness": "w", "value": 5, "source": "s", "note": "n"},
    {"id": "F002", "family": "gap", "kind": "gap", "theorem": "f002_gap_002",
     "prop": "q", "tactic": "decide", "witness": "w", "value": None,
     "source": "s", "note": "n"},
]
META = {"seconds": 12.5, "audit": "propext only"}


class ReportTests(unittest.TestCase):
    def test_summary_order_and_counts(self):
        s = rep.summary(FIXTURE)
        self.assertEqual([r["family"] for r in s], ["equivalence_certT", "gap"])
        self.assertEqual([r["count"] for r in s], [1, 1])

    def test_csv_header_exact(self):
        text = rep.csv_text(FIXTURE)
        header = next(csv.reader(io.StringIO(text)))
        self.assertEqual(header, ["id", "family", "kind", "theorem", "proposition",
                                  "witness", "value_centavos", "source", "note"])

    def test_markdown_contains_counts_and_honesty(self):
        md = rep.markdown(FIXTURE, META)
        self.assertIn("| equivalence_certT | equivalence | 1 |", md)
        self.assertIn("274", md)
        self.assertIn("not 274 loopholes", md)
        self.assertIn("native_decide", md)

    def test_write_outputs(self):
        with tempfile.TemporaryDirectory() as td:
            c = Path(td) / "f.csv"
            m = Path(td) / "f.md"
            rep.write_outputs(FIXTURE, META, c, m)
            self.assertTrue(c.exists() and m.exists())
            self.assertEqual(len(list(csv.DictReader(c.open(encoding="utf-8")))), 2)

    def test_write_outputs_creates_nested_dirs_and_writes_lf(self):
        with tempfile.TemporaryDirectory() as td:
            c = Path(td) / "nested" / "deeper" / "f.csv"
            m = Path(td) / "nested" / "deeper" / "FINDINGS.md"
            self.assertFalse(c.parent.exists())
            rep.write_outputs(FIXTURE, META, c, m)
            self.assertTrue(c.exists() and m.exists())

            csv_bytes = c.read_bytes()
            csv_str = csv_bytes.decode("utf-8")
            self.assertNotIn(b"\r", csv_bytes)
            self.assertNotIn("\r", csv_str)
            self.assertEqual(csv_str.count("\n"), 3)  # header + 2 rows, LF-terminated
            self.assertTrue(csv_str.endswith("\n"))

            md_bytes = m.read_bytes()
            self.assertNotIn(b"\r", md_bytes)
            self.assertNotIn("\r", md_bytes.decode("utf-8"))


if __name__ == "__main__":
    unittest.main()
