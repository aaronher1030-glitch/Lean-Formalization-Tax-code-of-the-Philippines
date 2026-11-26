# -*- coding: utf-8 -*-
"""Ground truth for the 8%-regime (check8) engine study.

Mirrors tools/make_benchmark.py: an independent Python replication of the
verified spec computes expected values for every (case, elected) pair, then
a generated Lean file recomputes each with mkCert8 and check8. The dataset
is written only when Python and Lean agree on every row.

Cases: the 32 benchmark cases x elected in {false, true} = 64 rows.
Amounts in centavos.
"""

import csv
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LEAN_EXE = Path(os.environ.get("LEAN", str(ROOT / "tools" / "lean" / "dist" / "lean-4.35.0-windows" / "bin" / "lean.exe")))
LEAN_DIR = ROOT / "lean"
HARNESS = ROOT / "lean" / "_harness"
DATA = ROOT / "data"


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


def expected(gs, income, days, elected):
    tier = classify(gs)
    regime = "eight" if elected and gs <= 300_000_000 else "graduated"
    if regime == "eight":
        basic = max(gs - 25_000_000, 0) * 8 // 100
    else:
        basic = bracket_tax(income) + gs * 3 // 100
    s_rate, i_rate = (10, 6) if tier in ("micro", "small") else (25, 12)
    sur = basic * s_rate // 100
    intr = basic * i_rate * days // 36500
    return tier, regime, basic, sur, intr, basic + sur + intr


def main():
    with (DATA / "benchmark_cases.csv").open(encoding="utf-8") as f:
        cases = list(csv.DictReader(f))
    rows = []
    for c in cases:
        gs, inc, days = (int(c[k]) for k in
                         ("gross_sales_centavos", "income_centavos", "days_late"))
        for elected in (False, True):
            tier, regime, basic, sur, intr, total = expected(gs, inc, days, elected)
            rows.append({
                "case_id": c["case_id"], "elected": elected,
                "gross_sales_centavos": gs, "income_centavos": inc,
                "days_late": days, "tier": tier, "regime": regime,
                "basic": basic, "surcharge": sur, "interest": intr,
                "total_due": total,
            })

    HARNESS.mkdir(exist_ok=True)
    lines = ["import Opt8", "open PHTax"]
    for r in rows:
        gs, inc, d = r["gross_sales_centavos"], r["income_centavos"], r["days_late"]
        el = "true" if r["elected"] else "false"
        c = f"mkCert8 {gs} {inc} {d} {el}"
        lines.append(f'#eval ("{r["case_id"]}", {el}, check8 ({c}), ({c}).total)')
    bench = HARNESS / "BenchCheck8.lean"
    bench.write_text("\n".join(lines) + "\n", encoding="utf-8")

    os.environ["LEAN_PATH"] = str(LEAN_DIR)
    proc = subprocess.run([str(LEAN_EXE), str(bench)],
                          capture_output=True, text=True, timeout=600)
    if proc.returncode != 0:
        print(proc.stdout)
        print(proc.stderr)
        sys.exit("Lean compile of BenchCheck8.lean failed")

    parsed = {}
    for line in proc.stdout.splitlines():
        line = line.strip()
        if line.startswith('("'):
            body = line[1:-1]
            cid, rest = body.split(",", 1)
            cid = cid.strip().strip('"')
            el, ok, total = [v.strip() for v in rest.split(",")]
            assert ok == "true", f"{cid} elected={el}: honest Cert8 rejected"
            parsed[(cid, el == "true")] = int(total)

    bad = 0
    for r in rows:
        got = parsed.get((r["case_id"], r["elected"]))
        if got != r["total_due"]:
            bad += 1
            print(f"MISMATCH {r['case_id']} elected={r['elected']}: "
                  f"python={r['total_due']} lean={got}")
    if bad:
        sys.exit(f"{bad} mismatches: dataset NOT written")

    out = DATA / "benchmark8_cases.csv"
    with out.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    print(f"PASS: {len(rows)} rows agree between Python and Lean; wrote {out}")


if __name__ == "__main__":
    main()