# Task 9 — FINDINGS.md framing audit and loophole cross-link

Status: complete. One edit made (`LOOPHOLE_FINDINGS.md`); `FINDINGS.md` untouched.
Nothing staged, committed, or pushed. No subagents dispatched.

Repo: `C:/Users/Ma Christine/Downloads/LEAN FORMALIZATION OF TAX CODE/ph-tax-code-lean`

---

## 1. Framing audit of `FINDINGS.md` (274 rows, generated)

Method: read `FINDINGS.md` line by line against the claim ladder; cross-checked
every count against `data/findings.csv` (274 rows), `lean/_harness/Findings.lean`
(274 `theorem` declarations; 174 closed by `rfl`, 100 by `by decide`; zero
matches for `native_decide` or `sorry`), and re-rendered the harness in memory
from `tools/findings_families.py` + `tools/findings_render.py` (byte-identical
to the file on disk, so `FINDINGS.md` describes the current row set). Verified
the two external attributions against Han et al., arXiv:2610.02792v1 (HTML).

### Verdict summary

| Ladder item | Location | Verdict |
|---|---|---|
| (a) the number, 274 | L1 title, L30 table total, L49 file list | PASS |
| (b) the kind split | L20–L30 summary table | PASS (matches CSV exactly) |
| (c) "not 274 loopholes" | L9 | PASS (explicit, prominent) |
| (d) `native_decide` contrast | L14–L16 | PRESENT but MISATTRIBUTED — see F2 |
| (e) incentive rows conditional on spec fidelity | L12–L13 | PASS |
| gap family ≠ law defects | L13–L14 | PASS, weak wording — see F3 |
| divergence ≠ deployed-law defects | L11 | PASS in substance, unqualified wording — see F1 |
| axiom-audit claim | L15, L32 | OVERSTATED coverage — see F0 |

**Primary requirement met.** No sentence anywhere in `FINDINGS.md` presents the
274 as legal loopholes, gaps in the real tax code, or defects in deployed tax
software. The only explicit use of the word is the negation at L9.

### Per-section detail

**Title and opening paragraph (L1–L7).** "274 machine-checked propositions from
the verified core" is accurate: 274 theorems, all closed by `rfl`/`by decide`,
no `sorry`, no `native_decide`, kernel-checked. The counting-unit sentence cites
Han et al. §4.4 for "a finding is a theorem relating two computations — an
equivalence at a witness, or a divergence counterexample". Verified: Han et al.
§4.4 is titled "Proving Semantic Equivalence and Divergence" and reports 43
equivalence proofs plus 7 divergence counterexamples over 50 sampled cells, so
the convention is genuinely theirs. PASS. Minor note (non-blocking): the
parenthetical "(arXiv:2610.02792, section 4.4)" is placed where this repo's own
paper §4.4 ("The tiered checker") is also cited elsewhere, so a fast reader can
take it as the local paper's §4.4; "Han et al., §4.4" would remove the ambiguity.

**Honesty paragraph (L9–L16).** Carries the load and does it correctly in four
of five respects. L9 "**The battery is not 274 loopholes.**" is the required
negation. L10–L11 assigns each kind its claim. L12–L13 conditions boundary,
incentive and identity rows on "the specification's fidelity". L13–L14 ties the
gap family to L1, L2, L5 — verified against the CSV: the 16 `gap` rows are
exactly L1 (4), L2 (8), L5 (4); L3/L4 land in `incentive` (cliff 18, crossover
20), so the gap family is not silently absorbing the statutory-incentive
findings. Nothing here asserts an unguarded premise is a property of NIRC as
enacted. PASS (with F1–F3 wording qualifiers below).

**Summary table (L20–L30).** equivalence_certT 32 + equivalence_cert8 96 = 128
equivalence; divergence 56; boundary 16; cliff 18 + crossover 20 = 38 incentive;
monotone 20 identity; gap 16. Total 274. Every figure matches
`Counter(kind)` / `Counter(family)` over `data/findings.csv`. PASS. Note: the
aggregate 128 / 56 / 90 split is not stated in prose — it is derivable from the
table and is stated in the new `LOOPHOLE_FINDINGS.md` cross-link.

**"Kernel compile: 12.0 s" (L32).** Timing value transcribed from the gated run;
not independently re-timed here (zero consequences for any claim). Noted as
unverified, not as an overclaim.

