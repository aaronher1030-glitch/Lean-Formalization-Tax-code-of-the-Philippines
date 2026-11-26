# -*- coding: utf-8 -*-
"""Build the Philippine benchmark dataset and cross-check it against Lean.

Ground truth: tools/make_benchmark.py computes expected values with an
independent Python replication of the verified spec, then generates a Lean
file that recomputes every case with mkCertT and compares. A dataset is
written only when Python and Lean agree on every row.

Cases: income_tax_bracket x tier x days_late, including every statutory
boundary and its +-1-centavo neighbours. Amounts in centavos.
"""

import csv
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LEAN_EXE = ROOT / "tools" / "lean" / "dist" / "lean-4.35.0-windows" / "bin" / "lean.exe"
LEAN_DIR = ROOT / "lean"
HARNESS = ROOT / "lean" / "_harness"
DATA = ROOT / "data"

TIER_NAMES = ["micro", "small", "medium", "large"]

# (case_id, gross_sales, income, days_late, note)
CASES = [
    # -- Micro taxpayers (gross sales < P3M); income <= gross sales --
    ("B01", 250_000_000, 0, 30, "zero income"),
    ("B02", 250_000_000, 25_000_000, 0, "P250k boundary income, paid on time"),
    ("B03", 250_000_000, 25_000_001, 30, "one centavo into the 15% bracket"),
    ("B04", 299_999_999, 40_000_000, 90, "P400k boundary income, top of micro"),
    ("B05", 250_000_000, 10_000_000, 365, "tax is zero; penalty must be zero"),
    ("B06", 250_000_000, 50_000_000, 30, "second bracket, micro"),
    ("B07", 299_999_999, 290_000_000, 30, "P2.9M income at the top of micro"),
    ("B08", 300_000_000, 50_000_000, 30, "gross sales exactly P3M: small, not micro"),
    # -- Small taxpayers (P3M <= gross sales < P20M) --
    ("B09", 300_000_000, 25_000_005, 30, "just above the 15% floor, small"),
    ("B10", 500_000_000, 80_000_000, 90, "P800k boundary income"),
    ("B11", 500_000_000, 80_000_001, 30, "one centavo into the 25% bracket"),
    ("B12", 500_000_000, 150_000_000, 30, "middle of the 25% bracket"),
    ("B13", 500_000_000, 200_000_000, 365, "P2M boundary income, a year late"),
    ("B14", 500_000_000, 25_000_000, 30, "zero tax with days late: penalty on zero"),
    ("B15", 1999_999_999, 200_000_001, 30, "one centavo into the 30% bracket"),
    ("B16", 1999_999_999, 800_000_000, 30, "P8M boundary income"),
    ("B17", 1999_999_999, 800_000_001, 365, "one centavo into the 35% bracket"),
    # -- Medium taxpayers (P20M <= gross sales < P1B) --
    ("B18", 2000_000_000, 250_000_000, 30, "30% bracket, boundary tier"),
    ("B19", 2000_000_000, 400_000_000, 90, "30% bracket"),
    ("B20", 2000_000_000, 800_000_000, 1, "one day late"),
    ("B21", 2000_000_000, 100_000_000, 730, "two years late"),
    ("B22", 50_000_000_000, 900_000_000, 30, "35% bracket"),
    ("B23", 99_999_999_999, 1_000_000_000, 30, "P10M income, near the P1B tier line"),
    ("B24", 2000_000_000, 25_000_000, 90, "zero tax, medium tier"),
    # -- Large taxpayers (gross sales >= P1B) --
    ("B25", 100_000_000_000, 25_000_000, 0, "boundary tier, paid on time"),
    ("B26", 100_000_000_000, 900_000_000, 365, "35% bracket, a year late"),
    ("B27", 150_000_000_000, 50_000_000, 30, "the P42,500 worked case"),
    ("B28", 150_000_000_000, 2_000_000_000, 30, "P20M boundary income"),
    ("B29", 150_000_000_000, 2_000_000_001, 90, "one centavo over P20M"),
    ("B30", 150_000_000_000, 850_000_000, 30, "35% bracket"),
    ("B31", 100_000_000_000, 30_000_000, 30, "small income, large taxpayer"),
    ("B32", 100_000_000_000, 8_000_000_000, 730, "P80M income, two years late"),
]

