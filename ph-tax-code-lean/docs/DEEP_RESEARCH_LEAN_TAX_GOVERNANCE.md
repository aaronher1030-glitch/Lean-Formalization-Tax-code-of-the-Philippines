# Deep Research: Verified Tax Rules for the Philippines in Lean 4

**How strong is the idea, and is it a winning one?**
Prepared 16 November 2026 by Aaron Y. Hernandez (BSANHS). These are research notes; the paper built from them is `paper/Verified_Core_Tax_Governance_PH.pdf`.

---

## TL;DR

- **The general idea is not new.** Turning tax law into executable, checkable code has a 40-year history and is now in production. France runs Catala at its tax and family-benefits agencies, and a self-reported Lean 4 formalization covers most of the US Internal Revenue Code. On novelty alone this is not a winning idea. [High]
- **The narrow idea is defensible and fresh.** The angle we can defend is a *verified checker* for tax assessments produced by untrusted engines (agency software, spreadsheets, LLMs), applied to the Philippine NIRC. We found no prior Philippine formalization in our searches. Our demo proves the checker sound (accepted means correct) and complete (honest means accepted). [Medium-High]
- **The demo is rigorous but small.** It has 54 theorems, 64 kernel-checked examples, 0 `sorry` and 859 lines of Lean across six files. It covers the computational parts of seven of the NIRC's 292 sections (about 2.4%) — schedule, penalties, VAT threshold, taxpayer tiers, the 8% election and the Sec. 116 percentage tax — and the hardest part, deciding whether the law applies to the facts, is not modelled. [High]
- **The biggest risk is the spec, not the code.** Our first model applied the 25% surcharge and 12% interest to everyone; RA 11976 Sec. 45 grants micro and small taxpayers a 10% surcharge and half the interest rate. Lean did not and could not catch this. The repair is now formalized and proven (`Tiers.lean`), but the repaired spec still awaits practitioner review. This is the same class of error behind Robodebt. [High]
- **Verdict.** It is a strong entry for a regional mathematics convention (MSP Region 3). It is not yet a winning research program internationally. It becomes one if it adds (a) a Philippine benchmark grounded in real assessments (a model-grounded one now exists), (b) legal review of the spec, and (c) a measured detection rate on real LLM- or software-generated assessments (a 254-certificate study with zero false accepts now exists for one model family). [Medium]

---

## 1. Research Question and Parameters

**Main question.** Can a small, machine-checked core of Philippine tax rules make tax computations auditable, and is this a strong research direction?

| Parameter | Setting |
|---|---|
| RQ1 | Which kinds of NIRC rules are formalizable, and what does it cost? |
| RQ2 | Can a small Lean 4 core prove useful properties of real NIRC rules? |
| RQ3 | Can a certificate checker make untrusted engines auditable, with proven soundness and completeness? |
| RQ4 | How strong is the idea relative to the literature: novelty, rigor, significance, feasibility? |
| Scope (in) | TRAIN individual schedule for 2023 onward (NIRC Sec. 24(A)(2)); 25%/10% surcharge (Sec. 248(A), RA 11976 Sec. 45); 12%/6% deficiency interest (Sec. 249, RA 11976 Sec. 45); ₱3M VAT threshold (Sec. 109(CC), Sec. 236); taxpayer tiers (Sec. 21(b) as amended); 8% optional regime (Sec. 24(A)(2)(b), RR 8-2018) and Sec. 116 percentage tax |
| Scope (out) | Deductions, corporate tax, mixed-income earners/VAT-registered/GPP under the 8% option, quarterly election mechanics, case law, fact-finding |
| Units | Centavos as natural numbers; floor division per term; 365-day year |
| Tooling | Lean 4.35.0, core library only (no Mathlib) |
| Metrics | Theorems; `sorry` count; axioms used; kernel-checked examples; mutation kill; build time; trusted-base size; statutory coverage |
| Depth | Deep: 52 sources (48 cited in the paper), tiered T1/T2/T3 |

---

## 2. Methodology

