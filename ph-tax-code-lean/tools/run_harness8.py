# -*- coding: utf-8 -*-
"""Run every 8%-regime engine certificate through the verified checker check8.

Generates lean/_harness/Harness8.lean containing one Cert8 literal per
certificate, compiles it with the project toolchain, and reads back
(engine, case_id, elected, check8 verdict, certified total). The acceptance
verdict comes only from Lean; Python never re-implements the checker.
Python adds an UNVERIFIED diagnosis column explaining which conjunct
failed, for reporting only.

Inputs:  data/engine8_certs/*.json, data/benchmark8_cases.csv
Outputs: data/results8.csv, data/summary8.json
"""

import csv
import json
import os
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LEAN_EXE = Path(os.environ.get("LEAN", str(ROOT / "tools" / "lean" / "dist" / "lean-4.35.0-windows" / "bin" / "lean.exe")))
LEAN_DIR = ROOT / "lean"
HARNESS = ROOT / "lean" / "_harness"
DATA = ROOT / "data"
OUT_DIR = DATA / "engine8_certs"

ENGINES = ["G0_honest", "G1_eight_on_income", "G2_no_exempt_floor",
           "G3_ineligible_eight", "G4_pct_double", "G5_missing_pct",
           "G6_rate10", "G7_penalty_wrong_base"]

RESULT_RE = re.compile(
    r'\("([^"]+)", "([^"]+)", (true|false), (true|false), (\d+)\)')


def lean_opt(hi):
    return "none" if hi is None else f"(some {hi})"


def cert_literal(c):
    lines = ", ".join(
        f"⟨⟨{l['lo']}, {lean_opt(l['hi'])}, {l['rate']}⟩, {l['base']}, {l['amount']}⟩"
        for l in c["lines"])
    el = "true" if c["elected"] else "false"
    return (f"⟨{c['gross_sales']}, {c['income']}, {c['days_late']}, {el}, "
            f".{c['regime']}, [{lines}], {c['basic']}, {c['surcharge']}, "
            f"{c['interest']}, {c['total']}⟩")


def build_lean(entries):
    items = ",\n  ".join(
        f'("{e}", "{cid}", {"true" if el else "false"}, {lit})'
        for e, cid, el, lit in entries)
    src = f"""import Opt8
open PHTax

def certs8 : List (String × String × Bool × Cert8) :=
  [
  {items}
  ]

#eval certs8.map (fun (e, cid, el, c) => (e, cid, el, check8 c, c.total))
"""
    path = HARNESS / "Harness8.lean"
    path.write_text(src, encoding="utf-8")
    return path


