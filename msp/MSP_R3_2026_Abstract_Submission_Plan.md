# MSP Region 3 Convention 2026

## Abstract Submission Plan — Lean 4 Formalization of the Philippine Tax Code

Prepared for: **Aaron Y. Hernandez**, BSANHS Senior Researcher

Adviser: **Oliver R. Francisco**

Date: **15 November 2026**

Hard deadline: **20 November 2026 (Friday)**

<!-- pagebreak -->

# 1. Verified call and format

The live call matching the 20 November date is the **2026 MSP Region 3 Annual Convention and General Assembly**, not the national annual convention (held 3–5 June 2026, deadline 21 March 2026). The Region 3 convention was moved from 27 November to 4 December 2026.

| Item | Confirmed detail |
|---|---|
| Organizer | Mathematical Society of the Philippines — Region 3 Chapter |
| Event | 2026 MSP Region 3 Annual Convention and General Assembly |
| Date and venue | 4 December 2026 (Friday), Central Luzon State University, Science City of Muñoz, Nueva Ecija |
| Abstract deadline | **20 November 2026** |
| Early-bird registration | Until 27 November 2026 |
| Submission form | https://bit.ly/2026mspr3_abstract |
| Registration form | https://bit.ly/2026mspr3_registration |
| Templates | https://bit.ly/2026mspr3_templates (DOCX, LaTeX, sample PDF) |
| Overleaf template | https://bit.ly/2026mspr3_overleaf |
| Inquiries | math.soc.phil.region3@gmail.com |
| Audience | Teachers, students, administrators, and researchers |

**Format, taken from the official Region 3 template.** A4 paper; 12 pt body text; Times New Roman in Word; title 14 pt bold; author line 12 pt with superscript affiliation numbers and an asterisk on the presenting author; affiliations italic; emails in a monospaced font; running header "MSP Region 3 Convention 2026" on the left and "4 December 2026, CLSU" on the right. The LaTeX template uses `article` at 12 pt, A4, a 6.5 in × 9 in text block, and the same header. The abstract must be **100–250 words**, justified. References are optional with a **maximum of five**. Submit the **DOCX or TEX source plus a compiled PDF**. Delete the instruction paragraph in the DOCX.

**Unverified detail.** The template does not state a filename convention, and the submission form returned HTTP 401 to an unauthenticated request, so its exact fields could not be read. Open the form in a signed-in browser on 15 November and mirror its fields; use `HERNANDEZ-MSPR3-2026-Abstract.docx` and `.pdf` unless the form or organizers say otherwise.

# 2. What the abstract should claim

One sentence controls the whole text: *the NIRC can be partly formalized now, but the binding constraint is formalizability and encoding fidelity, not proof engineering.* This keeps the paper honest, matches the feasibility study, and gives a mathematics audience a result rather than an advocacy pitch.

**Recommended title (Option A):** *What Can Be Proved About the Tax Code? A Lean 4 Feasibility Study of the Philippine NIRC.*

- **A (recommended).** *What Can Be Proved About the Tax Code? A Lean 4 Feasibility Study of the Philippine NIRC.* A question, a method, and an object in one line; works for a mixed mathematics audience.
- **B.** *From Statute to Proof: A Formalizability Audit of the National Internal Revenue Code.* Emphasizes the empirical map; weaker signal that a Lean artifact exists.
- **C.** *A Lean 4 Micro-Pilot for Philippine Tax Law: The TRAIN Schedule and a 40-Section Audit.* Most concrete; slightly narrow for a plenary audience.

**Authors.** Aaron Y. Hernandez¹ (presenting author) and Oliver R. Francisco¹ (or ² if the adviser is at a different institution). Confirm affiliation wording and emails before drafting. Do not list an unconfirmed co-author.

**Positioning.** This is formalization and proof engineering with an empirical formalizability component. It is not a governance essay, not a tax calculator, and not legal advice. No claim of a whole-code proof, BIR endorsement, or legal validation.

# 3. Word budget

Target 235–245 words, leaving room under the 250 cap for a late result sentence.

| Move | What it says | Words | Evidence to insert |
|---|---|---|---|
| Context | The NIRC has 292 sections in 14 titles, about 85,000 words; automation needs machine-checked specifications | 35 | Verified section index |
| Gap | No systematic evidence exists on which Philippine provisions are formalizable; the US precedent covers one year and one tax | 35 | Section 3 of the feasibility study |
| Aim | Audit a stratified sample of 40 sections and build a Lean 4 micro-pilot of the TRAIN schedule | 25 | Study protocol |
| Method | Five-level codebook (L0–L4); 25% double-coded; Cohen's kappa; centavo amounts; boundary and validation checks | 70 | Codebook and Appendix C |
| Results | Share directly computable; kappa; Lean compile status and checks passed | 50 | Fill on 19 November |
| Contribution | Public index, reusable codebook, verified micro-model; separates arithmetic from discretion | 30 | Artifacts |

**Result slots to fill on 19 November.** R1: share of sampled sections coded L1 or L2, with a Wilson interval if space allows. R2: kappa on the 10 double-coded sections. R3: whether the Lean file compiles and how many checks pass. R4: number of cross-reference anomalies, only if that audit is finished. Use three of the four; do not crowd the abstract.

# 4. Day-by-day plan