- **Retrieval.** The lead agent ran web searches and page fetches sequentially. The parallel retrieval subagents this method normally uses were not available in the session where retrieval ran, so no independent retrieval or verification agents were used. This narrows coverage and means no second reader spot-checked the citations.
- **Citation pinning.** All 27 DOIs were resolved against the Crossref API (last re-run 16 Nov 2026; 27/27 resolved). Titles, volumes and pages come from Crossref. Where Crossref has no volume or pages (Huttner & Merigoux 2022; Lawsky 2017b; Hildebrandt 2020), none are given. Non-DOI sources (statutes, reports, court decisions) were taken from official sites (LawPhil, BIR, judiciary.uk, tweedekamer.nl, royalcommission.gov.au).
- **Tiers.** T1 means peer-reviewed work, an official statute or report, or a court decision. T2 means an established institution's news, a credible firm, or a preprint from an identifiable research group. T3 means self-reported repositories or forums.
- **Confidence.** [High] needs 3+ independent sources including T1/T2. [Medium] needs 2 sources or one strong T1. [Low] means a single source or absence-of-evidence.
- **Lean evidence.** Everything in Section 6 was re-run on 16 Nov 2026 with `lean/run_demo.sh`: exit 0, with zero error, warning or `sorry` lines. All four mutation tests were re-run the same day.
- **Limits.** English-language search only, except for Dutch and French official pages. The search for Philippine rules-as-code work returned nothing, but absence of evidence is not evidence of absence, so that finding is [Low].

---

## 3. Status Quo: What the Literature Says

### 3.1 Rules as code and computational law

- **Logic programming of statutes is old.** Sergot et al. (1986) encoded the British Nationality Act as a Prolog program and found that the exercise exposed drafting ambiguities [42]. Bench-Capon et al. (2012) trace 25 years of AI-and-law work [2].
- **Governments now pilot official machine-consumable rules.** Examples are the OECD's *Cracking the Code* [30], New Zealand's Better Rules discovery (2018) [34], and OpenFisca, an open tax-benefit engine started by the French government in 2011 [35]. Waddington (2021) summarises the movement [44]. In 2026 the OECD consulted on a shared reference framework for "law as code" [46].
- **Lawsky's line of work** argues that the US tax code has logical structure that can be made explicit with default logic [21]. It shows how to formalize the Code [22] and evaluates Catala for computationally accessible tax law [23].
- **Takeaway:** The idea of encoding tax law is mainstream in policy circles, but most government deployments are calculators and pilots, not proofs. [Medium-High]

### 3.2 Formalizing tax law specifically

- **Catala** is a language designed for faithful, line-by-line translation of statutes, with a formal semantics [28]. Its authors reported finding a bug in an official French implementation. Huttner & Merigoux (2022) place it among legal expert systems [15]. Monat, Fromherz & Merigoux (2024) formalized date arithmetic in law and statically detected ambiguities [31].
- **France's DGFiP tax computation** language "M" was given a modern compiler (Merigoux, Monat & Protzenko 2021) [29]. Inria reports Catala in use at DGFiP and CNAF [16]. In June 2026 CNAF formally committed to the open-source project [47].
- **Lean 4 and the US Internal Revenue Code.** Kavanagh's `us-tax-code-lean` repository self-reports 765 IRC sections, about 537,400 lines, 607 theorems and 17 remaining `sorry`, generated with AI assistance on Lean 4.14.0. It is not peer-reviewed or audited [17]. A Reddit discussion of it started this project [48].
- **Takeaway:** Faithful formalization of computational tax law finds real bugs and is in production in France. [High] Mass AI-assisted formalization in Lean exists but is self-reported. [Medium]

### 3.3 Formal verification and certifying algorithms

- **Lean 4** is both a theorem prover and a programming language [9]. Mathlib is its community mathematics library [26]. Neither our proofs nor the checker use Mathlib.
- **Landmark verified systems.** The seL4 microkernel [19] and the CompCert compiler [24] show that full functional correctness proofs of real software are achievable but expensive.
- **The certificate pattern.** Proof-carrying code [33], programs that check their work [4] and certifying algorithms [27] share one idea: let an untrusted program produce an answer *plus a witness*, and trust only a small checker. This shrinks the trusted computing base. [High]
- **Takeaway:** The certificate idea is well established in computer science. Applying it to tax assessment explanations is, as far as we found, uncommon; Han et al. [11] is the closest. [Medium]

### 3.4 LLMs, statutes and tax computation

- **Statutory reasoning benchmarks.** SARA introduced a tax statutory-reasoning benchmark [14]. Blair-Stanek et al. (2023) probed GPT-3 on it and found it unreliable on simple synthetic statutes [3]. Nay et al. (2024) found LLM tax-law ability emerging with scale but not at expert level [32]. LegalBench collects 162 legal reasoning tasks [10].
- **Hallucination.** Dahl et al. (2024) document frequent legal hallucinations by general LLMs [8]. Magesh et al. (2025) found that leading commercial legal research tools still hallucinate on a substantial share of queries [25].
- **Tax returns.** On TaxCalcBench, frontier models alone computed fewer than one-third of federal returns correctly [5]. Han et al. (2026) report that their neuro-symbolic Law&Order pipeline reached 100% cell- and form-level accuracy on 51 held-out returns, against 66% for the best LLM alone [11]. This is a preprint.
- **Autoformalization.** LLMs can translate a meaningful fraction of informal math into formal statements [45].
- **Takeaway:** LLMs alone are unreliable at tax computation. [High] Adding symbolic verification and repair can close the gap. [Medium; one preprint]

