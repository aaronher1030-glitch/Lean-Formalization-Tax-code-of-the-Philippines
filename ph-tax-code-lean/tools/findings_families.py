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
            "theorem": f"f{n:03d}_{family.lower()}_{n:03d}",
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
    with (DATA / "benchmark8_cases.csv").open(encoding="utf-8") as fh:
        cases = {r["case_id"]: r for r in csv.DictReader(fh)}
    with (DATA / "results8.csv").open(encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
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
