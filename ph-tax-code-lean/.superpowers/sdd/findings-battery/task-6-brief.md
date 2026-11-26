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
### Task 6: Kernel run, timing, and output verification

**Files:**
- Modify (only if timing demands): `tools/findings_render.py`
- Generated: `lean/_harness/Findings.lean`, `data/findings.csv`, `FINDINGS.md`

**Interfaces:**
- Consumes: Task 5 CLI.
- Produces: the three artifacts with 274 rows and an axiom log containing only `propext`.

- [ ] **Step 1: First full kernel run**

Run: `cd "C:/Users/Ma Christine/Downloads/LEAN FORMALIZATION OF TAX CODE/ph-tax-code-lean" && export LEAN="C:/Users/Ma Christine/Downloads/LEAN FORMALIZATION OF TAX CODE/tools/lean/dist/lean-4.35.0-windows/bin/lean.exe" && time python -X utf8 tools/findings.py`
Expected: `PASS: 274 findings kernel-checked in <N> s; axioms: propext only`, eight family rows, `wrote ...findings.csv and ...FINDINGS.md`.

- [ ] **Step 2: If any theorem fails, fix the witness, never the tactic claim**

For each `Findings.lean:<line>` reported, read the rendered theorem, compare the Python literal with `findings_spec`. The usual cause is an integer witness mismatch; correct the family builder so Python and the kernel agree. Never replace `rfl` with `native_decide`, never add `sorry`, never weaken an equality to an inequality. Re-run Step 1 after each fix.

- [ ] **Step 3: Confirm performance and axiom profile**

Run: `cd "C:/Users/Ma Christine/Downloads/LEAN FORMALIZATION OF TAX CODE/ph-tax-code-lean" && python -X utf8 -c "print(open('data/findings.csv', encoding='utf-8').read().count(chr(10))-1)"` and `grep -c "#print axioms" lean/_harness/Findings.lean`
Expected: `274` and `8`. Wall time under 900 s; note the exact seconds for Task 7 and STATUS.md.

- [ ] **Step 4: Independent audit of the audit**

Run: `cd "C:/Users/Ma Christine/Downloads/LEAN FORMALIZATION OF TAX CODE/ph-tax-code-lean" && export LEAN_PATH="$PWD/lean" && "$LEAN" lean/_harness/Findings.lean 2>&1 | grep -E "depends on axioms|does not depend" | sort | uniq -c`
Expected: lines showing `[propext]` and/or "does not depend on any axioms" only; zero occurrences of `sorryAx`, `Classical.choice`, `Lean.ofReduceBool`.

- [ ] **Step 5: Confirm nothing else broke**

Run: `cd "C:/Users/Ma Christine/Downloads/LEAN FORMALIZATION OF TAX CODE/ph-tax-code-lean" && export LEAN="C:/Users/Ma Christine/Downloads/LEAN FORMALIZATION OF TAX CODE/tools/lean/dist/lean-4.35.0-windows/bin/lean.exe" && bash lean/run_demo.sh && echo BUILD_OK`
Expected: `BUILD_OK` (seven hand-written files unchanged, exit 0).

- [ ] **Step 6: Verify and leave uncommitted**

Run: `cd "C:/Users/Ma Christine/Downloads/LEAN FORMALIZATION OF TAX CODE/ph-tax-code-lean" && git status --short | head -30`
Expected: no tracked file modified except none; new artifacts listed as untracked. No staging.

---

