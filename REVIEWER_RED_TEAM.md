# Reviewer Red-Team: Likely Attacks and How to Answer Them

**Purpose:** Stress-test the Philippine tax-law formalization project as a skeptical research reviewer, legal reviewer, and public-interest technology reviewer might. This is a preparation memo, not a claim that every criticism is already proven.

## The central thesis to defend

Do not claim that Lean proves the tax law, that it makes governance safe, or that the project found exploitable BIR loopholes. Defend this narrower thesis:

> For a bounded set of computational tax rules, a machine-checked specification can make some calculation claims independently checkable and expose assumptions and missing predicates. Its value depends on legal source fidelity, independent validation, version control, and a process that preserves human responsibility and contestability.

This makes the paper a contribution about **verification as one part of accountable rule implementation**, not a proposal to automate legal judgment wholesale.

## The attacks reviewers are most likely to make

| Reviewer attack | Why it can land against the current project | Best response / evidence to add |
|---|---|---|
| **“You proved the code, not the law.”** | Correct. The proof checker establishes results relative to the formal definitions. The practitioner review packet is currently unsigned/not performed. | Make legal fidelity a separate research question. Complete independent review, attach citations and effective dates to each modeled rule, log disagreements, and rerun proofs after revisions. Keep “proved correct” qualified as “proved relative to this specification.” |
| **“This is already done by Catala and recent tax autoformalization.”** | Legal DSLs, verified implementations, tax law-to-code benchmarks, and LLM-based tax formalization already exist. A Lean implementation in a new jurisdiction may look like an application note. | Compare with prior work by task, language, jurisdiction, proof obligations, legal-validation process, evaluation data, and deployment/governance claims. Make the contribution the jurisdiction-specific review method, checkable certificate contract, and explicit error boundary—not Lean by itself. |
| **“The 274 findings are a count, not a contribution.”** | Many generated propositions may be repeated witness cases or simple identities. The raw theorem count does not establish independent scientific value. | Report the number of distinct claim families, their selection rule, what each family teaches, and representative proofs. Report coverage and counterexamples, not theorem volume as a headline. Explain which claims required nontrivial formalization. |
| **“The checker just recomputes the answer; why use certificates?”** | For small deterministic tax arithmetic, recomputation may be simpler than checking a certificate. The certificate may add data format and integration burden without reducing the trusted core materially. | Compare the checker with a direct trusted calculator and ordinary tests. State exactly which component is untrusted, what the certificate adds (audit trail, modular engine checking, or result provenance), and measure cost/complexity. If no benefit is demonstrated, present the certificate pattern as a prototype rather than a proven efficiency gain. |
| **“Your ‘independent’ cross-checks share the same assumptions.”** | Python and Lean can agree because both encode the same interpretation or copied formulas. Agreement does not validate the statutory reading. | Separate implementation independence from specification independence. Have a practitioner author or validate ground-truth cases from primary sources; document independent derivation; use mutation tests to show detection of distinct errors. State clearly that implementation agreement is not legal validation. |
| **“The benchmark is synthetic and small.”** | Model-generated cases and 32/64 structured rows may not represent real taxpayers, tax forms, or the distribution of errors in deployed systems. Seeded-fault engines are not a sample of actual products. | Describe the benchmark as a controlled fault-injection study. Publish sampling strata and provenance. Add independently authored worked cases and, if authorized, anonymized cases. Report per-fault-class denominators and uncertainty; do not infer population error rates. |
| **“Zero false accepts is a benchmark artifact.”** | It may mean only that those seeded faults and inputs were caught. Some engineered faults can be rejected for incidental reasons; realistic correlated errors may pass. | Build a fault taxonomy first: arithmetic, threshold, regime, eligibility, penalty base, rounding, omitted context, and stale rule. Test multiple mutations per class, include near-miss cases, explain catches, and report escapes. Treat 0 false accepts as scoped to the tested set. |
| **“You call these loopholes, but they are missing model premises.”** | The project's own report labels L1, L2, L5 as encoding gaps and says it cannot claim actual BIR-system vulnerabilities. “Loophole” invites an overclaim. | Use “specification gap,” “accepted out-of-domain certificate,” or “modeled statutory incentive.” Separate checker bugs, unmodeled legal conditions, and policy effects. Never imply that BIR software accepts the fabricated inputs. |
| **“The paper is mixing law-as-code, formal verification, AI benchmarking, and governance.”** | Each field has different standards and research questions. A sprawling paper could be shallow in all of them. | Choose one lead contribution. Recommended: technical AI-and-law paper focused on soundness/completeness plus structured error evaluation. Move BetterGov, governance adoption, and public value into a follow-up study unless you collect stakeholder evidence. |
| **“Your laws are incomplete or stale.”** | Tax obligations may depend on amendments, revenue regulations, dates, elections, prescription, taxpayer status, cross-references, facts, and changing thresholds. The current report identifies omitted inputs. | Pin the legal version and effective dates. Make omitted context explicit in the certificate contract. Add a dependency/version map and change log. Do not silently treat the model as current for every tax year. Practitioner review should decide which gaps are in scope. |
| **“The 20M cliff may be a model or source interpretation artifact.”** | The dramatic end-to-end difference relies on formalized tier-dependent rates and claimed gross sales. Without review, it may not reflect all eligibility conditions, assessment facts, or actual practice. | Present it as a conditional result of the encoded rules. Show the exact premises and direct threshold comparisons. Ask the practitioner to validate statutory application and identify possible alternative readings. Avoid language suggesting one-centavo real-world arbitrage is proven. |
| **“This confuses computation with governance.”** | A tax calculation is not the full administrative decision: facts, notice, discretion, enforcement, evidence, appeal, and institutional authority are outside the prototype. | Use the model as a narrow component in a governance pipeline. Draw a clear boundary: machine-checkable calculation vs human/legal predicates and review. Make no deployment or decision-automation claim. |
| **“A verified answer may create false authority.”** | People may interpret a proof or polished interface as an official or legally endorsed result. | Label the artifact as research and non-authoritative. Show input provenance, legal sources, assumptions, version date, and the checked steps. Include a correction/appeal pathway in any prototype and name the accountable decision-maker. |
| **“Where is the actual user or institutional evidence?”** | BetterGov alignment is plausible, but the folder currently contains no study of citizen comprehension, practitioner workflow, agency adoption, or contestability. | Do not claim user benefit yet. Conduct a small, ethics-approved formative study: ask practitioners/citizens to inspect a certificate and identify assumptions, errors, and next steps. For agency claims, secure an authorized institutional partner and measure concrete workflow outcomes. |

