# Findings Battery Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build `tools/findings.py`, which generates, compiles and documents 274 kernel-checked findings from the verified PH tax core — one Lean theorem per finding, cross-checked by an independent Python implementation, with no `sorry` and no `native_decide`.

**Architecture:** Eight enumeration families over the verified core produce a flat list of finding rows (one schema). A renderer turns rows into `lean/_harness/Findings.lean`; a report module writes `data/findings.csv` and `FINDINGS.md`; a driver orchestrates enumerate → render → compile (pinned Lean 4.35.0) → axiom audit → write, and refuses to write outputs unless the kernel accepts every theorem. Modules are split so three of them can be implemented in parallel against a frozen row schema.

**Tech Stack:** Lean 4.35.0 (core library only, no Mathlib, no Lake), Python 3 stdlib (`csv`, `subprocess`, `unittest`, `pathlib`), existing repo conventions (`python -X utf8`, `LEAN` env override, generated harness files gitignored).

**Spec:** No separate spec file; the approved design is the "Design summary" section below, agreed in conversation on 2026-11-18 (loophole/engine study context: `LOOPHOLE_FINDINGS.md`, `STATUS.md` Engine study 2).

## Design summary (approved 2026-11-18)

Han et al. (arXiv:2610.02792, §4.4) verified 50 tax-form cells in Lean as theorems: 43 equivalence proofs (`:= rfl`) and 7 divergence counterexamples (`by native_decide`). This plan adopts that unit of counting — a theorem relating two computations — and automates its production against our verified core. Findings are stratified by kind so the headline number is honest:

| Family | Kind | Count | Proposition form |
|---|---|---|---|
| equivalence_certT | equivalence | 32 | `(mkCertT gs inc d).total = <python value>` (`rfl`) |
| equivalence_cert8 | equivalence | 96 | `(mkCert8 gs inc d elected).total = <python value>` (`rfl`) |
| divergence | divergence | 56 | `<engine claimed total> ≠ (mkCert8 ...).total` (`decide`) |
| boundary | boundary | 16 | tier / eligibility / rate / regime at ±1 centavo (`rfl`/`decide`) |
| cliff | incentive | 18 | `penaltyT .hi t d = penaltyT .lo t d + K` at ₱3M / ₱20M / ₱1B |
| crossover | incentive | 20 | shelter holds at crossover income, fails one centavo below; 10 gross-sales levels |
| monotone | identity | 20 | closed-form penalty/interest values and monotonicity instances |
| gap | gap | 16 | unguarded-premise acceptances for L1, L2, L5 |
| **Total** | | **274** | |

The battery is **not** 274 legal loopholes; the kind column carries the claim. The incentive families are conditional on specification fidelity exactly like L3/L4; the gap family documents premises our checker lacks. `rfl`/`decide` only — the axiom audit must show no `sorryAx`, no `Classical.choice`, no `Lean.ofReduceBool`.

## Global Constraints

- Lean 4.35.0 from the pinned toolchain; core library only; no Mathlib, no Lake. Axiom audit of the generated file must contain only `propext` (or no axioms), never `sorryAx`, `Classical.choice`, or `Lean.ofReduceBool`.
- No `native_decide` anywhere in generated Lean; no `sorry`.
- **Do not stage, commit, or push anything** (standing rule: only on explicit request). Every task ends with verification, not a commit.
- All Python runs as `python -X utf8 ...`; file writes use `encoding="utf-8"`.
- Generated Lean file `lean/_harness/Findings.lean` stays gitignored and is regenerated on every run.
- All tools honor the `LEAN` environment override; default is `ROOT/tools/lean/dist/lean-4.35.0-windows/bin/lean.exe`.
- The 59-theorem hand-written count in `STATUS.md` / `THEOREMS.md` / README badges does **not** change; the battery is reported separately as generated.
- Windows toolchain for every compile: `export LEAN="C:/Users/Ma Christine/Downloads/LEAN FORMALIZATION OF TAX CODE/tools/lean/dist/lean-4.35.0-windows/bin/lean.exe"`.
- The MSP Region 3 abstract is out of scope; do not modify anything under `msp/`.

## Parallel Execution Map

| Wave | Tasks | Agents | Why this shape |
|---|---|---|---|
| 0 | Task 1 | 1 implementer + 1 reviewer | Foundation; everything imports it |
| 1 | Tasks 2, 3, 4 | 3 implementers in parallel + 3 reviewers in parallel | Disjoint files; both depend only on Task 1's frozen row schema / module API |
| 2 | Task 5 | 1 implementer + 1 reviewer | Driver wires 2+3+4 together |
| 3 | Task 6 | 1 implementer + 1 verifier | Kernel run and timing |
| 4 | Tasks 7, 8, 9 | 3 implementers in parallel + 3 reviewers in parallel | Disjoint deliverables (paper / repo docs / findings doc) |
| 5 | Task 10 | 1 implementer + 1 visual verifier | Depends on Task 7 |
| 6 | Task 11 | 1 implementer + 1 end-to-end verifier | Depends on 6–10 |

Do not exceed three concurrent implementers in a wave: Waves 1 and 4 touch disjoint files by construction; adding more agents would create shared-file conflicts (Tasks 7 and 8 are the only doc tasks that must not overlap, and they are already separated by file).

## File Structure

- `tools/findings_spec.py` — independent Python ground truth (pure functions, no I/O).
- `tools/test_findings_spec.py` — unittest: reproduces committed CSV truths.
- `tools/findings_families.py` — enumerates the 274 rows; imports `findings_spec` and reads `data/results8.csv`, `data/benchmark8_cases.csv`.
- `tools/test_findings_families.py` — counts, ids, schema, naming.
- `tools/findings_render.py` — rows → Lean source; audit lines.
- `tools/test_findings_render.py` — golden snippet, forbidden tokens, audit count.
- `tools/findings_report.py` — rows → CSV text and FINDINGS.md text; write function.
- `tools/test_findings_report.py` — header/counts/goal anchor assertions.
- `tools/findings.py` — CLI driver (`--dry-run`); compile, audit, write.
- `lean/_harness/Findings.lean` — generated (gitignored).
- `data/findings.csv`, `FINDINGS.md` — generated outputs.
- Docs edited later: `Verified_Core_Tax_Governance_PH.md`, `STATUS.md`, `THEOREMS.md`, `README.md`, `ROADMAP.md`, `LOOPHOLE_FINDINGS.md`, `.gitignore`, `lean/_harness/README.md`.

Frozen row schema (all later tasks rely on these exact keys):

```python
{
  "id": "F001",            # 1-based, zero-padded to 3
  "family": "equivalence_certT",
  "kind": "equivalence",   # equivalence|divergence|boundary|incentive|identity|gap
  "theorem": "f001_equivalence_certT_001",
  "prop": "(mkCertT 50000000 50000000 0).total = 4675000",
  "tactic": "rfl",         # "rfl" or "decide"
  "witness": "gs=income=50000000, days=0",
  "value": 4675000,        # int or None (None for propositions with no single value)
  "source": "tools/findings_spec.py cert_t_total",
  "note": "free text, no tabs, no newlines",
}
```

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

