# Design: PhilConst — a Lean 4 architecture for formalizing the 1987 Philippine Constitution

Date: 2026-11-17 · Status: design approved by the user ("Yes", 2026-11-17) ·
Phase 2 proposal · **Implementation deferred** until after the MSP Region 3
submission (abstract deadline 2026-11-20; convention 2026-12-04) and a
separate implementation approval.

## Context and recorded decisions

The project already holds a verified tax core: six Lean files, 859 lines,
54 theorems, 64 kernel-checked examples, zero `sorry`; three proven
certificate checkers (`check`, `checkT`, `check8`); four mutation-proven
guards; a 32-case dual-ground-truth benchmark; a 254-certificate engine
study with zero false accepts; an unsigned legal-review packet; a committed
local repository (`ph-tax-code-lean`, commit `91b2607`, never pushed).

Decisions taken in conversation on 2026-11-16/17:

1. The MSP abstract keeps the v2 phrasing adapted from Han et al.
   (arXiv:2610.02792); it is the submission draft.
2. The tax core remains the focus now. Nothing in this spec is built yet.
3. A consultation transcript proposing a three-library "computational
   governance" program (PhilConst / PhilLaw / PhilStats / PhilGov) was
   assessed: its honesty mechanisms are adopted, its scope and its
   lookup-table Lean example are rejected. A `trivial` proof over a
   case-split definition cannot fail and therefore proves nothing; every
   encoding here must carry a guard that a mutation can break.
4. The user's longer-term vision includes a politician scorecard modeled on
   cadre-evaluation systems (weighted indicators plus veto items). It is
   parked on the vision shelf below, not in scope.

## Design principles

- **Provenance first.** No anonymous definitions: every encoded provision
  carries its source text, citation, interpretation, assumptions, and
  reviewer field.
- **Two species of provision.** Counting/procedural rules are computable
  and decidable; standards (due process, equal protection, "equitable")
  are obligations on procedure, never predicates on outcomes.
- **Three verdicts, and a theorem about them.** `verified`, `violated`,
  `undetermined`; the system is *proved* unable to claim certainty where a
  standard is involved.
- **Certificates, not trust.** Institutional actions submit certificates;
  a small proven checker accepts only what follows the encoded grant,
  thresholds, and procedure — the tax pattern extended.
- **The constitution constrains the statute as a theorem.** The integration
  layer's first content is a proved bridge from Art. VI Sec. 28(1) to the
  existing tax core, not a diagram.

## Layer 1 — Provenance record

```lean
structure Provision where
  id : Nat
  source : String          -- verbatim constitutional text
  citation : String        -- Official Gazette URL, article, section
  concept : String         -- legal concept represented
  interpretation : String  -- human reading, including rounding/denominator choices
  assumptions : List String
  reviewer : Option String -- none until a constitutional lawyer signs
```

Every definition and theorem in Layers 2–4 references a `Provision.id`.
The tax review packet's S-item format generalizes to this record; the
packet for PhilConst is signed by a constitutional lawyer, not a tax
practitioner.

## Layer 2 — Two encodings and the humility theorem

Counting rules become `Nat` arithmetic with cross-multiplied inequalities
so that no rounding mode is silently chosen: "two-thirds of all its
Members" is `votes * 3 ≥ allMembers * 2`, and the choice to read the
threshold this way (rather than a rounded quotient) is an explicit
`interpretation` field, reviewed like any other assumption.

Standards become lists of procedural obligations (notice, hearing,
authority, reasoned decision). The decidable prerequisites are checked as
procedure steps and can yield `violated` when absent; the standard's
substance is never evaluated, so any action invoking a standard carries
`undetermined` for that standard, and the overall verdict is `verified`
only when no standard is invoked.

```lean
inductive Verdict | verified | violated | undetermined

-- target theorem (machine-checked humility):
theorem no_false_certainty (a : ActionCert) (h : a.standards ≠ []) :
    checkA a ≠ .verified
```

This is the consultation transcript's best idea turned from policy into
proof: the checker cannot manufacture legal certainty about standards.

## Layer 3 — Authority certificates

```lean
structure ActionCert where
  grant : Nat               -- Provision.id claimed as authority
  action : ActionKind
  steps : List ProcedureStep
  allMembers present votes : Nat
  standards : List StandardObligation
  claimedAuthority : Bool
```

`checkA` verifies, conjunct by conjunct: the grant applies to the action
kind (structural correspondence); each threshold holds on the *correct
denominator* (denotational correspondence); required procedural steps are
present; standards route to `undetermined` per Layer 2. Targets:
`checkA_sound` (accepted ⇒ the action satisfies every encoded requirement)
and `checkA_complete` (an honestly built certificate is accepted), both
relative to the encoded specification, exactly as `checkT_sound` /
`checkT_complete` are.

Guards, each mutation-proven necessary before the layer is claimed done:

| Mutation | Expected failure |
|---|---|
| delete a threshold conjunct | the corresponding soundness proof fails; an under-voted action is accepted |
| swap denominator (`allMembers` ↔ `present`) | the denominator boundary theorem fails; boundary examples refuted |
| drop a required procedural step | step-completeness proof fails; a notice-less action is accepted |
| accept a mismatched grant | grant-application proof fails; an ultra-vires action is accepted |
| force `verified` on a standard | `no_false_certainty` fails |

