# Specification Review Packet

**Project:** A Verified Core for Tax Administration — a computational core of the Philippine NIRC in Lean 4 (schedule, penalties, VAT threshold, taxpayer tiers, and the 8% election)
**Packet prepared:** 16 November 2026, by Aaron Y. Hernandez (researcher)
**Status of review:** NOT PERFORMED. This packet is the input to a review by a Philippine tax practitioner. Nothing here is legal advice, and no attorney has read or endorsed these encodings.

---

## 1. Why this packet exists

The Lean development proves that the checker is correct *for the specification as written*:

- `checkT_sound`: any certificate the checker accepts states the exact statutory liability under the modeled rules;
- `checkT_complete`: the honest certificate is always accepted;
- `check8_sound` / `check8_complete`: the same guarantees for the election-aware checker, including that the claimed regime matches the election and eligibility;
- mutation tests show the schedule guard, the tier guard, the 8% rate, and the election eligibility guard are all load-bearing.

What no proof can establish is whether the specification *matches the law*. That question needs a human practitioner. This packet lists every statement the model encodes, the statutory source we relied on, and the modeling assumptions a reviewer should challenge.

**Reproduce the artifact first:**

```bash
cd lean && bash run_demo.sh   # Lean 4.35.0, core library only; ~34 s, six files
```

Each review item below names the Lean file and definition it encodes, in `lean/TaxSchedule.lean`, `lean/GovernanceDemo.lean`, `lean/Certificate.lean`, `lean/Tiers.lean`, and `lean/Opt8.lean`.

---

## 2. Review items

For each item, mark **Agree** or **Disagree** and add comments. "Disagree" should say what the statute actually requires, with citation.

### S1 — Income tax schedule (TRAIN, effective 2023)

| | |
|---|---|
| **Encoded statement** | Taxable income *t* (centavos) is taxed 15% of the slice between ₱250,000 and ₱400,000, 20% between ₱400,000 and ₱800,000, 25% between ₱800,000 and ₱2,000,000, 30% between ₱2,000,000 and ₱8,000,000, 35% above ₱8,000,000; zero at or below ₱250,000. |
| **Lean** | `TaxSchedule.slice`, `TaxSchedule.bracketTax`; boundary checks in `TaxScheduleChecks.lean` (20 `decide` proofs). |
| **Source** | RA 10963 (TRAIN, 2017) amending NIRC §24(A)(2), individual graduated rates effective January 1, 2023. lawphil: https://www.lawphil.net/statutes/repacts/ra2017/ra_10963_2017.html |
| **Assumptions** | (a) thresholds are inclusive at the lower end (income of exactly ₱250,000 pays nothing); (b) all arithmetic truncated (floor) to centavos; (c) "taxable income" is taken as an input, not computed from gross income less deductions. |
| **Reviewer verdict** | Agree / Disagree: ______ |

### S2 — Taxpayer tier classification

| | |
|---|---|
| **Encoded statement** | By gross sales: micro = under ₱3,000,000; small = ₱3,000,000 up to (but not including) ₱20,000,000; medium = ₱20,000,000 up to (but not including) ₱1,000,000,000; large = ₱1,000,000,000 and above. |
| **Lean** | `Tiers.classify`, `Tiers.Tier`. |
| **Source** | RA 11976 (Ease of Paying Taxes Act, 2024) §3, amending NIRC §21(b). Quoted words from lawphil (the printed numerals in the source contain typographical errors, so the words control): micro — "Less than Three million pesos"; small — "Three million pesos … to less than Twenty million pesos"; medium — "Twenty million pesos … to less than One billion pesos"; large — "One billion pesos … and above". https://www.lawphil.net/statutes/repacts/ra2024/ra_11976_2024.html |
| **Assumptions** | (a) classification keys on *gross sales* for a taxable year, taken as an input field of the certificate; (b) the model does not handle taxpayers whose gross sales straddle year boundaries or registration changes mid-year. |
| **Reviewer verdict** | Agree / Disagree: ______ |

### S3 — Surcharge at 25% (default civil penalty)

