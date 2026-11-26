# -*- coding: utf-8 -*-
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import findings_render as render_mod

FIXTURE = [
    {"id": "F001", "family": "equivalence_certT", "kind": "equivalence",
     "theorem": "f001_equivalence_certT_001",
     "prop": "(mkCertT 50000000 50000000 0).total = 4675000", "tactic": "rfl",
     "witness": "gs=income=50000000, days=0", "value": 4675000,
     "source": "tools/findings_spec.py cert_t_total", "note": "n"},
    {"id": "F002", "family": "gap", "kind": "gap", "theorem": "f002_gap_002",
     "prop": "checkT (mkCertT 1000000 100000000 0) = true", "tactic": "decide",
     "witness": "w", "value": None, "source": "s", "note": "n"},
]


class RenderTests(unittest.TestCase):
    def test_golden_snippet(self):
        src = render_mod.render(FIXTURE)
        self.assertIn("import Opt8\nopen PHTax", src)
        self.assertIn("theorem f001_equivalence_certT_001 : "
                      "(mkCertT 50000000 50000000 0).total = 4675000 := rfl", src)
        self.assertIn("theorem f002_gap_002 : "
                      "checkT (mkCertT 1000000 100000000 0) = true := by decide", src)

    def test_forbidden_tokens(self):
        src = render_mod.render(FIXTURE)
        for bad in ("sorry", "native_decide", "Classical.choice", "axiom "):
            self.assertNotIn(bad, src.replace("-- axiom audit", ""))

    def test_one_audit_per_family(self):
        src = render_mod.render(FIXTURE)
        audits = [ln for ln in src.splitlines() if ln.startswith("#print axioms")]
        self.assertEqual(len(audits), len(FIXTURE))
        self.assertEqual(audits,
                         [f"#print axioms {r['theorem']}" for r in FIXTURE])

    def test_each_row_once(self):
        src = render_mod.render(FIXTURE)
        for r in FIXTURE:
            self.assertEqual(src.count(f"theorem {r['theorem']} "), 1)


if __name__ == "__main__":
    unittest.main()
