-- Opt8.lean
-- The 8% optional income tax, NIRC Sec. 24(A)(2)(b) as introduced by
-- RA 10963 (TRAIN) Sec. 5 and left untouched by RA 11976 (EOPT).
-- Statute (verbatim, lawphil RA 10963): purely self-employed individuals
-- and/or professionals whose gross sales/receipts and other non-operating
-- income "does not exceed" the VAT threshold may elect "an eight percent
-- (8%) tax on gross sales or gross receipts and other non-operating income
-- in excess of Two hundred fifty thousand pesos (P250,000) in lieu of the
-- graduated income tax rates ... and the percentage tax under Section 116".
-- RR 8-2018 (BIR): the election is signified in the first-quarter return,
-- is irrevocable for the year, defaults to graduated rates when absent,
-- and reverts to graduated rates automatically if the annual gross exceeds
-- the threshold. The graduated branch therefore includes the Sec. 116
-- percentage tax (3% of gross sales, EOPT text); the 8% branch replaces both.
-- Scope: purely self-employed, one annual certificate (the election flag is
-- fixed for the year). Mixed income earners, VAT-registered persons, GPP
-- partners, and quarterly credit mechanics are out of scope.
-- Amounts in centavos. Models, not legal advice.

import Tiers

namespace PHTax

/- Eligibility: "does not exceed" the VAT threshold, so exactly P3M qualifies.
   This is the VAT boundary (<=), not the micro-tier boundary (<). -/

def eligible8 (gs : Nat) : Bool := decide (gs ≤ vatThreshold)

theorem eligible8_iff_vatExempt (gs : Nat) : eligible8 gs = true ↔ vatExempt gs := by
  unfold eligible8 vatExempt
  simp

/- The two regimes. -/

inductive Regime
  | graduated
  | eight
deriving DecidableEq, Repr

/- Sec. 116 (EOPT text): 3% percentage tax on gross sales, VAT-exempt persons. -/
def pctTax (gs : Nat) : Nat := gs * 3 / 100

/- Sec. 24(A)(2)(b): 8% of gross in excess of P250,000. Nat subtraction
   floors at zero, so gross at or below P250,000 pays nothing. -/
def tax8 (gs : Nat) : Nat := (gs - 25000000) * 8 / 100

/- RR 8-2018: no election means graduated rates; an election above the
   threshold reverts to graduated rates automatically. -/
def regimeOf (elected : Bool) (gs : Nat) : Regime :=
  if elected then .eight else .graduated

/- Basic tax before penalties: graduated income tax plus percentage tax,
   or the flat 8% which replaces both. -/
def basicTax (r : Regime) (gs income : Nat) : Nat :=
  match r with
  | .graduated => bracketTax income + pctTax gs
  | .eight     => tax8 gs

theorem tax8_zero {gs : Nat} (h : gs ≤ 25000000) : tax8 gs = 0 := by
  unfold tax8
  rw [Nat.sub_eq_zero_of_le h]

theorem tax8_mono {a b : Nat} (h : a ≤ b) : tax8 a ≤ tax8 b :=
  Nat.div_le_div_right (Nat.mul_le_mul_right 8 (Nat.sub_le_sub_right h 25000000))

theorem pctTax_mono {a b : Nat} (h : a ≤ b) : pctTax a ≤ pctTax b :=
  Nat.div_le_div_right (Nat.mul_le_mul_right 3 h)

theorem regimeOf_default (gs : Nat) : regimeOf false gs = .graduated := rfl

theorem regimeOf_ineligible {gs : Nat} (h : ¬ vatExempt gs) (e : Bool) :
    regimeOf e gs = .graduated := by
  unfold regimeOf eligible8 vatExempt at *
  rw [decide_eq_false_iff_not.mpr h]
  cases e <;> rfl

/- The graduated tax is at least 15% of the excess over P250,000:
   every marginal rate above the first bracket is at least 15%.
   Proved interval by interval; each interval is division-free after
   the slices are evaluated, so the kernel certificates stay small. -/

private theorem slice_lo {t lo hi : Nat} (hhi : t ≤ hi) : slice t lo hi = t - lo := by
  unfold slice
  exact Nat.min_eq_left (Nat.sub_le_sub_right hhi lo)

private theorem slice_hi {t lo hi : Nat} (h : hi ≤ t) : slice t lo hi = hi - lo := by
  unfold slice
  exact Nat.min_eq_right (Nat.sub_le_sub_right h lo)

private theorem slice_zero {t lo hi : Nat} (h : t ≤ lo) : slice t lo hi = 0 := by
  unfold slice
  rw [Nat.sub_eq_zero_of_le h]
  exact Nat.zero_min _

