# Loophole Findings — Derived from the Verified Core

Five findings obtained by inspecting what the checked specification does
and does not constrain. None comes from a literature or web search; each
is demonstrated inside this artifact by kernel-checked Lean statements
(`lean/Loopholes.lean`, 5 theorems, 18 examples, axioms `[propext]` only)
and by `tools/loopholes.py`, which constructs exploiting certificates,
judges them with `checkT`/`check8`, and cross-checks every total against
an independent Python implementation (11 rows, full agreement,
`data/loophole_cases.csv`).

Two kinds are distinguished:

- **Encoding gap** — the checker accepts an input that could not arise
  under a faithful reading of the statute. The arithmetic is verified;
  the *premises* are not guarded.
- **Statutory incentive** — every input is honest, but the encoded law
  itself creates an arbitrage or a cliff. These are findings about the
  law as formalized, not bugs in the checker.

Nothing here is legal advice. The encoding awaits practitioner review,
and we make no claim that these observations are new to the world — only
that they were derived here, from the verified core, with machine-checked
evidence.

## L1. Taxable income may exceed gross sales (encoding gap)

Neither `checkT` nor `check8` requires `income ≤ grossSales`. A
certificate claiming ₱1,000,000 gross sales and ₱100,000,000 taxable
income is accepted by both checkers:

| checker | total accepted |
|---|---|
| `checkT` | ₱38,012,406.16 |
| `check8` | ₱38,045,554.10 |

Under the statute, taxable income of a self-employed taxpayer is gross
receipts less deductions and cannot exceed gross sales. The benchmark
enforced `income ≤ grossSales` as a data-generation constraint; the
checker never did. Evidence: `Loopholes.lean` L1 examples (acceptance via
`checkT_complete` / `check8_complete`); tool rows `income_gt_gross_*`.
**Proposed guard:** add `income ≤ grossSales` as a conjunct of both
checkers; soundness statements would need the same premise. Not
implemented — changing the verified checker requires separate approval.

## L2. Costless, retroactive regime switch (encoding gap)

`Cert8` carries no taxable year and no election date. The same delinquent
taxpayer (gs = income = ₱3,000,000, 30 days late) is accepted under both
regimes, and flipping only the `elected` flag saves ₱632,573.28
(₱875,658.21 → ₱243,084.93). RR 8-2018 requires the election in the
first-quarter filing, irrevocable for that year; an audited taxpayer
cannot switch after the fact. The model cannot see the difference.
Evidence: theorem `election_switch_saves` (kernel-checked difference
63,257,328 centavos); tool rows `retro_graduated` / `retro_eight`.
**Proposed guard:** add `taxableYear` and an election-timing field;
accept an eight-regime certificate only when the election was declared
on time for that year. Not implemented.

## L3. Exactly one penalty cliff, at ₱20,000,000 (statutory incentive)

The four taxpayer classes carry only **two** penalty regimes: micro and
small share 10%/6%, medium and large share 25%/12%. So the ₱3,000,000 and
₱1,000,000,000 lines are penalty-neutral (kernel-checked equalities at
the ₱1B line), and the only discontinuity is at ₱20,000,000, where the
surcharge jumps 10% → 25% and the interest 6% → 12%.

- On a ₱1,000,000 basic tax, one year late: the cliff adds ₱150,000
  surcharge + ₱60,000 interest = **₱210,000** (theorem `tier_cliff_20M`).
- End to end: gs = ₱19,999,999.99 vs ₱20,000,000.00, income ₱15,000,000,
  30 days late: totals ₱5,803,652.71 vs ₱6,617,430.47 — **₱813,777.76
  for one centavo of gross sales** (tool rows `cliff_below_20M` /
  `cliff_at_20M`).

This is a feature of RR 6-2024 as encoded, not a checker bug — but it is
an incentive to understate gross sales at exactly that line, and the
checker verifies the tier only against the *claimed* gross sales. It
complements the study-1 `vat_tier_gap` finding at ₱3M: that line changes
classification and 8% eligibility, this one changes penalties.
**No guard is possible without changing the law**; the mitigation is
disclosure plus an audit flag for gross sales within a centavo-scale
neighborhood of ₱20M.

## L4. The 8% election is a penalty shelter only above an income crossover

Penalties are monotone in the base (new lemmas `surchargeT_mono_tax`,
`interestT_mono_tax`), so whenever `tax8 gs ≤ bracketTax income + pctTax
gs`, electing 8% weakly reduces a delinquent taxpayer's surcharge and
interest (`election_shelters_penalty`). But the base inequality is **not
unconditional** — an earlier draft of this finding claimed it was, and
the kernel refuted it. At gs = ₱3,000,000 with income at the ₱250,000
exemption floor, the graduated penalty base is only the ₱90,000
percentage tax while the 8% base is ₱220,000: electing 8% *raises*
penalties from ₱9,443.83 to ₱23,084.93 (kernel-checked negation; tool
rows `trap_graduated` / `trap_eight`).

The crossover at gs = ₱3M is exactly **₱910,000.00** of taxable income,
kernel-checked one centavo apart (`bracketTax 90999999` fails the base
inequality, `bracketTax 91000000` satisfies it; binary search in
`tools/loopholes.py` agrees). Above it the option shelters penalties;
below it the option is a penalty trap. Combined with L2, the model
accepts either direction even when claimed after the delinquency.
**Policy finding, no checker change proposed.**

## L5. No prescriptive period: interest accrues forever (encoding gap)

`daysLate` is unbounded. A certificate 100 years late is accepted, with
interest exactly twelve times the basic tax: basic ₱61,902,500.00,
interest ₱742,830,000.00, total ₱820,208,125.00 (tool row
`hundred_years_late`; kernel-checked `interestT .large 5000000000 36500 =
60000000000` at smaller scale). NIRC §203 gives the Bureau three years to
assess, ten under §222 for fraud or failure to file; the model has no
assessment date and no prescription guard, so it cannot flag a time-barred
assessment. **Proposed guard:** assessment and filing dates plus a
prescription conjunct (with a fraud flag for the §222 exception). Not
implemented.

## Reproduce

```bash
bash lean/run_demo.sh          # builds all seven files incl. Loopholes.lean
python -X utf8 tools/loopholes.py   # 11 rows, Python/Lean agreement
```

## Honesty notes

- L1, L2, L5 are gaps in *our encoding*, demonstrated by acceptance of
  constructed inputs; they are not claims that the BIR's actual systems
  have these gaps.
- L3, L4 are properties of the statute as formalized; whether they
  matter in practice (e.g., how often gross sales land near ₱20M) is an
  empirical question this artifact cannot answer.
- The proposed guards are designs, not verified changes; implementing
  them would alter `checkT`/`check8` and their soundness statements and
  requires separate approval.
- Practitioner review of the whole encoding remains pending.