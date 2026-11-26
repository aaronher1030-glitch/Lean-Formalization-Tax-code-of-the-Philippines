# Coverage

What is formalized, what is not, and where every statutory claim comes from.
**Coverage is deliberately small and honest**: seven NIRC sections in their
computational parts — 7 of the Code's 292 numbered sections, about **2.4%**,
and each section only partially. This is a verified *core*, not a
formalization of the Tax Code.

## Formalized provisions

| NIRC section (as amended) | Provision modeled | Lean definitions | Theorems | Statute source |
|---|---|---|---|---|
| **§24(A)(2)(a)** — individual income tax schedule (TRAIN, effective 2023) | five graduated brackets: 0% to ₱250k; 15% to ₱400k; 20% to ₱800k; 25% to ₱2M; 30% to ₱8M; 35% above | `slice`, `bracketTax` (`TaxSchedule.lean`); `statute`, `check` (`Certificate.lean`) | monotonicity (no notch); checker soundness/completeness | RA 10963 Sec. 5 — [lawphil](https://www.lawphil.net/statutes/repacts/ra2017/ra_10963_2017.html); extract `data/sources/RA_10963_sec24_sec116.txt` |
| **§24(A)(2)(b)** — 8% optional regime | 8% of gross sales/receipts above ₱250k, in lieu of graduated income tax and percentage tax; election limited to VAT-exempt taxpayers | `eligible8`, `tax8`, `regimeOf`, `basicTax`, `check8` (`Opt8.lean`) | election guard; `tax8_le_graduated`; soundness/completeness | RA 10963 Sec. 5 (same extract); BIR [RR 8-2018 digest](https://bir-cdn.bir.gov.ph/local/pdf/Digest%20RR%208-2018_copy.pdf), extract `data/sources/RR_8-2018_digest.{pdf,txt}` |
| **§116** — percentage tax | 3% of gross sales for non-VAT persons under the graduated regime | `pctTax`, `basicTax` (`Opt8.lean`) | monotonicity; enters `tax8_le_graduated` | RA 11976 amendatory list — [lawphil](https://www.lawphil.net/statutes/repacts/ra2024/ra_11976_2024.html); extract `data/sources/RA_11976_sec109CC_sec116.txt` |
| **§109(CC)** — VAT exemption threshold | exemption at gross sales ≤ ₱3,000,000 (EOPT-adjusted) | `vatThreshold`, `vatExempt`, `mustRegisterVAT` (`GovernanceDemo.lean`); `eligible8` (`Opt8.lean`) | complement at the boundary; `vat_tier_gap` | RA 11976 (same extract); base NIRC archived as `data/ra8424.html` |
| **§21(b)** — taxpayer classification (EOPT) | micro < ₱3M; small < ₱20M; medium < ₱1B; large ≥ ₱1B, with 10% surcharge / 6% interest for micro and small | `Tier`, `classify`, `surchargeT`, `interestT`, `totalDueT`, `checkT` (`Tiers.lean`) | tier guard; conservative-repair theorem; boundary theorem | RA 11976 Sec. 3 & Sec. 45 (same extract); BIR [RR 6-2024](https://bir-cdn.bir.gov.ph/BIR/pdf/RR%20No.%206-%202024.pdf), extract `data/sources/RR_6-2024_final.{pdf,txt}` |
| **§248(A)** — civil penalties | 25% surcharge (10% for micro/small); failure-to-file/pay cases | `surcharge`, `penalty` (`GovernanceDemo.lean`); `surchargeT` (`Tiers.lean`) | zero-tax ⇒ zero penalty; bounds; monotonicity | base NIRC (`data/ra8424.html`); RR 6-2024 for reduced rates |
| **§249** — deficiency interest | 12% p.a. (double the 6% legal rate; 6% for micro/small), day-counted on 365 | `interest` (`GovernanceDemo.lean`); `interestT` (`Tiers.lean`) | monotone in days; tier bounds | base NIRC; RA 10963 (double-rate amendment); RR 6-2024 |

Cross-cutting: `Cert`/`CertT`/`Cert8` certificate structures and the three
proven checkers (`check`, `checkT`, `check8`) are an engineering layer, not a
statutory provision; they make the provisions above checkable for untrusted
engines.

## Modeling choices (disclosed, awaiting legal review)

- Amounts are integer centavos (`Nat`); division truncates toward zero,
  matching whole-centavo assessment practice. No rounding modes beyond
  truncation are modeled (engine F4 tests half-up as a fault).
- Interest uses a 365-day year (`tax * rate * days / 36500`); the 360-day
  variant is a seeded engine fault (F3), not the model.
- The 8% election is an annual `Bool` flag; quarterly timing, irrevocability
  within the year, and credit mechanics are **not** modeled.
- Penalties under the 8% option apply to the combined basic tax; whether the
  surcharge base should differ across regimes is flagged as review question
  S12 in the [review packet](docs/spec_review_packet.md).
- The printed numerals in the RA 11976 source contain typographical errors;
  the model follows the spelled-out words (verified against RR 6-2024).

## Not covered

Deductions and exemptions beyond the ₱250k floor; corporate income tax;
VAT computation itself (only the threshold); withholding taxes; mixed-income
earners, VAT-registered persons and general professional partnership partners
under the 8% option; estate/donor taxes; tax treaties; remedies, assessments
and procedure; everything else in Titles II–XV. The roadmap
([ROADMAP.md](ROADMAP.md)) lists what would come next.

## Source integrity

All four primary legal sources were fetched and archived under
`data/sources/` (plus `data/ra8424.html` for the base Code); the paper's
references [37]–[39], [46], [48] point at the same texts. The one URL that
failed during research (a wrong-year lawphil path for RA 10963) was corrected,
not guessed around; see the deep-research notes in
[docs/DEEP_RESEARCH_LEAN_TAX_GOVERNANCE.md](docs/DEEP_RESEARCH_LEAN_TAX_GOVERNANCE.md).