| | |
|---|---|
| **Encoded statement** | Surcharge = 25% of the income tax. |
| **Lean** | `GovernanceDemo.surcharge`; `Tiers.surchargeT` at rate 25 for medium/large. |
| **Source** | NIRC §248(A)(1), as amended by RA 11976 §41 (verified verbatim from lawphil this session): "There shall be imposed, in addition to the tax required to be paid, a penalty equivalent to twenty-five percent (25%) of the amount due, in the following cases: (1) Failure to file any return and pay the tax due thereon … (2) Failure to pay the deficiency tax within the time prescribed … (3) Failure to pay the full or part of the amount of tax shown on any return …" |
| **Assumptions** | (a) the model computes one "filed late / paid late" case only and applies the 25% once (no distinction between filing and payment failures); (b) "amount due" is taken to be the income tax, exclusive of interest; (c) no criminal penalties, compromise penalties, or §248(B) fraud rate are modeled. |
| **Reviewer verdict** | Agree / Disagree: ______ |

### S4 — Reduced surcharge at 10% for micro and small

| | |
|---|---|
| **Encoded statement** | Surcharge = 10% of the income tax for micro and small taxpayers. |
| **Lean** | `Tiers.surchargeRate` (10 for `reduced` tiers), `Tiers.surchargeT`. |
| **Source** | RA 11976 §45(b) (verified verbatim from lawphil this session): "A reduced rate of ten percent (10%) for civil penalties as provided under Section 248 of the NIRC, as amended". |
| **Assumptions** | The 10% substitutes for the 25% in all three §248(A) cases; the model cannot distinguish the cases. RR 6-2024 (verified verbatim, see S6) mirrors the three §248(A) cases A–C and imposes "a penalty equivalent to ten percent (10%) of the amount due" for covered taxpayers — consistent with this reading. |
| **Reviewer verdict** | Agree / Disagree: ______ |

### S5 — Interest at 12% per annum (default)

