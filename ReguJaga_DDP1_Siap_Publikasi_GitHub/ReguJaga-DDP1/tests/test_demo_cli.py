"""Smoke test CLI: akses tetap tersedia tanpa lingkungan GUI."""
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class DemoCliTest(unittest.TestCase):
    def test_initial_scenario(self):
        r = subprocess.run([sys.executable, str(ROOT / "demo.py")], cwd=ROOT,
                           capture_output=True, text=True, timeout=10)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("Greedy: 1/2 terisi", r.stdout)
        self.assertIn("Solver: 2/2 terisi", r.stdout)
        self.assertIn("Verifikasi: LULUS", r.stdout)

    def test_cancellation(self):
        r = subprocess.run([sys.executable, str(ROOT / "demo.py"), "--cancel", "V02"], cwd=ROOT,
                           capture_output=True, text=True, timeout=10)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("Solver: 1/2 terisi", r.stdout)

    def test_invalid_volunteer(self):
        r = subprocess.run([sys.executable, str(ROOT / "demo.py"), "--cancel", "TIDAK_ADA"], cwd=ROOT,
                           capture_output=True, text=True, timeout=10)
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("tidak ada", r.stderr)
