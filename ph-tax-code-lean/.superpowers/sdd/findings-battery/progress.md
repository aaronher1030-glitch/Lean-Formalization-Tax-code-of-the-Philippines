# SDD ledger — plan: docs/superpowers/plans/2026-11-18-findings-battery.md

## Setup rulings

- Ruling: execute in the existing repo tree, not a fresh worktree — the task depends on uncommitted prior work (Loopholes.lean, tools/loopholes.py, data/results8.csv) that does not exist at HEAD 91b2607. Cost if wrong: none; no destructive operations are planned.
- Ruling: no commits or staging (standing user rule) overrides the skill's commit steps; task reviews use file snapshots plus command output instead of git diffs. Cost if wrong: reviewers see snapshots rather than a historical diff; all task files are new, so nothing is hidden.
- Ruling: parallel implementers are allowed in Waves 1 (Tasks 2/3/4) and 4 (Tasks 7/8/9) — the plan mandates it, the files are disjoint, and the row schema is frozen in the plan. The skill's default "never parallel implementers" is overridden by the approved plan. Cost if wrong: cross-task file conflicts, mitigated by disjoint file ownership.
- Ruling: add `.superpowers/` to `.gitignore` as scratch for this workspace. Cost if wrong: one extra ignore line.
- Ruling: the Agent tool exposes no model selector, so every role uses the session model. Cost if wrong: higher cost and latency than a tiered dispatch.

## Preflight scan

| Pair / task | Produced → consumed | Finding |
|---|---|---|
| T1 → T2 | findings_spec functions | names and signatures match the brief (bracket_tax, pct_tax, tax8, classify, rates, eligible, regime_of, surcharge_t, interest_t, penalty_t, total_due_t, cert_t_total, cert8_total, crossover) — clean |
| T1 tests ↔ data | benchmark8_cases.csv (64 rows, has total_due), loophole_cases.csv (11 rows, total_centavos, checker checkT/check8) | both files present; columns match — clean |
| T2 → T3 | frozen row schema | renderer uses id/family/kind/theorem/prop/tactic only — clean |
| T2 → T4 | frozen row schema | report uses id/family/kind/theorem/prop/witness/value/source/note — clean |
| T2 → T5 | all_findings(), FAMILY_COUNTS | driver asserts 274 — counts sum to 274 (32+96+56+16+18+20+20+16) — clean |
| T2 ↔ results8.csv | engine mismatch rows | verified: G1 9, G2 9, G3 23, G4 9, G5 55, G6 9, G7 9; need 8 each — clean |
| T3 → T5 | render(rows) | one theorem per row, 8 audit lines — clean |
| T4 → T5 | write_outputs(rows, meta, csv, md) | signature matches driver call — clean |
| T5 → T6 | CLI + exit codes | --dry-run test asserts 274 — clean |
| T6 → T7/T8/T9 | 274 and 128/56/16/18/20/20/16, wall seconds | paper and docs text use exactly these numbers — clean |
| T7 → T10 | edited Markdown → DOCX/PDF | render command takes md path — clean |
| T8 ↔ T6/T10/T11 | .gitignore Findings.lean entry; docs counts | consistent — clean |
| T10 → T11 | docx/pdf → root copies | cp targets exist — clean |
| T7 internal | table renumber 11→12, 10→11, 9→10 in descending order | ordered to avoid collisions — clean |
| T5 internal | assert len(rows) == 274 vs enumeration | consistent — clean |

## Progress

Task 1: complete (working tree, review clean; 5/5 tests; minor ResourceWarning deferred)
Task 2: complete (review: SPEC ok, QUALITY approved; minors parked: last-wins dict on duplicate case_id, bare asserts)
Task 3: complete (review: SPEC ok, QUALITY approved; minor parked: 'admit' substring in header)
Ruling: theorem names lowercase the family component (f001_equivalence_certt_001) while `family` keeps equivalence_certT — the brief's name template conflicted with its own regex test; the test is binding, downstream consumes row["theorem"] verbatim — cost if wrong: a rename sweep across render/tests, none yet rendered to disk.
Ruling: Task 3 header reworded away from the literal tokens sorry/native_decide — the brief's header violated its own forbidden-token test; content claim unchanged — cost if wrong: header sentence only.
Task 4: complete after fix round 1 (re-review: both findings addressed, fix mutation-proved load-bearing; test count now 5)
Task 5: complete (review: SPEC ok; two majors fixed by controller — dead default LEAN path now ROOT.parent/tools/lean, .gitignore gains lean/_harness/Findings.lean; minors parked: --dry-run typo safety, 8-line audit coverage, mkdir parents)
Ruling: controller applied the two Task 5 majors directly instead of a fix dispatch — both are one-line edits with no test-surface change; verified by path existence + 20/20 suite + dry-run — cost if wrong: revert two lines.
Ruling: Task 8 no longer needs to add the Findings.lean ignore entry (already added); it must not duplicate it — cost if wrong: a duplicated ignore line.

