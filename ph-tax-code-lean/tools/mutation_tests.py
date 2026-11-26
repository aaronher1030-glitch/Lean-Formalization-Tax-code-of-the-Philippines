#!/usr/bin/env python3
"""Guard-necessity mutation tests.

Each guard named in STATUS.md and the paper is deleted (or its rate changed)
in a throwaway copy of the Lean sources. The copy must then fail to build at
the expected file: a mutant that still compiles would mean the guard is not
load-bearing. An unmutated control copy must build first, so a failure is
attributed to the mutation, not to a broken copy or toolchain.
"""

import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LEAN_DIR = ROOT / "lean"

# (file, writes an .olean) in dependency order, mirroring lean/run_demo.sh
BUILD = [
    ("TaxSchedule.lean", True),
    ("TaxScheduleChecks.lean", False),
    ("GovernanceDemo.lean", True),
    ("Certificate.lean", True),
    ("Tiers.lean", True),
    ("Opt8.lean", True),
    ("Loopholes.lean", False),
]

MUTATIONS = [
    {
        "name": "statute_guard",
        "file": "Certificate.lean",
        "old": "  c.lines.map Line.br == statute\n  && allOK c.income c.lines\n",
        "new": "  allOK c.income c.lines\n",
        "break_at": "Certificate.lean",
        "breaks": "check_sound (the checker accepts a forged schedule)",
    },
    {
        "name": "tier_guard",
        "file": "Tiers.lean",
        "old": "  c.tier == classify c.grossSales\n  && c.lines.map Line.br == statute\n",
        "new": "  c.lines.map Line.br == statute\n",
        "break_at": "Tiers.lean",
        "breaks": "claimTier_rejected and checkT_sound (a tier-forged certificate is accepted)",
    },
    {
        "name": "eight_rate",
        "file": "Opt8.lean",
        "old": "(gs - 25000000) * 8 / 100",
        "new": "(gs - 25000000) * 10 / 100",
        "break_at": "Opt8.lean",
        "breaks": "tax8_le_graduated and the worked examples",
    },
    {
        "name": "election_eligibility",
        "file": "Opt8.lean",
        "old": "if elected && eligible8 gs then .eight else .graduated",
        "new": "if elected then .eight else .graduated",
        "break_at": "Opt8.lean",
        "breaks": "regimeOf_ineligible and the boundary examples",
    },
]


def find_lean():
    env = os.environ.get("LEAN")
    if env:
        return env
    widget = Path("tools/lean/dist/lean-4.35.0-windows/bin/lean.exe")
    for base in (ROOT, ROOT.parent):
        if (base / widget).exists():
            return str(base / widget)
    return "lean"


LEAN = find_lean()


def build(copy_dir):
    """Build the copy in order; return (failing file or None, output tail)."""
    env = dict(os.environ)
    env["LEAN_PATH"] = str(copy_dir)
    output = []
    for name, emits_olean in BUILD:
        cmd = [LEAN] + (["-o", name.replace(".lean", ".olean")] if emits_olean else []) + [name]
        proc = subprocess.run(
            cmd, cwd=str(copy_dir), env=env,
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
            encoding="utf8", errors="replace",
        )
        output.append(proc.stdout)
        if proc.returncode != 0:
            return name, "".join(output)
    return None, "".join(output)


def fresh_copy():
    tmp = Path(tempfile.mkdtemp(prefix="lean-mutant-"))
    for src in LEAN_DIR.glob("*.lean"):
        shutil.copy2(src, tmp / src.name)
    return tmp


def apply_mutation(mut, copy_dir):
    path = copy_dir / mut["file"]
    text = path.read_text(encoding="utf8")
    count = text.count(mut["old"])
    if count != 1:
        raise SystemExit(
            f"mutation {mut['name']}: pattern occurs {count} times in "
            f"{mut['file']}, expected exactly 1"
        )
    path.write_text(text.replace(mut["old"], mut["new"]), encoding="utf8", newline="\n")


def main():
    print(f"lean: {LEAN}")
    control = fresh_copy()
    try:
        failed, tail = build(control)
    finally:
        shutil.rmtree(control, ignore_errors=True)
    if failed is not None:
        print(f"FAIL control: unmutated copy does not build ({failed})")
        print(tail[-2000:])
        return 1
    print("control: unmutated copy builds")

    failures = 0
    for mut in MUTATIONS:
        copy_dir = fresh_copy()
        try:
            apply_mutation(mut, copy_dir)
            failed, tail = build(copy_dir)
        finally:
            shutil.rmtree(copy_dir, ignore_errors=True)
        if failed is None:
            print(f"FAIL {mut['name']}: mutant still builds; guard is not load-bearing")
            failures += 1
        elif failed != mut["break_at"]:
            print(f"FAIL {mut['name']}: broke at {failed}, expected {mut['break_at']}")
            print(tail[-2000:])
            failures += 1
        else:
            print(f"ok   {mut['name']}: build fails at {failed} ({mut['breaks']})")

    if failures:
        print(f"{failures} of {len(MUTATIONS)} mutation tests did not behave as expected")
        return 1
    print(f"all {len(MUTATIONS)} mutations detected")
    return 0


if __name__ == "__main__":
    sys.exit(main())
