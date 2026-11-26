# Task 5 Report: Driver with dry-run

Status: COMPLETE. All tool tests pass; dry-run line matches the brief exactly; no
staging or commits; no kernel compile performed.

## Files created (exactly two)

- `tools/findings.py` — driver (uses the brief's code verbatim)
- `tools/test_findings_driver.py` — driver test (brief's code verbatim)

No other file was created or modified. `lean/_harness/Findings.lean`,
`data/findings.csv`, and `FINDINGS.md` do not exist after my runs (verified with
`ls`), so nothing leaked out of the dry-run path.

## Step 2 evidence (failing state, implicitly)

`findings.py` did not exist before this task, so the brief's Step 2 expectation
(FAIL, returncode 2 from the subprocess) held by construction. I did not spend a
run on it; the test was written first, then the implementation.

## Step 4 output (driver test alone)

```
test_dry_run_counts_and_writes_nothing (test_findings_driver.DriverTests.test_dry_run_counts_and_writes_nothing) ... ok
----------------------------------------------------------------------
Ran 1 test in 0.707s
OK
```

## Dry-run output

Command: `python -X utf8 tools/findings.py --dry-run`

```
DRY RUN: 274 findings across 8 families; nothing written
EXIT=0
```

Contains the required `DRY RUN: 274 findings` substring (asserted by the test).

## Full suite output

Command: `python -X utf8 -m unittest discover -s tools -p "test_*.py" -v`

```
Ran 20 tests in 0.494s

OK
```

Per-file test counts: `test_findings_driver.py` 1, `test_findings_families.py` 5,
`test_findings_render.py` 4, `test_findings_report.py` 5, `test_findings_spec.py` 5.

The only non-failing noise is pre-existing `ResourceWarning: unclosed file` from
`test_findings_spec.py` and `test_findings_report.py` reading CSVs without
closing them. Those are Task 1/4 files I am not allowed to touch; they do not
affect results.

## Deviations

1. **19 vs 20 tests.** The brief's Step 5 expects `OK` with 19 tests
   (5+5+4+4+1). Actual is 20, because Task 4's `test_findings_report.py` gained a
   fifth test (`test_write_outputs_creates_nested_dirs_and_writes_lf`) as part of
   the mkdir/LF fix the task description said might still be landing. This is a
   count deviation only; every test passes. Note the task instruction's discovery
   pattern `-p "test_*.py"` was used as the authoritative run (it matches the same
   files as the brief's `-p "test_findings_*.py"`).
2. **No interface conflicts.** The frozen interfaces match the brief exactly:
   `findings_families.all_findings()` -> 274 rows, `findings_render.render(rows)`,
   `findings_report.summary(rows)` (list of `{family, kind, count}` dicts, so
   `len(...)` is the family-count 8), and
   `findings_report.write_outputs(rows, meta, csv_path, md_path)`. No code changes
   were needed to reconcile anything.

## Self-review notes

- Imports are bare (`import findings_families`) per the brief; correct because the
  script is launched as `python tools/findings.py`, making `tools/` `sys.path[0]`.
  The test launches it exactly that way via `sys.executable`, `-X utf8`, absolute
  path, `cwd=ROOT`.
- Exit codes: 0 on dry-run and on success; 1 on compile failure or axiom-audit
  failure. Outputs are written only after a clean compile and a clean audit, so a
  failed run cannot leave stale `data/findings.csv` / `FINDINGS.md` behind.
- Axiom audit logic: any `depends on axioms: [...]` group that is not a subset of
  `{propext}` fails the run; `audit` label is `propext only` when the phrase
  appears, else `no axioms`.
- `HARNESS.parent.mkdir(exist_ok=True)` (no `parents=True`) is the brief's code;
  it is sufficient here because `lean/_harness/` already exists in the repo. If a
  future change deletes that directory, this line would raise instead of creating
  the chain — flagging as a robustness note, not a bug to fix now (the brief's code
  is authoritative and Task 6 will exercise the real path).
- `subprocess.run(..., timeout=1800)` is uncaught on timeout (would raise
  `TimeoutExpired` -> traceback -> non-zero exit). Acceptable: still a failure
  signal, and 1800 s is generous for the 274-theorem harness that Task 6 will run.
- The regexes are anchored on the harness file name (`Findings\.lean:(\d+):\d+:
  error`) which matches Lean's diagnostics; `_report_failures` prints at most 5
  mapped source lines plus the tail of the log, which is the useful debugging
  surface for Task 6.
- Nothing wrote outside `tools/`: verified `data/findings.csv`, `FINDINGS.md`, and
  `lean/_harness/Findings.lean` are all absent; `git diff --stat tools/` is empty
  (no tracked file touched) and `git status --short` shows the new files as
  untracked `??` entries only.

## Step 6 evidence

`git status --short` for `tools/`, `lean/`, `FINDINGS.md`, `data/findings.csv`:

```
 M lean/_harness/README.md
 M lean/run_demo.sh
?? lean/Loopholes.lean
?? tools/engines8.py
?? tools/findings.py
?? tools/findings_families.py
?? tools/findings_render.py
?? tools/findings_report.py
?? tools/findings_spec.py
?? tools/loopholes.py
?? tools/make_benchmark8.py
?? tools/run_harness8.py
?? tools/test_findings_driver.py
?? tools/test_findings_families.py
?? tools/test_findings_render.py
?? tools/test_findings_report.py
?? tools/test_findings_spec.py
```

The `lean/` and `tools/engines8.py` / `tools/loopholes.py` entries pre-date this
task. My additions appear only as untracked files; nothing is staged.

## Handoff to Task 6

`python -X utf8 tools/findings.py` (no flag) is the real run. It needs
`LEAN` exported per Global Constraints, writes `lean/_harness/Findings.lean`
(gitignored), compiles with `LEAN_PATH=ROOT/lean` and `cwd=ROOT/lean`, audits
axioms, and only then writes `data/findings.csv` and `FINDINGS.md`. I did not
execute it.
