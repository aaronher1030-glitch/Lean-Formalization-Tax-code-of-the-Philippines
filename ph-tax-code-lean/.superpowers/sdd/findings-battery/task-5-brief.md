# Task brief (generated from the plan)

Read the plan section below as your requirements. Also binding: the Global
Constraints section of the plan, reproduced here:

- Lean 4.35.0 pinned toolchain, core library only.
- No `native_decide`, no `sorry`; axiom audit must stay at `propext`.
- Do NOT stage, commit, or push anything (standing user rule).
- Python runs as `python -X utf8`; writes use encoding="utf-8".
- Generated `lean/_harness/Findings.lean` stays gitignored.
- `LEAN` env override honored; default ROOT/tools/lean/dist/lean-4.35.0-windows/bin/lean.exe.
- 59/82 hand-written counts must not change.
- Windows: run from repo root `C:/Users/Ma Christine/Downloads/LEAN FORMALIZATION OF TAX CODE/ph-tax-code-lean`.
- Toolchain export for compiles: LEAN="C:/Users/Ma Christine/Downloads/LEAN FORMALIZATION OF TAX CODE/tools/lean/dist/lean-4.35.0-windows/bin/lean.exe".

Frozen row schema for any task using rows:

    {"id": "F001", "family": "...", "kind": "equivalence|divergence|boundary|incentive|identity|gap",
     "theorem": "f001_<family>_001", "prop": "...", "tactic": "rfl"|"decide",
     "witness": "...", "value": int|None, "source": "...", "note": "..."}

---
### Task 5: Driver with dry-run

**Files:**
- Create: `tools/findings.py`
- Test: `tools/test_findings_driver.py`

**Interfaces:**
- Consumes: `findings_families.all_findings()`, `findings_render.render(rows)`, `findings_report.write_outputs(rows, meta, csv_path, md_path)`.
- Produces: CLI `python -X utf8 tools/findings.py [--dry-run]`; exit 0 on success; writes `lean/_harness/Findings.lean`, `data/findings.csv`, `FINDINGS.md` only on full success.

- [ ] **Step 1: Write the failing test**

Create `tools/test_findings_driver.py`:

```python
# -*- coding: utf-8 -*-
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


class DriverTests(unittest.TestCase):
    def test_dry_run_counts_and_writes_nothing(self):
        csv_path = ROOT / "data" / "findings.csv"
        before = csv_path.stat().st_mtime if csv_path.exists() else None
        proc = subprocess.run(
            [sys.executable, "-X", "utf8", str(ROOT / "tools" / "findings.py"),
             "--dry-run"], capture_output=True, text=True, cwd=str(ROOT))
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertIn("DRY RUN: 274 findings", proc.stdout)
        after = csv_path.stat().st_mtime if csv_path.exists() else None
        self.assertEqual(before, after)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd "C:/Users/Ma Christine/Downloads/LEAN FORMALIZATION OF TAX CODE/ph-tax-code-lean" && python -X utf8 -m unittest discover -s tools -p "test_findings_driver.py" -v`
Expected: FAIL — `findings.py` missing (returncode 2).

- [ ] **Step 3: Write the implementation**

Create `tools/findings.py`:

```python
# -*- coding: utf-8 -*-
"""Generate, kernel-check and report the findings battery."""

import os
import re
import subprocess
import sys
import time
from pathlib import Path

import findings_families
import findings_render
import findings_report

ROOT = Path(__file__).resolve().parent.parent
LEAN_DIR = ROOT / "lean"
HARNESS = LEAN_DIR / "_harness" / "Findings.lean"
CSV_OUT = ROOT / "data" / "findings.csv"
MD_OUT = ROOT / "FINDINGS.md"
LEAN = os.environ.get(
    "LEAN", str(ROOT / "tools" / "lean" / "dist" /
                "lean-4.35.0-windows" / "bin" / "lean.exe"))

ERR_RE = re.compile(r"Findings\.lean:(\d+):\d+: error")
AXIOM_RE = re.compile(r"depends on axioms: \[(.*?)\]")
ALLOWED = {"propext"}


def main(argv):
    rows = findings_families.all_findings()
    assert len(rows) == 274, len(rows)
    source = findings_render.render(rows)

    if "--dry-run" in argv:
        print(f"DRY RUN: {len(rows)} findings across "
              f"{len(findings_report.summary(rows))} families; nothing written")
        return 0

    HARNESS.parent.mkdir(exist_ok=True)
    HARNESS.write_text(source, encoding="utf-8")
    env = dict(os.environ)
    env["LEAN_PATH"] = str(LEAN_DIR)
    t0 = time.time()
    proc = subprocess.run([LEAN, str(HARNESS)], capture_output=True, text=True,
                          env=env, cwd=str(LEAN_DIR), timeout=1800)
    seconds = round(time.time() - t0, 1)
    log = proc.stdout + proc.stderr
    if proc.returncode != 0:
        _report_failures(log, source)
        return 1

    bad = []
    for m in AXIOM_RE.finditer(log):
        items = {x.strip() for x in m.group(1).split(",") if x.strip()}
        if not items <= ALLOWED:
            bad.append(m.group(0))
    if bad:
        print("AXIOM AUDIT FAILED:\n" + "\n".join(bad))
        return 1

    audit = "propext only" if "depends on axioms" in log else "no axioms"
    findings_report.write_outputs(rows, {"seconds": seconds, "audit": audit},
                                  CSV_OUT, MD_OUT)
    print(f"PASS: {len(rows)} findings kernel-checked in {seconds} s; "
          f"axioms: {audit}")
    for r in findings_report.summary(rows):
        print(f"  {r['family']:20s} {r['kind']:12s} {r['count']:>3}")
    print(f"wrote {CSV_OUT} and {MD_OUT}")
    return 0


def _report_failures(log, source):
    lines = source.splitlines()
    for m in list(ERR_RE.finditer(log))[:5]:
        n = int(m.group(1))
        context = lines[n - 1] if 0 < n <= len(lines) else "?"
        print(f"Findings.lean:{n}: {context.strip()}")
    print(log[-4000:])


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd "C:/Users/Ma Christine/Downloads/LEAN FORMALIZATION OF TAX CODE/ph-tax-code-lean" && python -X utf8 -m unittest discover -s tools -p "test_findings_driver.py" -v`
Expected: `OK` with 1 test.

- [ ] **Step 5: Run the whole new test suite**

Run: `cd "C:/Users/Ma Christine/Downloads/LEAN FORMALIZATION OF TAX CODE/ph-tax-code-lean" && python -X utf8 -m unittest discover -s tools -p "test_findings_*.py" -v`
Expected: `OK` with 19 tests (5+5+4+4+1).

- [ ] **Step 6: Verify and leave uncommitted**

Run: `cd "C:/Users/Ma Christine/Downloads/LEAN FORMALIZATION OF TAX CODE/ph-tax-code-lean" && git status --short tools/ | head -20`
Expected: new files untracked; no staging.

---

