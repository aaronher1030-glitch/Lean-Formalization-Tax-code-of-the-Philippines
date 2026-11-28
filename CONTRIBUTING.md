# Contributing

This is an open, public-interest project. It is meant to be built and checked by anyone in the Philippines with a laptop or desktop and an internet connection — not only by people who already write Lean.

Everything measured here is reproducible from the repository: the Python tools use only the standard library, the data is plain CSV, and the statute text is in `data/ra8424.html`. A Lean installation is needed only for the proof files.

## The two keys

A claim about Philippine tax law needs two independent signatures:

1. **the kernel key** — the arithmetic or the proof checks out against the specification;
2. **the practitioner key** — a Philippine tax lawyer or CPA confirms that the specification says what the law says.

Most contributions supply one key. That is the point: a programmer can close the arithmetic without pretending to be a lawyer, and a lawyer can correct the reading without touching Lean. Do not present a single-key result as a legal conclusion.

## What you need

- A laptop or desktop, any recent operating system, and Python 3 (standard library only).
- An editor and a browser to read the BIR page and the statute.
- Optional: [elan](https://github.com/leanprover/elan) for the Lean files, pinned by `ph-tax-code-lean/lean-toolchain`. The build is small, needs no Mathlib and no GPU.
- Nothing here requires a fast machine or paid software. The whole repository works offline once cloned.

## Pick a work unit

The Code is split into section-sized units so a contribution can finish in an evening. The dependency frontier — which sections can be worked on now without waiting for another — is in [`NIRC_CLUSTER_GRAPH.md`](NIRC_CLUSTER_GRAPH.md), generated from `data/nirc_clusters.csv`. Pick one section, not a whole title.

Open an issue naming the NIRC section and what you intend to do. One section and one claim per pull request keeps review possible.

## Work that needs no Lean

| Task | Where | What counts as done |
|---|---|---|
| Read a section against the source | `data/ra8424.html` | Quote the text, list every undefined term it uses, and say which parts are computational |
| Add a boundary case | `tools/bir_calculator_check.py`, `data/benchmark_cases.csv` | The case fails before the fix and passes after; live-calculator cases must reproduce the live answer |
| Check a period table | `ANNEX_E` and `ANNEX_D` in `tools/bir_calculator_check.py` — both tranches are transcribed, see §4 of [`BIR_CALCULATOR_CROSSCHECK.md`](BIR_CALCULATOR_CROSSCHECK.md) | A second source for the fourteen 2018 bases RR 11-2018's illustrations do not print, or a dated list of differences when a table is amended |
| Verify a citation edge | `data/nirc_refs.csv`, `tools/cluster_graph.py` | A false edge is removed or a missing one added, with the quoted reference |
| Write a bug report from a finding | an issue | Reproduction steps, statute citation, expected and actual figures |
| Explain or translate a section | new Markdown beside the report | Plain-language summary in English, Filipino, Cebuano or Ilocano, checked by a second reader |
| Review a pull request | the changed files | You ran the commands and the claim matches its quoted source |
| Improve a data dictionary or a limit section | `README.md`, the reports | A reader can reproduce the number without asking a question |

## Work that needs Lean

```bash
elan toolchain install leanprover/lean4:v4.35.0
cd ph-tax-code-lean
bash lean/run_demo.sh          # exit 0, no sorry
```

Rules for proof changes: no `sorry`, no `native_decide`, keep the build at the pinned toolchain, and state the legal reading each definition assumes. If a proof needs a new assumption, say so in the PR body so the practitioner key can be asked for.

## Rules of evidence

- **Quote the source.** Every legal claim carries the section, the text, and the date or amendment it comes from. `data/ra8424.html` is the 1997 base text, a floor rather than current law; amendments must be cited separately.
- **The statute settles disagreements** — never the software, never the model, never the test suite. Do not tune a model until the numbers match.
- **Say which key a claim rests on.** "The kernel checks this" and "a practitioner confirmed this reading" are different sentences.
- **One home per measured number.** Generated results live in `data/*.csv`; the measured graph lives in `NIRC_CLUSTER_GRAPH.md`. Link to them instead of copying figures into prose, so a stale number cannot spread.
- **Mark readings as readings.** If a finding depends on how a form, a label or a regulation is interpreted, write that down next to the number.
- **No taxpayer data, no legal advice, no implied endorsement** by the BIR, BetterGov.ph or any agency.

## Before you open a pull request

```bash
python -X utf8 tools/cluster_graph.py          # deterministic; should not change unless you changed the graph
python -X utf8 tools/make_benchmark.py         # Python vs Lean ground truth
python -X utf8 tools/bir_calculator_check.py   # exits non-zero if the replay drifts from the live calculator
```

If a generated file changes, commit it in the same pull request and say why. If you only edited prose, the generated files should be untouched.

## Review, credit and licence

Every pull request gets one maintainer review. A change to a legal reading additionally needs a Philippine tax practitioner or CPA; until then the claim stays marked as a reading. Contributors are credited in the commit and in release notes, and the project is MIT-licensed (statute texts remain public documents of the Republic of the Philippines and the BIR).

Disagreement is useful: if a finding here is wrong, a dated issue with the statute quote is the most valuable contribution you can make.