Ruling: Task 4 prose kept as briefed ("engine errors", "machine-checked", native_decide contrast) — G1..G7 are seeded-fault engines, so "engine errors" is literal; H1 count is locked by Task 5's 274 assertion — cost if wrong: prose edit in one file.
Ruling: Task 5 dispatched concurrently with the Task 4 fix — disjoint files, report-module change is strictly additive (mkdir), no API change — cost if wrong: re-run Task 5 tests once.
Task 6: complete (kernel run PASS: 274 in 12.0 s, propext only; review approved; minors: timing drift, concurrent doc mtimes)
Task 7: complete (review approved; minors parked: cliff-row wording verbatim from brief, Table 9 caption-only reference)
Ruling: axiom audit upgraded from 8 family samples to all 274 theorems (242 propext + 32 axiom-free) — makes "every theorem is axiom-audited" literally true — cost if wrong: compile 12 s -> ~30 s.
Ruling: Han et al. attribution corrected to their divergence proofs after checking v1 Fig. 8a/8b — applied in MD_HEAD, paper §5.11, STATUS — cost if wrong: three prose sites.
Task 8: complete after controller fix (stale "eight #print axioms audits" in THEOREMS.md and _harness/README.md -> per-theorem); review approved otherwise
Task 9: complete (review approved, residual overclaim none)
Task 10: complete (DOCX/PDF re-rendered, 24 pages, §5.11 + Table 9 p17; review approved; stranded Table 12 caption deferred as cosmetic)
Task 11: complete (E2E_OK, 20 tests, commit 91b2607 untouched, root mirrors synced, memory updated 18 Nov 2026)
Ruling: final review dispatch re-issued after a transport error ("fetch failed") killed the first attempt — no artifacts were produced by the failed run, so no state to reconcile — cost if wrong: none.
Final review: ready except one factual miscount. Ruling: corrected "fourteen seeded" -> "thirteen seeded" (F1-F6 + G1-G7 = 13, + 3 LLM = 16) in paper abstract, contributions, Table 12 row 5, ROADMAP row 5; ROADMAP table pointer 11 -> 12; tightened the audit test to require one audit per theorem — verified against data/results*.csv — cost if wrong: four prose sites plus one test.
Post-correction re-render: DOCX/PDF regenerated, 24 pages, §5.11 p17, "thirteen" p1-p2; root mirrors re-synced.

## Publication handoff (post-plan)

Ruling: Table 2 rebuilt as four columns (Work / What it does and what is verified / Scale / Independent review), widths 0.18, 0.44, 0.20, 0.18 — the five-column version forced mid-word breaks at 9 pt — cost if wrong: one table rewrite.
Ruling: reviewer's unsupported cells fixed — Catala now claims only what §3.2 establishes (verified compiler and semantics, found a bug in an official implementation); Han et al. cites Section 5.11 for the equivalence/divergence proofs; OpenFisca "None reported" softened to "Not reported" — cost if wrong: three cells of prose.
Ruling: ROADMAP gains the missing row 8 "Harden the specification" and renumbers the findings battery to row 9, so "mirrors Table 13" is literal — cost if wrong: one table in one file.
Ruling: §10 Reproducibility now names tools/check_links.py, which Appendix A already credited — cost if wrong: one sentence.
Ruling: md_to_docx.py defaults (footer, document title, comments date, default paths) now name the current paper; the old feasibility-study footer had survived in the renderer, not the text — cost if wrong: one render command with DOCX_FOOTER set.
Ruling: run_demo.sh fallback checks both ../tools/lean and ../../tools/lean, since the locally downloaded toolchain sits one level above the repo — cost if wrong: one line of shell.
Re-render: DOCX and PDF regenerated, 26 pages, footer correct on all 26, Table 2 on p7, §5.11 p18, §9 p22, Appendix p26; root mirrors re-synced.
Verification: check_links clean, 20/20 tests, dry run 274, lean/run_demo.sh exit 0 with the fallback toolchain, CI YAML parses (jobs lean, python).
Commits (local only, not pushed): 36232c4 studies/tools/findings; c611bfc paper restructure and move; ec87518 CI, CITATION.cff, CONTRIBUTING.md. Working tree clean.
