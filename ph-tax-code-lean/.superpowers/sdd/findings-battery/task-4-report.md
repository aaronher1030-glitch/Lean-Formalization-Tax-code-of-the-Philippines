# Task 4 report — CSV and FINDINGS.md writer

Date: 2026-11-18
Repo: `C:/Users/Ma Christine/Downloads/LEAN FORMALIZATION OF TAX CODE/ph-tax-code-lean`
Status: **complete** — 4/4 tests pass, nothing staged, no outputs written to the repo.

## Files created (exactly two)

- `tools/findings_report.py` — implementation, verbatim from the brief (Step 3).
- `tools/test_findings_report.py` — tests, verbatim from the brief (Step 1).

No other file touched. `data/findings.csv` and `FINDINGS.md` were **not** created;
all sample rendering was done in a `tempfile.TemporaryDirectory()`.

## TDD sequence observed

1. Test file written first.
2. Run → expected failure confirmed:
   `ModuleNotFoundError: No module named 'findings_report'`
   (`ERROR: test_findings_report (unittest.loader._FailedTest...)`, `FAILED (errors=1)`).
3. Implementation written.
4. Run → green.

## Test output

Command:
```
cd "C:/Users/Ma Christine/Downloads/LEAN FORMALIZATION OF TAX CODE/ph-tax-code-lean" \
  && python -X utf8 -m unittest discover -s tools -p "test_findings_report.py" -v
```

```
test_csv_header_exact (test_findings_report.ReportTests.test_csv_header_exact) ... ok
test_markdown_contains_counts_and_honesty (test_findings_report.ReportTests.test_markdown_contains_counts_and_honesty) ... ok
test_summary_order_and_counts (test_findings_report.ReportTests.test_summary_order_and_counts) ... ok
test_write_outputs (test_findings_report.ReportTests.test_write_outputs) ... ok

----------------------------------------------------------------------
Ran 4 tests in 0.101s

OK
```

`test_write_outputs` emits a `ResourceWarning: unclosed file` from the test's own
`csv.DictReader(c.open(...))` one-liner. That line is verbatim from the brief and the
test still passes; left unchanged deliberately (see Deviations).

## Sample CSV header and rows

Header (exactly the 9 frozen-schema columns, `prop` → `proposition`, `value` → `value_centavos`):

```
id,family,kind,theorem,proposition,witness,value_centavos,source,note
```

Sample rows rendered from a two-row fixture (temp dir):

```
id,family,kind,theorem,proposition,witness,value_centavos,source,note
F001,equivalence_certT,equivalence,f001_equivalence_certT_001,certT 250000 = 0,250000,0,RA 10963 s.24(A)(1),n
F002,gap,gap,f002_gap_002,p,-,,s,n
```

Notes on the encoding decisions:
- `value is None` → empty cell (not `None`/`nan`), so downstream readers see a missing
  amount rather than a string. Verified: row `F002` has `,,` before `s`.
- `lineterminator="\n"` on the `csv` writer, and `newline=""` on the CSV `write_text`,
  so no doubled `\r\r\n` on Windows.

## Sample Markdown summary table

```
## Summary

| Family | Kind | Findings |
|---|---|---|
| equivalence_certT | equivalence | 1 |
| gap | gap | 1 |
| **Total** | | **2** |

Kernel compile: 12.5 s. Axiom audit: propext only.
```

The table is kind-stratified (each row is a `(family, kind)` pair) and ordered by first
appearance in `rows`, matching `summary()`; the `**Total**` row sums the counts.

Honesty framing present in the generated document (all three literal strings the tests
assert):
- `274` — in the H1 `# Findings Battery — 274 machine-checked propositions from the verified core`, in the bold paragraph `**The battery is not 274 loopholes.**`, and in the Files list (`tools/findings_families.py — the 274 rows`).
- `not 274 loopholes` — the bold paragraph, immediately followed by the kind-by-kind
  breakdown: `equivalence` = core vs independent Python value, `divergence` = engine
  errors, `boundary`/`incentive`/`identity` = structure of the law conditional on spec
  fidelity, `gap` = missing checker premises (L1, L2, L5).