### 3.5 Failures and critiques of automated government

| Case | What failed | Would verification have helped? |
|---|---|---|
| Robodebt, Australia (Royal Commission 2023) [41] | Income averaging was unlawful as a basis for debts; the rule itself was wrong | No. A proof would faithfully verify an unlawful rule. A visible formal spec might have made the averaging assumption easier to challenge. |
| Toeslagenaffaire, Netherlands (*Ongekend onrecht*, 2020) [36] | Rule-of-law principles violated; harsh all-or-nothing recovery; weak contestability | No. These were policy, process and discrimination failures. |
| MiDAS, Michigan (*Cahoo v. SAS Analytics*, 6th Cir. 2019) [6] | Automated fraud findings; a state review of about 22,000 determinations found 93% involved no fraud | Partly. Logic and notice defects; a checkable trail helps contestability. |
| Horizon, UK (*Bates v Post Office (No 6)*, 2019) [1] | Software bugs caused accounting shortfalls blamed on sub-postmasters | Yes. This is the implementation-bug case that verification and certificates target. |

- **Scholarly critiques.** Citron (2008) argues that automated agency decisions erode notice and hearing ("technological due process") [7]. Kroll et al. (2017) argue for technical accountability tools rather than transparency alone [20]. Hildebrandt (2020) warns that code-driven law "freezes the future and scales the past" [13]. Kennedy (2024) asks how courts can review administration by software [18]. Hart's *open texture* means many legal terms cannot be fixed in advance [12]. Smith, Godfrey & Burdon (2026) reconceptualize rules as code through legal design patterns [43].
- **Takeaway:** The largest public harms came from wrong rules and weak contestability, not arithmetic bugs. [High] Horizon is the counterexample where code defects were the cause. Verification addresses one failure class, not all.

### 3.6 The Philippine context

- **Statutory base.** The NIRC (RA 8424) [37] was amended by TRAIN (RA 10963) [38], which set the 2023-onward schedule and fixed deficiency interest at double the legal rate (12%) [38], [49]. EOPT (RA 11976, 2024) [39] classified taxpayers as micro (under ₱3M), small, medium and large. It set the ₱3M VAT threshold with CPI adjustment every three years, mandated BIR digitalization (Secs. 43–44) and gave micro/small concessions (Sec. 45). The E-Governance Act (RA 12254, 2025) [40] mandates digital government services.
- **Gap.** In two searches we found no Philippine rules-as-code or theorem-prover formalization of the NIRC. [Low, absence of evidence]
- **Takeaway:** Philippine law now mandates digital tax administration, so the question of how to make that software trustworthy is timely. [High]

---

## 4. Trends (2024–2026)

1. **From pilots to production in France.** Catala is used at DGFiP and CNAF [16], and CNAF committed to the open-source project in 2026 [47]. [High]
2. **AI-assisted mass formalization.** The US Code in Lean [17] and Law&Order [11] show LLMs drafting formal tax code at scale. Quality assurance shifts to the checker and the spec. [Medium]
3. **Standardization.** The OECD 2026 consultation on a law-as-code reference framework [46]. [Medium]
4. **Design-pattern and rule-of-law critiques maturing** [18], [43]. The field is moving from "can we" to "how do we keep it lawful and reviewable". [Medium-High]
5. **LLM tax tools under benchmark scrutiny** [5], [11]. Pure LLM accuracy is far from acceptable; hybrids look promising. [High]

---

## 5. Critical Assessment

| # | Claim | Confidence | Basis |
|---|---|---|---|
| C1 | Faithful formalization of computational tax law finds real bugs | High | [28], [29], [42] |
| C2 | Government rules-as-code is mostly pilots and calculators, with France as the production exception | Medium-High | [16], [30], [34], [35] |
| C3 | LLMs alone are unreliable at tax computation | High | [3], [5], [8], [25] |
| C4 | Neuro-symbolic pipelines with verification reach high accuracy | Medium | [11] (single preprint) |
| C5 | The worst harms came from wrong rules and weak contestability; Horizon is the bug case | High | [1], [6], [36], [41] |
| C6 | Code can freeze law and miss open texture | High (as a recognised risk) | [12], [13], [18] |
| C7 | Certifying algorithms shrink the trusted base | High | [4], [27], [33] |
| C8 | The Philippines mandates digital tax administration | High | [39], [40] |
| C8b | No prior Philippine formalization exists | Low | Absence in two searches |
| C9 | Our Lean demo's numbers | High | Reproducible: `lean/run_demo.sh` |
| C10 | AI-assisted mass formalization of a national tax code exists | Medium | [17], self-reported |

