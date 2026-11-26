import TaxSchedule
namespace PHTax
theorem net_mono {a b : Nat} (h : a ≤ b) : a - bracketTax a ≤ b - bracketTax b := by
  unfold bracketTax slice
  omega
theorem bracketTax_le (t : Nat) : bracketTax t ≤ t := by
  unfold bracketTax slice
  omega
end PHTax
