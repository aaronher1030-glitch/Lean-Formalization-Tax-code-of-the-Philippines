# Philippine Tax Code Formalization in Lean 4

**A verified core of the Philippine National Internal Revenue Code (NIRC), with a proven certificate checker for untrusted tax engines**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Lean 4](https://img.shields.io/badge/Lean-4.35.0-blue)](https://leanprover.github.io/lean4/)
[![Theorems](https://img.shields.io/badge/Theorems-59-blue)](THEOREMS.md)
[![Examples](https://img.shields.io/badge/Kernel--checked_examples-82-brightgreen)](STATUS.md)
[![Sorry](https://img.shields.io/badge/sorry-0-success)](STATUS.md)

## Mission

Make Philippine tax computations auditable: any engine — agency software, a
spreadsheet, or a large language model — may produce a line-by-line
*certificate* of an assessment, and a small, machine-proven checker accepts it
only if every line follows the statute. Prove the checker sound (accepted
means correct under the specification) and complete (honest means accepted),
and measure what it catches when untrusted engines are wrong.

This repository is the Philippine companion to
[`kavanaghpatrick/us-tax-code-lean`](https://github.com/kavanaghpatrick/us-tax-code-lean)
(US Title 26 in Lean 4, AI-generated via Harmonic Aristotle). The approaches
are complementary: that project pursues breadth (765 sections, self-reported,
17 remaining `sorry`); this one pursues a small core with **zero unproven
steps**, proven checker guards, and a measured engine study.

## Current Status (18 November 2026)

### Coverage Summary

**Seven NIRC sections formalized in their computational parts** — about 2.4%
of the Code's 292 sections, each only in part. See [COVERAGE.md](COVERAGE.md).

| Area | NIRC sections | Lean file | Notes |
|---|---|---|---|
| **Individual income tax schedule (TRAIN, 2023+)** | §24(A)(2)(a) | `TaxSchedule.lean`, `TaxScheduleChecks.lean` | five brackets, monotonicity, 30 checked values |
| **Penalties and VAT threshold** | §248(A), §249, §109(CC), §236 | `GovernanceDemo.lean` | surcharge, interest, exemption/registration complements |
| **Certificate checker** | (engineering layer) | `Certificate.lean` | soundness, completeness, tampering examples |
| **Taxpayer tiers (EOPT)** | §21(b) as amended by RA 11976 | `Tiers.lean` | 10%/6% reduced rates, tier guard, ₱3M boundary theorem |
| **8% optional regime + percentage tax** | §24(A)(2)(b), §116 | `Opt8.lean` | election guard, ineligible-election rejection, universal comparison |

### Project Statistics

| Metric | Value |
|---|---|
| **Lean files** | 7 |
| **Lines of Lean** | 1,024 |
| **Theorems & lemmas** | 59 ([list](THEOREMS.md)) |
| **Kernel-checked examples** | 82 |
| **Remaining `sorry`** | 0 |
| **Mutation tests** | 4, automated in `tools/mutation_tests.py` (statute guard, tier guard, 8% rate, election eligibility); CI-gated |
| **Clean rebuild** | ~57 s warm on a Windows laptop, core library only |
| **Engine studies** | 766 certificates, 16 engines across both checkers, 0 false accepts |
| **Findings battery** | 274 kernel-checked propositions generated per run ([FINDINGS.md](FINDINGS.md)) |
| **Loophole findings** | 5, derived from the core itself, kernel-checked ([record](LOOPHOLE_FINDINGS.md)) |

All figures are re-runnable: `bash lean/run_demo.sh` exits 0 with no error,
warning or `sorry` line. Details and the axiom audit: [STATUS.md](STATUS.md).

### Key Achievements

- **Proven checkers, three generations**: `check`, `checkT`, `check8`, each
  sound and complete, each guard mutation-proven necessary.
- **A specified repair, not a silent patch**: the first model omitted RA 11976's
  micro/small concessions; the flaw is documented, the repair proven
  conservative, and the boundary theorem `vat_tier_gap` pins the one peso-value
  where two statutes disagree.
- **A measured study, twice**: seven seeded-fault engines plus three fresh LLM
  sessions computing by hand against `checkT` (254 certificates), then eight
  engines against the election-aware `check8` (512 certificates); the verified
  checkers are the only judges; the subtlest faults pass 30 of 32 boundary
  cases and 55 of 64 election rows respectively, and are caught only by the
  tier and regime guards.
- **A choice-justifying certificate**: under the 8% election the certificate
  must justify the regime itself; an ineligible election is rejected even when
  every amount is recomputed consistently (`claimEight_rejected`).
- **The core audits itself**: five loophole findings derived from the verified
  definitions, not the literature — missing income-realism, election-timing
  and prescription guards; one penalty cliff at ₱20M; and an income crossover
  where the 8% election turns from penalty shelter into penalty trap. Each is
  kernel-checked in `Loopholes.lean` and cross-checked by `tools/loopholes.py`.

### Major Gaps

| Area | Status |
|---|---|
| Legal review of the specification | **Not performed.** [Review packet](docs/spec_review_packet.md) ready, unsigned |
| Deductions, corporate tax, mixed-income earners | Not modeled |
| Quarterly mechanics of the 8% election | Not modeled (annual election flag only); the cost of the unguarded flag is demonstrated in [LOOPHOLE_FINDINGS.md](LOOPHOLE_FINDINGS.md) L2 |
| Guards for the loophole gaps (income realism, election timing, prescription) | Designed, not implemented; would change the checkers' soundness statements |
| Benchmark grounded in BIR-processed returns | Not yet (model-grounded, dual implementation) |

## Architecture

```
lean/                  # the verified core: seven Lean files, core library only
  TaxSchedule.lean     # TRAIN bracket schedule + monotonicity
  TaxScheduleChecks.lean  # 20 kernel-checked values
  GovernanceDemo.lean  # penalties, VAT threshold, totals
  Certificate.lean     # Cert, check, soundness/completeness
  Tiers.lean           # RA 11976 tiers, checkT, boundary theorem
  Opt8.lean            # 8% election, check8, comparison theorem
  Loopholes.lean       # five loophole findings, kernel-checked
  run_demo.sh          # builds and checks everything
  _harness/            # generated harness files (see its README)
tools/                 # benchmarks, engines, harnesses, loophole tool,
                       # findings battery, link checker, docx rendering
data/                  # benchmark cases (both studies), engine certificates,
                       # results, loophole cases, raw LLM sessions, sources
paper/                 # the research paper: Markdown, DOCX, PDF
  figures/             # paper figures
docs/                  # review packet, deep-research notes, design spec
.github/workflows/     # CI: Lean build and Python tests
COVERAGE.md STATUS.md THEOREMS.md ROADMAP.md LOOPHOLE_FINDINGS.md
FINDINGS.md CITATION.cff CONTRIBUTING.md
```

## Core Types

```lean
-- Amounts are centavos as natural numbers; subtraction truncates at zero,
-- so a bracket slice is automatically 0 below its bracket.
def slice (t lo hi : Nat) : Nat := min (t - lo) (hi - lo)

-- The 8% election: eligibility is the VAT comparison (<=), not the micro
-- tier's (<); exactly P3,000,000 qualifies and is small, not micro.
def regimeOf (elected : Bool) (gs : Nat) : Regime :=
  if elected && eligible8 gs then .eight else .graduated

theorem check8_sound {c : Cert8} (h : check8 c = true) :
    c.total = totalDueT (classify c.grossSales)
      (basicTax (regimeOf c.elected c.grossSales) c.grossSales c.income) c.daysLate
```

## Quick Start

Prerequisites: Lean 4.35.0 (the `lean-toolchain` file pins it). No Mathlib, no
Lake — the artifact uses only Lean's core library.

```bash
# Option A: elan installs the pinned toolchain
elan toolchain install leanprover/lean4:v4.35.0
export LEAN="$(elan which lean)"

# Option B: a downloaded Lean 4.35.0 distribution
export LEAN=/path/to/lean-4.35.0/bin/lean     # lean.exe on Windows

bash lean/run_demo.sh        # builds all seven files; exit 0, no sorry
```

Reproduce the benchmarks and engine studies (Python 3, stdlib only):

```bash
python -X utf8 tools/make_benchmark.py   # dual ground truth: Python vs Lean
python -X utf8 tools/run_harness.py      # 254 certificates judged by checkT
python -X utf8 tools/make_benchmark8.py  # 64 election truth rows, dual-agreed
python -X utf8 tools/engines8.py         # eight election-aware engines
python -X utf8 tools/run_harness8.py     # 512 certificates judged by check8
python -X utf8 tools/loopholes.py        # 11 exploiting certificates, cross-checked
python -X utf8 tools/findings.py   # 274 kernel-checked findings; writes data/findings.csv and FINDINGS.md
python -X utf8 tools/mutation_tests.py  # each guard deleted in a copy; build must fail
```

Optional paper/figure tooling: `pip install -r requirements.txt`, then
`tools/make_figures.py` and `tools/md_to_docx.py`. To rebuild the paper
from source:

```bash
python -X utf8 tools/md_to_docx.py paper/Verified_Core_Tax_Governance_PH.md \
  paper/Verified_Core_Tax_Governance_PH.docx
```

## Honesty Notes

1. **A proof is not a legal review.** The theorems show the code matches our
   reading of the law, not that the reading is correct. The specification
   awaits a Philippine tax practitioner; the packet is unsigned.
2. **Soundness is relative to the specification.** Our first specification was
   legally incomplete (omitted EOPT concessions); the checker happily accepted
   the wrong totals until the spec was repaired. That lesson is the paper's
   central finding, not a footnote.
3. **Both checkers are now measured, but the inputs are not guarded.** `check8`
   was measured against eight engines (512 certificates, 0 false accepts).
   Separately, `Loopholes.lean` shows the checkers accept inputs the statute
   would not allow (income above gross sales, retroactive elections, assessments
   a century late): the arithmetic is verified, the premises are not. Guards are
   designed in `LOOPHOLE_FINDINGS.md` but not implemented.
4. **The LLM engines are self-referential**: three sessions of the same
   assistant family as the research orchestration, on a task far smaller than
   a real return. 30/30 characterizes that regime only.
5. **Ground truth is the model.** The benchmark validates engines against the
   verified specification, not against BIR-processed returns.
6. This work is a model, **not legal advice**.

## Citation

If you use this artifact, please cite the accompanying paper:
*How Strong Is a Verified Tax Code? A Critical Study of Formalizing Philippine
Tax Rules in Lean 4, with a Proven Certificate Checker* (Hernandez, 2026),
included in this repository as `paper/Verified_Core_Tax_Governance_PH.pdf`.
Machine-readable metadata is in [CITATION.cff](CITATION.cff).

## License

MIT — see [LICENSE](LICENSE). Statute texts archived under `data/sources/`
are public documents of the Republic of the Philippines and of the BIR.