## A sharper attack plan for the research itself

These are constructive tests that can turn likely reviewer criticism into the paper's methodology.

### 1. Adversarial specification review

Ask a tax practitioner to review claims without first presenting the Lean proofs as evidence of legal correctness. Give them the source texts, definition table, and assumptions. Record:

- disagreements about the legal source or its hierarchy;
- missing facts and statutory conditions;
- effective-date and amendment problems;
- ambiguity that admits more than one defensible model;
- claims that should remain human decisions.

Then compare the original model with the reviewed model. Report which theorems survive, fail, or need narrower premises. This directly tests the distinction between formal validity and legal fidelity.

### 2. Fault-injection matrix

Classify faults before testing. For each class, include at least one caught and one attempted-to-escape example where feasible:

- arithmetic/rate error;
- bracket boundary or rounding error;
- taxpayer-tier boundary error;
- wrong regime or ineligible 8% election;
- penalty/interest base error;
- missing election date, taxable year, assessment date, or prescription condition;
- inconsistent/fabricated input facts;
- stale legal version;
- errors in explanations while numeric certificate is correct.

The final two categories matter for governance: a checker can verify a number and still fail to verify the story or factual basis that justifies it.

### 3. Baseline comparison

Compare at least three approaches on the same cases:

1. ordinary hand-authored calculator plus unit tests;
2. independent computation engine with no certificate checker;
3. untrusted engine plus Lean certificate checker.

