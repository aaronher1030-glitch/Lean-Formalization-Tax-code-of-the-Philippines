-- Tiers.lean
-- Specification repair: RA 11976 (Ease of Paying Taxes Act) taxpayer tiers.
-- Sec. 21(b) classifies taxpayers by gross sales; Sec. 45 gives micro and
-- small taxpayers a 10% civil penalty and a 50% reduction in interest.
-- The certificate now carries gross sales and a claimed tier, and the
-- checker verifies the tier before it verifies the penalties.
-- Amounts in centavos. Models, not legal advice.

import Certificate

namespace PHTax

inductive Tier
  | micro
  | small
  | medium
  | large
deriving DecidableEq, Repr

/- Sec. 21(b): micro < P3M <= small < P20M <= medium < P1B <= large. -/

def classify (gs : Nat) : Tier :=
  if gs < 300000000 then .micro
  else if gs < 2000000000 then .small
  else if gs < 100000000000 then .medium
  else .large

def Tier.rank : Tier → Nat
  | .micro => 0
  | .small => 1
  | .medium => 2
  | .large => 3

def Tier.reduced : Tier → Bool
  | .micro => true
  | .small => true
  | _ => false

def surchargeRate (k : Tier) : Nat := if k.reduced then 10 else 25

def interestRate (k : Tier) : Nat := if k.reduced then 6 else 12

def surchargeT (k : Tier) (tax : Nat) : Nat := tax * surchargeRate k / 100

def interestT (k : Tier) (tax days : Nat) : Nat := tax * interestRate k * days / 36500

def penaltyT (k : Tier) (tax days : Nat) : Nat := surchargeT k tax + interestT k tax days

def totalDueT (k : Tier) (tax days : Nat) : Nat := tax + penaltyT k tax days

/- Classification is monotone in gross sales. -/

theorem classify_mono {a b : Nat} (h : a ≤ b) : (classify a).rank ≤ (classify b).rank := by
  unfold classify
  repeat' split
  all_goals simp only [Tier.rank]
  all_goals omega

/- The repair is conservative: medium and large taxpayers are unchanged. -/

theorem totalDueT_full {k : Tier} (hk : k.reduced = false) (tax days : Nat) :
    totalDueT k tax days = totalDue tax days := by
  simp only [totalDueT, penaltyT, surchargeT, interestT, surchargeRate, interestRate, hk,
    totalDue, penalty, surcharge, interest]
  rfl

/- No tier pays more than the untiered model. -/

theorem surchargeT_le (k : Tier) (tax : Nat) : surchargeT k tax ≤ surcharge tax := by
  unfold surchargeT surcharge
  apply Nat.div_le_div_right
  apply Nat.mul_le_mul_left
  cases k <;> decide

theorem interestT_le (k : Tier) (tax days : Nat) : interestT k tax days ≤ interest tax days := by
  unfold interestT interest
  apply Nat.div_le_div_right
  apply Nat.mul_le_mul_right
  apply Nat.mul_le_mul_left
  cases k <;> decide

theorem totalDueT_le (k : Tier) (tax days : Nat) : totalDueT k tax days ≤ totalDue tax days := by
  have h1 := surchargeT_le k tax
  have h2 := interestT_le k tax days
  unfold totalDueT penaltyT totalDue penalty
  omega

theorem interestT_mono_days (k : Tier) (tax : Nat) {d₁ d₂ : Nat} (h : d₁ ≤ d₂) :
    interestT k tax d₁ ≤ interestT k tax d₂ := by
  unfold interestT
  exact Nat.div_le_div_right (Nat.mul_le_mul_left _ h)

/- The P3,000,000 boundary. Sec. 109(CC) exempts sales that "do not exceed"
   P3M; Sec. 21(b) makes micro "less than" P3M. Exactly one value of gross
   sales is VAT-exempt yet not micro. -/

theorem vat_tier_gap (gs : Nat) :
    (vatExempt gs ∧ classify gs ≠ .micro) ↔ gs = 300000000 := by
  unfold vatExempt vatThreshold classify
  constructor
  · intro ⟨h1, h2⟩
    by_cases h : gs < 300000000
    · simp [h] at h2
    · omega
  · intro h
    subst h
    decide

/- Tiered certificate and checker. -/

structure CertT where
  grossSales : Nat
  tier       : Tier
  income     : Nat
  daysLate   : Nat
  lines      : List Line
  incomeTax  : Nat
  surcharge  : Nat
  interest   : Nat
  total      : Nat
deriving Repr

