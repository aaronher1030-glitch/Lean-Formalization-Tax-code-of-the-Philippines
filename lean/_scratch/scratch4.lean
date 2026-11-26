theorem test1 (g : Nat) : g * 8 / 100 ≤ g := by
  have h : g * 8 ≤ g * 100 := Nat.mul_le_mul_left g (by decide : 8 ≤ 100)
  have := Nat.div_le_div_right h
  simpa using this

theorem test2 (g₁ g₂ : Nat) (h : g₁ ≤ g₂) : g₁ * 8 / 100 ≤ g₂ * 8 / 100 :=
  Nat.div_le_div_right (Nat.mul_le_mul_right 8 h)