**Reproduce / Files (L34–L52).** Accurate relative to `tools/findings.py`
(writes harness, compiles, refuses to write on compile or axiom failure, then
writes CSV + MD). PASS.

### Framing concerns to route to the generator (`tools/findings_report.py`)

These are reported, not fixed, because `FINDINGS.md` is generated.

**F0 — axiom audit covers 8 of 274 theorems, prose implies all.**
Quoted, L15: "the axiom audit stays at `propext` and nothing trusts the
compiler." Quoted, L32: "Kernel compile: 12.0 s. Axiom audit: propext only."
Evidence: `lean/_harness/Findings.lean` L300–L308 emits `#print axioms` only for
"first theorem of each family" (8 of 274), rendered by `tools/findings_render.py`
L26–L31, and `tools/findings.py` L53–L58 scans only those output lines. So the
`propext`-only result is attested for `f001, f033, f129, f185, f201, f219, f239,
f259` and untested for the other 266. The defect is coverage, not truth: all 274
close by `rfl`/`decide` with no `native_decide`/`sorry`, so no other axiom could
enter in practice. Fix in generator: print axioms for all 274, or soften to
"spot-checked at `propext` for one theorem per family (8 of 274)".
Severity: low (honesty about verification coverage, not about the law).

**F1 — "engine errors" without the seeded/untrusted qualifier.**
Quoted, L11: "`divergence` rows exhibit engine errors;". Substance is right:
the 56 rows come 8 each from the seven deliberately buggy benchmark engines
`G1_eight_on_income … G7_penalty_wrong_base` (rows carry
"engine claimed 0; the kernel total is 19888767" and `data/results8.csv`
provenance), i.e. seeded-engine disagreement, not a deployed-law defect. But
"engine" is bare; a reader who meets only the intro can read it as a defect in
some operating tax engine. Suggested generator wording: "`divergence` rows
exhibit errors seeded into our seven untrusted benchmark engines (G1–G7)".
Severity: low; no claim about real law is made.

**F2 — `native_decide` contrast attached to the wrong proof class.**
Quoted, L14–L15: "Unlike the equivalence proofs in Han et al., no proof here uses
`native_decide`;". Checked against Han et al. v1: Appendix A.1, Fig. 8(a), the
*equivalence* proof is closed by `rfl`, and the text says "Most proofs of
equivalence were short, using reflection tactics like Fig. 8(a)"; `native_decide`
appears only in Fig. 8(b), the *divergence* proof (`theorem neq_32 : … := by
native_decide`). So the contrast as written is misattributed — Han et al.'s
equivalence proofs use reflection/`rfl` like ours; the difference is that their
counterexample proofs use `native_decide` while our 56 divergence rows use
kernel `by decide`. Suggested generator wording: "Unlike the divergence proofs in
Han et al., no proof here uses `native_decide`;". Severity: low (a claim about a
third party's artifact, not about the tax code), but it is checkably wrong as
worded and the same sentence is mirrored at `STATUS.md` L139.

**F3 — gap family phrasing drifts from "unguarded certificate premises".**
Quoted, L13–L14: "`gap` rows document premises our checker lacks (L1, L2, L5)."
"Lacks" admits the misreading that the encoding is missing something it ought to
state, rather than that the checker accepts certificates without guarding a
premise. The plan's ladder asks for "unguarded certificate premises"; suggested
generator wording: "`gap` rows document certificate premises our checkers leave
unguarded (L1, L2, L5)". Severity: cosmetic; `LOOPHOLE_FINDINGS.md` states the
"Encoding gap" reading correctly and the cross-link repeats that neither
document claims encoding gaps are properties of the real tax code.

**Not a defect, recorded for the reader:** 128 equivalence + 20 identity rows are
consistency checks (against the independent Python oracle and closed-form
values), not discoveries. The prose discloses this at L10 and the "not 274
loopholes" sentence is doing exactly the work it should, so the generous word
"findings" is disclosed, not hidden.

---

## 2. The edit (`LOOPHOLE_FINDINGS.md` only)

Inserted, verbatim from the brief, at the end of the "Reproduce" section
(between the `python -X utf8 tools/loopholes.py` code fence and
`## Honesty notes`, now L125–L129):

```markdown
A generated battery of 274 kernel-checked propositions that extends these
five findings — 128 equivalences, 56 divergence counterexamples, and 90
boundary, incentive, identity and gap propositions — is documented in
[FINDINGS.md](FINDINGS.md); the two documents use the same kind labels, and
neither claims that encoding gaps are properties of the real tax code.
```