### Task 2: Enumerate the 274 findings

**Files:**
- Create: `tools/findings_families.py`
- Test: `tools/test_findings_families.py`

**Interfaces:**
- Consumes: every function from Task 1 (`findings_spec`); CSV files `data/benchmark8_cases.csv` (columns `case_id, elected, gross_sales_centavos, income_centavos, days_late, tier, regime, basic, surcharge, interest, total_due`) and `data/results8.csv` (columns `engine, case_id, elected, accepted, cert_total, true_total, error, claimed_regime, true_regime, python_diagnosis_unverified`).
- Produces: `all_findings() -> list[dict]` returning exactly 274 rows with the frozen schema; `FAMILY_COUNTS: dict[str, int]`.

- [ ] **Step 1: Write the failing tests**

Create `tools/test_findings_families.py`:

```python
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
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd "C:/Users/Ma Christine/Downloads/LEAN FORMALIZATION OF TAX CODE/ph-tax-code-lean" && python -X utf8 -m unittest discover -s tools -p "test_findings_families.py" -v`
Expected: ERROR `No module named 'findings_families'`.

- [ ] **Step 3: Write the implementation**

Create `tools/findings_families.py`:

```python
# -*- coding: utf-8 -*-
"""Enumerate the 274 kernel-checked findings over the verified PH tax core.

Every row becomes one Lean theorem in lean/_harness/Findings.lean. Witnesses
and expected values come from findings_spec (independent Python); the kernel
decides whether each proposition is true.
"""

import csv
from pathlib import Path

import findings_spec as spec

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"

KIND = {
    "equivalence_certT": "equivalence",
    "equivalence_cert8": "equivalence",
    "divergence": "divergence",
    "boundary": "boundary",
    "cliff": "incentive",
    "crossover": "incentive",
    "monotone": "identity",
    "gap": "gap",
}
FAMILY_COUNTS = {
    "equivalence_certT": 32,
    "equivalence_cert8": 96,
    "divergence": 56,
    "boundary": 16,
    "cliff": 18,
    "crossover": 20,
    "monotone": 20,
    "gap": 16,
}


def all_findings():
    out = []

    def add(family, prop, tactic, witness, value=None, source="", note=""):
        n = len(out) + 1
        out.append({
            "id": f"F{n:03d}",
            "family": family,
            "kind": KIND[family],
            "theorem": f"f{n:03d}_{family}_{n:03d}",
            "prop": prop,
            "tactic": tactic,
            "witness": witness,
            "value": value,
            "source": source,
            "note": note,
        })

    _equivalence_cert_t(add)
    _equivalence_cert8(add)
    _divergence(add)
    _boundary(add)
    _cliff(add)
    _crossover(add)
    _monotone(add)
    _gap(add)

    counts = {}
    for r in out:
        counts[r["family"]] = counts.get(r["family"], 0) + 1
    assert counts == FAMILY_COUNTS, counts
    return out


def _equivalence_cert_t(add):
    gs_inc = [50_000_000, 200_000_000, 300_000_000, 1_000_000_000,
              2_000_000_000, 50_000_000_000, 100_000_000_000, 500_000_000_000]
    for gs in gs_inc:
        for d in (0, 30, 365, 3650):
            v = spec.cert_t_total(gs, gs, d)
            add("equivalence_certT", f"(mkCertT {gs} {gs} {d}).total = {v}",
                "rfl", f"gs=income={gs}, days={d}", v,
                "tools/findings_spec.py cert_t_total",
                "CertT total equals the independent Python value at the witness")


def _equivalence_cert8(add):
    for gs in (50_000_000, 250_000_000, 300_000_000, 1_000_000_000):
        for inc in (50_000_000, 500_000_000, 5_000_000_000, 50_000_000_000):
            for elected in (False, True):
                for d in (0, 30, 365):
                    e = "true" if elected else "false"
                    v = spec.cert8_total(gs, inc, d, elected)
                    add("equivalence_cert8",
                        f"(mkCert8 {gs} {inc} {d} {e}).total = {v}",
                        "rfl", f"gs={gs}, income={inc}, days={d}, elected={e}", v,
                        "tools/findings_spec.py cert8_total",
                        "Cert8 total equals the independent Python value at the witness")


def _divergence(add):
    cases = {r["case_id"]: r for r in
             csv.DictReader((DATA / "benchmark8_cases.csv").open(encoding="utf-8"))}
    rows = list(csv.DictReader((DATA / "results8.csv").open(encoding="utf-8")))
    engines = ["G1_eight_on_income", "G2_no_exempt_floor", "G3_ineligible_eight",
               "G4_pct_double", "G5_missing_pct", "G6_rate10",
               "G7_penalty_wrong_base"]
    used = {e: 0 for e in engines}
    picked = []
    for r in rows:
        eng = r["engine"]
        if eng not in used or used[eng] >= 8:
            continue
        claim, truth = int(r["cert_total"]), int(r["true_total"])
        if claim == truth:
            continue
        picked.append((eng, r, claim, truth))
        used[eng] += 1
    assert all(n == 8 for n in used.values()), used
    assert len(picked) == 56, len(picked)
    for eng, r, claim, truth in picked:
        c = cases[r["case_id"]]
        gs = int(c["gross_sales_centavos"])
        inc = int(c["income_centavos"])
        days = int(c["days_late"])
        elected = r["elected"].lower() == "true"
        e = "true" if elected else "false"
        assert spec.cert8_total(gs, inc, days, elected) == truth
        add("divergence", f"{claim} ≠ (mkCert8 {gs} {inc} {days} {e}).total",
            "decide", f"{eng} on {r['case_id']} (elected={elected})", claim,
            "data/results8.csv + data/benchmark8_cases.csv",
            f"engine claimed {claim}; the kernel total is {truth}")


def _boundary(add):
    items = [
        ("classify 299999999 = .micro", "rfl", "one centavo below P3M"),
        ("classify 300000000 = .small", "rfl", "at P3M"),
        ("classify 1999999999 = .small", "rfl", "one centavo below P20M"),
        ("classify 2000000000 = .medium", "rfl", "at P20M"),
        ("classify 99999999999 = .medium", "rfl", "one centavo below P1B"),
        ("classify 100000000000 = .large", "rfl", "at P1B"),
        ("eligible8 300000000 = true", "decide", "election eligible at P3M"),
        ("eligible8 300000001 = false", "decide", "election ineligible one centavo above P3M"),
        ("surchargeRate .small = 10", "rfl", "small surcharge rate"),
        ("surchargeRate .medium = 25", "rfl", "medium surcharge rate"),
        ("interestRate .small = 6", "rfl", "small interest rate"),
        ("interestRate .medium = 12", "rfl", "medium interest rate"),
        ("regimeOf true 300000000 = .eight", "rfl", "elected and eligible"),
        ("regimeOf true 300000001 = .graduated", "rfl", "elected but ineligible"),
        ("regimeOf false 50000000 = .graduated", "rfl", "not elected"),
        ("regimeOf true 50000000 = .eight", "rfl", "elected below the threshold"),
    ]
    for prop, tactic, note in items:
        add("boundary", prop, tactic, note, None, "Tiers.lean / Opt8.lean", note)


def _cliff(add):
    pairs = [(".micro", ".small", "P3M line (penalty-neutral)"),
             (".small", ".medium", "P20M line (penalty cliff)"),
             (".medium", ".large", "P1B line (penalty-neutral)")]
    for lo, hi, label in pairs:
        for t in (1_000_000, 50_000_000, 500_000_000):
            for d in (30, 365):
                k = (spec.penalty_t(hi.strip("."), t, d)
                     - spec.penalty_t(lo.strip("."), t, d))
                add("cliff", f"penaltyT {hi} {t} {d} = penaltyT {lo} {t} {d} + {k}",
                    "rfl", f"{label}, basic={t}, days={d}", k,
                    "tools/findings_spec.py penalty_t", label)


def _crossover(add):
    for gs in range(75_000_000, 300_000_001, 25_000_000):
        x = spec.crossover(gs)
        assert x > 0
        add("crossover", f"tax8 {gs} ≤ bracketTax {x} + pctTax {gs}", "decide",
            f"gs={gs}, crossover income={x}", x,
            "tools/findings_spec.py crossover",
            "the 8% basic is sheltered at the crossover income")
        add("crossover", f"¬ (tax8 {gs} ≤ bracketTax {x - 1} + pctTax {gs})", "decide",
            f"gs={gs}, one centavo below the crossover ({x - 1})", x - 1,
            "tools/findings_spec.py crossover",
            "the shelter fails one centavo below the crossover")


def _monotone(add):
    for tier, t, d in ((".large", 50_000_000, 365), (".small", 50_000_000, 365),
                       (".medium", 200_000_000, 3650), (".micro", 10_000_000, 365)):
        v = spec.interest_t(tier.strip("."), t, d)
        add("monotone", f"interestT {tier} {t} {d} = {v}", "rfl",
            f"interestT {tier} {t} {d}", v, "tools/findings_spec.py interest_t",
            "closed-form interest value")
    for tier in (".micro", ".small", ".medium", ".large"):
        v = spec.surcharge_t(tier.strip("."), 50_000_000)
        add("monotone", f"surchargeT {tier} 50000000 = {v}", "rfl",
            f"surchargeT {tier} 50000000", v, "tools/findings_spec.py surcharge_t",
            "closed-form surcharge value")
    for tier, t, d in ((".large", 50_000_000, 365), (".small", 50_000_000, 365),
                       (".micro", 10_000_000, 0), (".large", 0, 365)):
        v = spec.penalty_t(tier.strip("."), t, d)
        add("monotone", f"penaltyT {tier} {t} {d} = {v}", "rfl",
            f"penaltyT {tier} {t} {d}", v, "tools/findings_spec.py penalty_t",
            "closed-form penalty value")
    for tier, t, d in ((".large", 50_000_000, 365), (".medium", 200_000_000, 3650)):
        v = spec.total_due_t(tier.strip("."), t, d)
        add("monotone", f"totalDueT {tier} {t} {d} = {v}", "rfl",
            f"totalDueT {tier} {t} {d}", v, "tools/findings_spec.py total_due_t",
            "closed-form total due")
    for prop in ("surchargeT .large 50000000 ≤ surchargeT .large 100000000",
                 "surchargeT .medium 50000000 ≤ surchargeT .medium 100000000",
                 "surchargeT .small 50000000 ≤ surchargeT .small 100000000",
                 "interestT .large 50000000 30 ≤ interestT .large 50000000 365",
                 "interestT .small 50000000 30 ≤ interestT .small 50000000 365",
                 "interestT .micro 10000000 0 ≤ interestT .micro 10000000 365"):
        add("monotone", prop, "decide", prop, None,
            "Loopholes.lean surchargeT_mono_tax / interestT_mono_tax",
            "monotonicity instance")


def _gap(add):
    for d in (0, 30, 365, 3650):
        add("gap", f"checkT (mkCertT 1000000 100000000 {d}) = true", "decide",
            f"income P1M above gross P10,000, days={d}", None,
            "LOOPHOLE_FINDINGS.md L1",
            "L1: taxable income above gross sales is accepted")
    for gs, inc, d in ((50_000_000, 50_000_000, 30), (300_000_000, 100_000_000, 365),
                       (250_000_000, 500_000_000, 3650), (100_000_000, 10_000_000, 0)):
        for e in ("true", "false"):
            add("gap", f"check8 (mkCert8 {gs} {inc} {d} {e}) = true", "decide",
                f"gs={gs}, income={inc}, days={d}, elected={e}", None,
                "LOOPHOLE_FINDINGS.md L2",
                "L2: both election states are accepted; no timing premise")
    for d in (36_500, 365_000, 3_650_000, 36_500_000):
        add("gap", f"checkT (mkCertT 500000000 1000000 {d}) = true", "decide",
            f"days_late={d} (100 to 100,000 years)", None,
            "LOOPHOLE_FINDINGS.md L5",
            "L5: no prescriptive period; the certificate is accepted")
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd "C:/Users/Ma Christine/Downloads/LEAN FORMALIZATION OF TAX CODE/ph-tax-code-lean" && python -X utf8 -m unittest discover -s tools -p "test_findings_families.py" -v`
Expected: `OK` with 5 tests. If `_divergence` asserts on engine counts, inspect `data/results8.csv` first — do not weaken the assertion; report the observed per-engine counts.

