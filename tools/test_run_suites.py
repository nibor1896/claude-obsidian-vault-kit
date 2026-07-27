"""Suite for run_suites.py — the runner that must never report green over zero tests."""

import shutil
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from _testkit import run_tool

PASSING = "import sys\nprint('fine')\nsys.exit(0)\n"
FAILING = "import sys\nsys.stderr.write('kaputt\\n')\nsys.exit(1)\n"
NON_ASCII = "import sys\nsys.stderr.write('Ärgernis in der Suite\\n')\nsys.exit(1)\n"


class RunSuitesTest(unittest.TestCase):
    def setUp(self):
        self.dir = Path(tempfile.mkdtemp(prefix="vaultkit_suites_"))

    def tearDown(self):
        shutil.rmtree(self.dir, ignore_errors=True)

    def suite(self, name, body):
        path = self.dir / name
        path.write_text(body, encoding="utf-8", newline="\n")
        return path

    # ------------------------------------------------------------------ control

    def test_healthy_control(self):
        self.suite("test_a.py", PASSING)
        self.suite("test_b.py", PASSING)
        code, out, err = run_tool("run_suites.py", "--tools", self.dir)
        self.assertEqual(code, 0, err)
        self.assertIn("2/2 suites green", out)

    # ------------------------------------------------------------ failure modes

    def test_zero_suites_is_not_green(self):
        code, out, err = run_tool("run_suites.py", "--tools", self.dir)
        self.assertEqual(code, 1)
        self.assertIn("0 suites collected", err)
        self.assertNotIn("green", out)

    def test_a_failing_suite_makes_the_run_red(self):
        self.suite("test_a.py", PASSING)
        self.suite("test_b.py", FAILING)
        code, out, err = run_tool("run_suites.py", "--tools", self.dir)
        self.assertEqual(code, 1)
        self.assertIn("1/2 suites green", out)
        self.assertIn("test_b.py", err)

    def test_helper_modules_are_not_counted_as_suites(self):
        self.suite("_testkit.py", PASSING)
        code, _, err = run_tool("run_suites.py", "--tools", self.dir)
        self.assertEqual(code, 1)
        self.assertIn("0 suites collected", err)

    def test_non_ascii_suite_output_survives_the_subprocess_round_trip(self):
        self.suite("test_umlaut.py", NON_ASCII)
        code, _, err = run_tool("run_suites.py", "--tools", self.dir)
        self.assertEqual(code, 1)
        self.assertIn("Ärgernis in der Suite", err)


if __name__ == "__main__":
    unittest.main(verbosity=1)
