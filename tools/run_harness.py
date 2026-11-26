# -*- coding: utf-8 -*-
"""Run every engine certificate through the verified Lean checker.

Generates lean/_harness/Harness.lean containing one CertT literal per
certificate, compiles it with the project toolchain, and reads back
(engine, case_id, checkT verdict, certified total). The acceptance
verdict comes only from Lean; Python never re-implements the checker.
Python adds an UNVERIFIED diagnosis column explaining which conjunct
failed, for reporting only.

Inputs:  data/engine_certs/*.json, data/llm_raw/*.json (optional)
Outputs: data/results.csv, data/summary.json
"""

import csv
import json
import os
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LEAN_EXE = ROOT / "tools" / "lean" / "dist" / "lean-4.35.0-windows" / "bin" / "lean.exe"
LEAN_DIR = ROOT / "lean"
HARNESS = ROOT / "lean" / "_harness"
DATA = ROOT / "data"
OUT_DIR = DATA / "engine_certs"
LLM_DIR = DATA / "llm_raw"

ENGINES = ["E0_honest", "F1_flat_top", "F2_untiered", "F3_year360",
           "F4_half_up", "F5_train2018", "F6_micro_le"]

RESULT_RE = re.compile(r'\("([^"]+)", "([^"]+)", (true|false), (\d+)\)')


def lean_opt(hi):
    return "none" if hi is None else f"(some {hi})"


def cert_literal(c):
    lines = ", ".join(
        f"⟨⟨{l['lo']}, {lean_opt(l['hi'])}, {l['rate']}⟩, {l['base']}, {l['amount']}⟩"
        for l in c["lines"])
    return (f"⟨{c['gross_sales']}, .{c['tier']}, {c['income']}, {c['days_late']}, "
            f"[{lines}], {c['income_tax']}, {c['surcharge']}, {c['interest']}, "
            f"{c['total']}⟩")


def build_lean(entries):
    items = ",\n  ".join(
        f'("{e}", "{cid}", {lit})' for e, cid, lit in entries)
    src = f"""import Tiers
open PHTax

def certs : List (String × String × CertT) :=
  [
  {items}
  ]

#eval certs.map (fun (e, cid, c) => (e, cid, checkT c, c.total))
"""
    path = HARNESS / "Harness.lean"
    path.write_text(src, encoding="utf-8")
    return path