set_option maxRecDepth 10000 in
theorem bracketTax_ge_15pct (gs : Nat) :
    (gs - 25000000) * 15 / 100 ≤ bracketTax gs := by
  unfold bracketTax
  rcases Nat.lt_or_ge gs 25000000 with h₁ | h₁
  · rw [Nat.sub_eq_zero_of_le (Nat.le_of_lt h₁)]
    exact Nat.zero_le _
  · rcases Nat.lt_or_ge gs 40000000 with h₂ | h₂
    · have e1 : slice gs 25000000 40000000 = gs - 25000000 := slice_lo (Nat.le_of_lt h₂)
      have e2 : slice gs 40000000 80000000 = 0 := slice_zero (Nat.le_of_lt h₂)
      have e3 : slice gs 80000000 200000000 = 0 := slice_zero (by omega)
      have e4 : slice gs 200000000 800000000 = 0 := slice_zero (by omega)
      have e5 : gs - 800000000 = 0 := Nat.sub_eq_zero_of_le (by omega)
      rw [e1, e2, e3, e4, e5]
      omega
    · rcases Nat.lt_or_ge gs 80000000 with h₃ | h₃
      · have e1 : slice gs 25000000 40000000 = 15000000 := slice_hi h₂
        have e2 : slice gs 40000000 80000000 = gs - 40000000 := slice_lo (Nat.le_of_lt h₃)
        have e3 : slice gs 80000000 200000000 = 0 := slice_zero (Nat.le_of_lt h₃)
        have e4 : slice gs 200000000 800000000 = 0 := slice_zero (by omega)
        have e5 : gs - 800000000 = 0 := Nat.sub_eq_zero_of_le (by omega)
        rw [e1, e2, e3, e4, e5]
        omega
      · rcases Nat.lt_or_ge gs 200000000 with h₄ | h₄
        · have e1 : slice gs 25000000 40000000 = 15000000 := slice_hi h₂
          have e2 : slice gs 40000000 80000000 = 40000000 := slice_hi h₃
          have e3 : slice gs 80000000 200000000 = gs - 80000000 := slice_lo (Nat.le_of_lt h₄)
          have e4 : slice gs 200000000 800000000 = 0 := slice_zero (Nat.le_of_lt h₄)
          have e5 : gs - 800000000 = 0 := Nat.sub_eq_zero_of_le (by omega)
          rw [e1, e2, e3, e4, e5]
          omega
        · rcases Nat.lt_or_ge gs 800000000 with h₅ | h₅
          · have e1 : slice gs 25000000 40000000 = 15000000 := slice_hi h₂
            have e2 : slice gs 40000000 80000000 = 40000000 := slice_hi h₃
            have e3 : slice gs 80000000 200000000 = 120000000 := slice_hi h₄
            have e4 : slice gs 200000000 800000000 = gs - 200000000 := slice_lo (Nat.le_of_lt h₅)
            have e5 : gs - 800000000 = 0 := Nat.sub_eq_zero_of_le (by omega)
            rw [e1, e2, e3, e4, e5]
            omega
          · have e1 : slice gs 25000000 40000000 = 15000000 := slice_hi h₂
            have e2 : slice gs 40000000 80000000 = 40000000 := slice_hi h₃
            have e3 : slice gs 80000000 200000000 = 120000000 := slice_hi h₄
            have e4 : slice gs 200000000 800000000 = 600000000 := slice_hi h₅
            rw [e1, e2, e3, e4]
            omega

/- With no deductions (income = gross), the 8% option never costs more
   than graduated rates plus percentage tax -- for any gross, in particular
   below the threshold. Division-free: 8 <= 15 and the bound above. -/

theorem tax8_le_graduated (gs : Nat) :
    tax8 gs ≤ bracketTax gs + pctTax gs := by
  have h8 : tax8 gs ≤ (gs - 25000000) * 15 / 100 :=
    Nat.div_le_div_right (Nat.mul_le_mul_left _ (by decide : 8 ≤ 15))
  have h15 := bracketTax_ge_15pct gs
  unfold tax8 at h8 ⊢
  omega

/- Election-aware certificate and checker. -/

structure Cert8 where
  grossSales : Nat
  income     : Nat
  daysLate   : Nat
  elected    : Bool
  regime     : Regime
  lines      : List Line
  basic      : Nat
  surcharge  : Nat
  interest   : Nat
  total      : Nat
deriving Repr

def check8 (c : Cert8) : Bool :=
  c.regime == regimeOf c.elected c.grossSales
  && (match c.regime with
      | .graduated => c.lines.map Line.br == statute
                      && allOK c.income c.lines
                      && c.basic == sumAmounts c.lines + pctTax c.grossSales
      | .eight     => c.lines.isEmpty
                      && c.basic == tax8 c.grossSales)
  && c.surcharge == surchargeT (classify c.grossSales) c.basic
  && c.interest == interestT (classify c.grossSales) c.basic c.daysLate
  && c.total == c.basic + c.surcharge + c.interest

theorem check8_regime {c : Cert8} (h : check8 c = true) :
    c.regime = regimeOf c.elected c.grossSales := by
  simp only [check8, Bool.and_eq_true, beq_iff_eq] at h
  exact h.1.1.1.1