### 5.1 Ten criticisms of our own idea

1. **A verified wrong spec is still wrong.** Our model omits EOPT Sec. 45. For a micro taxpayer owing ₱42,500 and paying 30 days late, the model demands ₱53,544.17. The statute implies ₱46,959.58 (10% surcharge and 6% interest), so the model overstates by ₱6,584.59, about 12%. This is hand arithmetic, not a Lean result. *Mitigation:* a lawyer reviews the spec; encode the taxpayer tier as an input.
2. **Tiny coverage.** Computational parts of seven of 292 sections. *Mitigation:* pick the next rules by computational density, not by order in the Code.
3. **Arithmetic is the easy part.** Monotonicity of a bracket schedule is close to obvious. The value is as a regression guard and a template, not as deep mathematics.
4. **The certificate is trivial for this schedule.** Checking costs about the same as recomputing. Certificates pay off when finding the answer is hard and checking is easy, for example choosing among regimes, eligibility chains, or deductions with documentary evidence.
5. **Facts are not verified.** Taxable income is an input. Garbage in, verified garbage out.
6. **Rounding and day-count are assumptions.** Floor division per bracket and a 365-day year may differ from BIR practice by a centavo or more.
7. **Trusted base is not zero.** It includes the Lean kernel, our approximately 15-line spec, the theorem statements, and, for native `#eval`, the Lean compiler. The kernel-checked `decide` examples avoid the compiler.
8. **No legal authority.** A Lean file is not law, and a proof is not a hearing [7], [18].
9. **Maintenance.** The VAT threshold is CPI-indexed every three years and the schedule changed in 2018 and 2023. Every change needs re-proof, but the proofs then act as a change detector.
10. **Crowded field.** Next to Catala in production and an AI-generated US Code, our contribution is small. It must be positioned as complementary, a Philippine instance plus a checker, not as competing on scale.

### 5.2 Verdict rubric (1 = weak, 5 = strong)

| Dimension | Score | Why |
|---|---|---|
| Novelty | 2.5 | Field is crowded. New are the first Lean model of a Philippine statute we found, and the checker framing for untrusted engines. |
| Rigor of claims | 4 | Kernel-checked, no `sorry`, axiom audit, mutation test; assumptions disclosed |
| Demonstrated significance | 2 | About 1.7% of sections; no real data; no legal review |
| Potential significance | 4 | EOPT and E-Governance mandates plus LLM tax tools create real demand for checkable outputs |
| Feasibility of next step | 4 | Individual income tax rules are computational; tooling works on a laptop |
| Fit for MSP Region 3 | 4.5 | Mathematics of proofs, a clean theorem pair, local relevance |

**Is it a winning idea?** For a regional student or early-career mathematics venue it is competitive: it has a real theorem, a working artifact and local relevance. We do not predict award outcomes. As an international research contribution it is not yet winning. The winning version is: **verified checkers for untrusted, LLM-generated Philippine tax assessments, evaluated on a public Philippine benchmark, with a legally reviewed spec that includes the EOPT taxpayer tiers.**

---

## 6. Lean Evidence (re-run 16 Nov 2026, after the tier repair, engine study and 8% election extension)

| Metric | Value |
|---|---|
| Files / lines | 6 files, 859 lines (`TaxSchedule` 63, `TaxScheduleChecks` 29, `GovernanceDemo` 85, `Certificate` 179, `Tiers` 207, `Opt8` 296) |
| Theorems | 54 (schedule 5, administration 10, certificate 10, tiers 13, 8% election 16) |
| Kernel-checked examples | 64 (schedule 10, checks 20, certificate 6, tiers 9, 8% election 19) |
| `sorry` | 0 |
| Axioms, `checkT_sound` / `check8_sound` | `propext`, `Quot.sound` |
| Axioms, `checkT_complete` / `check8_complete` | `propext`, `Classical.choice`, `Quot.sound` |
| Mutation tests | Statute guard removed: soundness breaks, forged certificate accepted. Tier guard removed: three proofs break, tier-forged certificate accepted. 8% rate 8→10: comparison proof breaks, worked examples refuted. Election eligibility guard removed: `regimeOf_ineligible` breaks, boundary examples refuted |
| Worked example | ₱500,000 income, 30 days late: tax ₱42,500.00, surcharge ₱10,625.00, interest ₱419.17, total ₱53,544.17 (medium); micro/small equivalent ₱46,959.58 |
| 8% worked cases | ₱3M gross/₱3M income, 30 days: elected total ₱243,084.93 vs graduated ₱875,658.21; ₱3M gross/₱250k income: graduated ₱99,443.83 beats elected ₱243,084.93; ineligible election with self-consistent amounts rejected (`claimEight_rejected`) |
| Engine study | 254 certificates, 8 engines, 0 false accepts; F6 boundary fault passes 30/32 and is caught only by the tier guard. Covers the default regime (`checkT`) only; `check8` not yet exercised by engines |
| RR 6-2024 | Verified verbatim 16 Nov 2026 from the official BIR text-layer PDF: 10% "of the amount due", interest "six percent (6%)" |
| RR 8-2018 | Verified verbatim 16 Nov 2026 from the official BIR PDF (labelled "digest", contains full text): Q1 election, irrevocable for the year, default graduated, automatic reversion above the threshold |
| Runtime | 33.6 s clean rebuild of all six files on a Windows laptop |