- [ ] **Step 5: Verify and leave uncommitted**

Run: `cd "C:/Users/Ma Christine/Downloads/LEAN FORMALIZATION OF TAX CODE/ph-tax-code-lean" && git status --short tools/findings_families.py tools/test_findings_families.py`
Expected: both untracked; no staging.

---

### Task 3: Render rows as Lean theorems (parallel with Task 2)

**Files:**
- Create: `tools/findings_render.py`
- Test: `tools/test_findings_render.py`

**Interfaces:**
- Consumes: the frozen row schema (above). No imports from other new modules.
- Produces: `render(rows) -> str` (complete Lean file text, LF newlines); module constants `HEADER_TEMPLATE`; exactly one `#print axioms` line per family (first theorem of each family, 8 lines).

- [ ] **Step 1: Write the failing tests**

Create `tools/test_findings_render.py`:

```python
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
        self.assertEqual(len(audits), len({r["family"] for r in FIXTURE}))
        self.assertIn("#print axioms f001_equivalence_certT_001", audits)

    def test_each_row_once(self):
        src = render_mod.render(FIXTURE)
        for r in FIXTURE:
            self.assertEqual(src.count(f"theorem {r['theorem']} "), 1)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd "C:/Users/Ma Christine/Downloads/LEAN FORMALIZATION OF TAX CODE/ph-tax-code-lean" && python -X utf8 -m unittest discover -s tools -p "test_findings_render.py" -v`
Expected: ERROR `No module named 'findings_render'`.

- [ ] **Step 3: Write the implementation**

Create `tools/findings_render.py`:

```python
# -*- coding: utf-8 -*-
"""Render finding rows as a Lean file judged by the kernel."""

HEADER_TEMPLATE = """\
/-
Generated by tools/findings.py -- do not edit.
{n} kernel-checked findings from the verified core (Lean 4.35.0, core only).
Every proof is closed by rfl or decide; no sorry, no native_decide.
-/

import Opt8
open PHTax

"""


def render(rows):
    lines = [HEADER_TEMPLATE.format(n=len(rows))]
    current = None
    for r in rows:
        if r["family"] != current:
            current = r["family"]
            lines.append(f"\n-- {current} ({r['kind']})\n")
        body = ":= rfl" if r["tactic"] == "rfl" else ":= by decide"
        lines.append(f"theorem {r['theorem']} : {r['prop']} {body}\n")
    lines.append("\n-- axiom audit: first theorem of each family\n")
    seen = set()
    for r in rows:
        if r["family"] not in seen:
            seen.add(r["family"])
            lines.append(f"#print axioms {r['theorem']}\n")
    return "".join(lines)
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd "C:/Users/Ma Christine/Downloads/LEAN FORMALIZATION OF TAX CODE/ph-tax-code-lean" && python -X utf8 -m unittest discover -s tools -p "test_findings_render.py" -v`
Expected: `OK` with 4 tests.

- [ ] **Step 5: Verify and leave uncommitted**

Run: `cd "C:/Users/Ma Christine/Downloads/LEAN FORMALIZATION OF TAX CODE/ph-tax-code-lean" && git status --short tools/findings_render.py tools/test_findings_render.py`
Expected: both untracked; no staging.

---

### Task 4: CSV and FINDINGS.md writer (parallel with Tasks 2–3)

**Files:**
- Create: `tools/findings_report.py`
- Test: `tools/test_findings_report.py`

**Interfaces:**
- Consumes: frozen row schema; `meta` dict with key `"seconds"` (float, compile wall time) and `"audit"` (str, e.g. `"propext only"`).
- Produces: `summary(rows) -> list[dict]` (`family`, `kind`, `count` in first-appearance order); `csv_text(rows) -> str`; `markdown(rows, meta) -> str`; `write_outputs(rows, meta, csv_path, md_path) -> None`.

- [ ] **Step 1: Write the failing tests**

Create `tools/test_findings_report.py`:

```python
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


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd "C:/Users/Ma Christine/Downloads/LEAN FORMALIZATION OF TAX CODE/ph-tax-code-lean" && python -X utf8 -m unittest discover -s tools -p "test_findings_report.py" -v`
Expected: ERROR `No module named 'findings_report'`.

- [ ] **Step 3: Write the implementation**

Create `tools/findings_report.py`:

```python
# -*- coding: utf-8 -*-
"""Write data/findings.csv and FINDINGS.md from finding rows."""

import csv
import io

FIELDS = ["id", "family", "kind", "theorem", "proposition", "witness",
          "value_centavos", "source", "note"]

MD_HEAD = """\
# Findings Battery — 274 machine-checked propositions from the verified core

Generated by `tools/findings.py`. Every row is one Lean theorem in
`lean/_harness/Findings.lean`, closed by `rfl` or `by decide` and judged by
the pinned Lean 4.35.0 kernel. The unit of counting follows Han et al.
(arXiv:2610.02792, section 4.4): a finding is a theorem relating two
computations — an equivalence at a witness, or a divergence counterexample.

**The battery is not 274 loopholes.** The kind column carries the claim:
`equivalence` rows relate the verified core to an independent Python value;
`divergence` rows exhibit engine errors; `boundary`, `incentive` and
`identity` rows quantify structure of the law as formalized, conditional on
the specification's fidelity; `gap` rows document premises our checker lacks
(L1, L2, L5). Unlike the equivalence proofs in Han et al., no proof here uses
`native_decide`; the axiom audit stays at `propext` and nothing trusts the
compiler.

"""

MD_TAIL = """\

## Reproduce

```bash
export LEAN=/path/to/lean-4.35.0/bin/lean   # lean.exe on Windows
python -X utf8 tools/findings.py
```

The script writes `lean/_harness/Findings.lean` (gitignored), compiles it,
refuses to write outputs on any compile or axiom-audit failure, then writes
`data/findings.csv` and this file.

## Files

- `tools/findings.py` — driver (enumerate, render, compile, audit, write)
- `tools/findings_spec.py` — independent Python ground truth
- `tools/findings_families.py` — the 274 rows
- `tools/findings_render.py` — Lean renderer
- `tools/findings_report.py` — CSV and Markdown writer
- `data/findings.csv` — one row per finding, with witness and provenance
"""


def summary(rows):
    order, counts = [], {}
    for r in rows:
        key = (r["family"], r["kind"])
        if key not in counts:
            counts[key] = 0
            order.append(key)
        counts[key] += 1
    return [{"family": f, "kind": k, "count": counts[(f, k)]} for f, k in order]


def csv_text(rows):
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=FIELDS, lineterminator="\n")
    w.writeheader()
    for r in rows:
        w.writerow({
            "id": r["id"], "family": r["family"], "kind": r["kind"],
            "theorem": r["theorem"], "proposition": r["prop"],
            "witness": r["witness"],
            "value_centavos": "" if r["value"] is None else r["value"],
            "source": r["source"], "note": r["note"],
        })
    return buf.getvalue()


def markdown(rows, meta):
    out = [MD_HEAD]
    out.append("## Summary\n\n| Family | Kind | Findings |\n|---|---|---|\n")
    total = 0
    for r in summary(rows):
        out.append(f"| {r['family']} | {r['kind']} | {r['count']} |\n")
        total += r["count"]
    out.append(f"| **Total** | | **{total}** |\n")
    out.append(f"\nKernel compile: {meta['seconds']} s. "
               f"Axiom audit: {meta['audit']}.\n")
    out.append(MD_TAIL)
    return "".join(out)


def write_outputs(rows, meta, csv_path, md_path):
    csv_path.write_text(csv_text(rows), encoding="utf-8", newline="")
    md_path.write_text(markdown(rows, meta), encoding="utf-8")
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd "C:/Users/Ma Christine/Downloads/LEAN FORMALIZATION OF TAX CODE/ph-tax-code-lean" && python -X utf8 -m unittest discover -s tools -p "test_findings_report.py" -v`
Expected: `OK` with 4 tests.

- [ ] **Step 5: Verify and leave uncommitted**

Run: `cd "C:/Users/Ma Christine/Downloads/LEAN FORMALIZATION OF TAX CODE/ph-tax-code-lean" && git status --short tools/findings_report.py tools/test_findings_report.py`
Expected: both untracked; no staging.

---

### Task 5: Driver with dry-run

**Files:**
- Create: `tools/findings.py`
- Test: `tools/test_findings_driver.py`

**Interfaces:**
- Consumes: `findings_families.all_findings()`, `findings_render.render(rows)`, `findings_report.write_outputs(rows, meta, csv_path, md_path)`.
- Produces: CLI `python -X utf8 tools/findings.py [--dry-run]`; exit 0 on success; writes `lean/_harness/Findings.lean`, `data/findings.csv`, `FINDINGS.md` only on full success.

