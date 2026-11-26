# Task 8 report — repo docs and ignore rules

Repo root: `C:/Users/Ma Christine/Downloads/LEAN FORMALIZATION OF TAX CODE/ph-tax-code-lean`
Date: 18 November 2026. Nothing staged, committed or pushed.

## Edits per file

### `STATUS.md`
1. Inserted the verbatim section `## Findings battery (`data/findings.csv`, `FINDINGS.md`)`
   immediately before `## Reproduce the studies`.
2. Added one line to the reproduce block, after the loopholes line:
   `python -X utf8 tools/findings.py        # 274 kernel-checked findings; writes data/findings.csv and FINDINGS.md`

### `THEOREMS.md`
1. Appended `## Generated findings battery` after the honesty-notes bullets (EOF),
   verbatim from the brief.
2. Added one closing sentence after that block so the file carries a runnable
   command: "Reproduce with `python -X utf8 tools/findings.py` (`--dry-run`
   enumerates the 274 propositions without writing)." (see Deviations)

### `README.md`
1. Stats table: new row after the "Engine studies" row —
   `| **Findings battery** | 274 kernel-checked propositions generated per run ([FINDINGS.md](FINDINGS.md)) |`.
2. Quick start: added `python -X utf8 tools/findings.py   # 274 kernel-checked findings; writes data/findings.csv and FINDINGS.md`
   after the loopholes line.
3. Architecture tree: a `tools/` entry already existed with a different comment
   (`# benchmarks, engines, harnesses, loophole tool,` / `# figures, docx rendering`),
   so per the brief I appended `; findings.py` to that comment instead of adding a
   duplicate line. No second `tools/` line exists.

### `ROADMAP.md`
1. Added the verbatim executed row `| 8. Findings battery | ... | **Done.** Compiled
   and axiom-audited 18 Nov 2026; kind column prevents the count from reading as 274
   loopholes |` after row 7.
2. Added a one-sentence reproduce note under the table (same reason as THEOREMS.md).

### `.gitignore`
No change made: `lean/_harness/Findings.lean` was already present at line 12 under
the generated-harness block. Verified `grep -c "Findings" .gitignore` = 1; no
duplicate added.

### `lean/_harness/README.md`
Appended the verbatim `Findings.lean` paragraph (274 theorems, eight `#print axioms`
audits, gitignored, regenerated, writes gated on kernel acceptance + `propext`-only
audit).

## Verification

```
$ grep -c "274" STATUS.md THEOREMS.md README.md ROADMAP.md
STATUS.md:3  THEOREMS.md:2  README.md:2  ROADMAP.md:1
$ grep -c "python -X utf8 tools/findings.py" STATUS.md THEOREMS.md README.md ROADMAP.md
STATUS.md:1  THEOREMS.md:1  README.md:1  ROADMAP.md:1
$ grep -c "Findings" .gitignore
1
$ grep -n "Findings.lean" .gitignore lean/_harness/README.md THEOREMS.md
.gitignore:12  lean/_harness/README.md:28  THEOREMS.md:124
$ grep -n "| **Total** | **1,024** | **59** | **82** |" STATUS.md
33: (unchanged hand-written total row)
$ grep -n "766 certificates" README.md ROADMAP.md
README.md:53  ROADMAP.md:15 (both unchanged)
$ python -X utf8 tools/findings.py --dry-run
DRY RUN: 274 findings across 8 families; nothing written
$ git status --short STATUS.md THEOREMS.md README.md ROADMAP.md .gitignore lean/_harness/README.md
 M .gitignore
 M README.md
 M ROADMAP.md
 M STATUS.md
 M THEOREMS.md
 M lean/_harness/README.md
$ git diff --cached --name-only
(empty — nothing staged)
```

No doc now asserts a change to the 59 theorems, 82 examples, 1,024 lines or 766
certificates; the battery is presented as a separate generated layer of 274 with
the `kind` column and the explicit "not 274 loopholes" caveat (STATUS.md, ROADMAP.md).

## Deviations

1. `THEOREMS.md` and `ROADMAP.md` — the brief's verbatim text only names
   `tools/findings.py` rather than giving a runnable command, but the task
   requirement is that each of the four docs carry a reproduce command. I kept the
   verbatim blocks untouched and added one short adjacent sentence in each:
   `python -X utf8 tools/findings.py` with the `--dry-run` note.
2. `README.md` `tools/` tree line — followed the brief's conditional: appended
   `; findings.py` to the existing comment instead of inserting the suggested
   replacement line (which would have duplicated `tools/`).
3. `.gitignore` was not edited at all, because the required entry pre-existed.

## Self-review notes

- Section placement matches the brief: STATUS section sits between "Loophole study"
  and "Reproduce the studies"; THEOREMS material is after the honesty notes.
- Family arithmetic is consistent: 128 (32 + 96) + 56 + 16 + 18 + 20 + 20 + 16 = 274,
  and incentive 38 = penalty cliff 18 + election crossover 20.
- Statement accuracy checked against the tool: `--dry-run` reports exactly 274
  findings across 8 families and writes nothing.
- The diffs for these six files include older uncommitted hunks from Tasks 16/18
  (Loopholes study, check8 study) that were already in the working tree before this
  task; I only added the findings-battery hunks listed above. Untouched: source
  Lean files, tests, paper, `FINDINGS.md`, `data/`.
- All six files lack a trailing newline, a pre-existing repo-wide trait; I left the
  endings as they were rather than introduce inconsistent whitespace churn.
