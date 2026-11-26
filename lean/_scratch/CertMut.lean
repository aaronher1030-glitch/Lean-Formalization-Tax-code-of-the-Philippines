-- Certificate.lean
-- A checkable explanation of a tax assessment.
-- Any engine (government system, spreadsheet, LLM) may emit a certificate:
-- one line per bracket plus penalty components. A small checker accepts it
-- only if every line matches the statute. Soundness: accepted implies correct.
-- Amounts in centavos. Models, not legal advice.

import GovernanceDemo

namespace PHTax

structure Bracket where
  lo   : Nat
  hi   : Option Nat
  rate : Nat
deriving DecidableEq, Repr

def Bracket.base (b : Bracket) (t : Nat) : Nat :=
  match b.hi with
  | some h => slice t b.lo h
  | none   => t - b.lo

def Bracket.tax (b : Bracket) (t : Nat) : Nat := b.base t * b.rate / 100

def statute : List Bracket :=
  [ ⟨25000000, some 40000000, 15⟩,
    ⟨40000000, some 80000000, 20⟩,
    ⟨80000000, some 200000000, 25⟩,
    ⟨200000000, some 800000000, 30⟩,
    ⟨800000000, none, 35⟩ ]

structure Line where
  br     : Bracket
  base   : Nat
  amount : Nat
deriving DecidableEq, Repr

structure Cert where
  income    : Nat
  daysLate  : Nat
  lines     : List Line
  incomeTax : Nat
  surcharge : Nat
  interest  : Nat
  total     : Nat
deriving Repr

def sumAmounts : List Line → Nat
  | []      => 0
  | l :: ls => l.amount + sumAmounts ls

def sumTax (t : Nat) : List Bracket → Nat
  | []      => 0
  | b :: bs => b.tax t + sumTax t bs

def lineOK (t : Nat) (l : Line) : Bool :=
  l.base == l.br.base t && l.amount == l.base * l.br.rate / 100

def allOK (t : Nat) : List Line → Bool
  | []      => true
  | l :: ls => lineOK t l && allOK t ls

def check (c : Cert) : Bool :=
  true
  && allOK c.income c.lines
  && c.incomeTax == sumAmounts c.lines
  && c.surcharge == PHTax.surcharge c.incomeTax
  && c.interest == PHTax.interest c.incomeTax c.daysLate
  && c.total == c.incomeTax + c.surcharge + c.interest

/- The statute table is the same schedule as `bracketTax`. -/

theorem assoc5 (a b c d e : Nat) :
    a + b + c + d + e = a + (b + (c + (d + (e + 0)))) := by omega

theorem sumTax_statute (t : Nat) : sumTax t statute = bracketTax t := by
  unfold bracketTax
  rw [assoc5]
  rfl

/- Each accepted line contributes exactly its statutory amount. -/

theorem lineOK_amount {t : Nat} {l : Line} (h : lineOK t l = true) :
    l.amount = l.br.tax t := by
  simp only [lineOK, Bool.and_eq_true, beq_iff_eq] at h
  obtain ⟨hb, ha⟩ := h
  rw [ha, hb]
  rfl

theorem sumAmounts_of_allOK (t : Nat) :
    ∀ ls : List Line, allOK t ls = true → sumAmounts ls = sumTax t (ls.map Line.br)
  | [], _ => rfl
  | l :: ls, h => by
    simp only [allOK, Bool.and_eq_true] at h
    simp only [sumAmounts, List.map, sumTax]
    rw [lineOK_amount h.1, sumAmounts_of_allOK t ls h.2]

/- Soundness: an accepted certificate states the statutory liability. -/

theorem check_sound_incomeTax {c : Cert} (h : check c = true) :
    c.incomeTax = bracketTax c.income := by
  simp only [check, Bool.and_eq_true, beq_iff_eq] at h
  obtain ⟨⟨⟨⟨⟨hmap, hall⟩, htax⟩, _⟩, _⟩, _⟩ := h
  rw [htax, sumAmounts_of_allOK c.income c.lines hall, hmap, sumTax_statute]

theorem check_sound {c : Cert} (h : check c = true) :
    c.total = totalDue (bracketTax c.income) c.daysLate := by
  have hi := check_sound_incomeTax h
  simp only [check, Bool.and_eq_true, beq_iff_eq] at h
  obtain ⟨⟨⟨⟨⟨_, _⟩, _⟩, hs⟩, hn⟩, htot⟩ := h
  rw [htot, hs, hn, hi]
  unfold totalDue penalty
  omega

/- Completeness: the honest certificate is always accepted. -/

def mkLine (t : Nat) (b : Bracket) : Line := ⟨b, b.base t, b.base t * b.rate / 100⟩

def mkCert (t days : Nat) : Cert :=
  let ls := statute.map (mkLine t)
  let it := sumAmounts ls
  ⟨t, days, ls, it, PHTax.surcharge it, PHTax.interest it days,
   it + PHTax.surcharge it + PHTax.interest it days⟩

theorem allOK_mkLine (t : Nat) :
    ∀ bs : List Bracket, allOK t (bs.map (mkLine t)) = true
  | [] => rfl
  | b :: bs => by
    simp only [List.map, allOK, lineOK, mkLine, beq_self_eq_true, Bool.and_self,
      Bool.true_and]
    exact allOK_mkLine t bs

theorem map_br_mkLine (t : Nat) :
    ∀ bs : List Bracket, (bs.map (mkLine t)).map Line.br = bs
  | [] => rfl
  | b :: bs => by
    simp only [List.map, mkLine, List.cons.injEq, true_and]
    exact map_br_mkLine t bs

theorem check_complete (t days : Nat) : check (mkCert t days) = true := by
  simp only [check, mkCert, map_br_mkLine, allOK_mkLine, beq_self_eq_true,
    Bool.and_self]

/- Consequence: accepted certificates inherit monotonicity. -/

theorem check_mono {c₁ c₂ : Cert} (h₁ : check c₁ = true) (h₂ : check c₂ = true)
    (hi : c₁.income ≤ c₂.income) : c₁.incomeTax ≤ c₂.incomeTax := by
  rw [check_sound_incomeTax h₁, check_sound_incomeTax h₂]
  exact bracketTax_mono hi

/- Tampering is caught: one centavo off in one line is rejected. -/

def tamper (c : Cert) : Cert :=
  match c.lines with
  | l :: ls => { c with lines := { l with amount := l.amount + 1 } :: ls }
  | []      => c

example : check (mkCert 50000000 30) = true := by decide
example : check (tamper (mkCert 50000000 30)) = false := by decide
example : check { mkCert 50000000 30 with total := (mkCert 50000000 30).total - 1 } = false := by
  decide
example : check { mkCert 50000000 30 with income := 50000100 } = false := by decide

/- A forged schedule (every rate zero, every amount zero) is rejected. -/

def forged : Cert :=
  let ls := statute.map (fun b => (⟨{ b with rate := 0 }, b.base 50000000, 0⟩ : Line))
  ⟨50000000, 0, ls, 0, 0, 0, 0⟩

example : allOK 50000000 forged.lines = true := by decide
example : check forged = false := by decide

#print axioms check_sound
#print axioms check_complete

#eval (mkCert 50000000 30).lines.map (fun l => (l.br.lo, l.br.rate, l.base, l.amount))
#eval let c := mkCert 50000000 30; (c.incomeTax, c.surcharge, c.interest, c.total)

end PHTax
