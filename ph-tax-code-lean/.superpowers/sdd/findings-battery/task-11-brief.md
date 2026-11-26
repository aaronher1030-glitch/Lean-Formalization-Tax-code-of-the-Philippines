# Task brief (generated from the plan)

Read the plan section below as your requirements. Also binding: the Global
Constraints section of the plan, reproduced here:

- Lean 4.35.0 pinned toolchain, core library only.
- No `native_decide`, no `sorry`; axiom audit must stay at `propext`.
- Do NOT stage, commit, or push anything (standing user rule).
- Python runs as `python -X utf8`; writes use encoding="utf-8".
- Generated `lean/_harness/Findings.lean` stays gitignored.
- `LEAN` env override honored; default ROOT/tools/lean/dist/lean-4.35.0-windows/bin/lean.exe.
- 59/82 hand-written counts must not change.
- Windows: run from repo root `C:/Users/Ma Christine/Downloads/LEAN FORMALIZATION OF TAX CODE/ph-tax-code-lean`.
- Toolchain export for compiles: LEAN="C:/Users/Ma Christine/Downloads/LEAN FORMALIZATION OF TAX CODE/tools/lean/dist/lean-4.35.0-windows/bin/lean.exe".

Frozen row schema for any task using rows:

    {"id": "F001", "family": "...", "kind": "equivalence|divergence|boundary|incentive|identity|gap",
     "theorem": "f001_<family>_001", "prop": "...", "tactic": "rfl"|"decide",
     "witness": "...", "value": int|None, "source": "...", "note": "..."}

---
### Task 11: Sync root copies and end-to-end verification from the repo

**Files:**
- Copy: repo artifacts to workspace root (`tools/findings*.py`, `data/findings.csv`, `FINDINGS.md`, paper `md/docx/pdf`).
- Modify: project memory `C:\Users\Ma Christine\.qoder\projects\C--Users-Ma-Christine-Downloads-LEAN-FORMALIZATION-OF-TAX-CODE\memory\project-ph-tax-code-lean-repo.md`.

**Interfaces:**
- Consumes: Tasks 6–10 outputs.
- Produces: root workspace mirrors; a verified, still-uncommitted repo; memory updated.

- [ ] **Step 1: Copy to the workspace root**

Run:

```bash
cd "C:/Users/Ma Christine/Downloads/LEAN FORMALIZATION OF TAX CODE" && cp ph-tax-code-lean/tools/findings*.py tools/ && cp ph-tax-code-lean/data/findings.csv data/ && cp ph-tax-code-lean/FINDINGS.md . && cp ph-tax-code-lean/Verified_Core_Tax_Governance_PH.md ph-tax-code-lean/Verified_Core_Tax_Governance_PH.docx ph-tax-code-lean/Verified_Core_Tax_Governance_PH.pdf .
```

Expected: no errors.

- [ ] **Step 2: End-to-end run from the repo copy**

Run:

```bash
cd "C:/Users/Ma Christine/Downloads/LEAN FORMALIZATION OF TAX CODE/ph-tax-code-lean" && export LEAN="C:/Users/Ma Christine/Downloads/LEAN FORMALIZATION OF TAX CODE/tools/lean/dist/lean-4.35.0-windows/bin/lean.exe" && bash lean/run_demo.sh && python -X utf8 -m unittest discover -s tools -p "test_findings_*.py" -v && python -X utf8 tools/findings.py && echo E2E_OK
```

Expected: build exit 0, 19 tests OK, `PASS: 274 findings ... axioms: propext only`, `E2E_OK`.

- [ ] **Step 3: Confirm repository state**

Run: `cd "C:/Users/Ma Christine/Downloads/LEAN FORMALIZATION OF TAX CODE/ph-tax-code-lean" && git status --short && git log --oneline -1`
Expected: last commit still `91b2607`; modified tracked docs + untracked new files; `lean/_harness/Findings.lean`, `*.olean` absent from status (ignored).

- [ ] **Step 4: Update project memory**

Append to `project-ph-tax-code-lean-repo.md` under the existing 18 Nov 2026 paragraph:

```markdown
19 Nov 2026 (uncommitted): findings battery — tools/findings{.py,_spec,_families,_render,_report}.py
plus 5 unittest files generate 274 kernel-checked findings in 8 families
(equivalence 128, divergence 56, boundary 16, cliff 18, crossover 20,
identity 20, gap 16), all rfl/decide, axioms propext only; outputs
data/findings.csv + FINDINGS.md; paper §5.11 + Table 9 (old 9/10/11 → 10/11/12);
STATUS/THEOREMS/README/ROADMAP/.gitignore/_harness README updated.
Not 274 loopholes: kind column separates equivalences, divergences,
incentives and gaps. Nothing committed.
```

- [ ] **Step 5: Final report**

Report to the user: the exact counts printed by the tool, wall time, axiom result, test count, the pages containing §5.11, and that everything remains uncommitted. State explicitly what was not done: no practitioner review, no commit, no MSP abstract change.

---

## Self-Review

- **Spec coverage:** all eight families, the driver, outputs, tests, paper, repo docs, PDF and verification are each owned by a task; the MSP abstract is explicitly out of scope.
- **Placeholder scan:** every code step contains complete code; doc steps contain the literal text to insert; no "TBD", no "similar to Task N".
- **Type consistency:** the row schema in File Structure matches the keys used by `findings_families`, `findings_render`, `findings_report` and the driver tests; `summary`, `csv_text`, `markdown`, `write_outputs`, `render`, `all_findings`, `FAMILY_COUNTS` are used exactly as defined.
- **Counts:** 32+96+56+16+18+20+20+16 = 274; 128 equivalence + 56 divergence + 90 other = 274; the abstract sentence uses exactly these splits.

