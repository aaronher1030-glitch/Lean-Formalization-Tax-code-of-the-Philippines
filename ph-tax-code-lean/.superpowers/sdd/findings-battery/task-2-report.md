# Task 2 report — enumerate the 274 findings

## Files created

- `tools/findings_families.py` — implementation (`all_findings()`, `FAMILY_COUNTS`, `KIND`).
- `tools/test_findings_families.py` — tests, verbatim from the brief.
- `.superpowers/sdd/findings-battery/task-2-report.md` — this report.

No other files were modified. `tools/findings_spec.py` and `data/` are untouched
(`git status --short data/` shows the same pre-existing untracked entries as at
session start). Nothing was staged, committed, or pushed.

## Test command and output

Command (from repo root):

    python -X utf8 -m unittest discover -s tools -p "test_findings_families.py" -v

Step 2 (before implementation) failed as predicted:
`ModuleNotFoundError: No module named 'findings_families'`.

Step 4 (final):

    test_counts (test_findings_families.FamilyTests.test_counts) ... ok
    test_crossover_is_two_sided (test_findings_families.FamilyTests.test_crossover_is_two_sided) ... ok
    test_divergence_covers_seven_engines (test_findings_families.FamilyTests.test_divergence_covers_seven_engines) ... ok
    test_ids_and_names (test_findings_families.FamilyTests.test_ids_and_names) ... ok
    test_schema_and_kinds (test_findings_families.FamilyTests.test_schema_and_kinds) ... ok

    ----------------------------------------------------------------------
    Ran 5 tests in 0.016s

    OK

Regression check on the rest of `tools/` (`discover -p "test_*.py"`): 18 tests, OK.

## Row counts

Total: 274 rows, ids `F001`..`F274`, 274 unique theorem names.

| family | count | kind | tactic mix |
|---|---|---|---|
| equivalence_certT | 32 | equivalence | rfl 32 |
| equivalence_cert8 | 96 | equivalence | rfl 96 |
| divergence | 56 | divergence | decide 56 |
| boundary | 16 | boundary | rfl 12 / decide 4 |
| cliff | 18 | incentive | rfl 18 |
| crossover | 20 | incentive | decide 20 |
| monotone | 20 | identity | rfl 14 / decide 6 |
| gap | 16 | gap | decide 16 |

Totals by tactic: 174 `rfl`, 100 `decide`. By kind: equivalence 128, divergence 56,
incentive 38, identity 20, boundary 16, gap 16.

## Divergence coverage (per-engine mismatch rows in `data/results8.csv`)

    G1_eight_on_income      9
    G2_no_exempt_floor      9
    G3_ineligible_eight    23
    G4_pct_double           9
    G5_missing_pct         55
    G6_rate10               9
    G7_penalty_wrong_base   9

Every engine has at least 8, so the selection of 8 per engine (56 total) succeeded
on the first pass; the assertion `all(n == 8 ...)` was not reached in a failing
state and was not weakened. `G0_honest` is excluded by construction (never enters
`used`), and all 56 picked rows were confirmed to satisfy
`spec.cert8_total(gs, inc, days, elected) == true_total` (the in-function assertion
passed for every row).

## Deviations from the brief's verbatim code

Two, both in `tools/findings_families.py`; `prop`, `value`, `witness`, `family`,
`kind`, `tactic`, `source`, `note`, ID assignment and ordering are exactly as
specified, and the test file is unmodified.

1. **Theorem name lowercases the family component.** The brief's
   `f"f{n:03d}_{family}_{n:03d}"` produces `f001_equivalence_certT_001`, which
   fails the brief's own `test_ids_and_names` regex `^[a-z][a-z0-9_]*$` (uppercase
   `T`). Implemented as `f"f{n:03d}_{family.lower()}_{n:03d}"`, giving
   `f001_equivalence_certt_001`. The `family` field itself stays `equivalence_certT`
   (required by `test_counts` / `FAMILY_COUNTS`). Downstream tasks must use
   `row["theorem"]` verbatim as the Lean identifier; they must not reconstruct it
   from `family`, or they will reintroduce the uppercase `T`.
2. **CSV handles are closed.** The brief opened the two CSVs inline without
   closing them, which emitted `ResourceWarning: unclosed file` during the test
   run. Replaced with `with ... as fh:` blocks; reading semantics are identical
   (same `DictReader` over the same encoding).

No assertion was weakened and no count was changed.

## Self-review notes

- Strict TDD order followed: test written first and observed failing with the
  expected `ModuleNotFoundError`, then implementation, then green.
- Schema is exactly the frozen 10-key set on all 274 rows; every `witness` is a
  non-empty string; no `prop` contains `sorry`; no `note` contains a newline.
- `cliff` arithmetic was spot-checked: the P3M (`micro`→`small`) and P1B
  (`medium`→`large`) lines are penalty-neutral, so `k = 0` there
  (e.g. `penaltyT .small 1000000 30 = penaltyT .micro 1000000 30 + 0`), while the
  P20M line (`small`→`medium`) yields a positive penalty cliff. This matches the
  brief's labels, so the rows are kernel-checkable as written (they assert the
  delta, not a strict inequality).
- `crossover` spot-check: `gs=300000000` gives `x=91000000` because
  `bracket_tax(91000000)` is exactly 13,000,000 = `tax8 - pct_tax`. The expected
  literal in the test is therefore consistent with `findings_spec`.
- One `divergence` row has claimed value 0
  (`0 ≠ (mkCert8 250000000 0 30 true).total`), where G1 claims zero tax. The
  proposition is still well-formed for `decide`; no special-casing needed.
- `data/` was only read, never written; `results8.csv` (512 rows),
  `benchmark8_cases.csv` (64 rows) and all other data files are unchanged.
- Left uncommitted as required; `git status --short` lists both new files as `??`.
