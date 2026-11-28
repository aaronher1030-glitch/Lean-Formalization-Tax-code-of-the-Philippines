# Deep Research: A Distributed, Cluster-Partitioned Formalization of a Tax Code

**What the P vs NP public proof desk actually proved, why tax law breaks the model, and a concrete design for an open contribution network built on this repository.**

Prepared 27 November 2026. Companion to `DEEP_RESEARCH_LEAN_TAX_GOVERNANCE.md` and `DEEP_RESEARCH_VENUES_GAPS_HURDLES.md`; it assumes their findings and does not repeat the bibliography except where a claim is new here.

---

## 0. The answer in one page

**The idea works, but not for the reason the P vs NP project works.**

pequalnp.com succeeded because a Lean-checked lemma is *unconditionally* true relative to definitions everybody already accepts. Its completion criterion is a kernel exit code. Tax formalization has no such oracle: a kernel accepts a proof of a *reading* of the statute, and the reading is the contested object. Copy the desk, the leases, the one-file-per-gap rule and the CI gate — they are good engineering — and you will have built a machine that distributes **unreviewed legal interpretations** at scale. That is worse than having none, because a proof badge reads as authority.

The correction is small and cheap, and this repository already half-implements it:

> **Two keys, not one.** The kernel certifies the proof. A named practitioner certifies the statement. Nothing enters the merged library with only one key.

Once you make that change, the design changes in four useful ways:

1. **Statements, not proofs, are the scarce resource.** So the platform's job is to curate statements (and their citations) and let proof work — human or agent — be as open and as cheap as possible.
2. **Ambiguity becomes output.** Where two readings of a provision differ, the deliverable is a kernel-checked divergence theorem, not a vote. That is exactly what this repo already does with `vat_tier_gap` and the five loophole findings.
3. **Clusters are not a metaphor.** The NIRC has 292 sections across 14 titles and an explicit cross-reference graph. Partition it by citation dependency — strongly connected components, topologically ordered — and you get atomic, assignable, parallelizable work units with a real dependency frontier.
4. **Volunteer compute helps with search and review support, almost not at all with checking.** Kernel checking is cheap and should be centralized behind CI. What scales horizontally is proof search, statement drafting, counterexample hunting, and — the actual bottleneck — reviewer attention.