# The LLM engine uses the first 30 cases; record that in the CSV.
LLM_IDS = {c[0] for c in CASES[:30]}


def classify(gs):
    if gs < 300_000_000:
        return "micro"
    if gs < 2_000_000_000:
        return "small"
    if gs < 100_000_000_000:
        return "medium"
    return "large"


def bracket_tax(t):
    if t <= 25_000_000:
        return 0
    if t <= 40_000_000:
        return (t - 25_000_000) * 15 // 100
    if t <= 80_000_000:
        return 2_250_000 + (t - 40_000_000) * 20 // 100
    if t <= 200_000_000:
        return 10_250_000 + (t - 80_000_000) * 25 // 100
    if t <= 800_000_000:
        return 40_250_000 + (t - 200_000_000) * 30 // 100
    return 220_250_000 + (t - 800_000_000) * 35 // 100


def expected(gs, income, days):
    tier = classify(gs)
    tax = bracket_tax(income)
    s_rate, i_rate = (10, 6) if tier in ("micro", "small") else (25, 12)
    sur = tax * s_rate // 100
    intr = tax * i_rate * days // 36500
    return tier, tax, sur, intr, tax + sur + intr


def main():
    rows = []
    for cid, gs, income, days, note in CASES:
        tier, tax, sur, intr, total = expected(gs, income, days)
        rows.append({
            "case_id": cid,
            "gross_sales_centavos": gs,
            "income_centavos": income,
            "days_late": days,
            "tier": tier,
            "income_tax": tax,
            "surcharge": sur,
            "interest": intr,
            "total_due": total,
            "in_llm_set": cid in LLM_IDS,
            "note": note,
        })

    HARNESS.mkdir(exist_ok=True)
    lines = ["import Tiers", "open PHTax"]
    for r in rows:
        gs, inc, d = r["gross_sales_centavos"], r["income_centavos"], r["days_late"]
        c = f"mkCertT {gs} {inc} {d}"
        lines.append(
            f'#eval ("{r["case_id"]}", ({c}).tier.rank, checkT ({c}),'
            f" ({c}).incomeTax, ({c}).surcharge, ({c}).interest, ({c}).total)"
        )
    bench = HARNESS / "BenchCheck.lean"
    bench.write_text("\n".join(lines) + "\n", encoding="utf-8")

    env_name = "LEAN_PATH"
    import os
    os.environ[env_name] = str(LEAN_DIR)
    proc = subprocess.run(
        [str(LEAN_EXE), str(bench)], capture_output=True, text=True, timeout=600
    )
    if proc.returncode != 0:
        print(proc.stdout)
        print(proc.stderr)
        sys.exit("Lean compile of BenchCheck.lean failed")

    parsed = {}
    for line in proc.stdout.splitlines():
        line = line.strip()
        if line.startswith('( "') or line.startswith('("'):
            body = line[1:-1]
            cid, rest = body.split(",", 1)
            cid = cid.strip().strip('"')
            vals = [v.strip() for v in rest.split(",")]
            rank, ok, tax, sur, intr, total = vals
            assert ok == "true", f"{cid}: honest certificate rejected"
            parsed[cid] = (int(rank), int(tax), int(sur), int(intr), int(total))

    bad = 0
    for r in rows:
        rank = TIER_NAMES.index(r["tier"])
        got = parsed.get(r["case_id"])
        want = (rank, r["income_tax"], r["surcharge"], r["interest"], r["total_due"])
        if got != want:
            bad += 1
            print(f"MISMATCH {r['case_id']}: python={want} lean={got}")
        else:
            print(f"ok {r['case_id']} {r['tier']:<6} tax={r['income_tax']:>12,}"
                  f" sur={r['surcharge']:>9,} int={r['interest']:>8,}"
                  f" total={r['total_due']:>13,}")
    if bad:
        sys.exit(f"{bad} mismatches: dataset NOT written")

    DATA.mkdir(exist_ok=True)
    out = DATA / "benchmark_cases.csv"
    with out.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    print(f"\nPASS: {len(rows)} cases agree between Python and Lean; wrote {out}")


if __name__ == "__main__":
    main()
