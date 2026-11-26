# Lean Formalization of the Philippine Tax Code

**A verified core of the Philippine National Internal Revenue Code (NIRC), with a proven certificate checker for untrusted tax engines.**

[![Lean 4](https://img.shields.io/badge/Lean-4.35.0-blue)](https://leanprover.github.io/lean4/)
[![Theorems](https://img.shields.io/badge/Theorems-59-blue)](ph-tax-code-lean/THEOREMS.md)
[![Sorry](https://img.shields.io/badge/sorry-0-success)](ph-tax-code-lean/STATUS.md)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](ph-tax-code-lean/LICENSE)

## Mission

Make Philippine tax computations auditable. Any engine — agency software, a
spreadsheet, or a large language model — may produce a line-by-line
*certificate* of an assessment, and a small, machine-proven checker accepts it
only if every line follows the statute. The checker is proven sound (accepted
means correct under the specification) and complete (honest means accepted),
and the repository measures what it catches when untrusted engines are wrong.

## What is formalized

Seven NIRC sections in their computational parts — each only in part. Full
detail in [`COVERAGE.md`](ph-tax-code-lean/COVERAGE.md).

| Area | NIRC sections | Lean file |
|---|---|---|
| Individual income tax schedule (TRAIN, 2023+) | §24(A)(2)(a) | `TaxSchedule.lean`, `TaxScheduleChecks.lean` |
| Penalties and VAT threshold | §248(A), §249, §109(CC), §236 | `GovernanceDemo.lean` |
| Certificate checker | engineering layer | `Certificate.lean` |
| Taxpayer tiers (EOPT) | §21(b) as amended by RA 11976 | `Tiers.lean` |
| 8% optional regime + percentage tax | §24(A)(2)(b), §116 | `Opt8.lean` |
| Loophole findings | derived from the core | `Loopholes.lean` |

| Metric | Value |
|---|---|
| Lean files / lines | 7 / 1,024 |
| Theorems & lemmas | 59 |
| Kernel-checked examples | 82 |
| Remaining `sorry` | **0** |
| Engine studies | 766 certificates, 16 engines, 0 false accepts |
| Loophole findings | 5, kernel-checked |

## Repository layout

| Path | Contents |
|---|---|
| [`ph-tax-code-lean/`](ph-tax-code-lean/) | **The project itself** — Lean proofs, tools, data, paper, CI. Start here. |
| [`lean/`](lean/) | Working copy of the Lean formalization |
| [`tools/`](tools/) | Python harness, benchmark generators, findings/loophole analysis, figure and docx builders |
| [`data/`](data/) | NIRC section index, benchmark cases, results, engine certificates, raw LLM runs |
| [`msp/`](msp/) | MSPR3-2026 abstract submissions and templates |
| [`docs/`](docs/) | Specification review packet |
| [`figures/`](figures/), [`preview*/`](previews/) | Plots and rendered page previews |
| [`bettergovtarlacph-publish/`](bettergovtarlacph-publish/) | Better Concepcion web project (TypeScript/Vite) |
| [`discord-mcp-lite/`](discord-mcp-lite/) | Discord MCP server |
| [`_git-bundles/`](_git-bundles/) | Full commit history of the three nested repositories |

Root-level papers: `Verified_Core_Tax_Governance_PH` (`.md`/`.pdf`/`.docx`),
`Feasibility_Study_Lean_Governance_PH`, `DEEP_RESEARCH_LEAN_TAX_GOVERNANCE.md`,
`DEEP_RESEARCH_VENUES_GAPS_HURDLES.md`, `REVIEWER_RED_TEAM.md`,
`FINDINGS.md`, `LOOPHOLE_FINDINGS.md`, `OVERVIEW_AND_BETTERGOV_PROPOSAL.md`.

## Quick start

Lean 4.35.0 is pinned by [`ph-tax-code-lean/lean-toolchain`](ph-tax-code-lean/lean-toolchain).
No Mathlib, no Lake — only Lean's core library.

```bash
elan toolchain install leanprover/lean4:v4.35.0
cd ph-tax-code-lean
bash lean/run_demo.sh          # builds all seven files; exit 0, no sorry
```

Reproduce the benchmarks and engine studies (Python 3, stdlib only):

```bash
python -X utf8 tools/make_benchmark.py    # dual ground truth: Python vs Lean
python -X utf8 tools/run_harness.py       # 254 certificates judged by checkT
python -X utf8 tools/engines8.py          # eight election-aware engines
python -X utf8 tools/run_harness8.py      # 512 certificates judged by check8
python -X utf8 tools/loopholes.py         # exploiting certificates, cross-checked
python -X utf8 tools/findings.py          # 274 kernel-checked findings
```

## Honesty notes

1. **A proof is not a legal review.** The theorems show the code matches our
   reading of the law, not that the reading is correct. The specification
   awaits a Philippine tax practitioner; the review packet is unsigned.
2. **Soundness is relative to the specification.** The first specification was
   legally incomplete (it omitted EOPT concessions) and the checker accepted
   wrong totals until the spec was repaired. That lesson is the paper's central
   finding.
3. **The inputs are not guarded.** The checkers accept inputs the statute would
   not allow (income above gross sales, retroactive elections, assessments a
   century late): the arithmetic is verified, the premises are not.
4. **Ground truth is the model**, not BIR-processed returns.
5. This work is a model, **not legal advice**.

## Backup and restore

This repository is also a full working archive of the project. Large binary
directories that git cannot hold (GitHub caps a single git file at 100 MB) are
published as release assets. See **[BACKUP.md](BACKUP.md)** for the complete
inventory and restore commands.

## Citation

*How Strong Is a Verified Tax Code? A Critical Study of Formalizing Philippine
Tax Rules in Lean 4, with a Proven Certificate Checker* (Hernandez, 2026).
Metadata in [`CITATION.cff`](ph-tax-code-lean/CITATION.cff).

## License

MIT — see [`LICENSE`](ph-tax-code-lean/LICENSE). Statute texts under
`data/sources/` are public documents of the Republic of the Philippines and the BIR.