| Date | Work | Output | Gate |
|---|---|---|---|
| Sun 15 Nov | Open the form signed in; download the DOCX and LaTeX templates; confirm co-author, affiliation, and emails; choose the title; draft the skeleton in Appendix A; email the adviser | Confirmed author block and title | Title and co-author locked |
| Mon 16 Nov | Study Day 1: verify the 292-section index; install Lean; compile the micro-pilot or record the failure | Corpus count and Lean GO/NO-GO | Lean decision made |
| Tue 17 Nov | Study Day 2: calibrate the codebook, compute kappa, lock sample statistics | R1 and R2 values | Kappa computed |
| Wed 18 Nov | Study Day 3: finish the Lean checks and optional cross-reference audit; insert results; adviser review | Results paragraph and reviewer comments | Adviser comments received |
| Thu 19 Nov | Study Day 4: final text; format in the official template; export PDF; count words; co-author approval | Final DOCX and PDF | PDF approved |
| Fri 20 Nov | Format QA; submit by 12:00 noon; save the confirmation; plan registration | Submitted abstract | Confirmation captured |

Submit before noon. The call states a date but not a time, so an early submission avoids a last-hour form failure.

# 5. Formatting and QA checklist

- ☐ Instruction paragraph deleted; header reads "MSP Region 3 Convention 2026" and "4 December 2026, CLSU".
- ☐ A4; Times New Roman 12 pt body; title 14 pt bold; affiliations italic; emails monospaced.
- ☐ Superscript affiliations and asterisk on the presenting author.
- ☐ Abstract 100–250 words, justified; count excludes title, authors, and references.
- ☐ At most five references; no user-defined LaTeX commands if the TEX route is used.
- ☐ PDF exports cleanly, with selectable text and embedded fonts.
- ☐ Claims match the evidence: no whole-code proof, no legal validation, no agency endorsement.
- ☐ Adviser approval recorded by 19 November.
- ☐ Filename consistent across DOCX and PDF.

# 6. Submission steps

1. Sign in to a Google account, then open the submission form. The unauthenticated link returns 401; this is an access restriction, not a dead link.
2. Prepare the answers in a text file first: title; authors, affiliations, emails; presenting author; abstract; keywords; presentation type if asked.
3. Upload the DOCX (or TEX) and the PDF. Submit.
4. Screenshot the confirmation page. If no acknowledgment arrives by 23 November, email math.soc.phil.region3@gmail.com with the title and attached files.
5. Register separately through the registration link; early-bird ends 27 November. Request an invitation letter if the school requires one.
6. Keep the submission packet in one folder: source, PDF, confirmation, reviewer comments.

# 7. Contingencies

| If | Then |
|---|---|
| Lean does not compile by 18 November | Report a specification and evaluation plan, not proofs; the audit remains a complete study. Say "mechanized specification" only if the file actually compiles. |
| The audit is incomplete by 19 November | Submit the protocol version: design, corpus counts, codebook, and planned checks. Label results "preliminary". |
| The adviser cannot review in time | Submit with confirmed authors only; do not add an unconfirmed co-author. Record the review status in your own notes. |
| The form stays inaccessible | Email the organizers on 16 November with title, abstract, and files; ask for an alternate channel. |
| The abstract exceeds 250 words | Cut context and references first; keep method and results. |
| A result is null or negative | Report it. A low formalizable share is a finding about governance, not a failed study. |

<!-- pagebreak -->
# 8. Reference shortlist (choose at most five)

1. The US formalization preprint, arXiv:2610.02792.
2. Catala: A Programming Language for the Law, arXiv:2103.03198.
3. OECD, *Cracking the Code: Rulemaking for humans and machines* (2020).
4. Lean 4 documentation, https://lean-lang.org/.
5. Republic Act No. 8424 (NIRC) and Republic Act No. 10963 (TRAIN), LawPhil.

# Appendix A. Draft skeleton to revise on 19 November

*Replace bracketed slots with measured values. Current length: 151 words with the slot filled; revise results before 250.*

Governments increasingly encode statutes in software, but the encoding is rarely checked against the law. Lean 4 offers machine-checked specifications, yet no systematic evidence exists on which Philippine provisions are formalizable. We report a formalizability audit of the National Internal Revenue Code: 292 sections in 14 titles, approximately 85,000 words. From a stratified sample of 40 sections, two coders classify each dominant operative rule as not a rule, directly computable, parameterized, discretionary, or open-textured; 25% are double-coded and agreement is reported with Cohen's kappa. We pair the audit with a Lean 4 micro-pilot of the 2023-onward TRAIN individual income tax schedule, representing amounts in centavos and checking non-negativity, boundary continuity, and [N] validation values. [RESULTS: share directly computable; kappa; compile status]. The contribution is a public section index, a reusable codebook, and a verified micro-model that separates arithmetic from discretion. The results show where formal verification can support tax administration now and where human judgment must remain.

# Appendix B. Submission-day card

1. Open the form signed in; paste prepared answers.
2. Upload `HERNANDEZ-MSPR3-2026-Abstract.docx` and `.pdf`.
3. Confirm word count is 100–250 and references are at most five.
4. Submit; screenshot the confirmation.
5. Register separately by 27 November.
6. File the confirmation with the abstract and reviewer comments.
