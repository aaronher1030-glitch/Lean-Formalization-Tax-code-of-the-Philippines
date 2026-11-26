# Deep Research: Research Positioning, Venues, Gaps, and Hurdles

**Prepared:** 19 November 2026  
**Project:** Lean formalization of selected Philippine tax rules  
**Purpose:** Identify a defensible research contribution and suitable publication path for work on formalizing law and accountable governance automation.

## Executive assessment

There is a real and growing research field here, but the project should not claim that formalizing tax law is itself new, or that a proof makes an automated government decision lawful. International work already includes legal domain-specific languages, verified compilers, tax-code implementations, LLM law-to-code benchmarks, and empirical studies showing that interdisciplinary legal software can still be wrong. Recent OECD work frames executable law as public infrastructure and explicitly raises questions of authority, legal review, versioning, maintenance, institutional responsibility, and discretion.

The most credible contribution is narrower and more useful:

> **A technically verified, source-traceable prototype for selected Philippine tax computations, evaluated as an accountability mechanism for digital public services, with independent legal review and explicit treatment of what the model cannot decide.**

That contribution is not complete yet. The project folder says the practitioner review packet has **not** been reviewed; benchmark cases are model-grounded rather than independently confirmed against real BIR assessments; and the current loophole report itself identifies missing certificate premises. Those are research findings and priorities, not footnotes to hide.

For the current artifact, **JURIX** or the **Artificial Intelligence and Law** journal are the closest fit if the paper foregrounds legal knowledge representation and formal verification. **dg.o** is the better fit if the study adds empirical evidence about accountability, adoption, public value, and institutional safeguards. **NLLP** is appropriate only if the central contribution becomes a legal NLP / law-to-code generation method or benchmark. Do not send the same paper to simultaneous archival venues.

## 1. What the project can claim today

Based on the project files:

- Lean models cover a bounded computational core: the individual income-tax schedule, taxpayer tiers, selected late-payment penalties and interest, the VAT threshold, and the 8% election.
- The code contains soundness/completeness theorems for certificate checkers and examples designed to expose computational behavior. The findings report documents a 274-proposition battery, while a separate report describes five model gaps or incentive effects.
- Results are conditional: Lean verifies the theorem against the encoded specification. It does not prove that the specification captures every applicable statute, regulation, BIR practice, factual condition, or taxpayer circumstance.
- The review packet explicitly records unresolved legal questions. The gap findings describe inputs the current checker accepts because particular legal/contextual premises are absent; they are not evidence that BIR software accepts such cases.
- Benchmarks and engine experiments provide an initial technical evaluation, but the project describes them as model-grounded, and the engine study is not broad evidence of performance across independent commercial systems or live tax cases.

This is enough for a strong **prototype / methods paper** if its scope and limitations are precise. It is not yet enough to claim a legally validated tax engine, successful deployment, reduction in tax errors, or demonstrated benefit to Filipino taxpayers.

## 2. Research landscape and what has already been done

### A. Executable legal rules and formal languages

Catala is a legal-specific programming language intended to translate statutory rules into executable code in a way lawyers and programmers can inspect together. Its published evaluation includes U.S. tax law and French family benefits; the authors report finding a bug in the official benefits implementation. Its compiler has formally verified components. This means the project's novelty cannot be “we use code to represent tax law.”

Comparative work on Rules as Code languages has also proposed evaluation criteria beyond raw expressiveness, including usability and organizational adoption. A 2025 framework paper argues that existing comparisons were inconsistent and often too technically focused, then evaluates a Dutch tax-administration language with adoption dimensions. This makes a Philippine implementation interesting as a contextual case, but a mere tool comparison would need to add something not covered there.

### B. LLM law-to-code work

Work in the 2025 Natural Legal Language Processing (NLLP) proceedings provides a benchmark and evaluation framework for generating Catala code from tax-law text. It identifies translation cost, continual amendments, cross-provision dependencies, and legal ambiguity as central difficulties.

The 2026 *Law and Order: Tax Law Autoformalization* preprint reports a neuro-symbolic process that uses LLM-generated symbolic programs, verification, and repair, evaluated on held-out U.S. federal tax returns. It reports 100% cell- and form-level accuracy on 51 held-out returns, compared with 66% for the strongest LLM alone. Because it is a preprint and concerns another jurisdiction and task, its results should be described as the authors' reported evaluation, not as settled general evidence. It nevertheless makes “LLMs plus symbolic checking for tax” an occupied research area.

