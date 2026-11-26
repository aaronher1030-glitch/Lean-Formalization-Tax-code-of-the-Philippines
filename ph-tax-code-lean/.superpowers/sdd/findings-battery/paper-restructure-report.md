# Paper restructure report — journal-style full-paper pass

Scope: structure and exposition only, in `paper/Verified_Core_Tax_Governance_PH.md`.
No number, table value, citation, abstract, title block, `paper/*.docx`, `paper/*.pdf`,
or `msp/` was changed. No staging, no commit, no subagents.

Baseline: 694 lines, 12 captioned tables. Final: 745 lines (`wc -l`; the script below reports 746
because it counts the empty string after the final newline), 13 captioned tables.

## 1. Edits, in order

### 1.1 New Table 2 (lines 199–211)

Inserted at the end of Section 3, after 3.6 and before `## 4. The Verified Core` (now line 213):

- line 199: caption `*Table 2. Comparison with related tax-formalization efforts.*`
- line 201: `<!-- widths: 0.22, 0.24, 0.20, 0.20, 0.14 -->` (5 columns, sums to 1.00)
- line 202: blank line
- lines 203–209: header, separator, five rows (OpenFisca [35]; Catala/French engine [16], [28], [29]; US IRC in Lean 4 [17]; Han et al. [11]; This work)
- line 211: the required closing sentence, verbatim: "Table 2 summarizes the comparison; the assessments in the subsections above carry the confidence tiers."

### 1.2 Renumbering of tables 2–12 to 3–13

Done mechanically over the whole paper with `re.sub(r"Table (\d+)")` bumping 2..12 by one,
plus an explicit replacement of the one combined form (`Tables 5 and 7` -> `Tables 6 and 8`,
line 655). Captions and in-text references moved together, so no manual reference was missed.

### 1.3 `**Paper organization.**` paragraph (line 36)

One paragraph after contributions item 6, before `## 2. Research Design`: Section 2 research
design; 3 background and related work; 4 the verified core; 5 results; 6 critical assessment;
7 how strong the idea is; 8 limitations and threats; 9 reproducibility and implementation
status; 10 conclusion; Appendix A maps the artifact and its commands.

### 1.4 New subsection 2.6 "Evaluation protocol" (lines 107–111)

Two short paragraphs inserted after 2.5 and before `## 3.`, derived only from Sections 5.7 and
5.9: ground truth computed twice (independent Python, verified Lean) with the build failing on
disagreement; 32 tiered cases and the same 32 crossed with the election flag for 64 rows;
254 and 512 certificates; `checkT`/`check8` as the only judges; acceptance requires every line
to follow the specification; zero errors among accepted certificates *predicted* by soundness
and tested, not assumed; engines are seeded faults or LLM sessions; results descriptive, not a
representative sample. No p-values, seeds, or protocols were invented.

### 1.5 New subsection 8.1 "Ethics, data, and code availability" (lines 639–641)

Appended at the end of Section 8 (after the "Experiment validity" bullet):
no human subjects or personal tax data; statutes and regulations are public documents;
LLM sessions were synthetic benchmark tasks; all data, code and the review packet are in the
repository under the MIT license (verified: `LICENSE` begins "MIT License"); the artifact is a
model, not legal advice.

*Numbering note:* the brief said "(8.3 or next free)". Section 8 had no numbered subsections,
so the next free number was 8.1, and 8.1 was used rather than opening at 8.3 with 8.1/8.2
undefined. If 8.1/8.2 are later split out of the threat bullets, this subsection should be
renumbered to 8.3.

### 1.6 Section 9 retitled plus commands (lines 643, 663–669)

- line 643: `## 9. Implementation Plan and Status` -> `## 9. Reproducibility and Implementation Status`
- body unchanged; the roadmap table keeps its (new) number, Table 13, at line 645
- lines 663–669: lead-in sentence and a fenced `bash` block with `bash lean/run_demo.sh`,
  `python -X utf8 -m unittest discover -s tools -p "test_*.py" -v`,
  `python -X utf8 tools/findings.py`

### 1.7 Appendix A (lines 730–745)

After `## References` (all 48 entries untouched): `## Appendix A. Artifact map and reproduction`
with a six-bullet map (`lean/`, `tools/`, `data/`, `paper/`, `docs/`, `FINDINGS.md`, with
`LOOPHOLE_FINDINGS.md` named as the loophole record, as Section 5.10 already says) and a fenced
`bash` block holding the three commands above plus
`python -X utf8 tools/md_to_docx.py paper/Verified_Core_Tax_Governance_PH.md paper/Verified_Core_Tax_Governance_PH.docx`.

### 1.8 Repo doc

