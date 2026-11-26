# Theorem Index

All 59 theorems and lemmas in the artifact, grouped by file. Every entry is
proved with **zero `sorry`**; the kernel accepts all of them on a clean
rebuild (`bash lean/run_demo.sh`). Amounts are centavos as `Nat`.

Counts: TaxSchedule 5 · GovernanceDemo 10 · Certificate 10 · Tiers 13 ·
Opt8 16 · Loopholes 5 = **59**.

## `TaxSchedule.lean` — the TRAIN income-tax schedule (§24(A)(2)(a))

| # | Name | Statement | Meaning |
|---|---|---|---|
| 1 | `bracketTax_nonneg` | `0 ≤ bracketTax t` | tax is never negative |
| 2 | `slice_mono` | `a ≤ b → slice a lo hi ≤ slice b lo hi` | a bracket slice grows with income |
| 3 | `sliceTerm_mono` | `a ≤ b → slice a lo hi * r / 100 ≤ slice b lo hi * r / 100` | slice tax grows with income at any rate |
| 4 | `subTerm_mono` | `a ≤ b → (a - c) * r / 100 ≤ (b - c) * r / 100` | the top open-ended term grows with income |
| 5 | `bracketTax_mono` | `a ≤ b → bracketTax a ≤ bracketTax b` | **earning more never lowers the tax** (no notch) |

## `GovernanceDemo.lean` — penalties and the VAT threshold (§248, §249, §109(CC))

| # | Name | Statement | Meaning |
|---|---|---|---|
| 6 | `penalty_nonneg` | `0 ≤ penalty tax days` | penalties are never negative |
| 7 | `penalty_zero` | `penalty 0 days = 0` | **zero tax ⇒ zero penalty**, however late |
| 8 | `interest_mono_days` | `d₁ ≤ d₂ → interest tax d₁ ≤ interest tax d₂` | interest grows with days late |
| 9 | `penalty_mono_days` | `d₁ ≤ d₂ → penalty tax d₁ ≤ penalty tax d₂` | total penalty grows with days late |
| 10 | `surcharge_le_penalty` | `surcharge tax ≤ penalty tax days` | surcharge is a lower bound on the penalty |
| 11 | `vatExempt_mono` | `s₁ ≤ s₂ → vatExempt s₂ → vatExempt s₁` | exemption is downward closed |
| 12 | `mustRegisterVAT_iff` | `mustRegisterVAT sales = true ↔ vatThreshold < sales` | registration test matches the statute's strict comparison |
| 13 | `vatExempt_iff_not_mustRegister` | `vatExempt sales ↔ mustRegisterVAT sales = false` | exemption and registration are exact complements at ₱3M |
| 14 | `totalDue_ge_tax` | `tax ≤ totalDue tax days` | total due never falls below the basic tax |
| 15 | `totalDue_nonneg` | `0 ≤ totalDue tax days` | total due is never negative |

## `Certificate.lean` — the proven checker, generation 1

| # | Name | Statement | Meaning |
|---|---|---|---|
| 16 | `assoc5` | reassociation of a five-term sum (private helper lemma) | bookkeeping for the sum proof |
| 17 | `sumTax_statute` | `sumTax t statute = bracketTax t` | the checker's statutory bracket list **is** the schedule function |
| 18 | `lineOK_amount` | `lineOK t l = true → l.amount = l.base * l.rate / 100` | an accepted line's arithmetic is correct |
| 19 | `sumAmounts_of_allOK` | all lines OK ⇒ sum of amounts = `sumTax t (map br lines)` | accepted line sums equal the schedule recomputation |
| 20 | `check_sound_incomeTax` | `check c = true → c.incomeTax = bracketTax c.income` | accepted income tax is correct |
| 21 | `check_sound` | `check c = true → c.total = totalDue (bracketTax c.income) c.daysLate` | **soundness: accepted ⇒ total correct** |
| 22 | `allOK_mkLine` | `allOK t (statute.map (mkLine t)) = true` | honestly built lines pass |
| 23 | `map_br_mkLine` | `(statute.map (mkLine t)).map Line.br = statute` | honest lines carry exactly the statutory brackets |
| 24 | `check_complete` | `check (mkCert t days) = true` | **completeness: honest ⇒ accepted** |
| 25 | `check_mono` | both accepted, `income₁ ≤ income₂` ⇒ `incomeTax₁ ≤ incomeTax₂` | monotonicity transfers through the checker |

