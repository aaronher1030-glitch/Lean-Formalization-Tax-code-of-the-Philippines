# Status

Measured facts about the artifact, re-runnable from this repository.
Last verified: **18 November 2026**, on the curated repo copy.

## Build

```bash
export LEAN=/path/to/lean-4.35.0/bin/lean   # lean.exe on Windows
bash lean/run_demo.sh
```

| Check | Result |
|---|---|
| Exit code | 0 |
| Error / warning / `sorry` lines in build log | 0 |
| Wall time, cold build of the six-file artifact (repo copy, 16 Nov 2026) | 50 s |
| Wall time, full build of all seven files (repo copy, 18 Nov 2026) | 71 s |
| Wall time, warm rebuild of all seven files (workspace, 18 Nov 2026) | 57.3 s |
| Toolchain | Lean 4.35.0, core library only (no Mathlib, no Lake) |

## Artifact metrics (re-counted from source, 2026-11-18)

| File | Lines | Theorems | Kernel-checked examples |
|---|---|---|---|
| `TaxSchedule.lean` | 63 | 5 | 10 |
| `TaxScheduleChecks.lean` | 29 | 0 | 20 |
| `GovernanceDemo.lean` | 85 | 10 | 0 |
| `Certificate.lean` | 179 | 10 | 6 |
| `Tiers.lean` | 207 | 13 | 9 |
| `Opt8.lean` | 296 | 16 | 19 |
| `Loopholes.lean` | 165 | 5 | 18 |
| **Total** | **1,024** | **59** | **82** |

Full theorem list: [THEOREMS.md](THEOREMS.md).

## Axiom audit (`#print axioms`, run 2026-11-18)

| Theorem | Axioms |
|---|---|
| `check_sound`, `checkT_sound`, `check8_sound` | `propext, Quot.sound` |
| `vat_tier_gap`, `tax8_le_graduated`, `claimEight_rejected` | `propext, Quot.sound` |
| `check_complete`, `checkT_complete`, `check8_complete` | `propext, Classical.choice, Quot.sound` |
| the five `Loopholes.lean` theorems | `propext` |

All soundness results are constructive (no choice). The completeness proofs
use `Classical.choice` through decidability case splits; this is standard and
does not affect the soundness guarantee. No `sorryAx` anywhere.

## Mutation tests (guard necessity)

Each guard was deliberately broken in a scratch copy of the artifact; the
build then failed at exactly the theorem that depends on the guard. This is
automated by `tools/mutation_tests.py`: it first builds an unmutated control
copy, then deletes (or changes) one guard per throwaway copy and requires the
build to fail at the expected file. CI runs it after the kernel checks. It is
not part of `run_demo.sh`, to keep the demo fast; run it directly with
`python -X utf8 tools/mutation_tests.py` (about 2.5 minutes).

| Mutation | Breaking change | Observed failure |
|---|---|---|
| Statute guard | statute guard removed from the checker | the soundness proof fails; a forged schedule certificate is accepted |
| Tier guard | tier claim accepted without checking `classify` | three proofs fail (including `claimTier_rejected`); a tier-forged certificate is accepted |
| 8% rate | `tax8` rate changed 8 → 10 | the comparison proof (`tax8_le_graduated`) fails; worked examples are refuted |
| Election eligibility | eligibility conjunct deleted from `regimeOf` | `regimeOf_ineligible` fails; the boundary examples are refuted |

## Engine study 1 (`data/results.csv`, `data/summary.json`)

254 certificates judged **only** by the verified Lean checker `checkT`
(default regime). Python never re-implements the checker; its diagnosis
column is labeled UNVERIFIED. Ground truth: 32 stratified benchmark cases
agreed by independent Python and Lean (`tools/make_benchmark.py`).

| Engine | n | Accepted | Accept rate | Accepted with wrong total | Max overclaim (rejected) |
|---|---|---|---|---|---|
| E0_honest | 32 | 32 | 100% | 0 | 0 |
| F1_flat_top (flat 35%) | 32 | 0 | 0% | 0 | ₱759,900.00 |
| F2_untiered (ignores EOPT rates) | 32 | 21 | 65.6% | 0 | ₱462,525.00 |
| F3_year360 (360-day interest) | 32 | 8 | 25% | 0 | ₱91,341.66 |
| F4_half_up (rounding) | 32 | 19 | 59.4% | 0 | ₱0.01 |
| F5_train2018 (pre-2023 schedule) | 32 | 0 | 0% | 0 | ₱746,800.00 |
| F6_micro_le (micro read as ≤ ₱3M) | 32 | 30 | 93.8% | 0 | ₱0.00 |
| LLM sessions 1–3 (10 cases each) | 30 | 30 | 100% | 0 | 0 |

