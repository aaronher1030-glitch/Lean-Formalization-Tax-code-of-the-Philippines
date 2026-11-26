import TaxSchedule

set_option maxRecDepth 100000

namespace PHTax

def taxTrace (t : Nat) : List (Nat × Nat) :=
  [(15, slice t 25000000 40000000),
   (20, slice t 40000000 80000000),
   (25, slice t 80000000 200000000),
   (30, slice t 200000000 800000000),
   (35, t - 800000000)]

theorem taxTrace_sound (t : Nat) :
    (taxTrace t).foldl (fun acc (p : Nat × Nat) => acc + p.2 * p.1 / 100) 0 = bracketTax t := by
  simp [taxTrace, bracketTax, List.foldl]

example : taxTrace 50000000 = [(15, 15000000), (20, 10000000), (25, 0), (30, 0), (35, 0)] := by decide
