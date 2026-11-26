/-
Loopholes.lean — findings derived from the verified core itself.

These are not literature findings. Each one is exposed by inspecting what
the checked specification does and does not constrain, and is demonstrated
by kernel-checked examples or theorems below. Two kinds are distinguished:

  * encoding gaps — inputs the checker accepts that could not arise under
    a faithful reading of the statute (missing guards);
  * statutory incentives — features of the encoded law that create
    arbitrage opportunities even when every input is honest.

Statute references: NIRC (RA 8424) as amended by RA 10963 (TRAIN) and
RA 11976; RR 8-2018 (8% option); RR 6-2024 (tiers). Nothing here is legal
advice; practitioner review is pending.
-/
import Opt8

namespace PHTax

/-! ## L1. No realism guard: taxable income may exceed gross sales.

Neither `checkT` nor `check8` requires `income ≤ grossSales`. A certificate
claiming ₱1,000,000 of gross sales but ₱100,000,000 of taxable income is
accepted, and its graduated assessment is enormous. Under the statute,
taxable income of a self-employed taxpayer is gross receipts less
deductions, so it cannot exceed gross sales; the benchmark enforced this as
a data-generation constraint, but the checker never did. The completeness
theorems make the acceptance immediate. -/

example : checkT (mkCertT 100000000 10000000000 30) = true :=
  checkT_complete 100000000 10000000000 30

example : check8 (mkCert8 100000000 10000000000 30 false) = true :=
  check8_complete 100000000 10000000000 30 false

#eval (mkCert8 100000000 10000000000 30 false).total

/-! ## L2. Costless, retroactive regime switch: no year, no timing.

`Cert8` carries no taxable year and no election date. The same taxpayer,
same gross sales, same lateness, is accepted under both regimes, and the
only difference between the two certificates is the `elected` flag. RR
8-2018 makes the 8% election in the first-quarter filing, irrevocable for
that year; an audited taxpayer could not switch after the fact. The model
cannot see the difference, so a delinquent taxpayer's certificate can claim
the cheaper regime retroactively. The saving below is kernel-checked. -/

example : check8 (mkCert8 300000000 300000000 30 false) = true :=
  check8_complete 300000000 300000000 30 false

example : check8 (mkCert8 300000000 300000000 30 true) = true :=
  check8_complete 300000000 300000000 30 true

theorem election_switch_saves :
    (mkCert8 300000000 300000000 30 false).total -
      (mkCert8 300000000 300000000 30 true).total = 63257328 := by
  rfl

/-! ## L3. One penalty cliff, at ₱20,000,000 — and only one.

Classification is monotone (`classify_mono`), but the penalty rates are
not continuous: at ₱20,000,000 the surcharge jumps 10% → 25% and the
interest 6% → 12%. One centavo of additional gross sales can therefore
add six figures of penalties on an almost unchanged tax base. The other
two tier lines are penalty-neutral: micro and small share 10%/6%, medium
and large share 25%/12%, so four classes carry only two penalty regimes
and the ₱1,000,000,000 line changes nothing in the penalties. This is a
feature of the encoded statute (RR 6-2024 tiers), not a checker bug — but
it is an incentive to understate gross sales at exactly the ₱20M line,
and the checker verifies the tier only against the *claimed* gross
sales. -/

example : classify 1999999999 = .small := rfl
example : classify 2000000000 = .medium := rfl

example : surchargeT .medium 100000000 - surchargeT .small 100000000 =
    15000000 := rfl

example : interestT .medium 100000000 365 - interestT .small 100000000 365 =
    6000000 := rfl

theorem tier_cliff_20M :
    totalDueT .medium 100000000 365 - totalDueT .small 100000000 365 =
      21000000 := by
  rfl

example : classify 99999999999 = .medium := rfl
example : classify 100000000000 = .large := rfl

/- The ₱1B line is penalty-neutral: medium and large share 25%/12%. -/
example : surchargeT .large 100000000 = surchargeT .medium 100000000 := rfl
example : interestT .large 100000000 365 = interestT .medium 100000000 365 := rfl

#eval (mkCert8 1999999999 1500000000 30 false).total
#eval (mkCert8 2000000000 1500000000 30 false).total

/-! ## L4. The 8% election shelters penalties only above an income crossover.

Penalties are monotone in the base (two new lemmas below), so whenever
`tax8 gs ≤ bracketTax income + pctTax gs` the election weakly reduces the
surcharge and interest of a delinquent eligible taxpayer. But that base
inequality is NOT unconditional: `tax8_le_graduated` compares against
`income = gs`, and for low income at high gross sales the graduated base
(percentage tax only, income below the ₱250k exemption) is smaller than
the 8% base. At gs = ₱3M, income = ₱250k, electing 8% *raises* the
penalties — the kernel checks the counterexample below. The shelter
therefore has an income crossover: at gs = ₱3M the base inequality flips
between income ₱909,999.99 and ₱910,000.00, kernel-checked one centavo
apart below. Above it the option is a penalty shelter, below it a penalty
trap. Combined with L2 (no timing), the model accepts either direction
even when claimed after the delinquency. -/

theorem surchargeT_mono_tax (k : Tier) {a b : Nat} (h : a ≤ b) :
    surchargeT k a ≤ surchargeT k b := by
  simp only [surchargeT]
  exact Nat.div_le_div_right (Nat.mul_le_mul_right _ h)

theorem interestT_mono_tax (k : Tier) (days : Nat) {a b : Nat} (h : a ≤ b) :
    interestT k a days ≤ interestT k b days := by
  simp only [interestT]
  exact Nat.div_le_div_right
    (Nat.mul_le_mul_right _ (Nat.mul_le_mul_right _ h))

theorem election_shelters_penalty {gs income days : Nat}
    (hb : tax8 gs ≤ bracketTax income + pctTax gs) :
    penaltyT (classify gs) (tax8 gs) days ≤
      penaltyT (classify gs) (bracketTax income + pctTax gs) days := by
  simp only [penaltyT]
  exact Nat.add_le_add (surchargeT_mono_tax _ hb)
    (interestT_mono_tax _ days hb)

/- Shelter direction: income at gross sales. -/
example : penaltyT (classify 300000000) (tax8 300000000) 30 ≤
    penaltyT (classify 300000000)
      (bracketTax 300000000 + pctTax 300000000) 30 := by
  decide

/- Trap direction: income at the exemption floor, gs at the eligibility
   ceiling. 8% penalties 2,308,493 centavos vs graduated 944,383. -/
example : ¬ (penaltyT (classify 300000000) (tax8 300000000) 30 ≤
    penaltyT (classify 300000000)
      (bracketTax 25000000 + pctTax 300000000) 30) := by
  decide

/- The crossover at gs = ₱3M, one centavo apart. -/
example : tax8 300000000 ≤ bracketTax 91000000 + pctTax 300000000 := by
  decide

example : ¬ (tax8 300000000 ≤ bracketTax 90999999 + pctTax 300000000) := by
  decide

/-! ## L5. No prescriptive period: interest accrues forever.

`daysLate` is unbounded. A certificate 100 years late is accepted, with
interest exactly twelve times the basic tax. NIRC §203 gives the Bureau
three years to assess (ten under §222 for fraud or failure to file); the
model has no assessment date and no prescription guard, so it cannot flag
an assessment that is time-barred. -/

example : check8 (mkCert8 150000000000 5000000000 36500 false) = true :=
  check8_complete 150000000000 5000000000 36500 false

example : interestT .large 5000000000 36500 = 60000000000 := rfl

end PHTax