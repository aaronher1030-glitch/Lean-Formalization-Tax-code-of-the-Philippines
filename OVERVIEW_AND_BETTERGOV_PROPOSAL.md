# Project Overview and BetterGov.ph Proposal

## Short overview

This project explores how selected Philippine tax rules can be represented as explicit, machine-checkable specifications using Lean 4. It focuses on computational parts of the National Internal Revenue Code (NIRC), including the individual income-tax schedule, taxpayer tiers and related penalties, the VAT threshold, and the optional 8% tax regime.

The work has grown from a feasibility study into a substantial technical prototype. It includes Lean definitions and proofs, certificate checkers for tax computations, benchmark cases, independent Python comparisons, seeded-error experiments, and analyses of boundaries and modeling gaps. The current findings battery reports 274 checked propositions. These results show what follows from the formal model; they do not establish that the model is a complete or authoritative statement of Philippine tax law.

The project also documents important limitations. The specification has not yet received the planned line-by-line review by a Philippine tax practitioner. Some certificate inputs and legal conditions are not represented, and the benchmark cases are model-grounded rather than validated against real taxpayer assessments. The findings therefore serve as research leads and demonstrations of method, not confirmed loopholes in BIR systems or legal advice.

## What is in the folder

- **Feasibility study** — the initial research question, scope, four-day study design, and rationale for studying formalizability rather than claiming to formalize the whole NIRC.
- **Deep research review** — background on formal methods, tax-law automation, public-sector risks, related projects, and the Philippine governance context.
- **Lean prototype** — executable definitions, certificate checkers, proofs, examples, and mutation checks for the modeled tax rules.
- **Benchmarks and results** — sampled NIRC sections, tax cases, results from deliberately faulty calculation engines, and Python/Lean comparison data.
- **Findings reports** — a 274-proposition findings battery and a separate five-item analysis of specification gaps and statutory incentives.
- **Practitioner review packet** — a structured list of encoded legal claims, sources, assumptions, and questions for a Philippine tax practitioner. Its review status is still **not performed**.
- **Rendered study documents** — DOCX and PDF versions of the feasibility study and verified-core paper draft.

## Main contribution and value

The strongest current contribution is a reproducible prototype for checking tax-computation certificates: a separate computation engine can produce a result, while a small Lean checker verifies the submitted calculation against the formal specification. The project also demonstrates how formalization can expose threshold behavior and missing assumptions, while making clear that proof correctness and legal fidelity are separate questions.

For BetterGov.ph, the most suitable framing is a **research and public-interest collaboration proposal**: assess whether transparent, independently reviewed, machine-checkable specifications can improve the auditability and contestability of digital public rules. The work should be presented as an early-stage research prototype, not a ready-to-deploy BIR tax calculator or a claim that BetterGov.ph or the government endorses its legal interpretation.

## Recommended next steps toward a full research paper

1. **Stabilize the research question and claims.** Center the paper on the method and evaluation of a verified checker for a bounded set of Philippine tax rules. Separate demonstrated Lean results, interpretation-dependent findings, and open hypotheses.
2. **Obtain independent legal review.** Ask a Philippine tax lawyer or CPA with tax-administration experience to review the specification packet. Record disagreements and revisions, then rerun the proofs and benchmark after any changes.
3. **Close the validation gap.** Confirm rounding, day-count, assessment-period, election-timing, taxpayer eligibility, and other currently omitted conditions against primary legal sources and applicable BIR practice. Add guard conditions only after review and preserve the old/new behavior for comparison.
4. **Improve the evaluation.** Document benchmark construction and provenance; seek permissioned, anonymized, representative cases or authoritative worked examples; compare more than one independent implementation/model family; report false acceptance and false rejection measures and limitations.
5. **Make the artifact reproducible.** Pin Lean and tool versions, provide a clean run guide, stable data dictionary, source citations, and a public repository release. Ensure generated results can be regenerated from documented commands.
6. **Write and submit the paper.** A credible structure is: problem and contribution; legal scope and source hierarchy; formal model and checker; evaluation; findings; threats to validity and ethics; governance implications; reproducibility appendix. Select a venue only after adviser and practitioner review.

## Suggested BetterGov.ph proposal

**Working title:** *Machine-Checkable Rules for Accountable Digital Government: A Philippine Tax-Code Pilot*

**Request:** Invite BetterGov.ph to discuss a small, time-bounded research collaboration or technical review of the project. The collaboration could help identify a public-interest use case, review the transparency and contestability requirements, and connect the team with independent legal and tax-administration expertise. Any evaluation using agency data or systems would require a separate agreement and appropriate privacy and security safeguards.

**Proposed pilot:** Review and refine one bounded tax-rule model and its certificate checker; publish the assumptions, legal sources, test cases, and reproducible results; then convene a short technical and policy review on how a person could inspect and contest a machine-generated calculation. The pilot would not make assessments, process taxpayer data, or replace agency or professional judgment.

**Potential outputs:**

- A practitioner-reviewed, versioned specification for the selected rules.
- A public checker, documentation, and reproducible benchmark where licensing and source permissions allow.
- A short findings paper and policy note describing benefits, limitations, and safeguards.
- A recommendation on whether a larger pilot is justified and what governance controls it would need.

**Measures of success:** independent review completed and disagreements resolved or disclosed; benchmark provenance and limitations documented; all published results reproducible; seeded computational errors detected with reported rates; and a clear process proposed for explanation, correction, and human appeal.

## Suggested immediate sequence

1. Have the adviser approve the paper's narrower claim and scope.
2. Complete practitioner review of the existing packet and revise the specification accordingly.
3. Prepare a clean, shareable project package and a two-page concept note using the proposal above.
4. Approach BetterGov.ph for an exploratory discussion, asking for feedback and possible collaboration rather than implying endorsement.
5. Incorporate feedback, complete the paper evaluation, and submit the research paper before making any deployment claim.

**Current readiness:** strong technical prototype and substantial draft research materials; independent legal validation, real-world evaluation, and external stakeholder review remain the key steps before presenting this as a full-fledged validated research result.