def diagnose(c, truth):
    """UNVERIFIED Python-side explanation of a rejection. Not the verdict."""
    tier = truth["tier"]
    s_rate, i_rate = (10, 6) if tier in ("micro", "small") else (25, 12)
    eligible = c["gross_sales"] <= 300_000_000
    want_regime = "eight" if c["elected"] and eligible else "graduated"
    if c["regime"] != want_regime:
        return "regime_claim"
    if c["regime"] == "graduated":
        if len(c["lines"]) != 5 or any(
                l["lo"] != lo or l["hi"] != hi or l["rate"] != rate
                for l, (lo, hi, rate) in zip(
                    sorted(c["lines"], key=lambda x: x["lo"]),
                    [(25000000, 40000000, 15), (40000000, 80000000, 20),
                     (80000000, 200000000, 25), (200000000, 800000000, 30),
                     (800000000, None, 35)])):
            return "schedule"
        if any(l["amount"] != l["base"] * l["rate"] // 100 for l in c["lines"]):
            return "line_amount"
        want_basic = sum(l["amount"] for l in c["lines"]) \
            + c["gross_sales"] * 3 // 100
    else:
        if c["lines"]:
            return "eight_lines_not_empty"
        want_basic = max(c["gross_sales"] - 25_000_000, 0) * 8 // 100
    if c["basic"] != want_basic:
        return "basic"
    if c["surcharge"] != c["basic"] * s_rate // 100:
        return "surcharge"
    if c["interest"] != c["basic"] * i_rate * c["days_late"] // 36500:
        return "interest"
    if c["total"] != c["basic"] + c["surcharge"] + c["interest"]:
        return "total_sum"
    return "none"


def main():
    with (DATA / "benchmark8_cases.csv").open(encoding="utf-8") as f:
        truth = {(r["case_id"], r["elected"] == "True"): r
                 for r in csv.DictReader(f)}
    entries = []
    for name in ENGINES:
        certs = json.loads((OUT_DIR / f"{name}.json").read_text(encoding="utf-8"))
        for c in certs:
            entries.append((name, c["case_id"], c["elected"], cert_literal(c), c))
    if not entries:
        sys.exit("no certificates found")

    path = build_lean([(e, cid, el, lit) for e, cid, el, lit, _ in entries])
    os.environ["LEAN_PATH"] = str(LEAN_DIR)
    proc = subprocess.run([str(LEAN_EXE), str(path)],
                          capture_output=True, text=True, timeout=900)
    if proc.returncode != 0:
        print(proc.stdout[-4000:])
        print(proc.stderr[-4000:])
        sys.exit("Harness8.lean failed to compile")
    verdicts = {(m.group(1), m.group(2), m.group(3) == "true"):
                (m.group(4) == "true", int(m.group(5)))
                for m in RESULT_RE.finditer(proc.stdout)}
    if len(verdicts) != len(entries):
        sys.exit(f"parsed {len(verdicts)} verdicts for {len(entries)} entries")

    rows, false_accepts = [], []
    for engine, cid, el, _, c in entries:
        t = truth[(cid, el)]
        accepted, cert_total = verdicts[(engine, cid, el)]
        true_total = int(t["total_due"])
        err = cert_total - true_total
        if accepted and err != 0:
            false_accepts.append({"engine": engine, "case_id": cid,
                                  "elected": el, "cert_total": cert_total,
                                  "true_total": true_total})
        rows.append({
            "engine": engine, "case_id": cid, "elected": el,
            "accepted": accepted, "cert_total": cert_total,
            "true_total": true_total, "error": err,
            "claimed_regime": c["regime"], "true_regime": t["regime"],
            "python_diagnosis_unverified": (diagnose(c, t)
                                            if not accepted else "none"),
        })

    results = DATA / "results8.csv"
    with results.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)

    summary = {"certificates_checked": len(rows),
               "false_accepts": false_accepts, "engines": {}}
    print(f"{'engine':<20} {'n':>3} {'acc':>4} {'rej':>4} "
          f"{'acc_rate':>8} {'wrong_accepts':>13} {'max_overclaim':>13}")
    for engine in ENGINES:
        rs = [r for r in rows if r["engine"] == engine]
        acc = [r for r in rs if r["accepted"]]
        over = max((r["error"] for r in rs if r["error"] > 0), default=0)
        summary["engines"][engine] = {
            "n": len(rs), "accepted": len(acc),
            "rejected": len(rs) - len(acc),
            "accept_rate": round(len(acc) / len(rs), 4),
            "accepted_with_wrong_total": sum(1 for r in acc if r["error"] != 0),
            "max_overclaim_rejected": over,
            "max_abs_error_any": max(abs(r["error"]) for r in rs),
        }
        print(f"{engine:<20} {len(rs):>3} {len(acc):>4} {len(rs)-len(acc):>4} "
              f"{len(acc)/len(rs):>8.2%} "
              f"{summary['engines'][engine]['accepted_with_wrong_total']:>13} "
              f"{over:>13,}")

    (DATA / "summary8.json").write_text(
        json.dumps(summary, indent=1), encoding="utf-8")
    print(f"\nresults -> {results}")
    if false_accepts:
        print(f"SOUNDNESS VIOLATION (harness bug): {false_accepts}")
    else:
        print("no false accepts: every accepted certificate stated the "
              "correct total")


if __name__ == "__main__":
    main()