- `native_decide` — in the explicit contrast: "Unlike the equivalence proofs in Han et
  al., no proof here uses `native_decide`; the axiom audit stays at `propext` and
  nothing trusts the compiler."

The counting unit is attributed (Han et al., arXiv:2610.02792, section 4.4: a finding
relates two computations), and every row is described as closed by `rfl` or `by decide`
and judged by the pinned Lean 4.35.0 kernel — no claim that a finding is a legal defect.

## Deviations

None from the brief's code. Two observations, both left as-specified:

1. **`ResourceWarning` in the test** — `csv.DictReader(c.open(encoding="utf-8"))` never
   closes the handle. Harmless under CPython (refcount close) and the test is verbatim
   from the brief, so not "fixed"; if the warning noise matters later, wrap it in a
   `with` block in both brief and code.
2. **Markdown newline translation** — `md_path.write_text(..., encoding="utf-8")` has no
   `newline=""`, so on Windows the `.md` gets `\r\n`. Markdown renders identically and
   no test asserts otherwise; CSV is the machine-read format and is explicitly locked to
   `\n`. Left verbatim.

## Self-review notes

- **Interface contract met**: `summary(rows) -> list[dict]` with keys `family`, `kind`,
  `count`; `csv_text(rows) -> str`; `markdown(rows, meta) -> str`;
  `write_outputs(rows, meta, csv_path, md_path) -> None`. `meta` consumes `"seconds"`
  (float) and `"audit"` (str) only; no other keys required.
- **`summary()` keying**: groups on `(family, kind)`, not `family` alone — so a family
  appearing under two kinds yields two rows. First-appearance order is preserved via the
  `order` list, which is insertion-ordered and independent of dict ordering guarantees.
- **No repo imports**: `findings_report.py` imports only `csv` and `io` from the stdlib.
  It does not import `findings.py`, `findings_families.py`, or any in-flight task module,
  so Tasks 2/3/5 landing later or differently cannot break it.