Constraint check on the inserted text: 128 + 56 + 90 = 274, and 90 = 16
boundary + 38 incentive + 20 identity + 16 gap, matching the CSV; "extends these
five findings" is true by provenance (battery gap rows cite L1/L2/L5, cliff rows
L3, crossover rows L4). The sentence adds no claim that the battery found legal
loopholes; the clause "neither claims that encoding gaps are properties of the
real tax code" is accurate for both documents as they now stand (F3 is a wording
quality issue, not a contradiction of that clause).

Honesty note on the prescribed phrase "the two documents use the same kind
labels": it is close but not literal. `LOOPHOLE_FINDINGS.md` distinguishes
"Encoding gap" and "Statutory incentive"; the battery's kinds are `gap` and
`incentive` (plus `equivalence`, `divergence`, `boundary`, `identity`). The
correspondence is gap↔Encoding gap and incentive↔Statutory incentive; the
strings differ. I used the brief's text verbatim rather than paraphrase; if the
plan author wants literal identity, the phrase should become "the two documents
agree on what a gap is and what an incentive is".

---

## 3. Verification

| Check | Command | Result |
|---|---|---|
| Link resolves | `test -f FINDINGS.md` + grep on `LOOPHOLE_FINDINGS.md` | PASS — `FINDINGS.md` exists at repo root; link on L128 |
| L1–L5 headings unchanged | `grep -n "^## L[0-9]" LOOPHOLE_FINDINGS.md` | PASS — 5 headings, same titles and same line numbers as before the edit (L26, L46, L60, L84, L105); L4's missing parenthetical is pre-existing, not introduced |
| No "battery found legal loopholes" claim | `grep -n "274\|not 274\|native_decide" FINDINGS.md LOOPHOLE_FINDINGS.md` (brief Step 3) | PASS — hits: FINDINGS.md L1, L9 ("not 274 loopholes"), L15, L30, L49; LOOPHOLE_FINDINGS.md L125 (new cross-link, "neither claims …"). No sentence asserts 274 legal loopholes |
| Inserted text verbatim | Python substring test against brief text | PASS — `verbatim match: True` |
| Harness/row consistency | in-memory `findings_render.render(findings_families.all_findings())` vs `lean/_harness/Findings.lean` | PASS — byte-identical, 274 rows |
| Not staged | `git status --short FINDINGS.md LOOPHOLE_FINDINGS.md`; `git diff --cached --name-only` | PASS — both `??` untracked (LOOPHOLE_FINDINGS.md was already untracked before the edit); index empty |

Files touched: `LOOPHOLE_FINDINGS.md` (edit) and this report. `FINDINGS.md`,
`tools/`, `lean/`, `msp/`, the paper and its DOCX/PDF were not modified; no
source file was touched; no generated file was rewritten (the harness comparison
was done in memory only).

---

## 4. Deviations

1. Brief Step 1 permits editing `FINDINGS.md`'s intro prose. The task brief for
   this session forbids editing it (generated from `tools/findings_report.py`)
   and requires reporting overclaims instead. I followed the stricter
   instruction: F0–F3 are report-only, with generator file/line targets supplied
   above.
2. The brief's "append to the Reproduce section" is satisfied by placing the
   paragraph after the Reproduce code fence, before `## Honesty notes` (it cannot
   go inside a fenced block without becoming code).
3. External verification used one network fetch of arXiv:2610.02792v1 to check
   F2 and the §4.4 citation; no repo content depends on it.

---

## Fix round (framing/audit)

Three verified review findings fixed in four files, then the artifacts were
regenerated. Nothing was staged, committed or pushed.

### Diff 1 — `tools/findings_render.py` (audit every theorem)

```diff
@@ def render(rows)
     lines = [HEADER_TEMPLATE.format(n=len(rows))]
     current = None
+    audited = False
     for r in rows:
         if r["family"] != current:
             current = r["family"]
             lines.append(f"\n-- {current} ({r['kind']})\n")
+        if not audited:
+            lines.append("-- axiom audit: every theorem\n")
+            audited = True
         body = ":= rfl" if r["tactic"] == "rfl" else ":= by decide"
         lines.append(f"theorem {r['theorem']} : {r['prop']} {body}\n")
-    lines.append("\n-- axiom audit: first theorem of each family\n")
-    seen = set()
-    for r in rows:
-        if r["family"] not in seen:
-            seen.add(r["family"])
-            lines.append(f"#print axioms {r['theorem']}\n")
+        lines.append(f"#print axioms {r['theorem']}\n")
     return "".join(lines)
```