`ROADMAP.md` line 3: "This mirrors Table 12 of the" -> "This mirrors Table 13 of the".
A repo-wide grep for `Table [0-9]` outside `paper/`, `.superpowers/` and `docs/superpowers/`
found no other reference to a paper table by number (README, STATUS, THEOREMS, CONTRIBUTING,
COVERAGE, FINDINGS, LOOPHOLE_FINDINGS, `docs/DEEP_RESEARCH_LEAN_TAX_GOVERNANCE.md`,
`docs/spec_review_packet.md` all clean).

## 2. Table map

| Old | New | Caption | Caption line |
|---|---|---|---|
| 1 | 1 | Documented failures of automated government | 162 |
| — | 2 | Comparison with related tax-formalization efforts (new) | 199 |
| 2 | 3 | Verification metrics of the artifact | 341 |
| 3 | 4 | Honest certificate for ₱500,000 taxable income | 364 |
| 4 | 5 | Checker response to altered certificates | 382 |
| 5 | 6 | Eight untrusted engines against the verified checker (254) | 441 |
| 6 | 7 | The 8% election, worked cases | 468 |
| 7 | 8 | Eight untrusted engines against the election-aware checker (512) | 486 |
| 8 | 9 | Five loophole findings | 515 |
| 9 | 10 | The findings battery, by family and kind | 540 |
| 10 | 11 | Effect of the omitted EOPT concession | 565 |
| 11 | 12 | Verdict rubric | 607 |
| 12 | 13 | The roadmap | 645 |