Measure false acceptance on the seeded set, implementation effort, runtime, auditability, and what each approach trusts. If the formal checker has no demonstrated advantage for this small calculation, say so and identify where the approach may scale better (e.g., many independent engines or auditable computation trails).

### 4. Public explanation test

If making a BetterGov/public-interest argument, test whether a non-expert can answer from the artifact:

- Which legal version was applied?
- Which facts were supplied and which were assumed?
- Which parts did the checker verify?
- What was not checked?
- How can the person correct the facts or contest the interpretation?

Without this evidence, call transparency and contestability design goals, not demonstrated outcomes.

## Reviewer-safe language

| Avoid | Prefer |
|---|---|
| “We proved the Philippine tax code.” | “We proved properties of a bounded formal specification of selected tax computations.” |
| “We found five tax loopholes.” | “We identified five conditional properties of the model: three missing certificate premises and two effects of the law as encoded.” |
| “The system prevents incorrect tax assessments.” | “The checker rejects the tested classes of inconsistent computation certificates under the stated assumptions.” |
| “AI can automate governance safely.” | “Formal checking can verify selected deterministic steps; responsible use also requires legal validation, factual review, update governance, and appeal.” |
| “The model is accurate.” | “The model agrees with the stated independent test oracle on these cases; the oracle and legal assumptions have these limits.” |
| “This is the first in the Philippines.” | “In a documented search of specified sources through [date], we found no prior study with this exact combination of jurisdiction, verifier, certificate evaluation, and review process.” |

## Best one-paper strategy

**Paper 1 — technical/legal formalization:**

- research question: what can a small proof checker guarantee about a bounded Philippine tax computation, and what assumptions does that guarantee leave outside the checker?
- main evidence: audited Lean properties, source-linked model, independently validated cases, fault-injection study, practitioner review log;
- target profile: JURIX or *Artificial Intelligence and Law*;
- avoid a broad claim about automating government.

**Paper 2 — governance and public value:**

- research question: under what institutional and user-facing conditions can machine-checkable rules improve the inspectability and contestability of a digital public service?
- main evidence: practitioner/citizen/agency co-design, comprehension tests, versioning/ownership proposal, privacy and appeal safeguards;
- target profile: dg.o or a public administration / digital government journal;
- BetterGov.ph could be a civic-tech partner or reviewer if it agrees, but it is not a substitute for legal authority or institutional approval.

## Recommendation

The strongest immediate move is to attack your own model with an independent legal review and a fault taxonomy before adding more theorem counts or extending to more of the tax code. The most publishable result may be the disciplined account of **where verification helps and where it stops**, especially if the review forces changes to the model. That is a more credible contribution to accountable governance than claiming automation itself is trustworthy.

## GitHub artifact check (19 November 2026)

I checked public GitHub repositories and indexed code for nearby implementations. Two artifacts are especially relevant:

- [kavanaghpatrick/us-tax-code-lean](https://github.com/kavanaghpatrick/us-tax-code-lean) is a public Lean 4 U.S. tax-code repository. Its README, marked last updated 18 December 2025, self-reports 765 formalized IRC sections, 607 theorems/lemmas, and 17 remaining `sorry`s. It describes wide but uneven coverage and a pipeline using generated Lean skeletons and Aristotle outputs. These are project-authored claims, not an independent quality audit. The comparison makes it untenable to market this work as the first or largest Lean tax-code project; it also gives you a concrete comparator for discussing scale versus reviewed scope, proof completeness, and legal traceability.
- [CatalaLang/catala](https://github.com/CatalaLang/catala) describes Catala as a domain-specific language for deriving algorithms from legislative texts. Its README emphasizes mapping legal text to code article by article, collaboration with legal professionals, lawyer-readable output, tests, and formalized compiler components. This is a direct design comparator: your paper should explain what kernel-checked Lean certificate verification contributes beyond a legal-facing executable DSL, and what Catala's literate legal traceability offers that your current prototype still needs to strengthen.

GitHub code searches for local names such as `checkT_sound` and `TaxSchedule.lean` did not surface a clear public copy of this workspace. That result is **not evidence that the project is unpublished or unique**: code search can miss unindexed repositories, alternate filenames, private repositories, and differently named implementations. Before claiming novelty, inspect the actual project remote and run a documented literature and code search across repository names, authors, and source concepts.

### How these comparisons change the attack plan

1. **Scale is not your differentiator.** The U.S. Lean project claims vastly greater section and theorem counts, so lead with Philippine statutory context, audited claims, practitioner review, and an explicit boundary between proven computation and unresolved legal predicates.
2. **Literate legal correspondence is a competitive standard.** Catala's workflow makes lawyer review and text-to-code correspondence central. Build a traceability table linking each Lean definition and theorem premise to the exact statute/regulation/version and reviewer disposition.
3. **Proof audit and specification audit must be separate.** Report Lean's trusted-kernel and axiom checks as evidence about proof integrity; report practitioner review and source mapping as separate evidence about legal fidelity.
4. **Use comparative dimensions rather than “Lean vs Catala” rhetoric.** Compare intended task, legal syntax/readability, source linking, theorem guarantees, update workflow, evaluator, and certificate use. A complementary account is more defensible than declaring one language superior.

## Public repository references

- [U.S. Tax Code Formalization in Lean 4](https://github.com/kavanaghpatrick/us-tax-code-lean) — README figures and status are self-reported and dated in that repository.
- [Catala language repository](https://github.com/CatalaLang/catala) — primary project description and documentation links.

## Software-only research routes

These routes do not require practitioner interviews or government data. They still require a human-authored formal scope and source text; the research claim is about software behavior under that fixed specification, not the law's ultimate meaning.

### Route A — Mutation-guided assurance benchmark for legal calculators (recommended)

**Question:** How well do formal proofs, property-based tests, and certificate checks detect realistic semantic faults in a legal computation model, and which fault families remain invisible?

**Software work:** Generate controlled mutants of the current tax model and independent calculation engines: incorrect rates, threshold inequalities, omitted eligibility guards, wrong penalty base, rounding/day-count changes, stale-rule versions, and missing certificate fields. Use property-based or SMT-guided input generation to find and minimize a counterexample for each surviving mutant. Compare Lean theorem suite alone, finite test suite alone, and both together.

**Metrics:** mutant kill rate overall and per fault class; false acceptance; counterexample discovery and minimization rate; runtime; proof/test maintenance after a rule-version change; surviving-mutant explanations.

**Gap statement (provisional):** Legal tax formalization has been evaluated through generated-code benchmarks and individual verified case studies. There appears to be room for a reproducible, fault-class-based evaluation of how verification and testing detect semantic defects in a legal certificate checker, with explicit accounting for errors that arise from missing context rather than arithmetic. This must be checked against the literature before being claimed as novel.

**Why it fits the current project:** The repo already has a Lean checker, generated findings, seeded faulty engines, and some mutation tests. The new contribution would be an experimentally designed fault model and a comparison of assurance techniques, not merely adding more mutants or counting more theorems.

**Caution:** Mutation testing and metamorphic testing are established software-engineering techniques; a 2024 legal-reasoning paper already proposes mutation-guided examples and metamorphic property-based testing for AI-driven statutory reasoning. Position this as a rigorous, reproducible evaluation for formal legal computation certificates and checker assurance, not as inventing mutation testing for law.

### Route B — Automatic semantic change-impact analysis across rule versions

**Question:** Given two versions of a formalized rule, can tooling automatically identify which inputs change outcomes, produce minimal witnesses, and determine which invariants or certificates need revalidation?

**Software work:** Encode selected policy versions side by side; construct a dependency graph from rule definitions and theorem assumptions; run differential/property-based tests to synthesize inputs with changed outcomes; test whether unchanged branches preserve prior theorems. Create controlled amendments (rate, threshold, exception, eligibility) and assess whether the tool detects affected outputs and boundary cases.

**Metrics:** affected-definition precision/recall against known injected changes; counterexample coverage; regression detection; time/effort saved over rerunning all tests; stale-version rejection.

**Gap statement (provisional):** Automated law-to-code research emphasizes generating an executable formalization and evaluating outputs. A narrower, software-only contribution could focus on maintaining formalized rules across amendments and automatically explaining semantic impact. The work should be compared carefully with software regression testing, concolic testing for computational law, and versioned legal knowledge systems.

**Why it fits:** The project already notes threshold updates and an update that broke old proofs. Formalizing that as a repeatable experimental framework may yield a distinctive software-engineering contribution.

### Route C — Boundary and incentive discovery with exact counterexamples

**Question:** Can automated search discover every discontinuity, crossover, monotonicity failure, or regime-dominance boundary in a bounded tax model, and can it return the smallest human-readable witness?

**Software work:** Express desired properties (monotonicity, continuity except at named thresholds, no negative liability, regime comparison). Use Lean decision procedures, SMT solving, symbolic execution, or property-based search to find violations and minimize witness inputs. Compare discovery algorithms and prove the resulting boundary classifications within the model.

**Metrics:** recall against a generated ground-truth mutant set; boundary localization error in smallest currency unit; witness minimality; solver/runtime; number of unclassified regions.

**Gap caution:** The current work already contains threshold, crossover, and incentive findings. CUTECat has studied concolic execution for computational law. To add value, the question must be about completeness/coverage and proof-backed witness minimization, not simply discovering another tax cliff.

### Route D — Proof-checked LLM output for one fixed Philippine tax task

**Question:** Can different LLMs generate a structured certificate or Lean expression for a fixed tax task that a small verifier accepts, and what error categories are rejected or survive?

**Software work:** Freeze prompts, model versions, tool configuration, and tasks; let models generate certificates and explanations; run deterministic checker and adversarial cases; score parse success, acceptance, correct rejection, unsupported claims, and cost. Use no real taxpayer records.

**Metrics:** valid certificate rate, sound acceptance rate against the frozen model, rejection categories, repair rounds, token/runtime cost, robustness to paraphrasing.

**Gap caution:** Recent work already combines LLM synthesis with symbolic verification and tax-return evaluation. A Philippine-only replication would be thin unless the output contract, theorem-checking architecture, language/jurisdiction challenges, or evaluation insight is technically distinct. Do not claim this is novel just because it uses Lean.

## Recommended fully software-executable study

Choose **Route A** first. It uses the artifacts that already exist and can produce a sharply bounded paper without implying legal approval. Title candidate:

> **Mutation-Guided Evaluation of a Proof-Checked Tax Computation Certificate System**

Minimum study design:

1. Freeze the current Lean specification and separately name the behaviors it assumes.
2. Define at least 6 semantic fault classes and create multiple independent mutants per class.
3. Compare theorem suite, current benchmark tests, and property-based/SMT-generated tests.
4. Generate and minimize counterexamples for surviving mutants; classify whether each escape is arithmetic, state/context omission, or an expected out-of-scope limitation.
5. Report per-class mutation score, false acceptance, runtime, and test/proof maintenance under injected rule amendments.
6. Publish all mutants, seeds, generator code, version hashes, and run scripts so a reviewer can reproduce every result.

The claim should remain: “this evaluation measures the ability of software assurance layers to detect selected faults in a formalized model.” It should not claim to measure legal correctness, actual BIR system behavior, or readiness for deployment.
