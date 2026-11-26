import TaxSchedule

namespace PHTax

-- Boundary continuity: tax at each threshold equals the next bracket's base.
example : bracketTax 25000000 = 0 := by decide
example : bracketTax 40000000 = 2250000 := by decide
example : bracketTax 80000000 = 10250000 := by decide
example : bracketTax 200000000 = 40250000 := by decide
example : bracketTax 800000000 = 220250000 := by decide

-- Validation points: 15 further values across all six brackets.
example : bracketTax 0 = 0 := by decide
example : bracketTax 10000000 = 0 := by decide
example : bracketTax 25000001 = 0 := by decide
example : bracketTax 30000000 = 750000 := by decide
example : bracketTax 45000000 = 3250000 := by decide
example : bracketTax 50000000 = 4250000 := by decide
example : bracketTax 90000000 = 12750000 := by decide
example : bracketTax 100000000 = 15250000 := by decide
example : bracketTax 150000000 = 27750000 := by decide
example : bracketTax 250000000 = 55250000 := by decide
example : bracketTax 400000000 = 100250000 := by decide
example : bracketTax 850000000 = 237750000 := by decide
example : bracketTax 900000000 = 255250000 := by decide
example : bracketTax 1000000000 = 290250000 := by decide
example : bracketTax 2000000000 = 640250000 := by decide

end PHTax