- [ ] **Step 1: Write the failing test**

Create `tools/test_findings_driver.py`:

```python
# -*- coding: utf-8 -*-
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


class DriverTests(unittest.TestCase):
    def test_dry_run_counts_and_writes_nothing(self):
        csv_path = ROOT / "data" / "findings.csv"
        before = csv_path.stat().st_mtime if csv_path.exists() else None
        proc = subprocess.run(
            [sys.executable, "-X", "utf8", str(ROOT / "tools" / "findings.py"),
             "--dry-run"], capture_output=True, text=True, cwd=str(ROOT))
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertIn("DRY RUN: 274 findings", proc.stdout)
        after = csv_path.stat().st_mtime if csv_path.exists() else None
        self.assertEqual(before, after)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd "C:/Users/Ma Christine/Downloads/LEAN FORMALIZATION OF TAX CODE/ph-tax-code-lean" && python -X utf8 -m unittest discover -s tools -p "test_findings_driver.py" -v`
Expected: FAIL — `findings.py` missing (returncode 2).

- [ ] **Step 3: Write the implementation**

Create `tools/findings.py`:

```python
# -*- coding: utf-8 -*-
"""Generate, kernel-check and report the findings battery."""

import os
import re
import subprocess
import sys
import time
from pathlib import Path

import findings_families
import findings_render
import findings_report

ROOT = Path(__file__).resolve().parent.parent
LEAN_DIR = ROOT / "lean"
HARNESS = LEAN_DIR / "_harness" / "Findings.lean"
CSV_OUT = ROOT / "data" / "findings.csv"
MD_OUT = ROOT / "FINDINGS.md"
LEAN = os.environ.get(
    "LEAN", str(ROOT / "tools" / "lean" / "dist" /
                "lean-4.35.0-windows" / "bin" / "lean.exe"))

ERR_RE = re.compile(r"Findings\.lean:(\d+):\d+: error")
AXIOM_RE = re.compile(r"depends on axioms: \[(.*?)\]")
ALLOWED = {"propext"}


def main(argv):
    rows = findings_families.all_findings()
    assert len(rows) == 274, len(rows)
    source = findings_render.render(rows)

    if "--dry-run" in argv:
        print(f"DRY RUN: {len(rows)} findings across "
              f"{len(findings_report.summary(rows))} families; nothing written")
        return 0

    HARNESS.parent.mkdir(exist_ok=True)
    HARNESS.write_text(source, encoding="utf-8")
    env = dict(os.environ)
    env["LEAN_PATH"] = str(LEAN_DIR)
    t0 = time.time()
    proc = subprocess.run([LEAN, str(HARNESS)], capture_output=True, text=True,
                          env=env, cwd=str(LEAN_DIR), timeout=1800)
    seconds = round(time.time() - t0, 1)
    log = proc.stdout + proc.stderr
    if proc.returncode != 0:
        _report_failures(log, source)
        return 1

    bad = []
    for m in AXIOM_RE.finditer(log):
        items = {x.strip() for x in m.group(1).split(",") if x.strip()}
        if not items <= ALLOWED:
            bad.append(m.group(0))
    if bad:
        print("AXIOM AUDIT FAILED:\n" + "\n".join(bad))
        return 1

    audit = "propext only" if "depends on axioms" in log else "no axioms"
    findings_report.write_outputs(rows, {"seconds": seconds, "audit": audit},
                                  CSV_OUT, MD_OUT)
    print(f"PASS: {len(rows)} findings kernel-checked in {seconds} s; "
          f"axioms: {audit}")
    for r in findings_report.summary(rows):
        print(f"  {r['family']:20s} {r['kind']:12s} {r['count']:>3}")
    print(f"wrote {CSV_OUT} and {MD_OUT}")
    return 0


def _report_failures(log, source):
    lines = source.splitlines()
    for m in list(ERR_RE.finditer(log))[:5]:
        n = int(m.group(1))
        context = lines[n - 1] if 0 < n <= len(lines) else "?"
        print(f"Findings.lean:{n}: {context.strip()}")
    print(log[-4000:])


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd "C:/Users/Ma Christine/Downloads/LEAN FORMALIZATION OF TAX CODE/ph-tax-code-lean" && python -X utf8 -m unittest discover -s tools -p "test_findings_driver.py" -v`
Expected: `OK` with 1 test.

- [ ] **Step 5: Run the whole new test suite**

Run: `cd "C:/Users/Ma Christine/Downloads/LEAN FORMALIZATION OF TAX CODE/ph-tax-code-lean" && python -X utf8 -m unittest discover -s tools -p "test_findings_*.py" -v`
Expected: `OK` with 19 tests (5+5+4+4+1).

- [ ] **Step 6: Verify and leave uncommitted**

Run: `cd "C:/Users/Ma Christine/Downloads/LEAN FORMALIZATION OF TAX CODE/ph-tax-code-lean" && git status --short tools/ | head -20`
Expected: new files untracked; no staging.

---

### Task 6: Kernel run, timing, and output verification

**Files:**
- Modify (only if timing demands): `tools/findings_render.py`
- Generated: `lean/_harness/Findings.lean`, `data/findings.csv`, `FINDINGS.md`

**Interfaces:**
- Consumes: Task 5 CLI.
- Produces: the three artifacts with 274 rows and an axiom log containing only `propext`.

- [ ] **Step 1: First full kernel run**

Run: `cd "C:/Users/Ma Christine/Downloads/LEAN FORMALIZATION OF TAX CODE/ph-tax-code-lean" && export LEAN="C:/Users/Ma Christine/Downloads/LEAN FORMALIZATION OF TAX CODE/tools/lean/dist/lean-4.35.0-windows/bin/lean.exe" && time python -X utf8 tools/findings.py`
Expected: `PASS: 274 findings kernel-checked in <N> s; axioms: propext only`, eight family rows, `wrote ...findings.csv and ...FINDINGS.md`.

- [ ] **Step 2: If any theorem fails, fix the witness, never the tactic claim**

For each `Findings.lean:<line>` reported, read the rendered theorem, compare the Python literal with `findings_spec`. The usual cause is an integer witness mismatch; correct the family builder so Python and the kernel agree. Never replace `rfl` with `native_decide`, never add `sorry`, never weaken an equality to an inequality. Re-run Step 1 after each fix.

- [ ] **Step 3: Confirm performance and axiom profile**

Run: `cd "C:/Users/Ma Christine/Downloads/LEAN FORMALIZATION OF TAX CODE/ph-tax-code-lean" && python -X utf8 -c "print(open('data/findings.csv', encoding='utf-8').read().count(chr(10))-1)"` and `grep -c "#print axioms" lean/_harness/Findings.lean`
Expected: `274` and `8`. Wall time under 900 s; note the exact seconds for Task 7 and STATUS.md.

- [ ] **Step 4: Independent audit of the audit**