theorem check8_sound_basic {c : Cert8} (h : check8 c = true) :
    c.basic = basicTax c.regime c.grossSales c.income := by
  obtain ⟨gs, income, days, elected, r, lines, basic, sur, int, tot⟩ := c
  simp only [check8, Bool.and_eq_true, beq_iff_eq] at h
  cases r with
  | graduated =>
    simp only [Bool.and_eq_true, beq_iff_eq] at h
    obtain ⟨⟨⟨⟨_, ⟨⟨hmap, hall⟩, hb⟩⟩, _⟩, _⟩, _⟩ := h
    simp only [basicTax, hb, sumAmounts_of_allOK _ _ hall, hmap, sumTax_statute]
  | eight =>
    simp only [Bool.and_eq_true, beq_iff_eq] at h
    obtain ⟨⟨⟨⟨_, ⟨_, hb⟩⟩, _⟩, _⟩, _⟩ := h
    simp only [basicTax, hb]

theorem check8_sound {c : Cert8} (h : check8 c = true) :
    c.total = totalDueT (classify c.grossSales)
      (basicTax (regimeOf c.elected c.grossSales) c.grossSales c.income) c.daysLate := by
  have hb := check8_sound_basic h
  have hr := check8_regime h
  simp only [check8, Bool.and_eq_true, beq_iff_eq] at h
  obtain ⟨⟨⟨⟨_, _⟩, hs⟩, hn⟩, ht⟩ := h
  rw [ht, hs, hn, hb, hr]
  unfold totalDueT penaltyT
  omega

def mkCert8 (gs income days : Nat) (elected : Bool) : Cert8 :=
  let r := regimeOf elected gs
  let ls := match r with
    | .graduated => statute.map (mkLine income)
    | .eight     => []
  let b := match r with
    | .graduated => sumAmounts ls + pctTax gs
    | .eight     => tax8 gs
  let k := classify gs
  ⟨gs, income, days, elected, r, ls, b, surchargeT k b, interestT k b days,
   b + surchargeT k b + interestT k b days⟩

theorem check8_complete (gs income days : Nat) (elected : Bool) :
    check8 (mkCert8 gs income days elected) = true := by
  simp only [mkCert8]
  cases hr : regimeOf elected gs with
  | graduated =>
    simp [check8, hr, allOK_mkLine]
    rw [← List.map_map, map_br_mkLine]
  | eight => simp [check8, hr]

/- An ineligible election is rejected even when every amount is
   recomputed consistently under the claimed regime. -/

def claimEight (c : Cert8) : Cert8 :=
  let b := tax8 c.grossSales
  let k := classify c.grossSales
  { c with elected := true, regime := .eight, lines := [], basic := b,
           surcharge := surchargeT k b, interest := interestT k b c.daysLate,
           total := b + surchargeT k b + interestT k b c.daysLate }

theorem claimEight_rejected (c : Cert8) (h : ¬ vatExempt c.grossSales) :
    check8 (claimEight c) = false := by
  cases hc : check8 (claimEight c)
  · rfl
  · have hr := check8_regime hc
    simp only [claimEight, regimeOf_ineligible h] at hr
    exact absurd hr (by decide)

/- The choice matters: neither regime dominates once deductions exist.
   P3M gross, no deductions: 8% basic tax P220,000 vs P702,500 + P90,000. -/

example : tax8 300000000 = 22000000 := by decide
example : bracketTax 300000000 + pctTax 300000000 = 79250000 := by decide
example : (mkCert8 300000000 300000000 0 true).total
        < (mkCert8 300000000 300000000 0 false).total := by decide

/- P3M gross, P250,000 taxable income: graduated P0 + P90,000 beats P220,000. -/
example : (mkCert8 300000000 25000000 0 false).total
        < (mkCert8 300000000 25000000 0 true).total := by decide

/- Below P250,000 gross the 8% tax is zero; the percentage tax is not. -/
example : tax8 20000000 = 0 := by decide
example : pctTax 20000000 = 600000 := by decide

/- The boundary: exactly P3M is eligible (VAT "<="), and is small, not micro. -/
example : eligible8 300000000 = true ∧ classify 300000000 = .small := ⟨by decide, by decide⟩
example : check8 (mkCert8 300000000 300000000 30 true) = true := by decide
example : regimeOf true 300000001 = .graduated := by decide
example : check8 (claimEight (mkCert8 300000001 300000000 30 false)) = false := by decide

/- Default and forgery. -/
example : regimeOf false 250000000 = .graduated := by decide
example : check8 (mkCert8 250000000 50000000 30 false) = true := by decide
example : check8 { mkCert8 250000000 50000000 30 false with total :=
  (mkCert8 250000000 50000000 30 false).total - 1 } = false := by decide
example : check8 { mkCert8 250000000 50000000 30 true with regime := .graduated } = false := by
  decide

#print axioms check8_sound
#print axioms check8_complete
#print axioms tax8_le_graduated
#print axioms claimEight_rejected

#eval [0, 20000000, 25000000, 100000000, 300000000, 300000001].map
  (fun gs => (gs, eligible8 gs, tax8 gs, pctTax gs))
#eval [(300000000, 300000000, true), (300000000, 25000000, false),
       (250000000, 50000000, false)].map
  (fun (gs, t, e) => let c := mkCert8 gs t 30 e; (gs, repr c.regime, c.basic, c.total))

end PHTax