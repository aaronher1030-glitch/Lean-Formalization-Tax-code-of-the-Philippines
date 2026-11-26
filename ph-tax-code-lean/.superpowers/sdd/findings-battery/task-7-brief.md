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
### Task 7: Paper section, Table 9, renumbering, abstract (parallel with Tasks 8–9)

**Files:**
- Modify: `Verified_Core_Tax_Governance_PH.md` (abstract L11; insert after §5.10 ending L509; renumber Tables 9/10/11 at L596 and in-text refs; add roadmap row to Table 12; extend reproducibility paragraph L619).

**Interfaces:**
- Consumes: exact counts from Task 6 (274; 128/56/16/18/20/20/16) and the wall time printed by `tools/findings.py`.
- Produces: paper Markdown consistent with generated data; no DOCX/PDF yet.

- [ ] **Step 1: Insert §5.11 and Table 9 after the last §5.10 paragraph**

Insert between L509 (ends "...as formalized.** ..." paragraph) and L512 (`## 6. Critical Assessment`):

```markdown
### 5.11 A battery of machine-checked findings

Han et al. close their evaluation by proving 43 semantic equivalences and seven divergences between generated and gold tax-form cells in Lean. We adopt their unit of counting — a theorem relating two computations — and automate its production against the verified core. `tools/findings.py` enumerates 274 propositions over the core, renders them as Lean theorems, and lets the kernel judge them: 128 state that a certificate total equals an independently computed Python value at a named witness, closed by `rfl`; 56 are divergence counterexamples from the seeded-fault engines, each stating that an engine's claimed total differs from the kernel's total at that engine's witness, closed by `decide`; 16 are tier, eligibility, rate and regime boundary propositions at ₱3M, ₱20M and ₱1B; 38 quantify the incentive structure — the ₱20M penalty cliff and the neutrality of the ₱3M and ₱1B lines at 18 witnesses, and the 8% shelter crossover proved from both sides at ten gross-sales levels; 20 are closed-form penalty and interest identities with monotonicity instances; and 16 are unguarded-premise acceptances for L1, L2 and L5. Every proof is closed by `rfl` or `decide`. Unlike the equivalence proofs in Han et al., none uses `native_decide`, so no proof trusts the compiler and the axiom audit stays at `propext`.

The battery is not 274 loopholes. It is a count of propositions the kernel has checked, stratified by kind, and its value is the same as the engine studies': every row carries its witness and its provenance, and any row can be refuted by editing the core. The incentive families are conditional on the specification's fidelity in the same sense as L3 and L4; the gap family documents premises our checker lacks, not the law. What changes with scale is the audit surface: a reader who distrusts one finding can re-derive it in one line.

*Table 9. The findings battery, by family and kind (generated 18 November 2026).*

| Family | Kind | Findings | Witness form |
|---|---|---|---|
| Equivalence, default regime | equivalence | 32 | certificate total = Python value, eight incomes × four day counts |
| Equivalence, election regime | equivalence | 96 | certificate total = Python value, 4 × 4 × 2 × 3 grid |
| Divergence | divergence | 56 | engine claimed total ≠ kernel total, eight rows for each of seven fault engines |
| Boundary | boundary | 16 | tier, eligibility, rate and regime at ±1 centavo around ₱3M, ₱20M, ₱1B |
| Penalty cliff | incentive | 18 | tier-line penalty difference at three basic taxes × two day counts |
| Election crossover | incentive | 20 | shelter holds at the crossover income and fails one centavo below, ten gross-sales levels |
| Identities | identity | 20 | closed-form surcharge, interest, penalty and total values; monotonicity instances |
| Unguarded premises | gap | 16 | accepted certificates violating L1, L2 and L5 premises |
| **Total** | | **274** | |
```

- [ ] **Step 2: Renumber existing tables in descending order**

Run: `cd "C:/Users/Ma Christine/Downloads/LEAN FORMALIZATION OF TAX CODE/ph-tax-code-lean" && grep -n "Table 9\|Table 10\|Table 11" Verified_Core_Tax_Governance_PH.md`
Then replace, in this order: every `Table 11` → `Table 12`, every `Table 10` → `Table 11`, every `Table 9` → `Table 10` (captions and in-text references alike; do not touch Table 1–8). Re-run the grep and confirm the sequence of table numbers is monotonically increasing by first appearance.

- [ ] **Step 3: Add the abstract sentence and roadmap row**

In L11, immediately after "...submit 766 certificates judged only by the verified checkers.", insert:

```text
 An automated battery renders 274 further propositions — 128 equivalence witnesses, 56 divergence counterexamples, and 90 boundary, incentive, identity and gap findings — each checked by the same kernel at `propext`.
```

In Table 12 (roadmap), append after the last row:

```markdown
| 9. Findings battery | 274 kernel-checked propositions generated by `tools/findings.py` | **Done.** Generated, compiled and axiom-audited on 18 November 2026; not 274 loopholes — the kind column separates equivalences, divergences, incentives and gaps |
```

- [ ] **Step 4: Extend the reproducibility paragraph**

At L619, after the sentence listing `tools/loopholes.py`, append: "`tools/findings.py` regenerates the 274-finding battery, its independent Python ground truth and the eight-family report; the generated Lean file lands in `lean/_harness/` with the other harness files."

- [ ] **Step 5: Verify**

Run: `cd "C:/Users/Ma Christine/Downloads/LEAN FORMALIZATION OF TAX CODE/ph-tax-code-lean" && grep -n "Table [0-9]" Verified_Core_Tax_Governance_PH.md | head -40 && grep -c "274" Verified_Core_Tax_Governance_PH.md`
Expected: no duplicate table numbers; `274` appears at least four times (section, table, abstract, roadmap); Table 12 is the roadmap.

- [ ] **Step 6: Verify and leave uncommitted**

Run: `cd "C:/Users/Ma Christine/Downloads/LEAN FORMALIZATION OF TAX CODE/ph-tax-code-lean" && git status --short Verified_Core_Tax_Governance_PH.md`
Expected: modified; not staged.

---

