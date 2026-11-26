# Task brief (generated from the plan)

Read the plan section below as your requirements. Also binding: the Global
Constraints section of the plan, reproduced here:

- Lean 4.35.0 pinned toolchain, core library only.
- No `native_decide`, no `sorry`; axiom audit must stay at `propext`.
- Do NOT stage, commit, or push anything (standing user rule).
- Python runs as `python -X utf8`; writes use encoding="utf-8".
- Generated `lean/_harness/Findings.lean` stays gitignored.
- `LEAN` env override honored; default ROOT/tools/lean/dist/lean-4.35.0-windows/bin/lean.exe.
- 59/82 hand-written counts must not change.
- Windows: run from repo root `C:/Users/Ma Christine/Downloads/LEAN FORMALIZATION OF TAX CODE/ph-tax-code-lean`.
- Toolchain export for compiles: LEAN="C:/Users/Ma Christine/Downloads/LEAN FORMALIZATION OF TAX CODE/tools/lean/dist/lean-4.35.0-windows/bin/lean.exe".

Frozen row schema for any task using rows:

    {"id": "F001", "family": "...", "kind": "equivalence|divergence|boundary|incentive|identity|gap",
     "theorem": "f001_<family>_001", "prop": "...", "tactic": "rfl"|"decide",
     "witness": "...", "value": int|None, "source": "...", "note": "..."}

---
### Task 1: Independent Python ground truth

**Files:**
- Create: `tools/findings_spec.py`
- Test: `tools/test_findings_spec.py`

**Interfaces:**
- Produces: constants `STATUTE`, `VAT_THRESHOLD`, `TIERS`; functions `bracket_tax(t) -> int`, `pct_tax(gs) -> int`, `tax8(gs) -> int`, `classify(gs) -> str`, `rates(tier) -> tuple[int, int]`, `eligible(gs) -> bool`, `regime_of(gs, elected) -> str`, `surcharge_t(tier, t) -> int`, `interest_t(tier, t, days) -> int`, `penalty_t(tier, t, days) -> int`, `total_due_t(tier, t, days) -> int`, `cert_t_total(gs, inc, days) -> int`, `cert8_total(gs, inc, days, elected) -> int`, `crossover(gs) -> int`.
- Consumes: `data/benchmark8_cases.csv`, `data/loophole_cases.csv` (test fixtures only).

- [ ] **Step 1: Write the failing tests**

Create `tools/test_findings_spec.py`:

```python
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
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `export LEAN="C:/Users/Ma Christine/Downloads/LEAN FORMALIZATION OF TAX CODE/tools/lean/dist/lean-4.35.0-windows/bin/lean.exe" && cd "C:/Users/Ma Christine/Downloads/LEAN FORMALIZATION OF TAX CODE/ph-tax-code-lean" && python -X utf8 -m unittest discover -s tools -p "test_findings_spec.py" -v`
Expected: FAIL/ERROR with `ModuleNotFoundError: No module named 'findings_spec'`.

- [ ] **Step 3: Write the implementation**

Create `tools/findings_spec.py`:

```python
# -*- coding: utf-8 -*-
"""Independent Python ground truth for the findings battery.

Re-implements the verified Lean core in Python. This module supplies witness
inputs and expected values; it never decides what Lean proves. The kernel
judges every proposition the battery generates.
"""

STATUTE = [
    (25_000_000, 40_000_000, 15),
    (40_000_000, 80_000_000, 20),
    (80_000_000, 200_000_000, 25),
    (200_000_000, 800_000_000, 30),
    (800_000_000, None, 35),
]
VAT_THRESHOLD = 300_000_000
TIERS = ("micro", "small", "medium", "large")


def bracket_tax(t):
    total = 0
    for lo, hi, rate in STATUTE:
        if t <= lo:
            break
        base = (min(t, hi) - lo) if hi is not None else (t - lo)
        total += base * rate // 100
    return total


def pct_tax(gs):
    return gs * 3 // 100


def tax8(gs):
    return max(gs - 25_000_000, 0) * 8 // 100


def classify(gs):
    if gs < 300_000_000:
        return "micro"
    if gs < 2_000_000_000:
        return "small"
    if gs < 100_000_000_000:
        return "medium"
    return "large"


def rates(tier):
    return (10, 6) if tier in ("micro", "small") else (25, 12)


def eligible(gs):
    return gs <= VAT_THRESHOLD


def regime_of(gs, elected):
    return "eight" if elected and eligible(gs) else "graduated"


def surcharge_t(tier, t):
    return t * rates(tier)[0] // 100


def interest_t(tier, t, days):
    return t * rates(tier)[1] * days // 36500


def penalty_t(tier, t, days):
    return surcharge_t(tier, t) + interest_t(tier, t, days)


def total_due_t(tier, t, days):
    return t + penalty_t(tier, t, days)


def cert_t_total(gs, inc, days):
    basic = bracket_tax(inc)
    return basic + penalty_t(classify(gs), basic, days)


def cert8_total(gs, inc, days, elected):
    tier = classify(gs)
    if regime_of(gs, elected) == "eight":
        basic = tax8(gs)
    else:
        basic = bracket_tax(inc) + pct_tax(gs)
    return basic + penalty_t(tier, basic, days)


def crossover(gs):
    """First income (centavos) where the graduated base shelters the 8% base."""
    target = tax8(gs) - pct_tax(gs)
    lo, hi = 0, 100_000_000_000
    while lo < hi:
        mid = (lo + hi) // 2
        if bracket_tax(mid) >= target:
            hi = mid
        else:
            lo = mid + 1
    return lo
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd "C:/Users/Ma Christine/Downloads/LEAN FORMALIZATION OF TAX CODE/ph-tax-code-lean" && python -X utf8 -m unittest discover -s tools -p "test_findings_spec.py" -v`
Expected: `OK` with 5 tests.

- [ ] **Step 5: Verify and leave uncommitted**

Run: `cd "C:/Users/Ma Christine/Downloads/LEAN FORMALIZATION OF TAX CODE/ph-tax-code-lean" && git status --short tools/findings_spec.py tools/test_findings_spec.py`
Expected: both listed as untracked. Do NOT stage or commit (standing rule).

---