### C. Empirical evidence about how teams encode law

The 2024 CSCW study *Code-ifying the Law* observed fifteen teams translating a bankruptcy statute into software: nine computer-science-only and six interdisciplinary legal/CS teams. Its qualitative results identify an epistemic divide, communication failures, and errors even when legal experts participate. This is directly relevant: proof can validate the software's behavior relative to a spec, while team process and source interpretation determine whether the spec is legally sound.

### D. Rules as Code and public-sector governance

The OECD's 2020 *Cracking the Code* describes repeated translation gaps from policy intent to legislation, rules interpretation, and implementation. A 2026 OECD consultation now treats “Law as Code” as a public infrastructure question: authoritative representations should remain linked to legal text and expose exceptions, references, hierarchy, responsibility, time limits, discretion, and legal consequences. It also states that executable representations do not replace authoritative legal text or decide individual cases.

This framing is highly relevant to the project, but it also raises the bar: the work should address provenance, authority, versioning, legal review, responsibility, and appealability, rather than present only a correct arithmetic function.

### E. Philippine context

The E-Governance Act (RA 12254) covers government offices and LGUs and expressly contains data/privacy and information-security constraints. It creates a timely local setting for research into trustworthy digital rules, but it does not itself endorse Lean, tax automation, or this project. The project should treat the Act as context and a policy motivation, not as proof of government demand or authorization.

BetterGov.ph describes itself as a volunteer-driven civic technology/open-source movement focused on making government data accessible, understandable, and actionable. Its current public materials also describe work with the DICT eGov team on the Gov.PH portal and a civic-tech fellowship. That makes BetterGov.ph a plausible **conversation and civic-tech collaboration partner** for transparency, public documentation, or usability feedback; it is not a peer-reviewed publication venue or a substitute for an independent tax-law reviewer. Do not imply endorsement or official status unless explicitly granted.

## 3. The research gap: what is defensible

### Claims to avoid

- “No one has formalized tax law.” False internationally.
- “This is the first verified tax code.” Not defensible given Catala, formal verification work, and new LLM-based tax formalization.
- “The checker proves the tax computation is legally correct.” It proves properties of the model; legal fidelity requires separate evidence.
- “We found BIR loopholes.” The documented findings are about the prototype's specification gaps or incentives in the law as encoded, not BIR production systems.
- “Formalization automates governance.” Too broad: the current artifact models a small set of calculations and does not automate fact-finding, discretionary judgment, assessment authority, notice, or appeal.

### A stronger gap statement

> Existing work demonstrates legal DSLs, verified rule implementations, LLM-assisted tax formalization, and the risks of cross-disciplinary legal-software development. There remains a practical need for jurisdiction-specific evidence about how a verified formal specification can be made reviewable and contestable in a public-service setting, particularly where the governing rules are amended across statutes and regulations and where factual and discretionary predicates sit outside the computation. This study contributes a Philippine tax-code case study with machine-checked properties, source-linked assumptions, adversarial certificate tests, and an explicit analysis of missing legal premises. Its contribution is a bounded method and artifact, not a validated government system.

This should be labeled a **provisional gap** until you conduct a documented search. It is not enough to say that two searches found no Philippine precedent. A defensible novelty statement needs a transparent search protocol across relevant scholarly indexes and local legal/technical repositories, with query terms, date, screening criteria, and excluded/related work. Phrase the outcome as “we found no prior study matching X in the databases searched,” not as an absolute first.

### Suggested research questions

1. **Specification and verification:** How can a bounded set of Philippine tax computation rules be encoded with machine-checkable guarantees while retaining traceability from each modeled claim to its legal source and assumptions?
2. **Model adequacy and review:** Which legal ambiguities, omitted predicates, or amendment dependencies are surfaced by independent practitioner review, and how do these change the specification and checker?
3. **Error checking:** How effectively does the checker detect seeded computation and certificate errors, and what errors remain undetectable because the input facts or legal predicates are outside the model?
4. **Governance:** What transparency, versioning, accountability, privacy, and human-review conditions would be required before a machine-checkable rule could responsibly support a public digital service?

Do not make the paper answer all four equally. For the first paper, lead with RQ1 and RQ3; treat RQ2 as a necessary planned validation phase; make RQ4 a bounded implications section unless you collect stakeholder data.

## 4. Biggest hurdles, ranked

