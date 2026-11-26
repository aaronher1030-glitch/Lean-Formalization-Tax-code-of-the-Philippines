# -*- coding: utf-8 -*-
"""Seeded-fault engines for the certificate benchmark.

Each engine is a plausible, self-consistent implementation of the tax
computation. Each emits a full certificate in the CertT schema; the Lean
checker, not this file, decides acceptance. The honest engine E0 replicates
the verified spec exactly and must be accepted on every case.

Engines
  E0_honest      the verified spec (RA 11976 tiers, TRAIN 2023+ schedule)
  F1_flat_top    top marginal rate applied to everything above P250k
  F2_untiered    the pre-repair model: 25%/12% for every taxpayer
  F3_year360     a 360-day year for interest
  F4_half_up     rounds half-up instead of truncating
  F5_train2018   the stale 2018-2022 TRAIN schedule
  F6_micro_le    reads the micro tier as "at most P3M" instead of "under P3M"
"""

import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
OUT = DATA / "engine_certs"

STATUTE = [
    (25_000_000, 40_000_000, 15),
    (40_000_000, 80_000_000, 20),
    (80_000_000, 200_000_000, 25),
    (200_000_000, 800_000_000, 30),
    (800_000_000, None, 35),
]

TRAIN_2018 = [
    (25_000_000, 40_000_000, 20),
    (40_000_000, 80_000_000, 25),
    (80_000_000, 200_000_000, 30),
    (200_000_000, 800_000_000, 32),
    (800_000_000, None, 35),
]


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


def cert(engine, case, tier, tax, surcharge, interest, table):
    lines = []
    for lo, hi, rate in table:
        base = slice_of(case["income_centavos"], lo, hi)
        lines.append({
            "lo": lo, "hi": hi, "rate": rate, "base": base,
            "amount": base * rate // 100,
        })
    return {
        "engine": engine,
        "case_id": case["case_id"],
        "gross_sales": case["gross_sales_centavos"],
        "tier": tier,
        "income": case["income_centavos"],
        "days_late": case["days_late"],
        "lines": lines,
        "income_tax": tax,
        "surcharge": surcharge,
        "interest": interest,
        "total": tax + surcharge + interest,
    }


def rates(tier):
    return (10, 6) if tier in ("micro", "small") else (25, 12)


def main():
    with (DATA / "benchmark_cases.csv").open(encoding="utf-8") as f:
        cases = list(csv.DictReader(f))
    for c in cases:
        for k in ("gross_sales_centavos", "income_centavos", "days_late"):
            c[k] = int(c[k])

    OUT.mkdir(exist_ok=True)
    results = {e: [] for e in
               ["E0_honest", "F1_flat_top", "F2_untiered", "F3_year360",
                "F4_half_up", "F5_train2018", "F6_micro_le"]}

    for c in cases:
        inc, days = c["income_centavos"], c["days_late"]
        true_tier = classify(c["gross_sales_centavos"])
        s_true, i_true = rates(true_tier)

        tax = tax_of(inc, STATUTE)
        sur = tax * s_true // 100
        intr = tax * i_true * days // 36500
        results["E0_honest"].append(
            cert("E0_honest", c, true_tier, tax, sur, intr, STATUTE))

        flat = (inc - 25_000_000) * 35 // 100 if inc > 25_000_000 else 0
        s_f = flat * s_true // 100
        i_f = flat * i_true * days // 36500
        results["F1_flat_top"].append(
            cert("F1_flat_top", c, true_tier, flat, s_f, i_f,
                 [(800_000_000, None, 35)]))

        sur_u = tax * 25 // 100
        intr_u = tax * 12 * days // 36500
        results["F2_untiered"].append(
            cert("F2_untiered", c, true_tier, tax, sur_u, intr_u, STATUTE))

        intr_360 = tax * i_true * days // 36000
        results["F3_year360"].append(
            cert("F3_year360", c, true_tier, tax, sur, intr_360, STATUTE))

        sur_h = (tax * s_true + 50) // 100
        intr_h = (tax * i_true * days + 18_250) // 36_500
        results["F4_half_up"].append(
            cert("F4_half_up", c, true_tier, tax, sur_h, intr_h, STATUTE))

        tax_18 = tax_of(inc, TRAIN_2018)
        results["F5_train2018"].append(
            cert("F5_train2018", c, true_tier, tax_18,
                 tax_18 * 25 // 100, tax_18 * 12 * days // 36500, TRAIN_2018))

        claimed = "micro" if c["gross_sales_centavos"] <= 300_000_000 \
            else true_tier
        s_m, i_m = rates(claimed)
        tax_m = tax_of(inc, STATUTE)
        results["F6_micro_le"].append(
            cert("F6_micro_le", c, claimed, tax_m,
                 tax_m * s_m // 100, tax_m * i_m * days // 36500, STATUTE))

    for name, certs in results.items():
        path = OUT / f"{name}.json"
        path.write_text(json.dumps(certs, indent=1), encoding="utf-8")
        print(f"{name}: {len(certs)} certificates -> {path.name}")


if __name__ == "__main__":
    main()