| | |
|---|---|
| **Encoded statement** | Interest = income tax × 12% × days ÷ 365, truncated, simple (not compounded). |
| **Lean** | `GovernanceDemo.interest` (`tax * 12 * days / 36500`). |
| **Source** | NIRC §249 as amended by RA 10963 (TRAIN §39): deficiency and delinquency interest at double the legal interest rate, i.e. 12% per annum. Corroborated by a practitioner source (MTF Counsel, "Deficiency interest," 16 May 2024, https://mtfcounsel.com/2024/05/16/deficiency-interest/). **Flag:** the TRAIN amendment's verbatim text was not re-fetched for this packet; the reviewer should confirm the §249 wording directly. |
| **Assumptions** | (a) a 365-day year, including leap years (the statute speaks per annum; we divide the annual rate by 365 uniformly); (b) simple interest, per day, no compounding; (c) interest accrues **on the tax only, not on the surcharge** — this is a deliberate modeling choice that BIR practice may contradict; treat as the packet's most important question. |
| **Reviewer verdict** | Agree / Disagree: ______ |

### S6 — Reduced interest at 6% for micro and small

| | |
|---|---|
| **Encoded statement** | Interest rate 6% (half of 12%) for micro and small taxpayers. |
| **Lean** | `Tiers.interestRate` (6 for `reduced` tiers), `Tiers.interestT`. |
| **Source** | RA 11976 §45(c) (verified verbatim from lawphil this session): "A fifty percent (50%) reduction on the interest rate imposed under Section 249 of the NIRC, as amended". |
| **Assumptions** | The reduction applies to the rate, not to the computed interest, and applies to both deficiency and delinquency interest. Implementing regulation BIR RR 6-2024 was verified verbatim on 2026-11-16 from the official BIR text-layer copy (https://bir-cdn.bir.gov.ph/BIR/pdf/RR%206-2024%20(final).pdf; local extract `data/sources/RR_6-2024_final.txt`): "There shall be assessed and collected on any unpaid amount of tax by the covered taxpayers, an interest at the reduced rate of fifty percent (50%) of the interest rate mandated in Section 249 of the Tax Code. For this purpose, the legal interest imposable to cover taxpayers shall be six percent (6%)." The same document imposes "a penalty equivalent to ten percent (10%) of the amount due" for the failure-to-file and failure-to-pay cases (supporting S4). An alternate official copy (RR%20No.%206-%202024.pdf) is a scanned image without a text layer. The regulation also sets a ₱500-per-failure information-return penalty capped at ₱12,500 per calendar year and a 50% reduction of compromise penalties for criminal violations of §§113/237/238 — outside the formalized core. |
| **Reviewer verdict** | Agree / Disagree: ______ |

### S7 — VAT exemption threshold

| | |
|---|---|
| **Encoded statement** | VAT-exempt when gross annual sales ≤ ₱3,000,000; registration required above it. |
| **Lean** | `GovernanceDemo.vatThreshold`, `vatExempt`, `mustRegisterVAT`. |
| **Source** | NIRC §109(CC) as amended by RA 11976 §19: VAT-exempt where "gross annual sales … do not exceed Three million pesos (P3,000,000)". The threshold is CPI-adjusted every three years — **not modeled**. |
| **Assumptions** | The modeled threshold is the 2024 baseline figure; the model has no calendar and will silently use a stale threshold in later years. |
| **Reviewer verdict** | Agree / Disagree: ______ |

### S8 — The ₱3,000,000 boundary (the packet's key finding)

| | |
|---|---|
| **Encoded statement** | At exactly ₱3,000,000 gross sales a taxpayer is **VAT-exempt** (§109(CC): "do not exceed") yet **small, not micro** (§21(b): micro is "less than"). One value of gross sales sits in this gap; the Lean theorem `Tiers.vat_tier_gap` proves the gap contains exactly ₱3,000,000. |
| **Lean** | `Tiers.vat_tier_gap`; worked examples at 299999999 / 300000000 / 300000001 centavos. |
| **Why it matters** | §45's reduced penalties cover micro *and* small taxpayers, so at exactly ₱3,000,000 the reduced rates apply either way — but the classification itself differs, and the micro-specific items that do differ (two-page ITR under §45(a), the ₱500 fine under §45(d), the reduced compromise rate under §45(e)) key on the wrong eligibility class. Engine F6 in our benchmark encodes the natural misreading of §21(b) as "at most ₱3,000,000"; it passes 30 of 32 benchmark cases and is rejected only at the boundary — evidence that this is the subtlest fault class, caught only because the checker verifies the tier claim. |
| **Reviewer verdict** | Agree / Disagree: ______ |

### S9 — Certificate architecture

| | |
|---|---|
| **Encoded statement** | An engine emits: gross sales, claimed tier, income, days late, one line per statutory bracket (base and amount), income tax, surcharge, interest, total. The checker recomputes everything and accepts only a full match, including that the claimed tier equals the classification of the stated gross sales. |
| **Lean** | `Certificate.Cert`, `check`; `Tiers.CertT`, `checkT`; soundness/completeness theorems; tampering and tier-forgery examples. |
| **Reviewer question** | Not statutory: confirm the *engineering* contract matches BIR filing realities (return structure, attachments, e-FPS/eBIR workflow). We claim no such alignment. |
| **Reviewer verdict** | Agree / Disagree: ______ |

### S10 — What is deliberately not modeled

- Mixed-income earners, VAT-registered persons and GPP partners under the 8% option; the quarterly timing, irrevocability mechanics and credit mechanics of the election (the annual election flag is modeled; see S12).
- Deductions, itemized or OSD; netting rules; withholding.
- CPI adjustment of the VAT threshold (every 3 years).
- Reduced compromise penalties and the ₱500 information-return fine (§45(d)–(e)); RR 6-2024 compromise schedule (RMO 7-2015 Annex "A") and the ₱12,500 annual cap — outside the formalized core, though the fine's existence is confirmed by the regulation text.
- Criminal penalties, fraud (§248(B)), deadline calendars (dates, holidays, e-filing windows).
- Corporate taxpayers; only individual graduated rates are modeled.

### S11 — Units and arithmetic conventions

Centavos as natural numbers throughout; every division truncated (floor); ₱250,000 = 25000000 centavos. The reviewer should rule on whether centavo truncation matches BIR rounding practice on actual returns (BIR forms round to the nearest centavo in some places; our model never rounds up — engine F4 shows a 1-centavo half-up difference is rejected).

### S12 — The 8% optional income tax and the Sec. 116 percentage tax

| | |
|---|---|
| **Encoded statement** | A purely self-employed individual/professional whose gross sales/receipts and other non-operating income **do not exceed** the VAT threshold (≤ ₱3,000,000) may elect 8% of gross in excess of ₱250,000, in lieu of the graduated rates **and** the Sec. 116 percentage tax. Without an election, or above the threshold, the regime is graduated: bracket tax on taxable income **plus** 3% percentage tax on gross sales. The election flag is fixed for the year. Penalties (tiered, S3–S6) apply to the combined basic tax. |
| **Lean** | `Opt8.eligible8`, `regimeOf`, `tax8`, `pctTax`, `basicTax`, `Cert8`, `check8`; theorems `check8_sound`, `check8_complete`, `claimEight_rejected`, `tax8_le_graduated`; rate and eligibility mutation tests. |
| **Source** | NIRC §24(A)(2)(b), introduced by RA 10963 (TRAIN) §5, verified verbatim from lawphil (https://www.lawphil.net/statutes/repacts/ra2017/ra_10963_2017.html; local extract `data/sources/RA_10963_sec24_sec116.txt`): "an eight percent (8%) tax on gross sales or gross receipts and other non-operating income in excess of Two hundred fifty thousand pesos (P250,000) in lieu of the graduated income tax rates … and the percentage tax under Section 116". RA 11976's amendatory list does **not** include §24, so the TRAIN text stands (https://www.lawphil.net/statutes/repacts/ra2024/ra_11976_2024.html; extract `data/sources/RA_11976_sec109CC_sec116.txt`). Sec. 116 in the EOPT text: 3% of gross quarterly sales/receipts (the TRAIN-era ₱500,000 exemption proviso was dropped). Election mechanics per BIR RR 8-2018, verified verbatim from the official BIR copy (https://bir-cdn.bir.gov.ph/local/pdf/Digest%20RR%208-2018_copy.pdf — the file labelled "digest" contains the full regulation; local extract `data/sources/RR_8-2018_digest.txt`): election signified in the first-quarter return, irrevocable for the year, default graduated, automatic reversion if annual gross exceeds the threshold. |
| **Assumptions** | (a) purely self-employed only — for mixed-income earners the ₱250,000 deduction does not apply and the compensation income is always graduated; not modeled; (b) penalties apply to the **combined** basic tax (income tax + percentage tax under graduated rates) — the reviewer should confirm whether BIR practice assesses penalties separately per tax type; (c) the ₱250,000 exclusion applies to gross sales/receipts plus non-operating income, modeled as one gross figure; (d) taxable income under the graduated branch remains an unverified input (S1); (e) exactly ₱3,000,000 is eligible (VAT "≤") and is small, not micro, for penalties (S8) — the same boundary now load-bearing in a second rule; (f) quarterly returns, creditable withholding and the mechanics of reversion mid-year are not modeled. |
| **Reviewer verdict** | Agree / Disagree: ______ |

---

## 3. Reviewer sign-off (to be completed by the practitioner — fields provided, not filled)

| | |
|---|---|
| Name (and roll/PTR no., optional): | |
| Items agreed without change: | S__ , S__ , S__ |
| Items disagreed, with correction and citation: | |
| Items needing statute text not available to the preparer: | |
| Overall: the encodings in S1–S9 and S12 are / are not a faithful model of the cited provisions for the stated assumptions: | |
| Signature / date: | |

---

## 4. Honesty notes

1. No legal review has been performed. Every statutory quote above was verified against lawphil during preparation **except** the §249 TRAIN wording (flagged in S5). RR 6-2024 was verified verbatim on 2026-11-16 against the official BIR text-layer copy (see S6); the alternate official copy is an unreadable scan, and the preparer cannot attest that the text-layer copy is the complete, final consolidated regulation. RR 8-2018 was verified verbatim on 2026-11-16 against the official BIR copy (see S12); the preparer cannot attest that the copy labelled "digest" is the complete, final consolidated regulation either.
2. Where the lawphil printed text of RA 11976 §3 contains numeral typos, the packet quotes the words ("Three million pesos"), not the numerals.
3. The benchmark's "ground truth" is the *modeled* spec — it validates engines against the model, not the model against the law. Only the reviewer can close that gap.
