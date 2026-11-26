-- GovernanceDemo.lean
-- A small, machine-checked core of tax administration.
-- Imports the TRAIN schedule and adds penalties, VAT registration, and totals.
-- Amounts in centavos. Models, not legal advice.

import TaxSchedule

namespace PHTax

/- Penalty: 25% surcharge plus 12% annual interest, simple, per day. -/

def surcharge (tax : Nat) : Nat := tax * 25 / 100

def interest (tax days : Nat) : Nat := tax * 12 * days / 36500

def penalty (tax days : Nat) : Nat := surcharge tax + interest tax days

theorem penalty_nonneg (tax days : Nat) : 0 ≤ penalty tax days :=
  Nat.zero_le _

theorem penalty_zero (days : Nat) : penalty 0 days = 0 := by
  simp [penalty, surcharge, interest]

theorem interest_mono_days (tax d₁ d₂ : Nat) (h : d₁ ≤ d₂) :
    interest tax d₁ ≤ interest tax d₂ := by
  unfold interest
  exact Nat.div_le_div_right (Nat.mul_le_mul_left (tax * 12) h)

theorem penalty_mono_days (tax d₁ d₂ : Nat) (h : d₁ ≤ d₂) :
    penalty tax d₁ ≤ penalty tax d₂ := by
  unfold penalty
  exact Nat.add_le_add_left (interest_mono_days tax d₁ d₂ h) (surcharge tax)

theorem surcharge_le_penalty (tax days : Nat) : surcharge tax ≤ penalty tax days := by
  unfold penalty
  omega

/- VAT registration: exempt at or below P3,000,000 of gross sales. -/

def vatThreshold : Nat := 300000000

def vatExempt (sales : Nat) : Prop := sales ≤ vatThreshold

theorem vatExempt_mono {s₁ s₂ : Nat} (h : s₁ ≤ s₂) (he : vatExempt s₂) :
    vatExempt s₁ := by
  unfold vatExempt at *
  omega

def mustRegisterVAT (sales : Nat) : Bool := decide (vatThreshold < sales)

theorem mustRegisterVAT_iff (sales : Nat) :
    mustRegisterVAT sales = true ↔ vatThreshold < sales := by
  unfold mustRegisterVAT
  simp

theorem vatExempt_iff_not_mustRegister (sales : Nat) :
    vatExempt sales ↔ mustRegisterVAT sales = false := by
  unfold vatExempt mustRegisterVAT vatThreshold
  simp

/- Composition: what a taxpayer owes. -/

def totalDue (tax days : Nat) : Nat := tax + penalty tax days

theorem totalDue_ge_tax (tax days : Nat) : tax ≤ totalDue tax days := by
  unfold totalDue
  omega

theorem totalDue_nonneg (tax days : Nat) : 0 ≤ totalDue tax days :=
  Nat.zero_le _

/- Executable output. -/

#eval List.map (fun ti => (ti, bracketTax ti))
  [0, 25000000, 30000000, 40000000, 50000000, 100000000, 250000000, 900000000]

#eval List.map (fun d => (d, penalty 10000000 d)) [0, 30, 90, 365]

#eval List.map (fun s => (s, decide (s ≤ vatThreshold), mustRegisterVAT s))
  [290000000, 300000000, 300000001]

#eval List.map (fun (ti, d) => (ti, d, totalDue (bracketTax ti) d))
  [(30000000, 0), (50000000, 30), (100000000, 365)]

end PHTax
