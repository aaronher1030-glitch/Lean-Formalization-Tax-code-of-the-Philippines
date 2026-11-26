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
    "LEAN", str(ROOT.parent / "tools" / "lean" / "dist" /
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