| Priority | Hurdle | Why it matters | Evidence or work needed |
|---|---|---|---|
| 1 | **Legal fidelity** | A kernel proves the encoded mathematics, not that the encoding is the law. Statutes, amendments, regulations, rulings, administrative practices, and factual conditions can interact. | Independent Philippine tax practitioner review, source-by-source traceability, documented resolution of disagreements, and versioned revisions. |
| 2 | **Scope and claim discipline** | “Automating governance” invites claims about decisions, people, and outcomes that the current arithmetic prototype does not support. | Bound the paper to verification of specified computations and certificates; clearly exclude fact-finding, discretion, enforcement, and adjudication. |
| 3 | **External validity of evaluation** | Synthetic/model-grounded cases and seeded engines show properties of this benchmark, not real-world error rates or general LLM performance. | Independent ground truth, case provenance, realistic edge-case sampling, multiple independent systems, and clear false-accept / false-reject denominators. Use sensitive administrative data only with authorization and safeguards. |
| 4 | **Versioning and legal dependencies** | Tax rules change; regulations and cross-references can modify how a statutory provision operates. A verified but stale model can mislead. | Pin effective dates, source versions, amendment history, dependency map, update process, and regression evidence. Treat dates/election/limitation rules as model inputs or explicit exclusions. |
| 5 | **Boundaries of automation** | Taxable income, eligibility, documentary evidence, intent, exceptions, and equitable judgment are not proved just because a calculation is. | Define a human-review boundary and a precise certificate contract; identify which predicates are asserted inputs and who verifies them. |
| 6 | **Interdisciplinary workflow** | Research finds legal/technical teams may misunderstand each other's assumptions; a lawyer's presence alone does not guarantee correctness. | Collaborative review records, question log, source-linked definitions, decision ownership, and a protocol that lets lawyers challenge technical representations directly. |
| 7 | **Public legitimacy and contestability** | A proof badge can create false confidence or make an interpretation seem official. Affected people need understandable reasons and correction/appeal paths. | Clearly mark non-authoritative status, expose calculation steps and assumptions, preserve human decision responsibility, and test whether explanations are understandable. |
| 8 | **Data protection and security** | Administrative tax cases may contain sensitive personal and financial data; RA 12254 also points to privacy and system-security controls. | Prefer public/constructed data initially; if real data are used, establish lawful authority, data minimization, access limits, retention/deletion, and ethics/security review. |
| 9 | **Research novelty and reproducibility** | Existing work already covers legal DSLs, tax autoformalization, benchmarks, and formal checking. | Compare contribution precisely; publish pinned tool versions, clean run instructions, source/data provenance, limitations, and artifacts. |
| 10 | **Institutional ownership and maintenance** | A research repository is not an agency service. Someone must authorize, update, host, audit, and answer for the executable rule. | Do not imply deployment readiness; propose a governance model and a non-deployment exploratory pilot first. |

## 5. Recommended research venue

| Venue | Fit for this project | What reviewers will expect | Assessment |
|---|---|---|---|
| **JURIX** | Very good for formal legal knowledge representation, computational law, legal systems, and socio-technical approaches. | Clear novelty, solid AI-and-law literature, technical/formal validity, and appropriate evaluation. It accepts long, short, and demo formats. | Best conference target for the current formalization/checker story. JURIX 2026 submission deadline was 5 September 2026 and has passed; plan for a future edition rather than submit late. |
| **Artificial Intelligence and Law (journal)** | Excellent topic fit for formal/computational legal models and technical, empirical, or formal work on AI's legal/social implications. | A substantial technical, empirical, or formal contribution; the journal says doctrinal/philosophical-only papers and surveys without such contribution are out of scope. | Strong journal target after legal review and stronger evaluation. A 274-theorem count alone will not establish significance. |
| **dg.o — Digital Government Research** | Strong fit if reframed around public value, accountable digital service design, public-sector adoption, institutional responsibility, or citizen contestability. | Explicit relevance to digital-government problems/policies and evidence suitable to the public administration claim. | Best venue for a later governance-impact paper. The 2026 conference is past; monitor the 2027 call. Technical formalization alone may not satisfy the governance contribution. |
| **NLLP (ACL workshop)** | Fit only if developing a language-processing contribution: statute-to-code generation, legal source extraction, benchmark/data, attribution, or LLM evaluation. | Novel NLP method/task/dataset and careful evaluation; workshop papers have limited length. | Not the best home for the current hand-specified Lean model alone. The 2026 call/deadline has passed. |
| **ICAIL** | High-prestige AI-and-law conference for a novel technical legal-AI contribution. | Strong AI/legal method or evaluation, beyond a localized implementation demonstration. | Aspirational target if the project adds a genuinely general method or compelling evaluation, not merely a Philippine case application. Check the next call when announced. |
| **Philippine law / public-administration journal or research forum** | Useful for local doctrine, implementation, institutional design, and policy recommendations. | Philippine legal-source rigor, local expert review, and clear governance implications. | Good companion publication or policy note after practitioner validation; choose a specific journal with adviser input and check its current author rules. |

