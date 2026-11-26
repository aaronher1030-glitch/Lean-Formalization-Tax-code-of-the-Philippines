# Contributing

## Before you start

This repository formalizes a reading of Philippine tax law; it is not legal
advice and not an official BIR implementation. Contributions that change a
statutory reading must cite the statute or regulation, and should update
`docs/spec_review_packet.md` so a practitioner can review the change.

## Build and test

Prerequisites: Lean 4.35.0 (pinned in `lean-toolchain`) and Python 3.

```bash
# Lean: core library only, no Lake/Mathlib
bash lean/run_demo.sh

# Python: tool tests, the findings battery, and the guard mutations
python -X utf8 -m unittest discover -s tools -p "test_*.py" -v
python -X utf8 tools/findings.py --dry-run
python -X utf8 tools/mutation_tests.py   # slow: rebuilds a copy per guard
```

If `lean` is not on `PATH`, export the binary first:

```bash
export LEAN=/path/to/lean-4.35.0/bin/lean     # lean.exe on Windows
```

CI runs the same commands on Ubuntu (`.github/workflows/ci.yml`), installing
Lean through elan from `lean-toolchain`.

## What a pull request should contain

- A focused change: one statutory area, one tool, or one documentation fix.
- Proofs with no `sorry`, no `native_decide`, and an axiom audit at
  `propext` only. The CI and `python -X utf8 tools/findings.py` enforce this
  for generated content.
- Updated counts in `STATUS.md` and `THEOREMS.md` only when the hand-written
  artifact changes; generated counts live in `FINDINGS.md` and
  `data/findings.csv`.
- Regenerated artifacts when a generator changes: run the generator, commit
  its outputs, and say so in the pull request.

## Scope

Out of scope unless discussed first: deductions, corporate income tax,
quarterly election mechanics, and penalties outside the modeled sections. See
`ROADMAP.md` for what is planned.

## Reporting problems

Open an issue with the command, the expected result, and the actual output.
For a soundness concern, include the certificate or the failing theorem name.