def diagnose(c, truth):
    """UNVERIFIED Python-side explanation of a rejection. Not the verdict."""
    if c["tier"] != truth["tier"]:
        return "tier_claim"
    if len(c["lines"]) != 5 or any(
            l["lo"] != lo or l["hi"] != hi or l["rate"] != rate
            for l, (lo, hi, rate) in zip(
                sorted(c["lines"], key=lambda x: x["lo"]),
                [(25000000, 40000000, 15), (40000000, 80000000, 20),
                 (80000000, 200000000, 25), (200000000, 800000000, 30),
                 (800000000, None, 35)])):
        return "schedule"
    if any((l["base"] != (0 if c["income"] <= l["lo"]
                          else min(c["income"], l["hi"] if l["hi"] is not None
                                   else c["income"]) - l["lo"]))
           for l in c["lines"]):
        return "line_base"
    if any(l["amount"] != l["base"] * l["rate"] // 100 for l in c["lines"]):
        return "line_amount"
    if c["income_tax"] != sum(l["amount"] for l in c["lines"]):
        return "income_tax_sum"
    s_rate = 10 if truth["tier"] in ("micro", "small") else 25
    i_rate = 6 if truth["tier"] in ("micro", "small") else 12
    if c["surcharge"] != c["income_tax"] * s_rate // 100:
        return "surcharge"
    if c["interest"] != c["income_tax"] * i_rate * c["days_late"] // 36500:
        return "interest"
    if c["total"] != c["income_tax"] + c["surcharge"] + c["interest"]:
        return "total_sum"
    return "none"


def load_entries():
    with (DATA / "benchmark_cases.csv").open(encoding="utf-8") as f:
        cases = {r["case_id"]: r for r in csv.DictReader(f)}
    entries, parse_failures = [], []
    for name in ENGINES:
        certs = json.loads((OUT_DIR / f"{name}.json").read_text(encoding="utf-8"))
        for c in certs:
            entries.append((name, c["case_id"], cert_literal(c), c))
    if LLM_DIR.exists():
        for path in sorted(LLM_DIR.glob("*.json")):
            agent = path.stem
            try:
                certs = json.loads(path.read_text(encoding="utf-8"))
                if isinstance(certs, dict):
                    certs = certs.get("certificates", [])
                for c in certs:
                    case = cases[c["case_id"]]
                    full = dict(c)
                    full["gross_sales"] = int(case["gross_sales_centavos"])
                    full["income"] = int(case["income_centavos"])
                    full["days_late"] = int(case["days_late"])
                    full["tier"] = str(c["tier"]).replace("PHTax.Tier.", "")
                    entries.append((f"LLM_{agent}", c["case_id"],
                                    cert_literal(full), full))
            except (json.JSONDecodeError, KeyError, TypeError) as exc:
                parse_failures.append({"agent": agent, "file": path.name,
                                       "error": str(exc)[:200]})
    return entries, parse_failures


def main():
    entries, parse_failures = load_entries()
    if not entries:
        sys.exit("no certificates found")

    with (DATA / "benchmark_cases.csv").open(encoding="utf-8") as f:
        truth = {r["case_id"]: r for r in csv.DictReader(f)}

    path = build_lean([(e, cid, lit) for e, cid, lit, _ in entries])
    os.environ["LEAN_PATH"] = str(LEAN_DIR)
    proc = subprocess.run([str(LEAN_EXE), str(path)],
                          capture_output=True, text=True, timeout=900)
    if proc.returncode != 0:
        print(proc.stdout[-4000:])
        print(proc.stderr[-4000:])
        sys.exit("Harness.lean failed to compile")
    verdicts = {(m.group(1), m.group(2)): (m.group(3) == "true", int(m.group(4)))
                for m in RESULT_RE.finditer(proc.stdout)}
    if len(verdicts) != len(entries):
        sys.exit(f"parsed {len(verdicts)} verdicts for {len(entries)} entries")

    rows, false_accepts = [], []
    for engine, cid, _, c in entries:
        t = truth[cid]
        accepted, cert_total = verdicts[(engine, cid)]
        true_total = int(t["total_due"])
        err = cert_total - true_total
        if accepted and err != 0:
            false_accepts.append({"engine": engine, "case_id": cid,
                                  "cert_total": cert_total,
                                  "true_total": true_total})
        rows.append({
            "engine": engine, "case_id": cid, "accepted": accepted,
            "cert_total": cert_total, "true_total": true_total,
            "error": err,
            "claimed_tier": c["tier"], "true_tier": t["tier"],
            "python_diagnosis_unverified": (diagnose(c, t)
                                            if not accepted else "none"),
        })

    results = DATA / "results.csv"
    with results.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)

    summary = {"certificates_checked": len(rows),
               "false_accepts": false_accepts,
               "llm_parse_failures": parse_failures, "engines": {}}
    print(f"{'engine':<12} {'n':>3} {'acc':>4} {'rej':>4} "
          f"{'acc_rate':>8} {'wrong_accepts':>13} {'max_overclaim':>13}")
    for engine in dict.fromkeys(r["engine"] for r in rows):
        rs = [r for r in rows if r["engine"] == engine]
        acc = [r for r in rs if r["accepted"]]
        over = max((r["error"] for r in rs if r["error"] > 0), default=0)
        summary["engines"][engine] = {
            "n": len(rs), "accepted": len(acc),
            "rejected": len(rs) - len(acc),
            "accept_rate": round(len(acc) / len(rs), 4),
            "accepted_with_wrong_total": sum(
                1 for r in acc if r["error"] != 0),
            "max_overclaim_rejected": over,
            "max_abs_error_any": max(abs(r["error"]) for r in rs),
        }
        print(f"{engine:<12} {len(rs):>3} {len(acc):>4} {len(rs)-len(acc):>4} "
              f"{len(acc)/len(rs):>8.2%} "
              f"{summary['engines'][engine]['accepted_with_wrong_total']:>13} "
              f"{over:>13,}")

    (DATA / "summary.json").write_text(
        json.dumps(summary, indent=1), encoding="utf-8")
    print(f"\nresults -> {results}")
    if false_accepts:
        print(f"SOUNDNESS VIOLATION (harness bug): {false_accepts}")
    else:
        print("no false accepts: every accepted certificate stated the "
              "correct total")


if __name__ == "__main__":
    main()