## `Tiers.lean` — RA 11976 tiers and the proven checker, generation 2

| # | Name | Statement | Meaning |
|---|---|---|---|
| 26 | `classify_mono` | `a ≤ b → (classify a).rank ≤ (classify b).rank` | higher gross sales never lowers the tier |
| 27 | `totalDueT_full` | non-reduced tier ⇒ `totalDueT k = totalDue` | medium/large keep the full 25%/12% penalties |
| 28 | `surchargeT_le` | `surchargeT k tax ≤ surcharge tax` | tiered surcharge never exceeds the full rate |
| 29 | `interestT_le` | `interestT k tax days ≤ interest tax days` | tiered interest never exceeds the full rate |
| 30 | `totalDueT_le` | `totalDueT k tax days ≤ totalDue tax days` | **the EOPT repair is conservative**: tiered totals never exceed the pre-repair totals |
| 31 | `interestT_mono_days` | `d₁ ≤ d₂ → interestT k tax d₁ ≤ interestT k tax d₂` | tiered interest grows with days late |
| 32 | `vat_tier_gap` | `(vatExempt gs ∧ classify gs ≠ .micro) ↔ gs = 300000000` | **exactly one value — ₱3,000,000.00 — is VAT-exempt yet not micro**: the two statutes use ≤ vs < |
| 33 | `checkT_tier` | `checkT c = true → c.tier = classify c.grossSales` | the tier claim is checked, not trusted |
| 34 | `checkT_sound_incomeTax` | `checkT c = true → c.incomeTax = bracketTax c.income` | accepted income tax is correct |
| 35 | `checkT_sound` | `checkT c = true → c.total = totalDueT (classify c.grossSales) (bracketTax c.income) c.daysLate` | **soundness with tiers** |
| 36 | `checkT_complete` | `checkT (mkCertT gs t days) = true` | **completeness with tiers** |
| 37 | `checkT_le_untiered` | `checkT c = true → c.total ≤ totalDue (bracketTax c.income) c.daysLate` | accepted tiered totals stay under the untiered bound |
| 38 | `claimTier_rejected` | `k ≠ classify c.grossSales → checkT (claimTier c k) = false` | **tier guard is necessary**: any false tier claim is rejected |

## `Opt8.lean` — the 8% optional regime (§24(A)(2)(b), §116), generation 3

| # | Name | Statement | Meaning |
|---|---|---|---|
| 39 | `eligible8_iff_vatExempt` | `eligible8 gs = true ↔ vatExempt gs` | election eligibility is the VAT comparison (≤ ₱3M), not the micro tier (< ₱3M) |
| 40 | `tax8_zero` | `gs ≤ 25000000 → tax8 gs = 0` | the ₱250k exemption applies under the 8% option |
| 41 | `tax8_mono` | `a ≤ b → tax8 a ≤ tax8 b` | 8% tax grows with gross sales |
| 42 | `pctTax_mono` | `a ≤ b → pctTax a ≤ pctTax b` | 3% percentage tax grows with gross sales |
| 43 | `regimeOf_default` | `regimeOf false gs = .graduated` | no election ⇒ graduated schedule |
| 44 | `regimeOf_ineligible` | `¬ vatExempt gs → regimeOf e gs = .graduated` | **an ineligible election is ignored**, for either flag value |
| 45 | `slice_lo` (private) | `t ≤ hi → slice t lo hi = t - lo` | slice evaluation lemma |
| 46 | `slice_hi` (private) | `hi ≤ t → slice t lo hi = hi - lo` | slice evaluation lemma |
| 47 | `slice_zero` (private) | `t ≤ lo → slice t lo hi = 0` | slice evaluation lemma |
| 48 | `bracketTax_ge_15pct` | `(gs - 25000000) * 15 / 100 ≤ bracketTax gs` | the graduated tax is at least a flat 15% above the exemption |
| 49 | `tax8_le_graduated` | `tax8 gs ≤ bracketTax gs + pctTax gs` | **the 8% option never costs more in basic tax** than graduated income tax plus 3% percentage tax |
| 50 | `check8_regime` | `check8 c = true → c.regime = regimeOf c.elected c.grossSales` | the claimed regime must match the election and eligibility |
| 51 | `check8_sound_basic` | `check8 c = true → c.basic = basicTax c.regime c.grossSales c.income` | accepted basic tax is correct in either regime |
| 52 | `check8_sound` | `check8 c = true → c.total = totalDueT (classify c.grossSales) (basicTax (regimeOf c.elected c.grossSales) c.grossSales c.income) c.daysLate` | **soundness with the election** |
| 53 | `check8_complete` | `check8 (mkCert8 gs income days elected) = true` | **completeness for both regimes** |
| 54 | `claimEight_rejected` | `¬ vatExempt c.grossSales → check8 (claimEight c) = false` | **election guard is necessary**: an ineligible taxpayer's 8% claim is rejected even with consistent amounts |