Rendered head: one `-- axiom audit: every theorem` header (after the first
family comment, before the first theorem), then `#print axioms <theorem>`
immediately after every `theorem` line.

### Diff 2 — `tools/findings_report.py` (`MD_HEAD` prose)

```diff
-`divergence` rows exhibit engine errors; `boundary`, `incentive` and
-`identity` rows quantify structure of the law as formalized, conditional on
-the specification's fidelity; `gap` rows document premises our checker lacks
-(L1, L2, L5). Unlike the equivalence proofs in Han et al., no proof here uses
-`native_decide`; the axiom audit stays at `propext` and nothing trusts the
-compiler.
+`divergence` rows exhibit errors seeded into our seven untrusted engines
+(G1-G7); `boundary`, `incentive` and
+`identity` rows quantify structure of the law as formalized, conditional on
+the specification's fidelity; `gap` rows document unguarded certificate
+premises (L1, L2, L5). Unlike the divergence proofs in Han et al., which use
+`native_decide`, ours close by kernel `decide`; every theorem is axiom-audited
+and the audit stays at `propext`, so nothing trusts the compiler.
```

### Diff 3 — `Verified_Core_Tax_Governance_PH.md` §5.11

```diff
-Every proof is closed by `rfl` or `decide`. Unlike the equivalence proofs in Han et al., none uses `native_decide`, so no proof trusts the compiler and the axiom audit stays at `propext`.
+Every proof is closed by `rfl` or `decide`. Unlike the divergence proofs in Han et al., which use `native_decide`, ours close by kernel `decide`; every theorem is axiom-audited and the audit stays at `propext`, so nothing trusts the compiler.
```

### Diff 4 — `STATUS.md` (near line 139)

```diff
-incentive structure and encoding gaps. Unlike the equivalence proofs in
-Han et al. (arXiv:2610.02792), no proof uses `native_decide`.
+incentive structure and encoding gaps. Unlike the divergence proofs in
+Han et al. (arXiv:2610.02792), which use `native_decide`, ours close by
+kernel `decide`; every theorem is axiom-audited and the audit stays at
+`propext`.
```

### Regenerated artifacts

- `lean/_harness/Findings.lean` — rewritten by the driver; 274 theorem lines,
  274 `#print axioms` lines, single header, zero `native_decide`.
- `data/findings.csv` — rewritten (unchanged content; prose only).
- `FINDINGS.md` — regenerated from `MD_HEAD`; paragraph now reads as in Diff 2
  and still contains "not 274 loopholes".

### Verification (real output)

```
$ python -X utf8 -m unittest discover -s tools -p "test_*.py" -v
Ran 20 tests in 0.950s
OK
```

```
$ python -X utf8 tools/findings.py
PASS: 274 findings kernel-checked in 29.5 s; axioms: propext only
  equivalence_certT    equivalence   32
  equivalence_cert8    equivalence   96
  divergence           divergence    56
  boundary             boundary      16
  cliff                incentive     18
  crossover            incentive     20
  monotone             identity      20
  gap                  gap           16
wrote ...\data\findings.csv and ...\FINDINGS.md
EXIT=0
```

Compile log (harness recompiled directly, exit 0):

| Metric | Count |
|---|---|
| `#print axioms` in `lean/_harness/Findings.lean` | 274 |
| `depends on axioms:` results | 242, every one `[propext]` |
| `does not depend on any axioms` results | 32 |
| total axiom-result lines | 274 |
| `native_decide` in harness (case-insensitive) | 0 |

Sample results:

```
'f001_equivalence_certt_001' depends on axioms: [propext]
'f002_equivalence_certt_002' depends on axioms: [propext]
'f185_boundary_185' does not depend on any axioms
```

`FINDINGS.md` contains the three new sentences and "not 274 loopholes".
`grep -n "Unlike the" Verified_Core_Tax_Governance_PH.md STATUS.md` shows the
corrected wording in both; `grep -c "Unlike the equivalence proofs"` is 0 in
both (and in `FINDINGS.md`).

`test_one_audit_per_family` passed unedited: the 2-row fixture has 2 theorems
and 2 families, so per-theorem auditing still yields 2 audits.