def checkT (c : CertT) : Bool :=
  c.tier == classify c.grossSales
  && c.lines.map Line.br == statute
  && allOK c.income c.lines
  && c.incomeTax == sumAmounts c.lines
  && c.surcharge == surchargeT c.tier c.incomeTax
  && c.interest == interestT c.tier c.incomeTax c.daysLate
  && c.total == c.incomeTax + c.surcharge + c.interest

theorem checkT_tier {c : CertT} (h : checkT c = true) : c.tier = classify c.grossSales := by
  simp only [checkT, Bool.and_eq_true, beq_iff_eq] at h
  exact h.1.1.1.1.1.1

theorem checkT_sound_incomeTax {c : CertT} (h : checkT c = true) :
    c.incomeTax = bracketTax c.income := by
  simp only [checkT, Bool.and_eq_true, beq_iff_eq] at h
  obtain ⟨⟨⟨⟨⟨⟨_, hmap⟩, hall⟩, htax⟩, _⟩, _⟩, _⟩ := h
  rw [htax, sumAmounts_of_allOK c.income c.lines hall, hmap, sumTax_statute]

theorem checkT_sound {c : CertT} (h : checkT c = true) :
    c.total = totalDueT (classify c.grossSales) (bracketTax c.income) c.daysLate := by
  have hi := checkT_sound_incomeTax h
  simp only [checkT, Bool.and_eq_true, beq_iff_eq] at h
  obtain ⟨⟨⟨⟨⟨⟨htier, _⟩, _⟩, _⟩, hs⟩, hn⟩, htot⟩ := h
  rw [htot, hs, hn, hi, htier]
  unfold totalDueT penaltyT
  omega

def mkCertT (gs t days : Nat) : CertT :=
  let k := classify gs
  let ls := statute.map (mkLine t)
  let it := sumAmounts ls
  ⟨gs, k, t, days, ls, it, surchargeT k it, interestT k it days,
   it + surchargeT k it + interestT k it days⟩

theorem checkT_complete (gs t days : Nat) : checkT (mkCertT gs t days) = true := by
  simp only [checkT, mkCertT, map_br_mkLine, allOK_mkLine, beq_self_eq_true, Bool.and_self]

/- An accepted tiered certificate never exceeds the untiered liability. -/

theorem checkT_le_untiered {c : CertT} (h : checkT c = true) :
    c.total ≤ totalDue (bracketTax c.income) c.daysLate := by
  rw [checkT_sound h]
  exact totalDueT_le _ _ _

/- Tier forgery: recompute penalties consistently under a false tier. -/

def claimTier (c : CertT) (k : Tier) : CertT :=
  { c with tier := k,
           surcharge := surchargeT k c.incomeTax,
           interest := interestT k c.incomeTax c.daysLate,
           total := c.incomeTax + surchargeT k c.incomeTax + interestT k c.incomeTax c.daysLate }

theorem claimTier_rejected (c : CertT) (k : Tier) (hk : k ≠ classify c.grossSales) :
    checkT (claimTier c k) = false := by
  cases hc : checkT (claimTier c k)
  · rfl
  · exact absurd (checkT_tier hc) hk

/- Worked case: P42,500 income tax (P500,000 taxable income), 30 days late. -/

example : bracketTax 50000000 = 4250000 := by decide
example : checkT (mkCertT 250000000 50000000 30) = true := by decide
example : (mkCertT 250000000 50000000 30).total = 4695958 := by decide
example : (mkCertT 150000000000 50000000 30).total = 5354417 := by decide
example : (mkCertT 150000000000 50000000 30).total = (mkCert 50000000 30).total := by decide

/- A large taxpayer claiming micro status is rejected. -/
example : checkT (claimTier (mkCertT 150000000000 50000000 30) .micro) = false := by decide

/- The boundary: P3,000,000 exactly is VAT-exempt and small, not micro. -/
example : vatExempt 300000000 ∧ classify 300000000 = .small := ⟨Nat.le_refl _, by decide⟩
example : checkT (claimTier (mkCertT 300000000 50000000 30) .micro) = false := by decide
example : checkT (mkCertT 299999999 50000000 30) = true := by decide

#print axioms checkT_sound
#print axioms checkT_complete
#print axioms vat_tier_gap

#eval [250000000, 300000000, 1999999999, 2000000000, 99999999999, 100000000000].map
  (fun gs => (gs, classify gs))
#eval [(250000000, 30), (2500000000, 30), (150000000000, 30)].map
  (fun (gs, d) => let c := mkCertT gs 50000000 d; (gs, repr c.tier, c.surcharge, c.interest, c.total))

end PHTax