Run: `cd "C:/Users/Ma Christine/Downloads/LEAN FORMALIZATION OF TAX CODE/ph-tax-code-lean" && export LEAN_PATH="$PWD/lean" && "$LEAN" lean/_harness/Findings.lean 2>&1 | grep -E "depends on axioms|does not depend" | sort | uniq -c`
Expected: lines showing `[propext]` and/or "does not depend on any axioms" only; zero occurrences of `sorryAx`, `Classical.choice`, `Lean.ofReduceBool`.

- [ ] **Step 5: Confirm nothing else broke**

Run: `cd "C:/Users/Ma Christine/Downloads/LEAN FORMALIZATION OF TAX CODE/ph-tax-code-lean" && export LEAN="C:/Users/Ma Christine/Downloads/LEAN FORMALIZATION OF TAX CODE/tools/lean/dist/lean-4.35.0-windows/bin/lean.exe" && bash lean/run_demo.sh && echo BUILD_OK`
Expected: `BUILD_OK` (seven hand-written files unchanged, exit 0).

- [ ] **Step 6: Verify and leave uncommitted**

Run: `cd "C:/Users/Ma Christine/Downloads/LEAN FORMALIZATION OF TAX CODE/ph-tax-code-lean" && git status --short | head -30`
Expected: no tracked file modified except none; new artifacts listed as untracked. No staging.

---

### Task 7: Paper section, Table 9, renumbering, abstract (parallel with Tasks 8–9)

**Files:**
- Modify: `Verified_Core_Tax_Governance_PH.md` (abstract L11; insert after §5.10 ending L509; renumber Tables 9/10/11 at L596 and in-text refs; add roadmap row to Table 12; extend reproducibility paragraph L619).

**Interfaces:**
- Consumes: exact counts from Task 6 (274; 128/56/16/18/20/20/16) and the wall time printed by `tools/findings.py`.
- Produces: paper Markdown consistent with generated data; no DOCX/PDF yet.

- [ ] **Step 1: Insert §5.11 and Table 9 after the last §5.10 paragraph**

Insert between L509 (ends "...as formalized.** ..." paragraph) and L512 (`## 6. Critical Assessment`):

```markdown
### 5.11 A battery of machine-checked findings

Han et al. close their evaluation by proving 43 semantic equivalences and seven divergences between generated and gold tax-form cells in Lean. We adopt their unit of counting — a theorem relating two computations — and automate its production against the verified core. `tools/findings.py` enumerates 274 propositions over the core, renders them as Lean theorems, and lets the kernel judge them: 128 state that a certificate total equals an independently computed Python value at a named witness, closed by `rfl`; 56 are divergence counterexamples from the seeded-fault engines, each stating that an engine's claimed total differs from the kernel's total at that engine's witness, closed by `decide`; 16 are tier, eligibility, rate and regime boundary propositions at ₱3M, ₱20M and ₱1B; 38 quantify the incentive structure — the ₱20M penalty cliff and the neutrality of the ₱3M and ₱1B lines at 18 witnesses, and the 8% shelter crossover proved from both sides at ten gross-sales levels; 20 are closed-form penalty and interest identities with monotonicity instances; and 16 are unguarded-premise acceptances for L1, L2 and L5. Every proof is closed by `rfl` or `decide`. Unlike the equivalence proofs in Han et al., none uses `native_decide`, so no proof trusts the compiler and the axiom audit stays at `propext`.

The battery is not 274 loopholes. It is a count of propositions the kernel has checked, stratified by kind, and its value is the same as the engine studies': every row carries its witness and its provenance, and any row can be refuted by editing the core. The incentive families are conditional on the specification's fidelity in the same sense as L3 and L4; the gap family documents premises our checker lacks, not the law. What changes with scale is the audit surface: a reader who distrusts one finding can re-derive it in one line.

*Table 9. The findings battery, by family and kind (generated 18 November 2026).*

| Family | Kind | Findings | Witness form |
|---|---|---|---|
| Equivalence, default regime | equivalence | 32 | certificate total = Python value, eight incomes × four day counts |
| Equivalence, election regime | equivalence | 96 | certificate total = Python value, 4 × 4 × 2 × 3 grid |
| Divergence | divergence | 56 | engine claimed total ≠ kernel total, eight rows for each of seven fault engines |
| Boundary | boundary | 16 | tier, eligibility, rate and regime at ±1 centavo around ₱3M, ₱20M, ₱1B |
| Penalty cliff | incentive | 18 | tier-line penalty difference at three basic taxes × two day counts |
| Election crossover | incentive | 20 | shelter holds at the crossover income and fails one centavo below, ten gross-sales levels |
| Identities | identity | 20 | closed-form surcharge, interest, penalty and total values; monotonicity instances |
| Unguarded premises | gap | 16 | accepted certificates violating L1, L2 and L5 premises |
| **Total** | | **274** | |
```

- [ ] **Step 2: Renumber existing tables in descending order**

Run: `cd "C:/Users/Ma Christine/Downloads/LEAN FORMALIZATION OF TAX CODE/ph-tax-code-lean" && grep -n "Table 9\|Table 10\|Table 11" Verified_Core_Tax_Governance_PH.md`
Then replace, in this order: every `Table 11` → `Table 12`, every `Table 10` → `Table 11`, every `Table 9` → `Table 10` (captions and in-text references alike; do not touch Table 1–8). Re-run the grep and confirm the sequence of table numbers is monotonically increasing by first appearance.

- [ ] **Step 3: Add the abstract sentence and roadmap row**

In L11, immediately after "...submit 766 certificates judged only by the verified checkers.", insert:

```text
 An automated battery renders 274 further propositions — 128 equivalence witnesses, 56 divergence counterexamples, and 90 boundary, incentive, identity and gap findings — each checked by the same kernel at `propext`.
```

In Table 12 (roadmap), append after the last row:

```markdown
| 9. Findings battery | 274 kernel-checked propositions generated by `tools/findings.py` | **Done.** Generated, compiled and axiom-audited on 18 November 2026; not 274 loopholes — the kind column separates equivalences, divergences, incentives and gaps |
```

- [ ] **Step 4: Extend the reproducibility paragraph**

At L619, after the sentence listing `tools/loopholes.py`, append: "`tools/findings.py` regenerates the 274-finding battery, its independent Python ground truth and the eight-family report; the generated Lean file lands in `lean/_harness/` with the other harness files."

- [ ] **Step 5: Verify**

Run: `cd "C:/Users/Ma Christine/Downloads/LEAN FORMALIZATION OF TAX CODE/ph-tax-code-lean" && grep -n "Table [0-9]" Verified_Core_Tax_Governance_PH.md | head -40 && grep -c "274" Verified_Core_Tax_Governance_PH.md`
Expected: no duplicate table numbers; `274` appears at least four times (section, table, abstract, roadmap); Table 12 is the roadmap.

- [ ] **Step 6: Verify and leave uncommitted**

Run: `cd "C:/Users/Ma Christine/Downloads/LEAN FORMALIZATION OF TAX CODE/ph-tax-code-lean" && git status --short Verified_Core_Tax_Governance_PH.md`
Expected: modified; not staged.

---

### Task 8: Repo docs and ignore rules (parallel with Tasks 7, 9)

