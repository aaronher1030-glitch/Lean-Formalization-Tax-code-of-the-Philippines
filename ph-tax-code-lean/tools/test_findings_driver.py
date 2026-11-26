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