## Layer 4 — The constitutional–statutory bridge

Art. VI Sec. 28(1): "The rule of taxation shall be uniform and equitable.
The Congress shall evolve a progressive system of taxation." Two decidable
shadows over the *existing* tax core, one standard left open:

- **Uniformity** as identity-invariance: the certificate type carries no
  taxpayer identity, status, or discretion field, and the statutory total
  depends only on the computational fields. Target: for accepted
  `c₁ c₂ : CertT` with equal `grossSales`, `income`, `daysLate`,
  `c₁.total = c₂.total` (a corollary of `checkT_sound`, since both totals
  reduce to `totalDueT (classify gs) (bracketTax income) days`). Uniformity
  is proved as the absence of discriminatory parameters, not asserted.
  (A verdict-level invariance claim would be false — `checkT` also checks
  the claimed tier and lines — so the theorem is stated over accepted
  totals, where it is true.)
- **Progressivity** as a non-decreasing average rate, cross-multiplied to
  stay division-free: target `theorem progressive {a b : Nat} (h : a ≤ b) :
  bracketTax a * b ≤ bracketTax b * a`. Proof obligation: interval case
  analysis over the five brackets using the existing slice lemmas; the
  division-free style that kept kernel certificates small in `Opt8.lean`.
- **Equitable** is a standard: `undetermined`, per Layer 2. No theorem
  claims to decide it.

## MVP scope (phase 2, first build)

| Provision (to be pinned against the Official Gazette text first) | Encoded content | Candidate theorems |
|---|---|---|
| Art. VI Sec. 16 | quorum majority; two-thirds expulsion of all Members; one-fifth yeas-and-nays of Members present | threshold monotonicity; denominator boundary theorem (exactly when "all" vs "present" readings disagree, in the spirit of `vat_tier_gap`) |
| Art. XI Sec. 3 | one-third House initiation; two-thirds Senate conviction, all Members | threshold guards; conviction-denominator boundary |
| Art. XVII Sec. 1 | three-fourths of all Members for constituent-assembly proposal | supermajority guard; comparison with alternative readings |
| Art. VI Sec. 28(1) | uniformity + progressivity bridge to the tax core | `uniformity`, `progressive`; "equitable" undetermined |
| Art. III Sec. 1 | procedural obligations only | `no_false_certainty` demonstration |

Target: four Lean files, 15–20 theorems including one denominator boundary
theorem and `no_false_certainty`; kernel-checked examples at every
threshold ±1 vote; the same `run_demo.sh`-style single-script rebuild; a
constitutional-lawyer review packet in the S-item format.

## Evaluation

Same five dimensions as the tax study: agreement with expert-reviewed
interpretations (the signed packet); kernel acceptance; completeness of
conditions and exceptions (disclosed per provision); consistency via
mutation detection; traceability via `Provision.id` back to Gazette text.
Plus the humility theorem as a sixth, constitution-specific dimension.
An engine study against `checkA` (faulty vote-counting implementations,
LLM sessions) is a later extension, mirroring how `checkT` was measured;
it is not part of the MVP claim.

## Honesty constraints

- Soundness is always relative to the encoded specification; the
  specification's fidelity to constitutional law awaits a constitutional
  lawyer's signature, exactly as the tax spec awaits a tax practitioner's.
- Standards are never decided. Any output touching them is `undetermined`,
  and the system proves it cannot say otherwise.
- Coverage claims stay fractional and explicit (five provisions of the
  Constitution, computational parts only), never "the Constitution
  formalized".
- Section numbers and quoted text are pinned against the Official Gazette
  before encoding; no guessed citations enter the artifact.

## Vision shelf (explicitly not deliverables of this spec)

- **PhilStats.** PSA national-accounts identities (GDP expenditure
  components) as integer/rational equalities checked against published
  tables. Cheap, genuinely verifiable; positioned as data verification,
  not deep mathematics.
- **Politician scorecard.** Cadre-evaluation-style scoring: weighted
  indicators plus veto items ("one-vote veto" as a guard). Formal content:
  veto discontinuity, monotonicity when no veto fires, constructed gaming
  counterexamples (Goodhart in theorem form). Requires political-science
  review of the indicator reading; same certificate pattern.
- **PhilGov.** An integration/simulation environment with an AI interface.
  The existing engine study is already the controlled
  AI-with-verification experiment; PhilGov remains a vision paragraph.

## Out of scope

Encoding standards as outcome predicates; formalizing the whole
Constitution or whole NIRC; implementing PhilStats, the scorecard, or
PhilGov; any AI simulation; any change to the submitted abstract or the
tax core; publishing anything to GitHub.

## Deferred implementation and next steps

1. After the 2026-11-20 submission: pin the five provisions' text and
   section numbers from the Official Gazette; archive extracts under
   `data/sources/` in the repository.
2. Separate user approval, then the writing-plans skill produces the
   implementation plan; build proceeds file by file with the mutation
   discipline above.
3. This spec stays uncommitted in the repository until the user asks for
   a commit; the repository's single initial commit remains the only
   commit until then.