**Files:**
- Modify: `STATUS.md` (after the Loophole study section, before "Reproduce the studies"), `THEOREMS.md` (append after honesty notes), `README.md` (stats row L53 area; quick start L150–157; architecture tree L105), `ROADMAP.md` (executed table after L17), `.gitignore`, `lean/_harness/README.md`.

**Interfaces:**
- Consumes: counts and wall time from Task 6.
- Produces: docs consistent with 274 / eight families / propext-only audit; hand-written 59/82 counts unchanged.

- [ ] **Step 1: STATUS.md — add the battery section**

Insert before the "## Reproduce the studies" heading (L129):

```markdown
## Findings battery (`data/findings.csv`, `FINDINGS.md`)

`tools/findings.py` enumerates 274 propositions over the verified core,
renders them as Lean theorems, compiles them with the pinned toolchain, and
writes nothing unless every theorem is accepted and the axiom audit shows
only `propext`. Findings by family: equivalence 128 (32 default regime, 96
election regime), divergence 56, boundary 16, penalty cliff 18, election
crossover 20, identities 20, unguarded premises 16. The battery is not 274
loopholes; the `kind` column separates equivalences and divergences from
incentive structure and encoding gaps. Unlike the equivalence proofs in
Han et al. (arXiv:2610.02792), no proof uses `native_decide`.
```

Add to the reproduce block (after the loopholes line):

```bash
python -X utf8 tools/findings.py        # 274 kernel-checked findings; writes data/findings.csv and FINDINGS.md
```

- [ ] **Step 2: THEOREMS.md — append the generated-battery note**

After the honesty-notes bullets (EOF), append:

```markdown
## Generated findings battery

`tools/findings.py` generates `lean/_harness/Findings.lean`, containing 274
further kernel-checked theorems, one per finding, plus eight `#print axioms`
audits. They are not counted in the 59 above: they are generated on every
run, gitignored, and must always close by `rfl` or `decide` with no
`native_decide` and no `sorry`. See `FINDINGS.md`.
```

- [ ] **Step 3: README.md — stats, quick start, tree**

After the "Engine studies" stats row (L53), add:

```markdown
| **Findings battery** | 274 kernel-checked propositions generated per run ([FINDINGS.md](FINDINGS.md)) |
```

In the quick-start second code block, after the loopholes line (L156), add:

```bash
python -X utf8 tools/findings.py   # 274 kernel-checked findings; writes data/findings.csv and FINDINGS.md
```

In the architecture tree, after the `tools/` line (L105), add one indented line:

```text
  tools/               # benchmark, engines, loophole and findings scripts
```

If a `tools/` line already exists with a different comment, append `; findings.py` to that comment instead of adding a duplicate.

- [ ] **Step 4: ROADMAP.md — executed row**

After the row for step 7 (L17), add:

```markdown
| 8. Findings battery | 274 kernel-checked propositions generated by `tools/findings.py`, stratified by kind | **Done.** Compiled and axiom-audited 18 Nov 2026; kind column prevents the count from reading as 274 loopholes |
```

- [ ] **Step 5: .gitignore and harness README**

Add to `.gitignore` under the generated harness files block:

```text
lean/_harness/Findings.lean
```

Append to `lean/_harness/README.md`:

```markdown
`Findings.lean` is generated by `tools/findings.py`: one theorem per finding
(274 in total), plus eight `#print axioms` audits. It is gitignored and
regenerated on every run; the script writes `data/findings.csv` and
`FINDINGS.md` only after the kernel accepts every theorem and the audit
shows only `propext`.
```

- [ ] **Step 6: Verify**

Run: `cd "C:/Users/Ma Christine/Downloads/LEAN FORMALIZATION OF TAX CODE/ph-tax-code-lean" && grep -n "274" STATUS.md THEOREMS.md README.md ROADMAP.md FINDINGS.md | head -20 && grep -n "Findings.lean" .gitignore lean/_harness/README.md`
Expected: at least one 274 line per file; both ignore and README entries present; `**Total** | **1,024** | **59** | **82**` in STATUS.md unchanged.

- [ ] **Step 7: Verify and leave uncommitted**

Run: `cd "C:/Users/Ma Christine/Downloads/LEAN FORMALIZATION OF TAX CODE/ph-tax-code-lean" && git status --short STATUS.md THEOREMS.md README.md ROADMAP.md .gitignore lean/_harness/README.md`
Expected: all modified/untracked; not staged.

---

### Task 9: FINDINGS.md review and loophole cross-link (parallel with Tasks 7, 8)

**Files:**
- Modify: `FINDINGS.md` (generated — edit only the framing paragraphs if needed; never edit rows or counts), `LOOPHOLE_FINDINGS.md` (Reproduce section).

**Interfaces:**
- Consumes: generated `FINDINGS.md` from Task 6; `data/findings.csv` for row examples.
- Produces: consistent framing across the two findings documents.

- [ ] **Step 1: Verify the generated framing against the claim ladder**

Read `FINDINGS.md`. Confirm it states: (a) the number, (b) the kind split, (c) "not 274 loopholes", (d) the `native_decide` contrast, (e) conditional-on-spec-fidelity for incentive rows. If any is missing or overstated, edit only the intro/honesty prose — not the summary table and not any generated row.

- [ ] **Step 2: Cross-link from LOOPHOLE_FINDINGS.md**

In its "Reproduce" section, append:

```markdown
A generated battery of 274 kernel-checked propositions that extends these
five findings — 128 equivalences, 56 divergence counterexamples, and 90
boundary, incentive, identity and gap propositions — is documented in
[FINDINGS.md](FINDINGS.md); the two documents use the same kind labels, and
neither claims that encoding gaps are properties of the real tax code.
```

- [ ] **Step 3: Verify**

Run: `cd "C:/Users/Ma Christine/Downloads/LEAN FORMALIZATION OF TAX CODE/ph-tax-code-lean" && grep -n "274\|not 274\|native_decide" FINDINGS.md LOOPHOLE_FINDINGS.md`
Expected: framing sentences present in both; no sentence claims 274 legal loopholes.

- [ ] **Step 4: Verify and leave uncommitted**

Run: `cd "C:/Users/Ma Christine/Downloads/LEAN FORMALIZATION OF TAX CODE/ph-tax-code-lean" && git status --short FINDINGS.md LOOPHOLE_FINDINGS.md`
Expected: `FINDINGS.md` untracked (generated), `LOOPHOLE_FINDINGS.md` modified or untracked as before; not staged.

---

### Task 10: Re-render DOCX and PDF, inspect the new pages

**Files:**
- Modify: `Verified_Core_Tax_Governance_PH.docx`, `Verified_Core_Tax_Governance_PH.pdf`
- Create: `previews/findings-page-*.png` (workspace scratch, gitignored)

**Interfaces:**
- Consumes: Task 7's edited Markdown.
- Produces: a 23+-page PDF containing §5.11 and the renumbered tables, visually inspected.

- [ ] **Step 1: Render the DOCX from the workspace tool**

Run: `cd "C:/Users/Ma Christine/Downloads/LEAN FORMALIZATION OF TAX CODE" && DOCX_FOOTER="How Strong Is a Verified Tax Code? — Research Paper" python -X utf8 tools/md_to_docx.py ph-tax-code-lean/Verified_Core_Tax_Governance_PH.md ph-tax-code-lean/Verified_Core_Tax_Governance_PH.docx`
Expected: `Wrote ...Verified_Core_Tax_Governance_PH.docx`.

- [ ] **Step 2: Export the PDF through Word**

Run:

```bash
cd "C:/Users/Ma Christine/Downloads/LEAN FORMALIZATION OF TAX CODE" && python -X utf8 - <<'PY'
from pathlib import Path
import win32com.client as win32
root = Path(r"C:\Users\Ma Christine\Downloads\LEAN FORMALIZATION OF TAX CODE\ph-tax-code-lean")
docx = root / "Verified_Core_Tax_Governance_PH.docx"
pdf = root / "Verified_Core_Tax_Governance_PH.pdf"
app = win32.DispatchEx("Word.Application")
app.Visible = False
try:
    doc = app.Documents.Open(str(docx))
    doc.SaveAs(str(pdf), FileFormat=17)
    doc.Close(False)
