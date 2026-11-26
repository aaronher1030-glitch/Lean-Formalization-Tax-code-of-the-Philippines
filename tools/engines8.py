# -*- coding: utf-8 -*-
"""Seeded-fault engines for the 8%-regime (check8) certificate study.

Each engine is a plausible, self-consistent implementation of the election-
aware computation. Each emits a full Cert8 certificate for every
(case, elected) pair; the Lean checker check8, not this file, decides
acceptance. The honest engine G0 replicates the verified spec exactly and
must be accepted on every row.

Engines
  G0_honest             the verified spec (regimeOf, basicTax, tiered penalties)
  G1_eight_on_income    8% applied to income instead of gross sales/receipts
  G2_no_exempt_floor    8% of full gross sales, forgetting the P250k exemption
  G3_ineligible_eight   claims the 8% regime whenever elected, even above P3M
  G4_pct_double         keeps the 3% percentage tax on top of the 8% tax
  G5_missing_pct        omits the 3% percentage tax when not elected
  G6_rate10             uses 10% instead of 8%
  G7_penalty_wrong_base penalties computed on the graduated basic tax even
                        when the 8% regime applies
"""

import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
OUT = DATA / "engine8_certs"

STATUTE = [
    (25_000_000, 40_000_000, 15),
    (40_000_000, 80_000_000, 20),
    (80_000_000, 200_000_000, 25),
    (200_000_000, 800_000_000, 30),
    (800_000_000, None, 35),
]

ENGINES = ["G0_honest", "G1_eight_on_income", "G2_no_exempt_floor",
           "G3_ineligible_eight", "G4_pct_double", "G5_missing_pct",
           "G6_rate10", "G7_penalty_wrong_base"]


def classify(gs):
    if gs < 300_000_000:
        return "micro"
    if gs < 2_000_000_000:
        return "small"
    if gs < 100_000_000_000:
        return "medium"
    return "large"


def slice_of(t, lo, hi):
    if t <= lo:
        return 0
    return (min(t, hi) - lo) if hi is not None else (t - lo)


def tax_of(t, table):
    return sum(slice_of(t, lo, hi) * rate // 100 for lo, hi, rate in table)


def rates(tier):
    return (10, 6) if tier in ("micro", "small") else (25, 12)


def grad_lines(income):
    out = []
    for lo, hi, rate in STATUTE:
        base = slice_of(income, lo, hi)
        out.append({"lo": lo, "hi": hi, "rate": rate, "base": base,
                    "amount": base * rate // 100})
    return out


def cert8(engine, case, elected, regime, lines, basic, penalty_base=None):
    tier = classify(case["gross_sales_centavos"])
    s, i = rates(tier)
    pb = basic if penalty_base is None else penalty_base
    sur = pb * s // 100
    intr = pb * i * case["days_late"] // 36500
    return {
        "engine": engine,
        "case_id": case["case_id"],
        "gross_sales": case["gross_sales_centavos"],
        "income": case["income_centavos"],
        "days_late": case["days_late"],
        "elected": elected,
        "regime": regime,
        "lines": lines,
        "basic": basic,
        "surcharge": sur,
        "interest": intr,
        "total": basic + sur + intr,
    }


def main():
    with (DATA / "benchmark_cases.csv").open(encoding="utf-8") as f:
        cases = list(csv.DictReader(f))
    for c in cases:
        for k in ("gross_sales_centavos", "income_centavos", "days_late"):
            c[k] = int(c[k])

    OUT.mkdir(exist_ok=True)
    results = {e: [] for e in ENGINES}

    for c in cases:
        gs, inc, days = c["gross_sales_centavos"], c["income_centavos"], c["days_late"]
        pct = gs * 3 // 100
        grad_basic = tax_of(inc, STATUTE) + pct
        eight_basic = max(gs - 25_000_000, 0) * 8 // 100
        eligible = gs <= 300_000_000
        gl = grad_lines(inc)

        for elected in (False, True):
            true_regime = "eight" if elected and eligible else "graduated"
            honest = (true_regime, [] if true_regime == "eight" else gl,
                      eight_basic if true_regime == "eight" else grad_basic)
            results["G0_honest"].append(
                cert8("G0_honest", c, elected, *honest))

            # G1: 8% on income instead of gross sales (eight branch only)
            if elected and eligible:
                r, ls, b = "eight", [], max(inc - 25_000_000, 0) * 8 // 100
            else:
                r, ls, b = honest
            results["G1_eight_on_income"].append(
                cert8("G1_eight_on_income", c, elected, r, ls, b))

            # G2: no P250k exemption under the 8% option
            if elected and eligible:
                r, ls, b = "eight", [], gs * 8 // 100
            else:
                r, ls, b = honest
            results["G2_no_exempt_floor"].append(
                cert8("G2_no_exempt_floor", c, elected, r, ls, b))

            # G3: election honoured even when ineligible
            if elected:
                r, ls, b = "eight", [], eight_basic
            else:
                r, ls, b = honest
            results["G3_ineligible_eight"].append(
                cert8("G3_ineligible_eight", c, elected, r, ls, b))

            # G4: percentage tax kept on top of the 8% tax
            if elected and eligible:
                r, ls, b = "eight", [], eight_basic + pct
            else:
                r, ls, b = honest
            results["G4_pct_double"].append(
                cert8("G4_pct_double", c, elected, r, ls, b))

            # G5: percentage tax omitted when not elected
            if true_regime == "graduated":
                r, ls, b = "graduated", gl, tax_of(inc, STATUTE)
            else:
                r, ls, b = honest
            results["G5_missing_pct"].append(
                cert8("G5_missing_pct", c, elected, r, ls, b))

            # G6: 10% instead of 8%
            if elected and eligible:
                r, ls, b = "eight", [], max(gs - 25_000_000, 0) * 10 // 100
            else:
                r, ls, b = honest
            results["G6_rate10"].append(
                cert8("G6_rate10", c, elected, r, ls, b))

            # G7: penalties on the graduated basic tax even under the 8% option
            r, ls, b = honest
            results["G7_penalty_wrong_base"].append(
                cert8("G7_penalty_wrong_base", c, elected, r, ls, b,
                      penalty_base=grad_basic))

    for name, certs in results.items():
        path = OUT / f"{name}.json"
        path.write_text(json.dumps(certs, indent=1), encoding="utf-8")
        print(f"{name}: {len(certs)} certificates -> {path.name}")


if __name__ == "__main__":
    main()