### Venue recommendation

**Primary route:** prepare a **JURIX-style short/long paper** around the formal specification, checker, adversarial evaluation, and legal-review method; later extend it to the **Artificial Intelligence and Law** journal after practitioner review and stronger empirical validation. JURIX 2026 is already closed as of this report, so this is a target profile, not an available late submission.

**Second route:** develop a separate **dg.o paper or policy paper** only after adding a governance evaluation: interviews or structured workshops with tax practitioners, citizens, public-sector digital teams, or civil-society groups; an explicit public-value framework; and a proposal for review, update, correction, and appeal. BetterGov.ph can be approached as a civic-tech discussion partner for this work, with its role and any endorsement stated accurately.

**Do not combine everything into one paper.** A technically rigorous proof paper and an empirically grounded digital-government paper have different research questions and reviewer expectations. They may share the artifact while making separate contributions.

## 6. Suggested paper positioning

### Working title

**Checking the Computation, Exposing the Assumptions: A Verified Core for Philippine Tax Rules**

Alternative governance-facing title: **From Statute to Checkable Service: Verification and Contestability in a Philippine Tax-Code Pilot**

### Proposed abstract-level claim

This paper presents a Lean 4 specification and certificate checker for a bounded set of Philippine individual tax computations. We prove checker properties relative to the stated model, compare outputs against an independent implementation, and evaluate seeded errors and boundary cases. We document assumptions and specification gaps, distinguishing implementation errors from unmodeled legal predicates and statutory incentives. The artifact demonstrates how machine checking can make selected computations inspectable and challengeable; it does not establish complete legal fidelity or suitability for government deployment. We identify the legal review, versioning, evidence, and human-appeal conditions required for responsible use.

### A contribution reviewers could recognize

1. A versioned executable specification for selected rules, with direct mappings to legal sources and explicit effective dates.
2. A small proof-checking architecture for calculation certificates, including formal guarantees and fault-injection evaluation.
3. A systematic taxonomy of **what the checker can verify, what it assumes, and which gaps arise from missing legal predicates**, supported by an independent legal review record.
4. A reproducible Philippine case study that offers evidence for how formal methods can support auditability without conflating verified computation with an automated legal decision.

Items 3 and 4 are where the current project most needs additional work.

## 7. Recommended work plan before submission

### Phase 1 — Narrow the claim and search literature

- Choose one primary research question and one target audience.
- Conduct a documented scoping review across AI-and-law, legal informatics, formal methods, digital-government, Philippine legal, and Rules as Code literature.
- Build a comparison matrix: jurisdiction, source types, formalism, verification properties, evaluation data, legal validation process, change management, and governance/appeal provisions.
- State novelty as a qualified result of the search protocol.

### Phase 2 — Establish legal validity

- Arrange independent review of the complete spec packet by a qualified Philippine tax practitioner.
- Record each issue, source citation, decision, and resulting code change.
- Resolve or explicitly retain disputed interpretations; do not bury unresolved questions as implementation details.
- Re-run Lean proofs and benchmark checks after changes and report which previous results changed.

### Phase 3 — Upgrade the evaluation

- Add source-grounded, independently checked cases and explain each case's provenance.
- Separate error classes: arithmetic fault, regime/tier fault, unsupported or inconsistent certificate, missing legal context, and uncertain facts.
- Expand beyond seeded code mutations when possible: independent implementations, fresh model runs, or expert-authored errors.
- Report denominators, test selection, false acceptances and false rejections, and avoid translating benchmark performance into deployment claims.

### Phase 4 — Add governance evidence (if targeting dg.o / BetterGov)

- Interview or workshop with a small, clearly sampled group of practitioners and civic/public-service stakeholders; obtain ethics approval/consent where required.
- Test whether a certificate explanation makes the calculation easier to inspect and contest.
- Map ownership: who approves the formal rule, who updates it after amendments, who hosts it, who handles disputes, and who is accountable when the source interpretation is challenged.
- Keep the demonstration non-operational until an authorized public institution establishes a governed pilot.

