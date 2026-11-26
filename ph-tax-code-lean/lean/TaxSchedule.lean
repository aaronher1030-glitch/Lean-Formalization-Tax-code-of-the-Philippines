-- TaxSchedule.lean
-- TRAIN individual income tax schedule for individuals, 2023 onwards.
-- Each marginal rate applies to the slice of taxable income inside its bracket.
-- Amounts are in centavos. This is a model, not legal advice.

set_option maxRecDepth 100000

namespace PHTax

def slice (t lo hi : Nat) : Nat := min (t - lo) (hi - lo)

def bracketTax (t : Nat) : Nat :=
  slice t 25000000 40000000 * 15 / 100
  + slice t 40000000 80000000 * 20 / 100
  + slice t 80000000 200000000 * 25 / 100
  + slice t 200000000 800000000 * 30 / 100
  + (t - 800000000) * 35 / 100

theorem bracketTax_nonneg (t : Nat) : 0 ≤ bracketTax t :=
  Nat.zero_le _

theorem slice_mono {a b lo hi : Nat} (h : a ≤ b) : slice a lo hi ≤ slice b lo hi := by
  unfold slice
  apply Nat.le_min.mpr
  constructor
  · exact Nat.le_trans (Nat.min_le_left _ _) (Nat.sub_le_sub_right h lo)
  · exact Nat.min_le_right _ _

theorem sliceTerm_mono {a b lo hi r : Nat} (h : a ≤ b) :
    slice a lo hi * r / 100 ≤ slice b lo hi * r / 100 :=
  Nat.div_le_div_right (Nat.mul_le_mul_right r (slice_mono h))

theorem subTerm_mono {a b c r : Nat} (h : a ≤ b) :
    (a - c) * r / 100 ≤ (b - c) * r / 100 :=
  Nat.div_le_div_right (Nat.mul_le_mul_right r (Nat.sub_le_sub_right h c))

theorem bracketTax_mono {a b : Nat} (h : a ≤ b) : bracketTax a ≤ bracketTax b := by
  unfold bracketTax
  apply Nat.add_le_add
  · apply Nat.add_le_add
    · apply Nat.add_le_add
      · apply Nat.add_le_add
        · exact sliceTerm_mono h
        · exact sliceTerm_mono h
      · exact sliceTerm_mono h
    · exact sliceTerm_mono h
  · exact subTerm_mono h

-- Boundary continuity at the five thresholds.
example : bracketTax 25000000 = 0 := by decide
example : bracketTax 40000000 = 2250000 := by decide
example : bracketTax 80000000 = 10250000 := by decide
example : bracketTax 200000000 = 40250000 := by decide
example : bracketTax 800000000 = 220250000 := by decide

-- Validation across bracket interiors.
example : bracketTax 30000000 = 750000 := by decide
example : bracketTax 50000000 = 4250000 := by decide
example : bracketTax 100000000 = 15250000 := by decide
example : bracketTax 250000000 = 55250000 := by decide
example : bracketTax 900000000 = 255250000 := by decide

end PHTax
