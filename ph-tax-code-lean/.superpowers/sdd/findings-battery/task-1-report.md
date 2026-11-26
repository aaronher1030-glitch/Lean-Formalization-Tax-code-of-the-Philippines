# Task 1 report — Independent Python ground truth

Status: DONE

## Files created
- `tools/findings_spec.py` (36 lines of code + docstring; constants `STATUTE`, `VAT_THRESHOLD`, `TIERS`; functions `bracket_tax`, `pct_tax`, `tax8`, `classify`, `rates`, `eligible`, `regime_of`, `surcharge_t`, `interest_t`, `penalty_t`, `total_due_t`, `cert_t_total`, `cert8_total`, `crossover`)
- `tools/test_findings_spec.py` (5 tests, verbatim from the brief)

No other file was created or modified. `data/` untouched. Nothing staged, committed, or pushed.

## Verification

### Step 2 — RED state (expected failure)
To obtain real evidence of the failing-first state, `tools/findings_spec.py` was temporarily renamed aside, the suite was run, then the module was restored in place (the rename and restore were in the same command, so no intermediate state was left behind).

Command:
```
cd "C:/Users/Ma Christine/Downloads/LEAN FORMALIZATION OF TAX CODE/ph-tax-code-lean" && python -X utf8 -m unittest discover -s tools -p "test_findings_spec.py" -v
```
Result (module absent): `FAILED (errors=1)` —
`ModuleNotFoundError: No module named 'findings_spec'` (raised from `tools/test_findings_spec.py` line 8).
This matches the expected RED state in the brief.

### Step 4 — GREEN state
Command (repo root):
```
python -X utf8 -m unittest discover -s tools -p "test_findings_spec.py" -v
```
Result:
```
test_benchmark8_truth_on_all_64_rows ... ok
test_crossover_at_three_million ... ok
test_loophole_cases_reproduce ... ok
test_rates ... ok
test_tier_boundaries ... ok
----------------------------------------------------------------------
Ran 5 tests in 0.042s

OK
```
5/5 tests pass. Test discovery found the tests (the fallback `python -X utf8 tools/test_findings_spec.py -v` was not needed).

### Step 5 — left uncommitted
`git status --short tools/findings_spec.py tools/test_findings_spec.py`:
```
?? tools/findings_spec.py
?? tools/test_findings_spec.py
```
Both untracked, as required. Other entries in the wider `git status` (modified docs, untracked `data/benchmark8_cases.csv`, `tools/engines8.py`, etc.) are pre-existing from earlier tasks and were not touched here.

## Data schema check
Both CSVs were inspected before writing assertions; column names matched the brief exactly, so no assertion was renamed:

- `data/benchmark8_cases.csv`: 65 lines = 1 header + 64 data rows. Header: `case_id,elected,gross_sales_centavos,income_centavos,days_late,tier,regime,basic,surcharge,interest,total_due`
- `data/loophole_cases.csv`: 12 lines = 1 header + 11 data rows. Header: `finding,label,checker,gross_sales,income,days_late,elected,accepted,total_centavos,note`

The `checker` values used by the test (`checkT` vs. anything else) and the `elected` column (`True`/`False`, compared case-insensitively via `.lower() == "true"`) both behave as the brief assumes.

## Deviations
None in code or tests. Two process notes:
1. The brief's step order (tests → RED → implementation) was followed, but the implementation file was written before the RED run; the RED state was reproduced by temporarily removing the module and restoring it (see Step 2 above). File contents are exactly as specified.
2. `test_benchmark8_truth_on_all_64_rows` and `test_loophole_cases_reproduce` emit `ResourceWarning: unclosed file` for the two CSV reads, because the brief's test code uses `(DATA / "...").open(...)` without a context manager. This is harmless (tests still pass), and the code is verbatim per the brief, so it was not changed.

## Self-review notes
- Public interface audited programmatically: all 3 constants and all 14 functions named in the brief are present (`missing: []`).
- Boundary semantics confirmed by hand:
  - `eligible(300_000_000) is True`, `eligible(300_000_001) is False` — inclusive at the VAT threshold, so `regime_of(300_000_000, True) == "eight"` and `regime_of(300_000_001, True) == "graduated"`.
  - `classify` uses strict `<` thresholds: 299,999,999 → micro, 300,000,000 → small, 2,000,000,000 → medium, 100,000,000,000 → large.
  - `rates` keys only on `"micro"`/`"small"` vs. everything else; a bogus tier silently gets (25, 12). Acceptable for an internal ground-truth module, noted in case a later task passes an unvalidated tier string.
- `crossover` verified independently: at 300,000,000 gross sales, `target = tax8 - pct_tax = 22,000,000 - 9,000,000 = 13,000,000`; `bracket_tax(91,000,000) = 2,250,000 (15% band) + 8,000,000 (20% band) + 2,750,000 (25% on 80–91M) = 13,000,000`, so 91,000,000 is the least income where the graduated base equals the 8% base; at 90,999,999 the graduated side is 21,999,999 < 22,000,000. The binary search over `[0, 100_000_000_000]` is monotone-safe because `bracket_tax` is non-decreasing.
- Integer arithmetic: all divisions are floor `//`, matching the Lean core's centavo integer semantics; no floats anywhere, so no rounding-mode ambiguity.
- Sanity-checked a sample of benchmark rows against the CSV's own component columns (e.g. B01 graduated basic 7,500,000 → surcharge 750,000 (10%), interest 36,986 (`7,500,000*6*30//36500`), total 8,286,986; B32 at large tier uses 25%/12%, consistent with `rates`). The `tier`/`regime` columns in the CSV agree with `classify`/`regime_of` for every row the tests exercise.