- **`total` is derived, not hardcoded**: the `**Total**` cell is the sum of actual counts,
  so the table can never disagree with the CSV length, even though the prose/heading
  hardcodes 274 (the brief's intended framing constant).
- **Field-name guard**: `csv.DictWriter` is constructed with `fieldnames=FIELDS` and each
  row is written from an explicit dict, so a row missing a schema key raises `KeyError`
  rather than silently emitting a short line. `prop`/`value` renaming happens only at the
  header boundary.
- **Byte-level check**: rendered CSV parses back to exactly 2 records through
  `csv.DictReader` in the test, confirming no stray BOM/quoting issues; non-ASCII in the
  Markdown (em dashes) round-trips under `encoding="utf-8"`.
- **Working tree**: `git status --short` shows `?? tools/findings_report.py` and
  `?? tools/test_findings_report.py` only — both untracked, nothing added to the index.
  The other `M`/`??` entries in the tree predate this task and belong to other tasks.

---

# Fix round 1

Date: 2026-11-18
Status: **complete** — review gap closed, 5/5 report tests and 20/20 tool tests green,
nothing staged, no repo outputs written.

## Findings addressed

1. **BLOCKING** — `write_outputs` did not create parent directories, so writing to a
   nested nonexistent path (e.g. `/tmp/nested/deeper/findings.csv`) raised
   `FileNotFoundError`. Confirmed against the pre-fix behaviour:
   `OLD CODE: FileNotFoundError -> FileNotFoundError`.
2. **MINOR** — the Markdown write lacked `newline=""`, so the `.md` got `\r\n` on
   Windows while the CSV was pinned to `\n`.
3. One new test appended to lock both behaviours.

## Files changed (2, both already task-4 files)

`tools/findings_report.py` — `write_outputs` only:

```diff
 import csv
 import io
+from pathlib import Path
@@
 def write_outputs(rows, meta, csv_path, md_path):
+    csv_path, md_path = Path(csv_path), Path(md_path)
+    for p in (csv_path, md_path):
+        p.parent.mkdir(parents=True, exist_ok=True)
     csv_path.write_text(csv_text(rows), encoding="utf-8", newline="")
-    md_path.write_text(markdown(rows, meta), encoding="utf-8")
+    md_path.write_text(markdown(rows, meta), encoding="utf-8", newline="")
```

Notes: paths are coerced with `Path()` so `str` and `Path` inputs both work (the
existing tests pass `Path`; a future driver may pass `str`). `mkdir(parents=True,
exist_ok=True)` runs for both paths *before* either write, so a failure leaves neither
file half-written and re-runs are idempotent. `newline=""` disables OS newline
translation on the Markdown handle, matching the CSV handle; the Markdown body's own
`\n` line breaks are untouched, so rendering is unchanged on every platform.

`tools/test_findings_report.py` — one test appended, the 4 brief-verbatim tests are
untouched (byte-identical):

```diff
+    def test_write_outputs_creates_nested_dirs_and_writes_lf(self):
+        with tempfile.TemporaryDirectory() as td:
+            c = Path(td) / "nested" / "deeper" / "f.csv"
+            m = Path(td) / "nested" / "deeper" / "FINDINGS.md"
+            self.assertFalse(c.parent.exists())
+            rep.write_outputs(FIXTURE, META, c, m)
+            self.assertTrue(c.exists() and m.exists())
+
+            csv_bytes = c.read_bytes()
+            csv_str = csv_bytes.decode("utf-8")
+            self.assertNotIn(b"\r", csv_bytes)
+            self.assertNotIn("\r", csv_str)
+            self.assertEqual(csv_str.count("\n"), 3)  # header + 2 rows, LF-terminated
+            self.assertTrue(csv_str.endswith("\n"))
+
+            md_bytes = m.read_bytes()
+            self.assertNotIn(b"\r", md_bytes)
+            self.assertNotIn("\r", md_bytes.decode("utf-8"))
```

What the test locks: two levels of nonexistent directories are created; both files
exist; the CSV contains no `\r` byte or character and exactly 3 LF-terminated lines
(header + 2 fixture rows), ending in `\n`; the Markdown bytes contain no `\r`. It fails
on the pre-fix code at the `write_outputs` call with `FileNotFoundError`, and on the
old Markdown write at the `md_bytes` assertion with a `b"\r"` hit — so it is a
regression test for both findings, not just the blocking one.

## Test output

Command 1 — report tests (5 tests):

```
python -X utf8 -m unittest discover -s tools -p "test_findings_report.py" -v
```

```
test_csv_header_exact (test_findings_report.ReportTests.test_csv_header_exact) ... ok
test_markdown_contains_counts_and_honesty (test_findings_report.ReportTests.test_markdown_contains_counts_and_honesty) ... ok
test_summary_order_and_counts (test_findings_report.ReportTests.test_summary_order_and_counts) ... ok
test_write_outputs (test_findings_report.ReportTests.test_write_outputs) ... ok
test_write_outputs_creates_nested_dirs_and_writes_lf (test_findings_report.ReportTests.test_write_outputs_creates_nested_dirs_and_writes_lf) ... ok

----------------------------------------------------------------------
Ran 5 tests in 0.163s

OK
```

Command 2 — all tool tests (20 tests):

```
python -X utf8 -m unittest discover -s tools -p "test_*.py" -v
```

```
Ran 20 tests in 0.554s

OK
```

Both runs report `OK`. The pre-existing `ResourceWarning: unclosed file` noise from
`test_write_outputs` (line 48, the brief-verbatim one-liner) and from
`test_findings_spec.py` is unchanged — those lines were deliberately not touched.

## Scope

Only the two task-4 files plus this report were modified. `data/`, the repo root and
all other files are untouched; `git status --short` shows no new paths from this round
and nothing staged. No commit was created.

The deviation noted in the original report ("Markdown newline translation … left
verbatim") is now resolved by finding 2; that earlier note stands as the record of the
state at review time.