---

## 7. Action Plan

| Step | Deliverable | Success parameter | Status (16 Nov 2026) |
|---|---|---|---|
| 1. Fix the spec | Add the EOPT taxpayer tier (micro/small/medium/large) as an input; Sec. 45 rates | Model matches hand-computed statutory values for all four tiers | **Done.** `Tiers.lean` (207 lines, 13 theorems); conservativity, no-tier-pays-more, ₱3,000,000 VAT/tier gap all proved; tier guard mutation-proven necessary |
| 2. Legal review | One practitioner reads the spec line by line against the statute | Number of disagreements found and resolved, reported honestly | **Packet ready, review not performed.** `docs/spec_review_packet.md`, 12 items with statute quotes and RR 6-2024 / RR 8-2018 verbatim extracts; unsigned |
| 3. Harder rule | 8% optional rate for self-employed individuals versus graduated rates (Sec. 24(A)(2)(b)); certificate proves the choice and amount | Checker smaller than any engine; proof of soundness | **Done.** `Opt8.lean` (296 lines, 16 theorems, 19 examples); `check8_sound`/`check8_complete`, `claimEight_rejected`, universal `tax8_le_graduated`; rate and eligibility guards mutation-proven; engines not yet run against `check8` |
| 4. Benchmark | 50–100 Philippine individual cases with answers from BIR forms and examples | Public dataset with documented provenance | **Done, model-grounded.** 32 stratified cases (`data/benchmark_cases.csv`); dual ground truth (Python + verified Lean agree or no output) |
| 5. Untrusted engines | Run 2–3 LLMs and one spreadsheet; check their certificates | Detection rate of wrong answers; false-rejection rate (0 by the completeness theorem) | **Done for one model family.** 7 seeded-fault engines + 3 fresh assistant sessions; 254 certificates, 0 false accepts (`data/results.csv`, `data/summary.json`, `data/llm_raw/`) |
| 6. Maintenance | CPI threshold updates as versioned specs | Time to update; proofs re-run green | **Process demonstrated.** The tier repair itself was versioned: old proofs broke, new file re-proved them |

The gap to a winning program: step 2's signature, real-assessment data for step 4, replication beyond one model family, and measuring untrusted engines against the election-aware checker.

---

## 8. Open Questions

1. Which BIR rounding conventions apply per line, and do they change any checked value?
2. Can the taxpayer-tier classification itself (gross sales thresholds) be certified from invoices or BIR e-invoicing data?
3. Where is the line between computational rules (formalizable) and open-textured rules (needing human judgment) in the NIRC's 292 sections?
4. Would BIR accept a certificate format as part of an assessment notice, and what does due process require of it?
5. How do certificates interact with LLM explanations: can an LLM be required to emit a checkable certificate and be rejected otherwise?

---

## 9. Bibliography

Tiers: T1 means peer-reviewed, official or a court decision; T2 means credible institutional or preprint; T3 means self-reported or forum.

