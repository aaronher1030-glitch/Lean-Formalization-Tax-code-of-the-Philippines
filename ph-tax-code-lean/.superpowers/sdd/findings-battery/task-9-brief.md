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
### Task 9: FINDINGS.md review and loophole cross-link (parallel with Tasks 7, 8)

**Files:**
- Modify: `FINDINGS.md` (generated — edit only the framing paragraphs if needed; never edit rows or counts), `LOOPHOLE_FINDINGS.md` (Reproduce section).

**Interfaces:**
- Consumes: generated `FINDINGS.md` from Task 6; `data/findings.csv` for row examples.
- Produces: consistent framing across the two findings documents.

- [ ] **Step 1: Verify the generated framing against the claim ladder**

Read `FINDINGS.md`. Confirm it states: (a) the number, (b) the kind split, (c) "not 274 loopholes", (d) the `native_decide` contrast, (e) conditional-on-spec-fidelity for incentive rows. If any is missing or overstated, edit only the intro/honesty prose — not the summary table and not any generated row.

- [ ] **Step 2: Cross-link from LOOPHOLE_FINDINGS.md**

In its "Reproduce" section, append:

```markdown
A generated battery of 274 kernel-checked propositions that extends these
five findings — 128 equivalences, 56 divergence counterexamples, and 90
boundary, incentive, identity and gap propositions — is documented in
[FINDINGS.md](FINDINGS.md); the two documents use the same kind labels, and
neither claims that encoding gaps are properties of the real tax code.
```

- [ ] **Step 3: Verify**

Run: `cd "C:/Users/Ma Christine/Downloads/LEAN FORMALIZATION OF TAX CODE/ph-tax-code-lean" && grep -n "274\|not 274\|native_decide" FINDINGS.md LOOPHOLE_FINDINGS.md`
Expected: framing sentences present in both; no sentence claims 274 legal loopholes.

- [ ] **Step 4: Verify and leave uncommitted**

Run: `cd "C:/Users/Ma Christine/Downloads/LEAN FORMALIZATION OF TAX CODE/ph-tax-code-lean" && git status --short FINDINGS.md LOOPHOLE_FINDINGS.md`
Expected: `FINDINGS.md` untracked (generated), `LOOPHOLE_FINDINGS.md` modified or untracked as before; not staged.

---

