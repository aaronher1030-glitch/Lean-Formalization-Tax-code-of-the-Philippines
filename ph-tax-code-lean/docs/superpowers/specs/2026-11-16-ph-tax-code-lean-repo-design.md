# Design: ph-tax-code-lean repository

Date: 2026-11-16 · Status: approved by the user ("yes") · Author: assistant,
for Aaron Y. Hernandez

## Request and resolved scope

Original request: "search for the github repo of the original research on
lean tax of the US, make a similar one for that." Two clarification rounds
resolved it:

- **Deliverable scope:** a repository for *our Philippine project*, mirroring
  the layout and README conventions of
  [`kavanaghpatrick/us-tax-code-lean`](https://github.com/kavanaghpatrick/us-tax-code-lean)
  (the US Title 26 formalization built with Harmonic Aristotle). No new tax
  formalization; the existing verified artifact is packaged, not extended.
- **Git scope:** local repository plus one initial commit inside a new
  curated `ph-tax-code-lean/` directory. **Nothing is published to GitHub.**
  (`gh` CLI and GitHub MCP are unavailable in this session anyway.)

## Reference layout (inspected via WebFetch, 2026-11-16)

Kavanagh's repo: MIT license, Lean 4.14.0, root status-document wall
(COVERAGE.md, STATUS.md, THEOREMS.md, ROADMAP.md, …), `src/` Lean tree,
`tools/` Python, `data/` scraped statutes, `docs/`, `lean-toolchain`,
`requirements.txt`, README with Mission / Current Status / Coverage /
Statistics / Achievements / Gaps / Architecture / Quick Start.

## Design decisions

1. **Curated copy, not the working directory.** The repo lives at
   `ph-tax-code-lean/` inside the workspace; the working directory keeps all
   scratch, previews, MSP submission material and toolchain binaries.
2. **Included:** six Lean files + `run_demo.sh`; six Python tools (engines,
   make_benchmark, run_harness, make_figures, md_to_docx, pin_refs); data
   (benchmark, results, summary, engine certificates, raw LLM sessions,
   statute sources, NIRC index, arxiv refs); two figures; docs (review
   packet, deep-research notes); the paper in md/docx/pdf.
3. **Excluded:** `msp/`, previews, feasibility drafts, `tools/lean/`
   (binaries), `tools/build_abstract.py`, `lean/_scratch/`, olean/ilean
   artifacts, `data/sample_40.csv`.
4. **Portability.** `lean-toolchain` pins `leanprover/lean4:v4.35.0`;
   `run_demo.sh`, `tools/run_harness.py` and `tools/make_benchmark.py` accept
   a `LEAN` environment override pointing at any Lean 4.35.0 executable.
   Generated harness files (`lean/_harness/Harness.lean`, `BenchCheck.lean`)
   are gitignored with an explanatory README; the tools regenerate them.
5. **Root docs from verified metrics only:** README.md, COVERAGE.md,
   STATUS.md, THEOREMS.md, ROADMAP.md. Every number re-counted from the
   sources before writing: 6 files / 859 lines / 54 theorems / 64 examples /
   0 sorry / 4 mutation tests / 7 NIRC sections ≈ 2.4% / 254 certificates /
   0 false accepts. Static shields.io badges; no CI badge (no CI yet).
6. **Honesty section in the README** (unreviewed specification; soundness
   relative to spec; engine study covers the default regime only; LLM
   engines are one model family; ground truth is model-grounded; not legal
   advice). STATUS.md records the axiom audit and mutation evidence.
7. **License:** MIT, copyright Aaron Y. Hernandez (mirrors the reference
   repo). Statute extracts remain public documents.
8. **Git:** `git init` in `ph-tax-code-lean/`, one initial commit including
   this spec; `git status` clean afterwards; no remote, no push.

## Verification plan

1. Run `lean/run_demo.sh` from the repo with `LEAN` pointing at the
   workspace toolchain; require exit 0, no error/warning/sorry lines; record
   wall time.
2. Re-count theorems (`theorem`/`private theorem`) and kernel-checked
   examples per file; confirm they match the docs (54 / 64).
3. `git init`, add all curated files, one commit, confirm clean status.

## Out of scope

Publishing to GitHub; new Lean development; changes to the submitted MSP
abstract; any modification of the working directory's existing files beyond
reading them.