1. Bates v Post Office Ltd (No 6: Horizon Issues) [2019] EWHC 3408 (QB). https://www.judiciary.uk/wp-content/uploads/2019/12/bates-v-post-office-judgment.pdf — T1
2. Bench-Capon, T., et al. (2012). A history of AI and Law in 50 papers: 25 years of the international conference on AI and Law. *Artificial Intelligence and Law*, 20(3), 215–319. https://doi.org/10.1007/s10506-012-9131-x — T1
3. Blair-Stanek, A., Holzenberger, N., & Van Durme, B. (2023). Can GPT-3 perform statutory reasoning? *ICAIL '23*, 22–31. https://doi.org/10.1145/3594536.3595163 — T1
4. Blum, M., & Kannan, S. (1995). Designing programs that check their work. *Journal of the ACM*, 42(1), 269–291. https://doi.org/10.1145/200836.200880 — T1
5. Bock, M. R., Molisee, K., Ozer, Z., & Shah, S. (2025). TaxCalcBench: Evaluating frontier models on the tax calculation task. arXiv:2507.16126. https://arxiv.org/abs/2507.16126 — T2
6. Cahoo v. SAS Analytics Inc., No. 18-1296 (6th Cir. Jan. 3, 2019). — T1
7. Citron, D. K. (2008). Technological due process. *Washington University Law Review*, 85(6), 1249–1313. — T1
8. Dahl, M., Magesh, V., Suzgun, M., & Ho, D. E. (2024). Large legal fictions: Profiling legal hallucinations in large language models. *Journal of Legal Analysis*, 16(1), 64–93. https://doi.org/10.1093/jla/laae003 — T1
9. de Moura, L., & Ullrich, S. (2021). The Lean 4 theorem prover and programming language. *CADE-28*, LNCS, 625–635. https://doi.org/10.1007/978-3-030-79876-5_37 — T1
10. Guha, N., et al. (2023). LegalBench: A collaboratively built benchmark for measuring legal reasoning in large language models. *NeurIPS 2023 Datasets and Benchmarks*. arXiv:2308.11462; https://doi.org/10.2139/ssrn.4583531 — T1
11. Han, S. S., Takashima, Y., Wei, A., Li, Z., & Genesereth, M. (2026). Law and Order: Tax law autoformalization. arXiv:2610.02792. https://arxiv.org/abs/2610.02792 — T2 (preprint)
12. Hart, H. L. A. (2012). *The Concept of Law* (3rd ed.), ch. VII. Oxford University Press. — T1
13. Hildebrandt, M. (2020). Code-driven law: Freezing the future and scaling the past. In S. Deakin & C. Markou (Eds.), *Is Law Computable?* Hart Publishing. https://doi.org/10.5040/9781509937097.ch-003 — T1
14. Holzenberger, N., Blair-Stanek, A., & Van Durme, B. (2020). A dataset for statutory reasoning in tax law entailment and question answering. *NLLP @ KDD 2020*, CEUR-WS Vol-2645. arXiv:2005.05257. https://arxiv.org/abs/2005.05257 — T1
15. Huttner, L., & Merigoux, D. (2022). Catala: Moving towards the future of legal expert systems. *Artificial Intelligence and Law*. https://doi.org/10.1007/s10506-022-09328-5 — T1
16. Inria (2025, March 24). CATALA translates law into code for more reliable administration. https://www.inria.fr/en/catala-software-dgfip-cnaf — T2
17. Kavanagh, P. (2025). *US Tax Code Formalization in Lean 4* (GitHub repository README, status 18 Dec 2025). https://github.com/kavanaghpatrick/us-tax-code-lean — T3
18. Kennedy, R. (2024). Rules as code and the rule of law: Ensuring effective judicial review of administration by software. *Law, Innovation and Technology*, 16(1), 170–193. https://doi.org/10.1080/17579961.2024.2313801 — T1
19. Klein, G., et al. (2009). seL4: Formal verification of an OS kernel. *SOSP '09*, 207–220. https://doi.org/10.1145/1629575.1629596 — T1
20. Kroll, J. A., Huey, J., Barocas, S., Felten, E. W., Reidenberg, J. R., Robinson, D. G., & Yu, H. (2017). Accountable algorithms. *University of Pennsylvania Law Review*, 165(3), 633–705. https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2765268 — T1
21. Lawsky, S. B. (2017). A logic for statutes. *Florida Tax Review*, 21(1). https://doi.org/10.5744/ftr.2017.0002 — T1
22. Lawsky, S. B. (2017). Formalizing the Code. SSRN. https://doi.org/10.2139/ssrn.2987065 — T1
23. Lawsky, S. B. (2022). Coding the Code: Catala and computationally accessible tax law. *SMU Law Review*, 75(3), 535. https://doi.org/10.25172/smulr.75.3.4 — T1
24. Leroy, X. (2009). Formal verification of a realistic compiler. *Communications of the ACM*, 52(7), 107–115. https://doi.org/10.1145/1538788.1538814 — T1
25. Magesh, V., Surani, F., Dahl, M., Suzgun, M., Manning, C. D., & Ho, D. E. (2025). Hallucination-free? Assessing the reliability of leading AI legal research tools. *Journal of Empirical Legal Studies*, 22(2), 216–242. https://doi.org/10.1111/jels.12413 — T1
26. The mathlib Community (2020). The Lean mathematical library. *CPP '20*, 367–381. https://doi.org/10.1145/3372885.3373824 — T1
27. McConnell, R. M., Mehlhorn, K., Näher, S., & Schweitzer, P. (2011). Certifying algorithms. *Computer Science Review*, 5(2), 119–161. https://doi.org/10.1016/j.cosrev.2010.09.009 — T1
28. Merigoux, D., Chataing, N., & Protzenko, J. (2021). Catala: A programming language for the law. *Proc. ACM Program. Lang.*, 5(ICFP), 1–29. https://doi.org/10.1145/3473582 — T1
29. Merigoux, D., Monat, R., & Protzenko, J. (2021). A modern compiler for the French tax code. *CC '21*, 71–82. https://doi.org/10.1145/3446804.3446850 — T1
30. Mohun, J., & Roberts, A. (2020). Cracking the code: Rulemaking for humans and machines. *OECD Working Papers on Public Governance*. https://doi.org/10.1787/3afe6ba5-en — T1
31. Monat, R., Fromherz, A., & Merigoux, D. (2024). Formalizing date arithmetic and statically detecting ambiguities for the law. *ESOP 2024*, LNCS, 421–450. https://doi.org/10.1007/978-3-031-57267-8_16 — T1
32. Nay, J. J., et al. (2024). Large language models as tax attorneys: A case study in legal capabilities emergence. *Phil. Trans. R. Soc. A*, 382(2270). https://doi.org/10.1098/rsta.2023.0159 — T1
33. Necula, G. C. (1997). Proof-carrying code. *POPL '97*, 106–119. https://doi.org/10.1145/263699.263712 — T1
34. New Zealand Service Innovation Lab (LabPlus) (2018). *Better Rules for Government Discovery Report*. https://www.digital.govt.nz/dmsdocument/95-better-rules-for-government-discovery-report/html — T1
35. OpenFisca (n.d.). OpenFisca: Open rules as code (initiated by the French government, 2011). https://openfisca.org/en/ — T2
36. Parlementaire ondervragingscommissie Kinderopvangtoeslag (2020, December 17). *Ongekend onrecht*. Tweede Kamer. https://www.tweedekamer.nl/sites/default/files/atoms/files/20201217_eindverslag_parlementaire_ondervragingscommissie_kinderopvangtoeslag.pdf — T1
37. Republic Act No. 8424 (1997). National Internal Revenue Code of 1997. https://lawphil.net/statutes/repacts/ra1997/ra_8424_1997.html — T1
38. Republic Act No. 10963 (2017). Tax Reform for Acceleration and Inclusion (TRAIN). https://www.lawphil.net/statutes/repacts/ra2017/ra_10963_2017.html — T1
39. Republic Act No. 11976 (2024, January 5). Ease of Paying Taxes Act. https://www.lawphil.net/statutes/repacts/ra2024/ra_11976_2024.html — T1
40. Republic Act No. 12254 (2025). E-Governance Act. https://www.lawphil.net/statutes/repacts/ra2025/ra_12254_2025.html — T1
41. Royal Commission into the Robodebt Scheme (2023). *Report* (published 7 July 2023; updated 11 July 2023). https://robodebt.royalcommission.gov.au/publications/report — T1
42. Sergot, M. J., Sadri, F., Kowalski, R. A., Kriwaczek, F., Hammond, P., & Cory, H. T. (1986). The British Nationality Act as a logic program. *Communications of the ACM*, 29(5), 370–386. https://doi.org/10.1145/5689.5920 — T1
43. Smith, Godfrey, & Burdon (2026). Reconceptualising rules as code with legal design patterns. *Computer Law & Security Review*, 62, 106377. https://doi.org/10.1016/j.clsr.2026.106377 — T1
44. Waddington, M. (2021). Rules as Code. *Law in Context*, 37(1), 179–186. https://doi.org/10.26826/law-in-context.v37i1.134 — T1
45. Wu, Y., Jiang, A. Q., Li, W., Rabe, M. N., Staats, C., Jamnik, M., & Szegedy, C. (2022). Autoformalization with large language models. *NeurIPS 35*, 32353–32368. https://doi.org/10.52202/068431-2344 — T1
46. OECD (2026). Consultation on the digital provision of law: Towards a shared reference framework for law as code. https://www.oecd.org/en/events/public-consultations/2026/07/consultation-on-the-digital-provision-of-law-towards-a-shared-reference-framework-for-law-as-code.html — T1 (notes only)
47. Le Monde Informatique (2026, June 15). Open Source : la Cnaf s'engage dans le projet Catala de l'Inria. https://www.lemondeinformatique.fr/applications-developpement/2026-06-15-open-source-la-cnaf-s-engage-dans-le-projet-catala-de-l-inria — T2 (notes only)
48. r/singularity (2026). Lean proof of the entire US tax code to find loopholes. https://www.reddit.com/r/singularity/comments/1xt3x96/lean_proof_of_the_entire_us_tax_code_to_find/ — T3 (notes only; the project's starting point)
49. MTF Counsel (2024, May 16). Deficiency interest. https://mtfcounsel.com/2024/05/16/deficiency-interest/ — T2 (notes only; corroborates the 12% rate)
50. Bureau of Internal Revenue (2024). Revenue Regulations No. 6-2024: Implementing Section 45 of RA 11976. https://bir-cdn.bir.gov.ph/BIR/pdf/RR%206-2024%20(final).pdf (official text-layer copy; verified verbatim 16 Nov 2026; local extract `data/sources/RR_6-2024_final.txt`) — T1
51. MPM Tax Consultancy (2024). RR 6-2024: Reduced interest and penalty rates for micro and small taxpayers. https://mpm.ph/rr-6-2024/ — T2
52. Bureau of Internal Revenue (2018). Revenue Regulations No. 8-2018: Implementing the income tax provisions of RA 10963 (TRAIN), including the 8% optional income tax. https://bir-cdn.bir.gov.ph/local/pdf/Digest%20RR%208-2018_copy.pdf (official BIR copy; the file labelled "digest" contains the full regulation text; verified verbatim 16 Nov 2026; local extract `data/sources/RR_8-2018_digest.txt`) — T1