## `Loopholes.lean` — findings derived from the verified core

These are not statutory claims but demonstrations about the encoding and
about incentives in the encoded law. See [LOOPHOLE_FINDINGS.md](LOOPHOLE_FINDINGS.md).
Axioms: `propext` only.

| # | Name | Statement | Meaning |
|---|---|---|---|
| 55 | `election_switch_saves` | `(mkCert8 300000000 300000000 30 false).total - (mkCert8 300000000 300000000 30 true).total = 63257328` | L2: flipping only the election flag on a delinquent certificate saves ₱632,573.28; no year or timing is guarded |
| 56 | `tier_cliff_20M` | `totalDueT .medium 100000000 365 - totalDueT .small 100000000 365 = 21000000` | L3: the ₱20M tier line adds ₱210,000 of penalties on a ₱1M basic tax, one year late |
| 57 | `surchargeT_mono_tax` | `a ≤ b → surchargeT k a ≤ surchargeT k b` | surcharge is monotone in the base |
| 58 | `interestT_mono_tax` | `a ≤ b → interestT k a days ≤ interestT k b days` | interest is monotone in the base |
| 59 | `election_shelters_penalty` | `tax8 gs ≤ bracketTax income + pctTax gs → penaltyT (classify gs) (tax8 gs) days ≤ penaltyT (classify gs) (bracketTax income + pctTax gs) days` | L4: the 8% election weakly reduces penalties **when the base inequality holds**; the kernel-checked negation example shows it can fail below the income crossover |

The file also carries 18 kernel-checked examples: acceptance of income above
gross sales (L1, both checkers), the tier-cliff boundary and the penalty-neutrality
of the ₱1B line (L3), the penalty trap and the one-centavo crossover at
₱910,000.00 (L4), and acceptance of a 100-years-late certificate (L5).

## Honesty notes on this index

- Three of the 59 (`assoc5`, `allOK_mkLine`, `map_br_mkLine`) are bookkeeping
  lemmas; three more (`slice_lo`, `slice_hi`, `slice_zero`) are private
  slice-evaluation lemmas. They are counted because the kernel checks them,
  but they are not statutory claims.
- Soundness is always *relative to the encoded specification*. Whether the
  specification matches Philippine law is a legal-review question, still
  open — see [docs/spec_review_packet.md](docs/spec_review_packet.md).
- Guard necessity is established by mutation: each guard (`statute` list,
  tier check, 8% rate, election eligibility) was deliberately broken in a
  scratch copy and the corresponding theorem failed to compile. See
  [STATUS.md](STATUS.md).

## Generated findings battery

`tools/findings.py` generates `lean/_harness/Findings.lean`, containing 274
further kernel-checked theorems, one per finding, each with its own
`#print axioms` audit. They are not counted in the 59 above: they are generated on every
run, gitignored, and must always close by `rfl` or `decide` with no
`native_decide` and no `sorry`. See `FINDINGS.md`.

Reproduce with `python -X utf8 tools/findings.py` (`--dry-run` enumerates the
274 propositions without writing).