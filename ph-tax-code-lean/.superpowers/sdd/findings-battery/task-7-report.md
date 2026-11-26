# Task 7 report — paper section §5.11, Table 9, renumbering, abstract

Status: done, uncommitted. Only `Verified_Core_Tax_Governance_PH.md` was modified by this
task. `msp/` lives one level above the repo root
(`C:/Users/Ma Christine/Downloads/LEAN FORMALIZATION OF TAX CODE/msp/`) and was not
touched (all files still dated 15–16 November 2026); no DOCX/PDF was touched.

## Edits (old line -> new line)

| Change | Old | New |
|---|---|---|
| Abstract: inserted the 274-proposition sentence after "...submit 766 certificates judged only by the verified checkers." | L11 | L11 (same line) |
| §5.11 heading + two paragraphs | — | L512, L514, L516 |
| Table 9 caption | — | L518 |
| Table 9 opacity/widths comment + table (9 rows incl. Total) | — | L520–L532 |
| `## 6. Critical Assessment` shifted down by the insertion | L512 | L535 |
| In-text `Table 9` -> `Table 10` (Section 5.6 forward reference) | L406 | L406 |
| In-text `Table 9` -> `Table 10` (§6.1 "shows what this cost") | L518 | L541 |
| Caption `Table 9. Effect of the omitted EOPT concession` -> `Table 10.` | L520 | L543 |
| In-text `(Table 9)` -> `(Table 10)` (§8 internal validity) | L588 | L611 |
| Caption `Table 10. Verdict rubric` -> `Table 11.` | L562 | L585 |
| Caption `Table 11. The roadmap` -> `Table 12.` | L596 | L619 |
| Roadmap row 9 "Findings battery" appended after row 8 | — | L633 |
| Reproducibility: `tools/findings.py` sentence after the `tools/loopholes.py` sentence | L619 | L643 |

## Renumbering map (applied in descending order, no collisions)

- Table 11 -> 12 (roadmap caption, L596 -> L619)
- Table 10 -> 11 (verdict rubric caption, L562 -> L585)
- Table 9 -> 10 (captions **and** in-text: L406, L518 -> 541, L520 -> 543, L588 -> 611)
- new Table 9 (findings battery) inserted in §5.11; Tables 1–8 untouched

## Verification greps

`grep -o "^\*Table [0-9]*\." | sort | uniq -c` — every caption number exactly once,
none duplicated:

```
1 *Table 1.   1 *Table 2.   1 *Table 3.   1 *Table 4.
1 *Table 5.   1 *Table 6.   1 *Table 7.   1 *Table 8.
1 *Table 9.   1 *Table 10.  1 *Table 11.  1 *Table 12.
```

Caption order by first appearance is monotonically increasing 1,2,3,4,5,6,7,8,9,10,11,12.
All in-text references resolve to the intended table: `Table 10` at L406/L541/L611 points at
the EOPT table (caption L543); `Table 9` at L518 is the findings battery; `Tables 5 and 7`
(plural, roadmap row 5) is unchanged and correct.

`grep -n "^### 5\.1[01]\|^## 6\."`:

```
489:### 5.10 Loopholes derived from the verified core
512:### 5.11 A battery of machine-checked findings
535:## 6. Critical Assessment
```

§5.11 sits between §5.10 and §6 as required.

`grep -c "274"` -> 6 (abstract, two in §5.11 prose, Table 9 total row, two in the roadmap
row; requirement was >= 4). Hand-written counts intact: "59 theorems and 82 kernel-checked
examples" still appears twice (abstract L11, Introduction L29) and 1,024 lines at L193/L325.

Data cross-check against `data/findings.csv` (274 rows): families
equivalence_certT 32, equivalence_cert8 96, divergence 56, boundary 16, cliff 18,
crossover 20, monotone 20, gap 16; kinds equivalence 128, divergence 56, incentive 38,
identity 20, boundary 16, gap 16. This matches the brief's 128/56/16/18/20/20/16, the
prose ("38 quantify the incentive structure", "90 boundary, incentive, identity and gap"
= 16+38+20+16) and every row of Table 9.

## Deviations

1. Added `<!-- widths: 0.28, 0.13, 0.09, 0.50 -->` above the new table (not in the brief's
   block). Every other table in the paper carries one and `tools/md_to_docx.py` parses it;
   ratios sum to 1.00. Harmless for Task 10, and removable if the brief is read strictly.
2. Kept the document's existing two-blank-line separation before `## 6.` (the original had
   two blank lines there), so the insertion ends with two blank lines at L533–L534.
3. §5.11 prose does not say "Table 9" in running text; the brief's paragraph text is
   verbatim and only the caption references the table, which is how Tables 2, 5, 7 and 8
   are handled elsewhere in the document.

## Self-review notes

- Renumbering was done caption-first-in-descending-order, so intermediate states never had
  two tables with the same number; each `Table 9` occurrence was edited by unique
  surrounding text rather than a bulk replace, so `Table 9` inside §5.11 was never
  accidentally rewritten to `Table 10`.
- The forward reference at L406 ("Table 10 in Section 6.1 was hand arithmetic") points
  forward across §5.7–5.10; that forward reference pre-existed (it was "Table 7", then
  "Table 9") and is intentional, so the "monotonic by first appearance" check holds for
  captions, not for that one in-text pointer.
- The new section changes no count of hand-written material: 59 theorems / 82 examples /
  1,024 lines are untouched, and the 274 propositions are described as a separate generated
  artifact in `lean/_harness/`.
- Unrelated working-tree modifications from earlier tasks (README, ROADMAP, STATUS,
  THEOREMS, DOCX/PDF, `lean/`, `tools/`, `data/`) were already present and were left alone;
  nothing was staged, committed or pushed.