---

## 10. Source Extracts (key facts relied on)

- **[39] RA 11976, Sec. 45:** "The following concessions shall be made available to micro and small taxpayers… (b) A reduced rate of ten percent (10%) for civil penalties as provided under Section 248… (c) A fifty percent (50%) reduction on the interest rate imposed under Section 249."
- **[50] BIR RR 6-2024 (verified verbatim 16 Nov 2026):** "a penalty equivalent to ten percent (10%) of the amount due, in the following cases: A. Failure to file… B. Failure to pay the deficiency tax… C. Failure to pay the full or part of the amount of tax shown on any return…" and "the legal interest imposable to cover taxpayers shall be six percent (6%)". Also sets a ₱500-per-failure information-return penalty capped at ₱12,500 per calendar year and a 50% reduction of compromise penalties for criminal violations of §§113/237/238 (outside the formalized core).
- **[38] RA 10963, Sec. 249 as amended:** deficiency and delinquency interest at double the legal interest rate (12% per annum), corroborated by [49].
- **[38] RA 10963, Sec. 5 (NIRC Sec. 24(A)(2)(b), verified verbatim 16 Nov 2026):** purely self-employed individuals and/or professionals whose gross sales/receipts and other non-operating income "does not exceed" the VAT threshold may elect "an eight percent (8%) tax on gross sales or gross receipts and other non-operating income in excess of Two hundred fifty thousand pesos (P250,000) in lieu of the graduated income tax rates … and the percentage tax under Section 116". RA 11976's amendatory list excludes Sec. 24, so this text stands; Sec. 116 in the EOPT text is 3% of gross quarterly sales (the TRAIN-era ₱500,000 exemption proviso was dropped). Local extracts: `data/sources/RA_10963_sec24_sec116.txt`, `data/sources/RA_11976_sec109CC_sec116.txt`.
- **[52] BIR RR 8-2018 (verified verbatim 16 Nov 2026):** the 8% election is signified in the first-quarter return, is irrevocable for the taxable year, defaults to graduated rates when absent, and reverts to graduated rates automatically if the annual gross exceeds the VAT threshold; unavailable to VAT-registered persons and GPP partners; the ₱250,000 deduction applies only to purely self-employed, not mixed-income earners.
- **[17] Kavanagh README:** 765 sections, about 537,400 lines, 607 theorems, 17 `sorry`, Lean 4.14.0, AI-generated (status 18 Dec 2025). Self-reported.
- **[11] Han et al.:** best LLM alone 66%; Law&Order 100% cell- and form-level on 51 held-out TaxCalcBench returns.
- **[5] TaxCalcBench:** frontier models alone compute fewer than one-third of federal returns correctly.
- **[41] Robodebt:** income averaging as a basis for raising debts found unlawful; report first published 7 July 2023, corrected 11 July 2023.
- **[36] Ongekend onrecht:** parliamentary inquiry found that fundamental rule-of-law principles were violated (17 Dec 2020).
- **[6] Cahoo:** a state review of about 22,000 MiDAS fraud determinations found 93% involved no fraud.
- **[1] Bates (No 6):** Fraser J found that Horizon contained bugs, errors and defects capable of causing branch account shortfalls.