**Verdict:** a strong project, conditionally. It is a *distribution and legitimacy* innovation, not a scientific one: the protocol already exists in the literature (Prove2Me, Choir), and Lean tax formalization is now a crowded space (Catala in production, Lexifina's 199-country corpus, Law&Order, the US Code repo). What does not exist is a jurisdiction-specific, openly contributed, **review-gated** tax formalization with a proven certificate checker — and none in Southeast Asia that this review could find. That is the defensible gap. Section 12 gives the score and the one decision that determines whether this succeeds.

---

## 1. The justification, stated so that it survives scrutiny

The weakest version of the pitch is "formalize the tax code to find loopholes and raise revenue." It is weak because formalization collects nothing, finds policy choices rather than bugs, and cannot fix a rule that is unlawful. The version that survives is narrower and better evidenced.

### 1.1 Four failure classes, and which one verification addresses

| Class | Example | What went wrong | Does formal verification help? |
|---|---|---|---|
| **Wrong rule** | Robodebt, Australia | Income averaging was not a lawful basis for raising debts; ~470,000 erroneous notices; >A$1.2bn in claimed repayments; ~A$2.4bn redress package; net cost of the scheme itself ~A$565m | **No.** A proof would have verified the unlawful rule faithfully. A *readable, versioned spec* might have made the averaging assumption easier to challenge — that is the only real benefit. |
| **Wrong implementation of a rule** | Horizon, UK Post Office | Bugs in accounting software produced shortfalls blamed on 900+ sub-postmasters | **Yes.** This is the target class. |
| **Wrong premises about facts** | MiDAS, Michigan | Automated fraud findings; ~93% of ~22,000 reviewed determinations involved no fraud | **No.** Facts are inputs. |
| **Uncontestable output** | Toeslagenaffaire, Netherlands | Rule-of-law failures, all-or-nothing recovery, no usable explanation | **Partly.** A line-by-line certificate gives a person something specific to challenge. |

The honest claim is therefore about **fidelity of implementation and contestability of explanation**, not about lawful policy or correct facts. Stated that way, it is defensible and it is exactly what the certificate architecture in this repo delivers.

### 1.2 Why tax, and why now

- **The money is large and the leakage is structural.** The World Bank's 2026 Philippines Public Finance Review puts the tax-to-GDP ratio at **14.6% in 2025**, with combined VAT, corporate and personal income tax gaps **above 11% of GDP**; only **26.7% of corporate income tax potential** is collected (≈3.0% of GDP), and about **40.6% of VAT potential**. For comparison, the US IRS projects a **$696bn gross tax gap** for tax year 2022 (85.0% voluntary compliance rate).
- **None of that gap is an arithmetic bug.** Leakage is driven by policy, exemptions, informality and enforcement. Formalization's contribution is not to close the gap; it is to make the *computational* layer of assessment — brackets, thresholds, tiers, elections, penalties, rounding — exactly reproducible and challengeable, so that disputes are about facts and law rather than about whether the software added correctly.
- **LLMs are now in the loop and are not good enough alone.** On TaxCalcBench, frontier models computed **fewer than one third** of federal returns correctly. The Law&Order pipeline (LLM synthesis + cell-level symbolic verification + repair) reports **100% cell- and form-level accuracy on 51 held-out returns against 66% for the best LLM alone** — a preprint, but the direction is unambiguous. Verification is what turns a plausible-looking tax answer into an auditable one.
- **The Philippines has mandated the digitization.** EOPT (RA 11976) requires BIR digitalization and reclassifies taxpayers; the E-Governance Act (RA 12254, 2025) mandates digital government services. Once assessment is software, "is the software right?" becomes a legal question with a technical answer, and someone has to be able to answer it.

### 1.3 The counter-evidence you must cite against yourself

Formal-ish encodings of tax law are routinely wrong in ways their authors did not see, and this is the strongest argument *for* the review gate rather than against the project:

- Lexifina reports that **Catala** — the French production language, with a verified compiler and lawyer-readable output — passes its own tests but was wrong on **18 of 209** simulator returns in their cross-check, and that public calculators and printed tables contain cell-level errors. (Company blog, not peer-reviewed; tier T3.)
- This project's own first specification omitted RA 11976's micro/small concessions and **the checker happily accepted the wrong totals** until the spec was repaired. That is the paper's central finding and it should be the platform's founding cautionary tale.
- Lexifina also reports **138 real drafting faults** in the US Code found by checking cross-references, and errors in live government calculators. A formalization that reads the statute carefully is, incidentally, a very effective statute *proofreader*.

So: proofs do not make a model right. They make a model's consequences explicit, and they make every later change to the reading break something loudly. That is the product.

### 1.4 The four claims to make, and the one never to make

| # | Claim | Support |
|---|---|---|
| J1 | A bounded, machine-checked core makes a class of assessment errors mechanically detectable | This repo: 766 certificates, 16 engines, **0 false accepts**; a one-centavo rounding fault caught |
| J2 | A certificate gives a person a line-by-line reason they can contest | Certificate architecture; `checkT_sound` / `check8_sound` |
| J3 | A formal spec is a **regression suite for legislation**: when the law moves, the dependent proofs break at the exact statement | The EOPT tier repair broke exactly the expected proofs |
| J4 | Open contribution can surface competing readings faster than a closed team, *if* review is the merge gate | Section 7's reviewer arithmetic |

**Never claim:** that a kernel-accepted theorem is a lawful assessment, that this finds "BIR loopholes," or that it raises revenue. Keep the repo's existing honesty notes verbatim in any public launch.

---

## 2. State of the art: six families, one empty chair

| Family | Representative | Scale | Machine-checked? | Fidelity evidence | Tier |
|---|---|---|---|---|---|
| Legal DSL, production | **Catala** (Inria; DGFiP, CNAF) | French tax + family benefits; CNAF committed 2026 | Compiler components verified; not a proof of the encoded law | Lawyer-readable PDF for review; found bugs in official implementations | T1/T2 |
| Rules-as-code platforms | **OpenFisca**, OECD *Cracking the Code*, NZ Better Rules | Many jurisdictions, microsimulation | No | Tests against official calculators | T1/T2 |
| Breadth-first Lean | **kavanaghpatrick/us-tax-code-lean** | 765 IRC sections, ~537k lines, 607 theorems, 17 `sorry` | Yes, self-reported, AI-generated | None published | T3 |
| Neuro-symbolic autoformalization | **Law&Order** (arXiv 2610.02792) | US federal forms, 51 held-out returns | Cell-level verification | 100% vs 66% LLM-alone | T2 (preprint) |
| Global corpus + audit | **Lexifina / global-law** | 197 countries' income tax, 1,864 of 2,597 other taxes, 4,080 theorems, 6,875 worked examples; CC0 | Yes | Cross-checked against government tables, calculators, other open models; found errors | T3 (company, but unusually detailed) |
| Depth-first, with a checker | **This repo** | 7 NIRC sections, 1,024 lines, 59 theorems, 0 `sorry`, proven sound+complete checkers | Yes, axiom-audited | Dual-implementation benchmark, 766-certificate engine study, 5 kernel-checked loophole findings | T1-equivalent artifact |

**What is genuinely unoccupied,** after this sweep:

1. **A jurisdiction-specific formalization that is openly contributed and review-gated.** Lexifina is a company corpus; the US repo is one author plus AI; Catala is institutional. None publishes a per-statement reviewer signature as a merge condition.
2. **Southeast Asian coverage.** No Philippine (or regional) Lean formalization was found in this or the earlier searches. Absence of evidence, not evidence of absence.
3. **A published protocol for legal-fidelity gating of crowd contributions.** Prove2Me and Choir solve decomposition and deterministic gating for *mathematics*; neither addresses a ground truth that is institutional rather than mathematical.

That third point is the publishable contribution. The first two are the reason to build it here.

---

## 3. The P vs NP experiment, decoded mechanically

### 3.1 What happened

pequalnp.com went live 22 November 2026, run by Brilliant (Amichai Mantinband and Lior), as a public attempt at P vs NP with a fleet of AI agents and a Lean 4 kernel as the only judge. Self-reported counters: 1,129 of 2,027 lemmas checked by 23 November with 317 agents and 8,145 sessions; by day three, **8.6M lines of Lean from 360+ external contributors**, 1.8M accepted and merged, 3.1M in review, 2,000+ checked lemmas, 4,000+ forks. Roughly half the checked total came from outside agents.

### 3.2 The unit of work

One **gap** = one statement in Lean that still needs a proof. The desk returns: the gap id, the exact Lean statement, the one file to write, the module name, and the modules the file may import. The contributor proves *exactly that statement, in exactly that file*, and opens a pull request adding only that file.

### 3.3 The protocol

| Endpoint / step | Behaviour |
|---|---|
| `GET /desk/next?handle=` | Assigns one gap; `&another=1` for a second; `&hard=1` for a stuck open problem; max 5 leases per handle |
| `POST /desk/beat?lease=` | Lease keep-alive every ≤45 min, 6 h maximum |
| `POST /desk/release?lease=&reason=` | Reason taxonomy: `hypothesis_too_weak`, `missing_lemma`, `statement_seems_false`, `out_of_time`, `other` |
| PR | One branch, one commit, one file, one theorem named after its module; helpers only inside the namespace |
| Credit | Accepted-and-merged ⇒ lemma recorded as checked, with the PR author as contributor |

### 3.4 The six acceptance invariants

1. Builds with the **pinned** toolchain and pinned Mathlib.
2. **No `sorry`** anywhere under the theorem.
3. Only the three standard axioms (`propext`, `Classical.choice`, `Quot.sound`); no added axioms, no `native_decide`.
4. The theorem proves **exactly the posted statement**, read against the project definitions — not against anything the contributor's file declares, so a local notation or instance cannot change meaning.
5. Imports limited to Mathlib plus the listed project modules.
6. Output is one line: `ACCEPTED` or `REJECTED (<reason>)`.

### 3.5 Why it worked

- **Verification is objective and cheap.** No reviewer judgement is needed to know whether the lemma is proved.
- **Statements are frozen before work starts.** The scarce good (what to prove) is produced centrally; the abundant good (proof attempts) is produced by the crowd.
- **Contributions compose.** One file, one theorem, one import list — no merge conflicts, no design negotiation.
- **Failure is recorded, not hidden.** Refutations and releases are first-class outcomes.

### 3.6 What it did not do

By its own front page and by press commentary: the answer remains open. 1,129 checked lemmas are **labour, not a proof** — they make no claim that P vs NP is settled. That is the correct epistemic posture and it is the part most worth copying.

### 3.7 Three properties that do not transfer to law

| Property in math | In tax law | Consequence |
|---|---|---|
| Ground truth is mathematical truth; Mathlib is a shared, uncontested base | Ground truth is *the statute as authoritatively read*: text, amendments, regulations, rulings, practice, courts | Definitions cannot be frozen by a curator alone; they need a citational warrant |
| A statement is either provable or not; a false statement is refuted by counterexample | A statement can be **faithful to one reading and false to another**, with no counterexample available because the disagreement is interpretive | Divergence, not refutation, is the characteristic output |
| Being wrong costs a wasted proof | Being wrong produces a confident, machine-checked **wrong legal conclusion** about someone's money | The cost asymmetry forbids "kernel accepts ⇒ publish" |

---

## 4. The transfer problem

### 4.1 Four consequences

**(a) Two keys.** Merge requires `kernel_accepted` **and** `review_signed`. The reviewer signs the *statement and its citation*, never the proof. This is Prove2Me's "audited core" insight — humans audit a small curated set of statements, agents supply unlimited detail — grafted onto Choir's deterministic gate. Neither paper applies it to a contested, institutional ground truth; that is the novel bit.

**(b) Curate statements, open everything else.** A tax formalization has roughly 10–30 statements per formalizable section. At 292 sections, that is thousands of statements. If each needs a lawyer, the project is dead. So: reviewers sign a **thin spine** — the definitions, the rate/threshold functions, and one statement per statutory sentence — and *derived* lemmas inherit the spine's warrant automatically, exactly as Prove2Me's milestones make downstream proofs buildable without re-audit.

**(c) Divergence is a deliverable.** When two readings differ, do not resolve by vote. Encode both, prove they differ, and file the pair as an `X` unit for the reviewer. This repo's `vat_tier_gap` (exactly one peso value is VAT-exempt yet not micro, because two statutes use `≤` and `<`) is the template. It is simultaneously a bug report, a legal question, and a theorem — and it is the single most valuable artefact type the project can produce.

**(d) Every unit carries provenance.** Citation, quoted text, a hash of that quote into the archived source, effective dates. Without this the desk cannot reject a unit for being untethered, and the library degrades into plausible Lean.

### 4.2 The asymmetry, in one line

> In mathematics the kernel is the oracle. In tax the kernel is a *type checker for an argument about the law*; the oracle is a practitioner reading a versioned text.

Everything below follows from that sentence.

---

## 5. Cluster design

### 5.1 Partitioning: use the statute's own graph

Tax codes are better suited to clustering than open mathematics problems, because the dependency structure is written down as cross-references.

**Algorithm** (offline, deterministic, re-runnable on each amendment):

1. **Extract** every section and its references from the versioned text, including verbal forms ("paragraph (2) of subsection (b)", "sections 922 through 927", "such subparagraph"). Lexifina reports doing exactly this for Title 26 and finding 138 real drafting faults in the process — so the extractor doubles as a statute proofreader.
2. **Build** a directed graph `section → referenced section`, labelled by reference type (definitional, rate, procedural, penalty, effective-date).
3. **Condense** strongly connected components. An SCC is an atomic cluster: its members cannot be formalized independently without circularity.
4. **Topologically order** the condensation. The order *is* the contribution frontier: a unit is `open` only when all definitional dependencies are `merged`.
5. **Weight** each cluster by computational density (fraction of its text that is arithmetic, thresholds, tables, or eligibility logic), not by section number.

**Steps 1–4 have been run.** `tools/cluster_graph.py` parses the RA 8424 body
(`data/ra8424.html`, 292 sections), extracts **163 section-level references**,
condenses the resulting digraph into **264 strongly connected components**, and
topologically orders the condensation. Method, measurements and the full cluster
worklist are in [`NIRC_CLUSTER_GRAPH.md`](NIRC_CLUSTER_GRAPH.md); the machine
readable outputs are `data/nirc_refs.csv`, `data/nirc_sections.csv`,
`data/nirc_clusters.csv` and `data/nirc_cluster_graph.json`. Re-run with
`python -X utf8 tools/cluster_graph.py`.

**What the measurement says.** Three things, one of them unexpected. The tables
themselves stay in the generated report —
[`NIRC_CLUSTER_GRAPH.md`](NIRC_CLUSTER_GRAPH.md) — and are deliberately not
restated here: a table copied into two documents stops being one measurement and
becomes two claims that can drift apart.

*The graph is sparse.* At section granularity the mean out-degree is well below
one, more than two thirds of sections reference no other section at all, and the
condensation is therefore almost a singleton partition — 260 of 264 clusters are
a single section, and four small cycles hold the rest. The two largest cycles are
the two things this repository has already found hardest: the income-tax schedule
and the VAT threshold. That is a good sign for the extractor — it rediscovered
the coupling from the text alone, without the source of the earlier `vat_tier_gap`
finding.

*The frontier is wide, not deep.* Depth here is the longest chain of unformalized
dependencies beneath a cluster. Most clusters sit at depth zero, the deepest
chain is seven clusters, and the clusters that are already unblocked hold a
majority of the estimated work. There is no ordering reason to sequence
contributors; the only thing that serializes this project is signature, not
proof.

*The formalizable count lands inside the earlier estimate but rejects its
concentration.* The earlier title-level estimate, built from section counts
alone, was 90–130 sections concentrated in Titles II, III, IV, V and VII. The
text-structure measure puts the number inside that band, yet it spreads the work
across every title, because assessment, limitation, penalty and allotment
provisions compute too. The two titles it was most wrong about are Title X, which
the earlier estimate called "medium: fine/penalty arithmetic only" and which is
in fact the second-largest block by section count — every offence carries a fine,
a surcharge and an interest period, each a computation with a statutory floor —
and Title VII, which has 29 sections and only five with arithmetic, because the
documentary stamp schedule is a rate table rather than a set of rules. The old
title-level table was not merely imprecise; it was wrong about where the work
sits.

**What survives, and what changes.** The roadmap argument survives: the next move
is still not "add deductions" but "finish the Title II definition cluster
(`gross income`, `taxable income`, `deduction`), then the rate cluster" — §22 and
§24 are in the same cycle, and §24 is the most-cited section in the code (11
inbound references), so it cannot be deferred behind anything. What changes is
the scheduling model: a queue ordered by dependency has almost nothing to
reorder. Order by **fan-in** and **cycle membership**, both of which the graph now
supplies, and let the reviewer — not the graph — supply the throttle.

**Two limits worth stating.** The parse is of the 1997 base text, not the Code as
amended, so the graph is a floor: RA 10963 and RA 11976 moved rates and at least
one cross-reference, and each must be re-parsed before these numbers are quoted
as current law. And the units are text-structure estimates, not measured effort:
they cannot see that a short section is legally hard. That one is now checked
rather than asserted — once, against the seven merged sections, where the
aggregate holds to about 20% and individual sections are off by a factor of two
in both directions, with two of the seven wrong in kind rather than in degree. Use
the units to rank clusters, not to schedule them. Both limits, with the formula
and the check, are in `NIRC_CLUSTER_GRAPH.md` §6.

One by-product: the extractor found a typesetting defect in the primary source on
its first run. §132 is set as `<b>Section </b>132.` instead of
`<b>Section 132.</b>`, so any strict marker parse silently loses the section and
shifts every later chunk boundary. That is the Lexifina claim demonstrated at
one-section scale — a formalization pipeline is a statute proofreader — and it is
the cheapest kind of finding the project produces.

### 5.2 Eight cluster types

Each is a persistent team with an owner and its own acceptance rule. Clusters are *work* clusters; compute clusters are Section 6.

| # | Cluster | Produces | Owner | Acceptance |
|---|---|---|---|---|
| C0 | **Law-as-data** | Versioned statute text, section index, cross-reference graph, quote hashes, effective dates | Data steward | Every quote resolves; every reference resolves or is filed as a drafting fault |
| C1 | **Shared algebraic core** | Money as integer centavos, rounding, date arithmetic, bracket/slice, thresholds, credits, monotonicity lemmas | Core maintainer | Kernel + reviewer; no jurisdiction-specific content |
| C2 | **Statute clusters** (one per graph cluster) | Definitions (`D`), theorems (`T`), worked examples (`E`) | Cluster maintainer | Kernel + reviewer for any `D`/`T` that fixes a reading |
| C3 | **Certificate & checker** | `Cert` structures, soundness/completeness, guard necessity | Verification maintainer | Kernel + mutation test (each guard deleted ⇒ build fails) |
| C4 | **Forms & returns** | The return line items a real filer sees (e.g. 1701, 2551Q), and the theorem that form = law | Domain maintainer | Kernel + reviewer + one worked return |
| C5 | **Benchmark & ground truth** | Cases with documented provenance; dual-implementation or authority-approved answers | Evaluation maintainer | No output unless two independent computations agree |
| C6 | **Red team** | Counterexamples, mutations, adversarial certificates, divergence proofs | Rotating | Any accepted counterexample is a result |
| C7 | **Review gate** | Signed statements, disagreement log, revision record | Practitioner panel | Signature, always |
| C8 | **Packaging** | Blueprint, docs, exercises, contributor onboarding | Community maintainer | Builds, links check |

Two observations about this repository: **C3, C5, C6 and C7 already exist in embryo** (`tools/mutation_tests.py`, `make_benchmark.py` + dual ground truth, `Loopholes.lean`, `docs/spec_review_packet.md`). **C0, C1, C4 and the desk itself are missing.** That is a much shorter build than it looks.

### 5.3 The work-unit schema

Five unit kinds, because a tax formalization has more kinds of progress than a math one:

| Kind | What it is | Example |
|---|---|---|
| `D` | Definition / encoding of a provision | `vatExempt`, `classify` |
| `T` | Property of the encoded rule | `bracketTax_mono`, `check8_sound` |
| `E` | Kernel-checked worked value | ₱500,000 at 30 days ⇒ ₱53,544.17 |
| `C` | Checker lemma + mutation requirement | `claimEight_rejected` |
| `X` | Divergence / counterexample / loophole | `vat_tier_gap`, `tier_cliff_20M` |

```yaml
id: PH-NIRC-24A2a-SCHED-01
cluster: statute.income.rate.24A
kind: D
title: "Graduated individual income tax schedule, TY beginning on/after 2023-01-01"
source:
  instrument: RA 10963
  provision: "NIRC §24(A)(2)(a)"
  url: https://www.lawphil.net/statutes/repacts/ra2017/ra_10963_2017.html
  archived: data/sources/RA_10963_sec24_sec116.txt
  quote_sha256: "<hash of the exact quoted text>"
  effective_from: 2023-01-01
  effective_to: null
statement: |
  def bracketTax (t : Nat) : Nat := ...
imports: [Spec.Money, Spec.Brackets]
depends_on: [PH-NIRC-22-DEF-01]
difficulty: 2
review:
  required: true
  status: unreviewed        # unreviewed | signed | disputed
  reviewer: null
  packet_item: S1
acceptance:
  no_sorry: true
  axioms: [propext, Quot.sound]
  forbid: [native_decide]
  statement_sha256: "<hash>"
```

The `packet_item: S1` field is the two-key hinge: it points at the exact row of `docs/spec_review_packet.md` where a practitioner signs. Units whose packet item is unsigned can be merged into a `draft` namespace but never into `Spec`.

### 5.4 Desk API and state machine

```
GET  /desk/next?handle=&cluster=&kind=&another=1&hard=1
POST /desk/beat?lease=
POST /desk/release?lease=&reason=
GET  /desk/unit/{id}
GET  /desk/status
```

```
open ──lease──▶ leased ──submit──▶ submitted ──CI──▶ kernel_accepted
  ▲               │                                        │
  │               └──release(reason)──────────┐             ▼
  └───────────────────────────────────────────┴──── review_pending
                                                          │
                                     reviewer signs ──────┼──▶ merged
                                     reviewer disputes ───┴──▶ disputed ──▶ X unit
```

Release reasons need two additions to the pequalnp taxonomy, and both are *productive* signals:

- `statute_does_not_say_this` — the contributor believes the encoded statement overstates the text. Routes straight to reviewer, becomes an `X` or a spec repair.
- `needs_definition` — the statement cannot be proved because a dependency is unencoded. Routes to C0/C1 and reorders the frontier.

**Leases matter more than they look.** They prevent two contributors formalizing the same lemma incompatibly — the exact failure Prove2Me names as the reason decomposition alone does not compose. Five concurrent leases per handle, 45-minute heartbeat, 6-hour cap, and a public list of who holds what.

### 5.5 The acceptance pipeline

Thirteen checks, all deterministic, all runnable locally before submission:

1. Builds with the pinned toolchain (no `lake update`; pinned Mathlib if used).
2. No `sorry` in the unit's dependency closure.
3. Axiom audit within `{propext, Classical.choice, Quot.sound}`; no `native_decide`, no `axiom`, no `unsafe`.
4. Statement hash equals the posted statement's hash; nothing in the contributor's file may alter its meaning (no local notation/instances outside the unit namespace).
5. Imports within the allowlist.
6. Path/namespace/module name match the unit id; one unit per PR.
7. Proof-size and elaboration-time budget (a 4-hour `decide` is a rejection, not an achievement).
8. **Non-vacuity**: the statement must be inhabited/consistent and must mention the statutory quantities — blocks `theorem foo : x = x` and hypothesis-laundering (`h : False`).
9. Duplicate detection: statement hash plus α-equivalence against the library; near-duplicate proofs flagged.
10. Provenance present and resolvable: citation, archived text, quote hash, effective dates.
11. Coverage delta computed: which `open` units became provable as a result.
12. Reviewer signature present for any `D`/`T` that fixes a reading.
13. For `C` units: mutation test — delete the guard, the build must fail at the named theorem.

Checks 8 and 11 are the anti-gaming core. Every open-contribution formalization gets flooded with true-but-useless theorems eventually; the defence is to score *coverage of the audited spine*, never theorem count.

---

## 6. Compute: where volunteer machines actually help

### 6.1 What is expensive in Lean

| Activity | Cost | Distributable? |
|---|---|---|
| Kernel checking an accepted proof | Very low; small trusted core | Yes, but pointless — it is already fast and must be authoritative |
| Elaboration + import of Mathlib | High, dominated by imports | Yes, via prebuilt cache and sharding |
| Tactic search / `decide` on finite cases | Can explode | **Yes — embarrassing parallelism** |
| LLM-guided proof search | Tokens and wall-clock | **Yes — the main donation surface** |
| Drafting statements from statute text | Human/LLM reading time | Yes, but needs review |
| Reviewing a statement against the statute | Human expert hours | **No. This is the bottleneck.** |

### 6.2 Measured baseline, and a projection

This repo's measured figure is **57.3 s warm rebuild for 1,024 lines** of core-library-only Lean (no Mathlib, no Lake), on a Windows laptop — about **56 ms per line**.

Projecting that to a 40,000-line formalization: ~2,240 s, or **~37 minutes serial per full build**, which is why CI must shard and cache rather than ask volunteers to rebuild the world. Treat the 56 ms/line figure as an extrapolation from one small, dependency-free artifact: real projects with Mathlib imports are dominated by import cost, which is why pequalnp ships `lake exe cache get` and a prebuilt Mathlib.

### 6.3 Four donation surfaces, in order of value

1. **Proof-search runners.** A small daemon that pulls an `open` unit, runs a bounded search (tactics, `aesop`-style automation, or an LLM loop with the contributor's own key), and submits only on success. Choir's model — each contributor runs their own agent on their own subscription, coordinating only through GitHub — is the right shape, and Prove2Me's case study shows the economics: a 130K-line textbook formalization cost ~$100,000 centralized against **$200–$600** for missions run on contributors' consumer subscriptions.
2. **Verification CI minutes.** Donate runners for the deterministic gate. Low intellectual value, high operational value.
3. **Cache and artifact hosting.** Content-addressed build artifacts; prebuilt dependency layers. Boring, load-bearing.
4. **Reviewer support (the real one).** Prove2Me's "sub-agent read-back": an independent agent translates the Lean statement back into plain language — ideally into the statutory phrasing — and the human reviewer compares *two prose statements* instead of reading Lean. For tax this is even more valuable than for mathematics, because the reviewer is a CPA or tax lawyer, not a Lean user. **This is the highest-leverage use of compute in the entire project**: it converts scarce expert hours into a comparison task.

### 6.4 What not to build

Do not build a distributed *checker*. Checking must be centralized, pinned and reproducible; a volunteer's "it built on my machine" is not acceptance. Do not let contributors pin their own toolchain. Do not accept proofs with a longer elaboration budget than the CI allows — that is how you get a library that only its author can build.

---

## 7. Reviewer economics: the number that decides the project

Take the mid-range estimate: **120 formalizable sections × 12 units = 1,440 units**.

- A practitioner reviewing a *statement plus citation* (not a proof) needs roughly **15 minutes** once the read-back exists: ~**360 reviewer-hours** for the whole spine.
- Three reviewers at 5 h/week = 15 h/week ⇒ **~24 weeks**, about six months, to sign a complete first-pass spine.
- If review capacity is one person at 5 h/week: **~18 months**, and the desk must be throttled to that rate or it will accumulate an unreviewed backlog that looks like progress and is not.

Three design consequences follow directly:

1. **The desk's throughput target is reviewer throughput, not contributor throughput.** Cap open leases per cluster to what the panel can absorb; publish the backlog as a first-class number.
2. **Split the review into two tiers.** Tier 1: does the Lean statement say what the quoted sentence says? (Para-legal, read-back assisted, cheap.) Tier 2: is our reading of the sentence right? (Practitioner, expensive, only for `D`/`T` on the spine.) Conflating them is how projects stall.
3. **Every merged unit must reduce future review.** Definitions and lemmas that other units import are worth more than terminal examples. Weight bounties by **downstream import count**, which is measurable, rather than by difficulty, which is not.

### 7.1 Eight anti-slop controls

1. Leases with expiry; max 5 per handle; per-handle submission rate limit.
2. Non-vacuity and relevance checks (Section 5.5, #8).
3. Statement immutability: the posted statement is the posted statement; changing it is a new unit with a new review.
4. Duplicate detection by hash and α-equivalence; duplicates are auto-closed, not merged.
5. Proof-size/time budget; huge `decide` proofs rejected.
6. Provenance required; untethered units cannot leave `draft`.
7. Coverage-based scoring, never theorem counts, on the public dashboard.
8. Reputation weighted by accepted-and-*not-reverted* units, with a visible reverted-count. Reverts are the only reliable slop signal.

---

## 8. Governance and legitimacy

| Role | Authority | Cannot |
|---|---|---|
| Contributor / prover | Submit units, release with reasons | Alter statements, merge |
| Cluster maintainer | Merge kernel-accepted, reviewed units in their cluster | Sign a statement |
| Reviewer (practitioner) | Sign `D`/`T` statements and citations | Merge code, change checker semantics |
| Verification maintainer | Checker semantics, mutation suite, axiom policy | Change a statutory reading |
| Data steward | Law-as-data, versions, quote hashes | Interpret |
| Steward / release manager | Version tags, public claims, security | Override a reviewer |

**Signature ladder, published per unit:** `draft` → `kernel_accepted` → `tier1_readback` → `practitioner_signed` → `merged`. A public page must show the distribution, not just the top line.

**Versioning by effective date.** A proof is valid for a `(provision, version)` pair, never for "the tax code." `global-law`'s model — one commit per law taking effect, with an `In-force` date — is the right data layer. The theorem `vat_tier_gap` is not true or false in the abstract; it is true of RA 11976 as enacted on a date.

**Ambiguity policy.** Two readings ⇒ two encodings ⇒ one divergence theorem ⇒ reviewer decides which is `Spec` and which is `Alt`, and both stay in the library with the decision recorded. Never delete the losing reading; it is the audit trail.

**Licensing.** MIT for code (as now), public-domain statute text archived with hashes, CC0 for the derived law-as-data layer if it is published separately. Do not relicense statute text.

**The claim discipline.** Every generated page carries: "Kernel-checked relative to the cited specification. Not legal advice. Not an official BIR implementation. Statements marked `draft` are unreviewed." This repo already does this in `README.md` and `STATUS.md`; the platform must make it structural rather than editorial.

---

## 9. Metrics that keep it honest

| Metric | Definition | Why it cannot be gamed | First target |
|---|---|---|---|
| **Spine coverage** | Signed `D`/`T` units ÷ spine units | Denominator is set by the statute, not the contributor | 100% of Title II core |
| **Provenance coverage** | Units whose quote hash resolves ÷ all units | Hash check is mechanical | 100% |
| **Proof debt** | `sorry` + non-standard axioms + `native_decide` in the closure | Axiom audit | 0 |
| **Review latency** | Median days `kernel_accepted` → `practitioner_signed` | Measures the real bottleneck | < 21 days |
| **Revert rate** | Merged units later reverted ÷ merged | The only honest slop signal | < 5% |
| **False-accept rate** | Accepted certificates with a wrong total ÷ accepted | Adversarial, seeded engines | 0 |
| **Mutation survival** | Guards removed that the build does *not* catch | Automatic | 0 |
| **Coverage delta per 100 units** | Newly provable units unlocked | Rewards structure over volume | rising |
| **Contributor retention** | Contributors with ≥2 accepted units ÷ all contributors | Detects a bounty-farming crowd | > 25% |
| **Spec revision rate** | Statements changed after review ÷ signed | High is *good* early — it means review is working; publish it | tracked, not targeted |

That last row is the one to defend in a paper. A project that reports zero spec revisions after review is either not reviewing or not reporting.

---

## 10. A 90-day rollout, gated

**Phase 0 — weeks 1–2: spine and gate.** Freeze the schema (Section 5.3); build C0 from `data/NIRC_section_index.csv` plus the archived sources; extract the cross-reference graph and publish the cluster map and frontier; migrate the existing 7 sections into units with packet items; publish `CONTRIBUTING.md` with the 13 checks and the two-key rule.
*Gate:* every existing theorem has a unit id, a citation and a packet item; `run_demo.sh` green; the graph resolves ≥90% of references (the remainder filed as drafting faults).

**Phase 1 — weeks 3–6: the desk, closed beta.** Implement `/desk/next|beat|release`; run the pipeline on a private runner; invite 10–15 contributors from the Lean and civic-tech communities; open only `T`/`E` units in already-signed clusters.
*Gate:* 50 accepted units, 0 reverts, median review latency < 7 days, and — critically — no unit merged without a signature.

**Phase 2 — weeks 7–10: opener and red team.** Public desk; `X` units (divergence and counterexample) get their own queue with a standing invitation; add the read-back agent for Tier 1 review; publish the dashboard with coverage, not theorem counts.
*Gate:* 10 external contributors with ≥2 accepted units each; ≥5 kernel-checked divergence findings; revert rate < 5%.

**Phase 3 — weeks 11–13: forms and evidence.** C4: one real return (1701 or 2551Q) encoded, with the theorem that form = law; expand the benchmark; write the methods paper around the *protocol*, not the coverage.
*Gate:* one worked return end-to-end, independently recomputed; paper draft; security and licensing review; a written statement of what the project still cannot claim.

**Do not skip Phase 0.** Launching the desk before the review gate exists means distributing unreviewed legal readings with a proof badge — the failure mode this whole design exists to prevent.

---

## 11. Risks, ranked

| # | Risk | Why it bites | Mitigation |
|---|---|---|---|
| 1 | **False authority** — a green check read as legal correctness | The single most likely harm; amplified by open contribution | Two-key merge; `draft` namespace; claim discipline on every page; publish unsigned counts |
| 2 | **Reviewer drought** | Kills throughput and forces unreviewed merges | Tier 1/2 split; read-back agent; bounties denominated in reviewer hours, not proofs |
| 3 | **Slop flood** | Agents produce thousands of vacuous or duplicate units | Non-vacuity, dedup, budgets, coverage-based scoring, revert-weighted reputation |
| 4 | **Statement drift** | Contributors restate the law slightly differently, silently | Frozen statements, hash equality, definitions-only-from-`Spec` |
| 5 | **Stale law** | A verified model of a repealed provision is worse than none | Effective-dated versions; the graph re-runs on each amendment; CI fails on drift |
| 6 | **Commons fatigue** | Novelty decays; leases go unclaimed | Cluster ownership, named credit, visible frontier, small wins early |
| 7 | **Legal challenge to the project's framing** | "Are you saying BIR is wrong?" | Never claim BIR error; frame as a public research artifact and a review method |
| 8 | **Being scooped on scale** | Lexifina is at 199 countries; a PH pilot is small | Compete on *review-gated openness and the checker*, not coverage |

---

## 12. Verdict

| Dimension | Score /5 | Note |
|---|---|---|
| Justification | 4 | Real failure class, real mandate, real LLM gap; overstated if it claims revenue or lawfulness |
| Technical feasibility | 4.5 | The verification machinery largely exists here; the desk is ~2–3 components |
| Novelty of the distributed protocol | 2.5 | Prove2Me and Choir already publish decomposition + deterministic gating |
| Novelty of the *legal-fidelity* gate | 4 | No published protocol curates statements against versioned statute with practitioner signatures |
| Risk of harm | Medium | Mitigable only by refusing to merge unsigned statements |
| Fit with this repository | 5 | C3/C5/C6/C7 already exist in embryo; the paper's central finding *is* the design rationale |

**The one decision that determines success:** whether the project treats **reviewer signatures** as the rate-limiting, first-class product — or treats **merged proofs** as the metric and review as an afterthought. Everything in Sections 5–11 is downstream of that choice. The P vs NP desk can be copied in a fortnight; a practitioner panel cannot.

**If it works,** the output is not a tax calculator. It is a public, versioned, machine-checked record of *what the law computes*, with every contested reading visible, every change breaking a proof, and every claim traceable to a signed statement — which is a more useful thing for a taxpayer to be able to challenge than any black-box assessment.

---

## 13. References

New sources used here; the rest are in `DEEP_RESEARCH_LEAN_TAX_GOVERNANCE.md` §9.

1. pequalnp.com — *What this is*, and `github.com/open-goat/pequalnp-proofs` (README, CONTRIBUTING): gap definition, desk endpoints, lease rules, six acceptance invariants, credit. Accessed 27 Nov 2026. T3 (primary protocol documentation).
2. Mantinband, A. — public progress update, 24 Nov 2026 (8.6M lines, 360+ contributors, 2,000+ checked lemmas). T3, self-reported.
3. Makarov, V. — "A live swarm has checked 1,129 lemmas toward P ≠ NP. That is labour, not a proof," Traictory, 24 Nov 2026. T3.
4. Maier, A. — "117 Agents, 457 Checked Lemmas and No Answer Yet," 25 Nov 2026. T3.
5. Chen, S. et al. — *Prove2Me: An Open Collaborative Platform for Scaling Math Formalization*, arXiv:2608.28433. Missions, curated-core auditing, proof-sketches, milestones, sub-agent read-back, cost case study. T2 (preprint).
6. Qi, Y. & Weber, M. — *Choir: An Open Protocol for Distributed Multi-Agent Autoformalization*, 2026. Task decomposition, deterministic merge gate, contributors run their own agents. T2.
7. Massot, P. — *Coordinating large formalization projects* (EuroProofNet, 2025): blueprints, distribution of work, Flyspeck bounties. T2.
8. The mathlib Community — *Growing Mathlib* (arXiv:2508.21593) and *The Lean Mathematical Library* (arXiv:1910.09336): review as the scaling constraint, multi-stage approval, onboarding function of review. T1.
9. Yahya, A. — Lexifina posts: *Formalizing the US tax code* (138 drafting faults; cross-reference checking), *Auditing the IRS and four other national tax systems*, *Formalizing the French tax code* (Catala 191/209 parts), *Formalizing Taxation Across 38 Nations*, *One master equation for all global tax* (197 countries; 4,080 theorems; 165k lines), and `github.com/lexifina/global-law` (CC0, dated law-as-data). T3 (company claims, unusually detailed).
10. Han, S. S. et al. — *Law and Order: Tax Law Autoformalization*, arXiv:2610.02792 (100% vs 66% on 51 held-out returns). T2.
11. Bock, M. R. et al. — *TaxCalcBench*, arXiv:2507.16126 (frontier models below one third). T2.
12. World Bank — *Philippines Public Finance Review*, Sept 2026: tax-to-GDP 14.6% (2025); VAT/CIT/PIT gaps >11% of GDP; 26.7% of CIT potential; ~40.6% of VAT potential. T1.
13. IRS — *The tax gap*: TY2022 gross gap $696bn, net $606bn, VCR 85.0%. T1.
14. Royal Commission into the Robodebt Scheme — *Report* (2023): net cost ~A$565.195m; ~470,000 erroneous notices (as reported); redress ~A$2.4bn (BBC, 2025). T1/T2.
15. `docs/spec_review_packet.md` — this repository's 12-item practitioner packet (S1–S12), the seed of cluster C7.
16. `ph-tax-code-lean/STATUS.md`, `THEOREMS.md`, `LOOPHOLE_FINDINGS.md`, `data/summary.json` — measured figures used in §1.4, §2 and §6.2.