### Phase 5 — Release and submit

- Publish source, release tag, Lean/toolchain versions, runbook, data dictionary, and provenance/permissions.
- Add a prominent statement that the checker validates claims relative to the encoded model and is not legal advice or an official assessment.
- Submit to one archival venue at a time; coordinate any preprint or workshop version with the target venue's rules.

## 8. BetterGov.ph: fit and a responsible ask

BetterGov.ph's public description emphasizes open-source civic technology and making Philippine government data accessible, understandable, and actionable. This aligns with an exploratory collaboration on **public explanation and contestability**, but does not make BetterGov the legal authority for tax interpretation. A sensible initial request would be feedback on whether a transparent rule artifact and citizen-facing explanation are useful, what accessibility and provenance standards matter, and whether a non-deployment civic-tech prototype could fit an open-government project or fellowship challenge.

Keep the ask modest and specific:

- seek feedback on the concept and its public-interest framing;
- invite connections to independent tax/legal reviewers or civic-tech researchers;
- offer a clearly labeled open-source research prototype and documentation;
- ask whether a later public-facing explanation/demo would be useful;
- make no claim that BetterGov, DICT, BIR, or another government institution endorses the model.

The government's broader E-Governance Act provides context for digital public services, but any use of agency systems or sensitive taxpayer data requires separate authority, privacy/security controls, and institutional approval.

## 9. Source notes and links

The following sources informed this report. The project documents remain the primary source for the status of the local artifact.

### Research and methods

- Merigoux, Chataing, and Protzenko, [“Catala: A Programming Language for the Law”](https://doi.org/10.1145/3473582), ICFP 2021.
- Van Woensel et al., [“A Systematic Approach to Assess Languages Proposed for Rules as Code”](https://doi.org/10.3233/FAIA251595), 2025.
- [“Translating Tax Law to Code with LLMs: A Benchmark and Evaluation Framework”](https://aclanthology.org/2025.nllp-1.4/), NLLP 2025.
- Han et al., [“Law and Order: Tax Law Autoformalization”](https://arxiv.org/abs/2610.02792), 2026 preprint; results are reported by the authors and await peer-reviewed confirmation.
- Green et al., [“Code-ifying the Law: How Disciplinary Divides Afflict the Development of Legal Software”](https://doi.org/10.1145/3686937), ACM PACM HCI / CSCW 2024.
- OECD, [*Cracking the Code: Rulemaking for Humans and Machines*](https://www.oecd.org/content/dam/oecd/en/publications/reports/2020/10/dechiffrer-le-code_d56cab77/3afe6ba5-en.pdf), 2020.
- OECD, [2026 consultation toward a shared reference framework for Law as Code](https://www.oecd.org/en/events/public-consultations/2026/07/consultation-on-the-digital-provision-of-law-towards-a-shared-reference-framework-for-law-as-code.html).

### Venues

- [JURIX 2026 call and scope](https://jurix.nl/); 2026 deadline listed as 5 September 2026.
- [Artificial Intelligence and Law journal scope](https://link.springer.com/journal/10506).
- [dg.o conference calls and tracks](https://dgsociety.org/); 2027 conference announcements are being posted, with the detailed paper call to monitor.
- [NLLP 2026 information](https://www.aclweb.org/portal/content/nllp-2026); confirm subsequent editions and deadlines from the workshop's official site.
- [ICAIL / International Association for AI and Law](https://iaail.org/).

### Philippine policy and possible civic-tech collaboration

- [Republic Act No. 12254, E-Governance Act, Supreme Court E-Library](https://elibrary.judiciary.gov.ph/thebookshelf/showdocs/2/99787).
- [BetterGov.ph: About](https://about.bettergov.ph/).
- [BetterGov.ph: Projects](https://about.bettergov.ph/projects/).

## Bottom line

The project has the beginnings of a publishable technical case study. To make it research rather than a demonstration, its next decisive step is independent legal review followed by a stronger, independently grounded evaluation. To make the broader “automating governance” argument credible, it also needs evidence about institutional ownership, versioning, explanations, and contestability. The best path is to publish a bounded AI-and-law paper first, then build a separate public-governance study with BetterGov or other civic/public-sector partners if that collaboration becomes concrete.
