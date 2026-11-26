# -*- coding: utf-8 -*-
"""Loophole demonstration tool.

Constructs certificates that exploit gaps and incentives found by
inspecting the verified core (see lean/Loopholes.lean and
LOOPHOLE_FINDINGS.md). Every certificate is internally consistent, so the
point is not that the checker is fooled about arithmetic — it is that the
checker ACCEPTS inputs the statute would not allow, or that the encoded
law itself creates arbitrage.

Method mirrors the engine studies: an independent Python implementation
computes expected totals, a generated Lean file asks checkT/check8 for
verdicts and totals, and the two must agree on every row before
data/loophole_cases.csv is written.
"""

import csv
import os
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LEAN_DIR = ROOT / "lean"
DATA = ROOT / "data"
HARNESS = LEAN_DIR / "_harness" / "LoopholeCheck.lean"
LEAN = os.environ.get(
    "LEAN", str(ROOT / "tools" / "lean" / "dist" /
                "lean-4.35.0-windows" / "bin" / "lean.exe"))

STATUTE = [
    (25_000_000, 40_000_000, 15),
    (40_000_000, 80_000_000, 20),
    (80_000_000, 200_000_000, 25),
    (200_000_000, 800_000_000, 30),
    (800_000_000, None, 35),
]


def bracket_tax(t):
    total = 0
    for lo, hi, rate in STATUTE:
        if t <= lo:
            break
        base = (min(t, hi) - lo) if hi is not None else (t - lo)
        total += base * rate // 100
    return total


def tax8(gs):
    return (gs - 25_000_000) * 8 // 100 if gs > 25_000_000 else 0


def pct_tax(gs):
    return gs * 3 // 100


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


def expected(gs, income, days, elected, checker="8"):
    tier = classify(gs)
    s, i = rates(tier)
    if checker == "T":
        basic = bracket_tax(income)  # CertT: income tax only, no pct, no 8%
    elif elected and gs <= 300_000_000:
        basic = tax8(gs)
    else:
        basic = bracket_tax(income) + pct_tax(gs)
    sur = basic * s // 100
    intr = basic * i * days // 36500
    return basic + sur + intr


# finding, label, checker, gs, income, days, elected, note
ROWS = [
    ("L1", "income_gt_gross_checkT", "T",
     100_000_000, 10_000_000_000, 30, False,
     "P1M gross sales, P100M taxable income: impossible, accepted"),
    ("L1", "income_gt_gross_check8", "8",
     100_000_000, 10_000_000_000, 30, False,
     "same inputs under the election-aware checker: accepted"),
    ("L2", "retro_graduated", "8",
     300_000_000, 300_000_000, 30, False,
     "delinquent taxpayer, no election"),
    ("L2", "retro_eight", "8",
     300_000_000, 300_000_000, 30, True,
     "same certificate with elected flipped after the fact"),
    ("L3", "cliff_below_20M", "8",
     1_999_999_999, 1_500_000_000, 30, False,
     "one centavo below the P20M tier line"),
    ("L3", "cliff_at_20M", "8",
     2_000_000_000, 1_500_000_000, 30, False,
     "one centavo above: penalties jump"),
    ("L4", "trap_graduated", "8",
     300_000_000, 25_000_000, 30, False,
     "income at exemption floor: graduated penalty base P90k"),
    ("L4", "trap_eight", "8",
     300_000_000, 25_000_000, 30, True,
     "electing 8% RAISES penalties here (base P220k)"),
    ("L4", "crossover_at", "8",
     300_000_000, 91_000_000, 30, True,
     "smallest income where the 8% base stops exceeding graduated"),
    ("L4", "crossover_below", "8",
     300_000_000, 90_999_999, 30, True,
     "one centavo below the crossover"),
    ("L5", "hundred_years_late", "8",
     150_000_000_000, 5_000_000_000, 36_500, False,
     "100 years late: accepted, interest = 12x basic, no prescription"),
]

RESULT_RE = re.compile(r'\("([^"]+)", (true|false), (\d+)\)')


def lean_source():
    lines = ["import Opt8", "open PHTax", ""]
    for _, label, checker, gs, inc, days, el, _ in ROWS:
        if checker == "T":
            mk = f"mkCertT {gs} {inc} {days}"
            chk = f"checkT ({mk})"
        else:
            mk = f"mkCert8 {gs} {inc} {days} {str(el).lower()}"
            chk = f"check8 ({mk})"
        lines.append(f'#eval ("{label}", {chk}, ({mk}).total)')
    return "\n".join(lines) + "\n"


def crossover():
    gs = 300_000_000
    target = tax8(gs) - pct_tax(gs)
    lo, hi = 0, gs
    while lo < hi:
        mid = (lo + hi) // 2
        if bracket_tax(mid) >= target:
            hi = mid
        else:
            lo = mid + 1
    return lo


def main():
    HARNESS.parent.mkdir(exist_ok=True)
    HARNESS.write_text(lean_source(), encoding="utf-8")
    env = dict(os.environ)
    env["LEAN_PATH"] = str(LEAN_DIR)
    proc = subprocess.run([LEAN, str(HARNESS)], capture_output=True,
                          text=True, env=env, cwd=str(LEAN_DIR))
    if proc.returncode != 0:
        raise SystemExit("Lean failed:\n" + proc.stdout + proc.stderr)
    got = {m.group(1): (m.group(2) == "true", int(m.group(3)))
           for m in RESULT_RE.finditer(proc.stdout)}

    rows = []
    for finding, label, checker, gs, inc, days, el, note in ROWS:
        exp_total = expected(gs, inc, days, el, checker)
        if label not in got:
            raise SystemExit(f"missing Lean result for {label}")
        accepted, total = got[label]
        if not accepted or total != exp_total:
            raise SystemExit(
                f"DISAGREEMENT {label}: lean={got[label]} "
                f"python=({True}, {exp_total})")
        rows.append([finding, label, f"check{checker}", gs, inc, days,
                     el, accepted, total, note])
        print(f"{finding} {label:24s} accepted={accepted} "
              f"total={total:>13,} centavos")

    x = crossover()
    assert x == 91_000_000, f"crossover moved: {x}"
    print(f"L4 crossover income at gs=P3M: {x:,} centavos "
          f"(P{x/100:,.2f}), matches kernel-checked examples")

    DATA.mkdir(exist_ok=True)
    out = DATA / "loophole_cases.csv"
    with out.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["finding", "label", "checker", "gross_sales", "income",
                    "days_late", "elected", "accepted", "total_centavos",
                    "note"])
        w.writerows(rows)
    print(f"\n{len(rows)} rows, Python/Lean agree on all -> {out}")


if __name__ == "__main__":
    main()