finally:
    try:
        app.Quit()
    except Exception:
        pass
print("wrote", pdf, pdf.stat().st_size)
PY
```

Expected: `wrote ...pdf <size>`. A `com_error` on Quit is harmless if the PDF exists.

- [ ] **Step 3: Locate and screenshot the new pages**

Run:

```bash
cd "C:/Users/Ma Christine/Downloads/LEAN FORMALIZATION OF TAX CODE" && mkdir -p previews && python -X utf8 - <<'PY'
import fitz
pdf = "ph-tax-code-lean/Verified_Core_Tax_Governance_PH.pdf"
doc = fitz.open(pdf)
print("pages", len(doc))
hits = [i + 1 for i in range(len(doc))
        if "5.11" in doc[i].get_text() or "findings battery" in doc[i].get_text().lower()]
print("hits", hits)
for p in hits:
    pix = doc[p - 1].get_pixmap(dpi=80)
    out = f"previews/findings-page-{p:02d}.png"
    pix.save(out)
    print("saved", out)
PY
```

Expected: page count 24 or more; at least one hit; PNG paths printed.

- [ ] **Step 4: Inspect the screenshots**

Read each `previews/findings-page-*.png` with the Read tool. Check: §5.11 heading present, Table 9 renders as a table with eight rows and a total, the roadmap table shows rows 1–9 with no duplicated numbers, no overflow or clipped columns. If anything is clipped, adjust the Markdown table widths (the paper uses a width comment line above tables) and repeat Steps 1–4.

- [ ] **Step 5: Verify and leave uncommitted**

Run: `cd "C:/Users/Ma Christine/Downloads/LEAN FORMALIZATION OF TAX CODE/ph-tax-code-lean" && git status --short Verified_Core_Tax_Governance_PH.docx Verified_Core_Tax_Governance_PH.pdf`
Expected: both modified; not staged. Do not commit.

---

### Task 11: Sync root copies and end-to-end verification from the repo

**Files:**
- Copy: repo artifacts to workspace root (`tools/findings*.py`, `data/findings.csv`, `FINDINGS.md`, paper `md/docx/pdf`).
- Modify: project memory `C:\Users\Ma Christine\.qoder\projects\C--Users-Ma-Christine-Downloads-LEAN-FORMALIZATION-OF-TAX-CODE\memory\project-ph-tax-code-lean-repo.md`.

**Interfaces:**
- Consumes: Tasks 6–10 outputs.
- Produces: root workspace mirrors; a verified, still-uncommitted repo; memory updated.

- [ ] **Step 1: Copy to the workspace root**

Run:

```bash
cd "C:/Users/Ma Christine/Downloads/LEAN FORMALIZATION OF TAX CODE" && cp ph-tax-code-lean/tools/findings*.py tools/ && cp ph-tax-code-lean/data/findings.csv data/ && cp ph-tax-code-lean/FINDINGS.md . && cp ph-tax-code-lean/Verified_Core_Tax_Governance_PH.md ph-tax-code-lean/Verified_Core_Tax_Governance_PH.docx ph-tax-code-lean/Verified_Core_Tax_Governance_PH.pdf .
```

Expected: no errors.

- [ ] **Step 2: End-to-end run from the repo copy**

Run:

```bash
cd "C:/Users/Ma Christine/Downloads/LEAN FORMALIZATION OF TAX CODE/ph-tax-code-lean" && export LEAN="C:/Users/Ma Christine/Downloads/LEAN FORMALIZATION OF TAX CODE/tools/lean/dist/lean-4.35.0-windows/bin/lean.exe" && bash lean/run_demo.sh && python -X utf8 -m unittest discover -s tools -p "test_findings_*.py" -v && python -X utf8 tools/findings.py && echo E2E_OK
```

Expected: build exit 0, 19 tests OK, `PASS: 274 findings ... axioms: propext only`, `E2E_OK`.

- [ ] **Step 3: Confirm repository state**

Run: `cd "C:/Users/Ma Christine/Downloads/LEAN FORMALIZATION OF TAX CODE/ph-tax-code-lean" && git status --short && git log --oneline -1`
Expected: last commit still `91b2607`; modified tracked docs + untracked new files; `lean/_harness/Findings.lean`, `*.olean` absent from status (ignored).

- [ ] **Step 4: Update project memory**

Append to `project-ph-tax-code-lean-repo.md` under the existing 18 Nov 2026 paragraph:

```markdown
19 Nov 2026 (uncommitted): findings battery — tools/findings{.py,_spec,_families,_render,_report}.py
plus 5 unittest files generate 274 kernel-checked findings in 8 families
(equivalence 128, divergence 56, boundary 16, cliff 18, crossover 20,
identity 20, gap 16), all rfl/decide, axioms propext only; outputs
data/findings.csv + FINDINGS.md; paper §5.11 + Table 9 (old 9/10/11 → 10/11/12);
STATUS/THEOREMS/README/ROADMAP/.gitignore/_harness README updated.
Not 274 loopholes: kind column separates equivalences, divergences,
incentives and gaps. Nothing committed.
```

- [ ] **Step 5: Final report**

Report to the user: the exact counts printed by the tool, wall time, axiom result, test count, the pages containing §5.11, and that everything remains uncommitted. State explicitly what was not done: no practitioner review, no commit, no MSP abstract change.

---

## Self-Review

- **Spec coverage:** all eight families, the driver, outputs, tests, paper, repo docs, PDF and verification are each owned by a task; the MSP abstract is explicitly out of scope.
- **Placeholder scan:** every code step contains complete code; doc steps contain the literal text to insert; no "TBD", no "similar to Task N".
- **Type consistency:** the row schema in File Structure matches the keys used by `findings_families`, `findings_render`, `findings_report` and the driver tests; `summary`, `csv_text`, `markdown`, `write_outputs`, `render`, `all_findings`, `FAMILY_COUNTS` are used exactly as defined.
- **Counts:** 32+96+56+16+18+20+20+16 = 274; 128 equivalence + 56 divergence + 90 other = 274; the abstract sentence uses exactly these splits.