**0 false accepts**: every accepted certificate stated the correct total.
F6 is the instructive fault: micro and small share the 10%/6% rates, so its
totals are right everywhere; only the false *tier claim* at exactly
₱3,000,000 is rejected — the boundary theorem `vat_tier_gap` made flesh.
F4 shows the checker catches a one-centavo rounding difference.

Limits: the three LLM engines are fresh sessions of one assistant family.
Raw outputs: `data/llm_raw/`.

## Engine study 2 (`data/results8.csv`, `data/summary8.json`)

512 certificates judged **only** by the verified election-aware checker
`check8`. Ground truth: 64 rows (32 stratified cases × elected {false, true})
agreed by independent Python and Lean (`tools/make_benchmark8.py`); the build
fails unless all 64 agree. Eight engines (`tools/engines8.py`), 64 rows each.

| Engine | n | Accepted | Rejected | Accepted with wrong total | Max overclaim (rejected) |
|---|---|---|---|---|---|
| G0_honest | 64 | 64 | 0 | 0 | 0 |
| G1_eight_on_income | 64 | 55 | 9 | 0 | ₱0.00 |
| G2_no_exempt_floor | 64 | 55 | 9 | 0 | ₱23,200.00 |
| G3_ineligible_eight | 64 | 41 | 23 | 0 | ₱94,410,984.59 |
| G4_pct_double | 64 | 55 | 9 | 0 | ₱100,331.50 |
| G5_missing_pct | 64 | 9 | 55 | 0 | ₱0.00 |
| G6_rate10 | 64 | 55 | 9 | 0 | ₱61,313.70 |
| G7_penalty_wrong_base | 64 | 55 | 9 | 0 | ₱56,925.34 |

**0 false accepts.** The 8% branch runs only on the nine eligible-and-elected
rows (B01–B09), so regime-conditional faults (G1, G2, G4, G6, G7) hide on the
other 55 rows — the election analogue of F6's boundary subtlety. G3's 23
rejections are exactly the ineligible elections, caught by the regime conjunct
(`claimEight_rejected` made empirical). G7 has correct basic tax and regime but
a wrong penalty base; the surcharge conjunct catches it. G1 and G5 undercharge,
so their rejected overclaims are zero; the checker polices equality, not direction.

## Loophole study (`data/loophole_cases.csv`, `LOOPHOLE_FINDINGS.md`)

`tools/loopholes.py` constructs 11 exploiting certificates, submits them to
`checkT`/`check8`, and requires an independent Python implementation to agree
with Lean on every verdict and total (full agreement). The findings themselves
are kernel-checked in `Loopholes.lean`: L1 income above gross sales accepted;
L2 retroactive election saves ₱632,573.28; L3 one penalty cliff at ₱20M
(₱813,777.76 per centavo of gross end-to-end), ₱3M and ₱1B penalty-neutral;
L4 penalty-shelter crossover at income ₱910,000.00 (gs ₱3M), trap below;
L5 no prescriptive period, 100-years-late accepted. Guards are designed, not
implemented.

## Findings battery (`data/findings.csv`, `FINDINGS.md`)

`tools/findings.py` enumerates 274 propositions over the verified core,
renders them as Lean theorems, compiles them with the pinned toolchain, and
writes nothing unless every theorem is accepted and the axiom audit shows
only `propext`. Findings by family: equivalence 128 (32 default regime, 96
election regime), divergence 56, boundary 16, penalty cliff 18, election
crossover 20, identities 20, unguarded premises 16. The battery is not 274
loopholes; the `kind` column separates equivalences and divergences from
incentive structure and encoding gaps. Unlike the divergence proofs in
Han et al. (arXiv:2610.02792), which use `native_decide`, ours close by
kernel `decide`; every theorem is axiom-audited and the audit stays at
`propext`.

## Reproduce the studies

```bash
python -X utf8 tools/make_benchmark.py   # writes data/benchmark_cases.csv only if Python and Lean agree on all 32 rows
python -X utf8 tools/run_harness.py      # writes data/results.csv and data/summary.json
python -X utf8 tools/make_benchmark8.py  # 64 election truth rows, dual-agreed
python -X utf8 tools/engines8.py         # eight election-aware engines, 512 certificates
python -X utf8 tools/run_harness8.py     # writes data/results8.csv and data/summary8.json
python -X utf8 tools/loopholes.py        # writes data/loophole_cases.csv
python -X utf8 tools/findings.py        # 274 kernel-checked findings; writes data/findings.csv and FINDINGS.md
```

All scripts honor the `LEAN` environment override. Generated harness files
land in `lean/_harness/` (gitignored; see its README).

## What is NOT verified

- The specification's fidelity to Philippine law — no practitioner has
  signed the [review packet](docs/spec_review_packet.md).
- Behavior on real BIR assessments; the benchmarks are model-grounded.
- The 8% election's quarterly mechanics (annual flag only).
- The certificate premises: income realism, election timing and prescriptive
  period are unguarded inputs (L1, L2, L5); guards are designed, not implemented.