In-text reference map (all moved with the captions): 340->362 ("Table 4 shows the honest
certificate"), 366->388 ("Honest certificate (Table 4)"), 358->380 ("Table 5 shows how the
checker responds"), 406->428 ("Table 11 in Section 6.1 was hand arithmetic"), 552->574
("engine F2 in Table 6"), 541->563 ("Table 11 shows what this cost"), 611->633 ("Hand-computed
figures (Table 11)"), 629->655 ("Tables 6 and 8"). Line 152/154 (Table 1) unchanged; line 211
is the new Table 2 sentence.

## 3. Comparison cells weakened because Section 3 did not support them

1. **Han et al. scale.** The brief's "26 forms" does not appear anywhere in the paper; Section
   3.4 reports only "51 held-out returns" and "100% accuracy … against 66% for the best LLM
   alone". The cell therefore reads "51 held-out returns; 100% accuracy reported, against 66%
   for the best LLM alone" — the "26 forms" figure was dropped rather than imported.
2. **Han et al. "what is verified".** The brief's "on 50 sampled cells" is not in the paper;
   Section 5.11 says only "43 semantic equivalences and seven divergences between generated and
   gold tax-form cells". The cell reads "Form accuracy; 43 equivalences and 7 divergences proved
   in Lean" — no sample size asserted.
3. **OpenFisca scale.** Section 3.1 says OpenFisca is "an open tax-and-benefit engine first
   developed for the French government" and, at movement level, that "most government
   deployments … are calculators and pilots rather than proofs". The brief's "national rules;
   not tax-formalization proofs" would attribute a national scale that Section 3 never states,
   so the cell reads "Calculators and pilots, not a tax-formalization proof" and the
   "what is verified" cell is simply "None; no proofs".
4. **Catala independent review.** Section 3.2 attributes both the bug finding and the agency
   use to their authors and Inria, and nowhere claims an independent audit. The cell reads
   "Reported by its authors and Inria" rather than "reported/peer-reviewed".
5. **This work scale.** The brief's "5 statutes" would misdescribe Section 2.2, which lists five
   modelled rules plus the 8% regime (and Section 5.1's "seven NIRC sections and four amending
   sections"). The cell reads "Five modelled rules plus the 8% regime; 59 theorems, 82 examples;
   766 certificates".
6. **US IRC review cell.** Strengthened only to what 3.2 already says: "None: not peer-reviewed
   or independently audited" (the paper's own words).

## 4. Verification

### 4.1 Link check

```
$ python -X utf8 tools/check_links.py
all relative Markdown links resolve
exit=0
```

### 4.2 Caption / reference audit (inline Python)

```
captions: [(162, 1), (199, 2), (341, 3), (364, 4), (382, 5), (441, 6), (468, 7), (486, 8),
           (515, 9), (540, 10), (565, 11), (607, 12), (645, 13)]
mentioned numbers: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13]
OK captions 1..13 ascending once; every mention has a caption; no Table 14
total lines: 746
```

The same script also asserted, for all 14 `<!-- widths: … -->` comments (13 captioned tables
plus the uncaptioned RQ table in 2.1): a blank line follows the comment and the next non-blank
line is a table row. Result: `OK: 14 widths comments, each followed by blank line then a table row`.
Figure lines: 2, unchanged.

Full mention map (line -> table):

```
Table 1   160, 162
Table 2   199, 211
Table 3   341
Table 4   362, 364, 388
Table 5   380, 382
Table 6   441, 574, 655
Table 7   466, 468
Table 8   486, 655
Table 9   515
Table 10  540
Table 11  428, 563, 565, 633
Table 12  607
Table 13  645
```

### 4.3 Stale-numbering grep

```
$ grep -n "Table 1[0-4]\|Tables 5 and 7" paper/Verified_Core_Tax_Governance_PH.md
428:**The worked case, corrected.** Table 11 in Section 6.1 was hand arithmetic. ...
540:*Table 10. The findings battery, by family and kind ...*
563:Table 11 shows what this cost. ...
565:*Table 11. Effect of the omitted EOPT concession ...*
607:*Table 12. Verdict rubric.*
633:- **Internal validity.** ... Hand-computed figures (Table 11) are labelled as such. ...
645:*Table 13. The roadmap, with what this study has executed and what remains.*
```

No `Table 14`, no `Tables 5 and 7`; every hit is a legitimate new 10–13 reference matching its
caption in section 4.2.

### 4.4 Git state

`paper/` is **untracked** at HEAD (the paper was moved from the repo root before this session:
`git status` shows ` D Verified_Core_Tax_Governance_PH.md` at root and `?? paper/`), so
`git diff --stat` does not display the paper edits. It does show the one tracked doc I edited:

```
$ git diff --stat
 .gitignore | 7 +-   README.md | 85 +++--   ROADMAP.md | 29 +-   STATUS.md | 89 ++++-
 THEOREMS.md | 38 +-   ... (all other entries are the pre-existing move/delete of the root
 paper copy, docx, pdf and figures) ...
```

`git status --short` (trimmed to the point): `M ROADMAP.md`, `?? paper/`, and the same
pre-existing set of modified/untracked files that were there beforehand (README, STATUS,
THEOREMS, `.gitignore`, `docs/DEEP_RESEARCH…`, `lean/run_demo.sh`, `lean/_harness/README.md`,
`?? tools/findings*.py`, `?? data/results8.csv`, …). Nothing was staged.

Because `paper/` is untracked, "only intended files changed" was proven by mtime instead:

```
2026-11-18_09:20:58 .gitignore            2026-11-18_12:16:07 docs/DEEP_RESEARCH...
2026-11-18_09:34:12 STATUS.md             2026-11-18_12:16:24 lean/run_demo.sh
2026-11-18_09:39:50 THEOREMS.md           2026-11-18_12:15:55 README.md
2026-11-18_09:39:50 lean/_harness/README.md
2026-11-18_12:20:43 ROADMAP.md            <- this session
paper/: Verified_Core_Tax_Governance_PH.md 2026-11-18_12:20:40  <- this session
        Verified_Core_Tax_Governance_PH.docx 2026-11-18_11:10:12 (untouched)
        Verified_Core_Tax_Governance_PH.pdf  2026-11-18_11:10:31 (untouched)
now = 2026-11-18_12:21:25
```

Only `paper/Verified_Core_Tax_Governance_PH.md` and `ROADMAP.md` carry this session's clock;
the `.docx` and `.pdf` predate it and were not written.

### 4.5 Abstract, title, and headline numbers

- Title block (lines 1–5) byte-identical to HEAD.
- Keywords line byte-identical to HEAD.
- Abstract: the rendered `.docx` (written 11:10, before this session) carries a copy of the
  abstract; the current Markdown abstract equals that rendered text exactly once Markdown
  emphasis markers (`*`, `` ` ``) are stripped (`identical after stripping markdown markers: True`).
  So the abstract text in the paper is unchanged by this pass.
- Number inventory in the final file: 59 (8 occurrences), 82 (5), 1,024 (2), 766 (7), 274 (8),
  254/512/32/64 all present in Table 6, Table 8, 2.6 and the roadmap. The reference list is
  contiguous 1..48 (48 entries, verified by parsing), all untouched. All 13 table captions and
  both `![...](figures/...)` lines are present; the figure lines were not touched.

## 5. What I could not verify

- The DOCX/PDF render of the new structure: rendering is out of scope here and `paper/*.docx`
  and `paper/*.pdf` were deliberately left untouched, so the new tables, the two new fenced
  blocks, the `## Appendix A.` heading and subsection 8.1 have not been visually inspected in
  Word. The converter's rules that this pass depends on (`*Table N. …*` caption shape, the
  widths comment + blank line + row form, fenced blocks, `##`/`###` headings) were read in
  `tools/md_to_docx.py` and are satisfied.
- Whether an unpinned `Table 2` mention exists in prose that refers to the *old* Table 2 by
  meaning: every surviving mention was checked against its caption in section 4.2, and the three
  ambiguous ones (362/388 for the worked certificate, 574 for engine F2, 655 for the two engine
  studies) were read in context and are correct.
- Section 8 subsection numbering: 8.1 was chosen over the brief's suggested 8.3 because Section
  8 had no numbered subsections (see 1.5).
