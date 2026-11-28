# Lean Formalization of the Philippine Tax Code

**A verified core of the Philippine National Internal Revenue Code (NIRC), with a proven certificate checker for untrusted tax engines.**

[![Lean 4](https://img.shields.io/badge/Lean-4.35.0-blue)](https://leanprover.github.io/lean4/)
[![Theorems](https://img.shields.io/badge/Theorems-59-blue)](ph-tax-code-lean/THEOREMS.md)
[![Sorry](https://img.shields.io/badge/sorry-0-success)](ph-tax-code-lean/STATUS.md)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](ph-tax-code-lean/LICENSE)

---

## What this project actually is

The Philippine tax code is a long document written in prose. Software computes
taxes from it — payroll systems, the BIR's own calculator, spreadsheets, and now
large language models — and when the software is wrong, almost nobody can tell.
The taxpayer sees one number. The employer sees the same number. The law that
produced it is 4,000+ sections of text, and the arithmetic connecting the two is
buried in a program nobody outside the vendor can read.

This project does two things about that.

**First, it turns parts of the law into exact arithmetic that a machine can
check.** Seven NIRC sections in their computational parts are written in Lean 4,
a proof assistant: the individual income tax schedule, the penalties and VAT
threshold, taxpayer tiers, the 8% optional regime, and a few neighbours. Each
definition is a claim — "taxable compensation of ₱800,000 owes ₱102,500" — and
each claim is proved from the schedule rather than tested on samples. There are
**59 theorems and 82 kernel-checked examples, with zero `sorry`** (no unproven
steps left in).

**Second — and this is the part that scales — it builds a checker for other
people's arithmetic.** Any engine can be made to emit a line-by-line
*certificate* of how it reached a number: income, minus deductions, times a
rate, plus a base, and so on. A small checker, itself proved correct in Lean,
reads that certificate and accepts it only if every line follows the statute.

> **If you want the five-year-old version:** think of a cashier's receipt. You
> don't have to trust the cashier — you just add up the lines yourself. This
> project is the machine that adds up the lines of a tax computation, and it has
> been *proved* to add them up the way the law says. If the receipt doesn't add
> up, it says so. If it does add up, it says that too.

The checker is proved **sound** (if it accepts, the computation is correct under
the specification) and **complete** (if the computation is honest, it accepts).
Because the specification is written by humans reading the law, a second,
independent signature is required before anything is presented as a legal
conclusion — see [the two keys](#the-two-keys) below.

### Why it matters

The Bureau of Internal Revenue publishes exactly one public calculator, and it
computes withholding tax for employees earning purely compensation income, for
one payroll period. The parts where a wrong number is hardest for a taxpayer to
challenge — the 8% election, self-employed and mixed income, penalties and
interest, anything corporate — have no public calculator at all.

This repository is the first place where one of those computations can be
checked against an independent, machine-verified model, and where the Bureau's
running code has been replayed and compared line by line. That comparison found
**27 of 34 cases identical to the centavo and 7 divergences** — two arithmetic,
the rest readings of the form. It is reported in
[`BIR_CALCULATOR_CROSSCHECK.md`](BIR_CALCULATOR_CROSSCHECK.md) as a reproducible
research finding, **not** as an audit of the Bureau.

### The two keys

A claim about Philippine tax law needs two independent signatures:

1. **The kernel key.** The arithmetic checks out. A proof assistant verified it;
   you can re-run it on your own machine in about a minute.
2. **The practitioner key.** A Philippine tax lawyer or CPA confirms that the
   specification says what the law actually says.

Most contributions supply exactly one key, and that is by design: a programmer
can close the arithmetic without pretending to be a lawyer, and a lawyer can
correct the reading without ever touching Lean. No single-key result is
presented here as a legal conclusion. The practitioner review packet is
**unsigned** — that is the project's largest open item, and one of the most
useful things a contributor can help close.

---

## What is formalized

Seven NIRC sections in their computational parts — each only in part, about 2.4%
of the Code's 292 sections. Full detail in
[`COVERAGE.md`](ph-tax-code-lean/COVERAGE.md).

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

---

## How the rest of the Code is divided into pieces you can take

Formalizing 292 sections is not one project; it is roughly **927 section-sized
units**. Rather than divide them by title, this repository divides them by the
Code's own cross-reference graph — measured, not assumed. See
[`NIRC_CLUSTER_GRAPH.md`](NIRC_CLUSTER_GRAPH.md), regenerated by
`tools/cluster_graph.py`.

| Quantity | Value |
|---|---|
| Sections parsed | 292 |
| Section-level reference edges | 163 |
| Dependency clusters (strongly connected components) | 264 |
| Estimated work units, whole Code | ~927 |
| Clusters at depth 0 (nothing to wait for) | 208 of 264 |
| Clusters whose dependencies are all already merged — **ready now** | 55, about 321 units |
| Longest dependency chain | 7 clusters |

The headline result: **at section granularity the graph is sparse.** 260 of 264
clusters are a single section, and only 32 sections sit in a citation cycle.
There is no ordering reason to hold work back. What limits this project is
**review capacity, not dependency depth** — which is exactly why it is built to
be contributed to by many people at once.

`data/nirc_clusters.csv` lists every cluster with its depth, status, unit
estimate and dependencies. `data/nirc_sections.csv` has the per-section unit
counts. Pick a section, check its row, and you know whether you can start today.

---

## How to contribute

You do **not** need Lean, a fast machine, or paid software. Everything measured
here reproduces from a clone with Python 3 and its standard library; the statute
text ships in `data/ra8424.html`. The full guide, with the rules of evidence, is
in [`CONTRIBUTING.md`](CONTRIBUTING.md) — this is the short version.

**Claim a unit.** Open an issue naming the NIRC section and what you intend to
do. One section and one claim per pull request. Ready-now clusters are listed in
§4 of [`NIRC_CLUSTER_GRAPH.md`](NIRC_CLUSTER_GRAPH.md); the largest are §42
(Income from Sources Within the Philippines, 20 units) and §148 (Manufactured
Oils, 13 units).

### Three ways in, by what you already know

**1. You can read a statute (no code required).** Take one section from
`data/ra8424.html`, quote its text, list every term it uses without defining,
and say which parts are actually computational — which parts are arithmetic a
program could be held to. That single write-up is a complete, mergeable
contribution, and it is the input every later step needs.

**2. You can write a little Python (no Lean required).** Add a boundary case to
`tools/bir_calculator_check.py`: a case at a bracket floor, a centavo above it,
a zero, a ceiling. A case counts as done when it fails before the fix and passes
after, and when a live-calculator case reproduces the live answer. Or verify a
citation edge in `data/nirc_refs.csv` — remove a false one or add a missing one,
with the quoted reference. Or check a period table: both the 2023 and the
2018–2022 withholding tranches are transcribed and checked against independent
publications, and what is still wanted is a **practitioner's derivation** of
either table, or a dated list of differences when a table is amended.

**3. You write Lean, or you are a tax practitioner.** Proof changes follow three
rules: no `sorry`, no `native_decide`, and state the legal reading each
definition assumes. If a proof needs a new assumption, say so in the pull
request so the practitioner key can be requested. If you are the practitioner,
you do not need the code at all — the review packet in `docs/` is a structured
list of encoded claims, sources and open questions, and your disagreements with
it are the most valuable contribution the project can receive.

Also welcome: plain-language explanations of a section in English, Filipino,
Cebuano or Ilocano (checked by a second reader), bug reports built from a
finding (reproduction steps, statute citation, expected and actual figures), and
pull-request review — run the commands, check that the claim matches its quoted
source.

### Before you open a pull request

```bash
python -X utf8 tools/cluster_graph.py          # deterministic; unchanged unless you changed the graph
python -X utf8 tools/make_benchmark.py         # Python vs Lean dual ground truth
python -X utf8 tools/bir_calculator_check.py   # exits non-zero if the replay drifts
```

If a generated file under `data/` changes, commit it in the same pull request
and say why. If you only edited prose, the generated files should be untouched.
Every pull request gets one maintainer review; a change to a legal reading
additionally needs a Philippine tax practitioner or CPA, and until then the
claim stays marked as a reading.

---

## Repository layout

| Path | Contents |
|---|---|
| [`ph-tax-code-lean/`](ph-tax-code-lean/) | **The project itself** — Lean proofs, tools, data, paper, CI. Start here. |
| [`lean/`](lean/) | Working copy of the Lean formalization |
| [`tools/`](tools/) | Python harness, benchmark generators, findings/loophole analysis, graph and docx builders |
| [`data/`](data/) | NIRC section index, cluster graph, benchmark cases, results, engine certificates, raw LLM runs |
| [`msp/`](msp/) | MSPR3-2026 abstract submissions and templates |
| [`docs/`](docs/) | Specification review packet |
| [`CONTRIBUTING.md`](CONTRIBUTING.md) | How to take a work unit, with or without Lean |
| [`figures/`](figures/), [`previews/`](previews/) | Plots and rendered page previews |
| [`bettergovtarlacph-publish/`](bettergovtarlacph-publish/) | Better Concepcion web project (TypeScript/Vite) |
| [`discord-mcp-lite/`](discord-mcp-lite/) | Discord MCP server |
| [`_git-bundles/`](_git-bundles/) | Full commit history of the three nested repositories |

Root-level papers: `Verified_Core_Tax_Governance_PH` (`.md`/`.pdf`/`.docx`),
`Feasibility_Study_Lean_Governance_PH`,
`DEEP_RESEARCH_LEAN_TAX_GOVERNANCE.md`,
`DEEP_RESEARCH_VENUES_GAPS_HURDLES.md`,
[`DEEP_RESEARCH_DISTRIBUTED_TAX_FORMALIZATION.md`](DEEP_RESEARCH_DISTRIBUTED_TAX_FORMALIZATION.md)
(the cluster/desk design this repository implements),
[`NIRC_CLUSTER_GRAPH.md`](NIRC_CLUSTER_GRAPH.md) (the measured section graph),
[`BIR_CALCULATOR_CROSSCHECK.md`](BIR_CALCULATOR_CROSSCHECK.md) (the BIR
withholding calculator, replayed and compared against the model),
`REVIEWER_RED_TEAM.md`, `FINDINGS.md`, `LOOPHOLE_FINDINGS.md`,
[`OVERVIEW_AND_BETTERGOV_PROPOSAL.md`](OVERVIEW_AND_BETTERGOV_PROPOSAL.md).

---

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
python -X utf8 tools/cluster_graph.py     # NIRC citation graph -> cluster frontier
python -X utf8 tools/bir_calculator_check.py   # BIR calculator vs the model
```

---

## Honesty notes

Read these before citing anything here. They are the project's own limits,
stated in the order they are most likely to mislead a reader.

1. **A proof is not a legal review.** The theorems show the code matches our
   reading of the law, not that the reading is correct. The specification awaits
   a Philippine tax practitioner; the review packet is unsigned.
2. **Soundness is relative to the specification.** The first specification was
   legally incomplete (it omitted EOPT concessions) and the checker accepted
   wrong totals until the spec was repaired. That lesson is the paper's central
   finding: a checker is only as good as the reading it was proved against.
3. **The inputs are not guarded.** The checkers accept inputs the statute would
   not allow (income above gross sales, retroactive elections, assessments a
   century late): the arithmetic is verified, the premises are not.
4. **Ground truth is the model**, not BIR-processed returns.
5. **Coverage is small.** Seven sections in part, about 2.4% of the Code — a
   demonstrated method, not a finished formalization.
6. This work is a model, **not legal advice**, and implies no endorsement by the
   BIR, BetterGov.ph or any agency.

A proof that is wrong is still useful here: if a reading in this repository is
wrong, a dated issue quoting the statute is the most valuable contribution you
can make.

---

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
