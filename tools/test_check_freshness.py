"""Suite for check_freshness.py."""

import shutil
import sys
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from _testkit import make_vault, run_tool


def stamp(hours_ago):
    return (datetime.now(timezone.utc) - timedelta(hours=hours_ago)).strftime("%Y-%m-%dT%H:%M:%S+00:00")


class CheckFreshnessTest(unittest.TestCase):
    def setUp(self):
        self.vault = make_vault(("ProjektEins",))
        self.log = self.vault / "00_Global" / "06_tools" / "runs.log"

    def tearDown(self):
        shutil.rmtree(self.vault.parent, ignore_errors=True)

    def write_log(self, *lines):
        self.log.parent.mkdir(parents=True, exist_ok=True)
        self.log.write_text("\n".join(lines) + ("\n" if lines else ""), encoding="utf-8", newline="\n")

    # ------------------------------------------------------------------ control

    def test_healthy_control(self):
        self.write_log(f"{stamp(1)}\tbuild_index\tok\t0 defects")
        code, out, err = run_tool("check_freshness.py", "--vault", self.vault, "--jobs", "build_index")
        self.assertEqual(code, 0, err)
        self.assertIn("1/1 jobs fresh", out)

    # ------------------------------------------------------------ failure modes

    def test_missing_log_is_did_not_run_not_fine(self):
        code, out, err = run_tool("check_freshness.py", "--vault", self.vault, "--jobs", "build_index")
        self.assertEqual(code, 1)
        self.assertIn("did not run", err)
        self.assertNotIn("fresh", out)

    def test_blank_log_is_did_not_run(self):
        self.write_log()
        code, _, err = run_tool("check_freshness.py", "--vault", self.vault, "--jobs", "build_index")
        self.assertEqual(code, 1)
        self.assertIn("did not run", err)

    def test_stale_healthy_run_is_red(self):
        self.write_log(f"{stamp(72)}\tbuild_index\tok\t0 defects")
        code, out, err = run_tool("check_freshness.py", "--vault", self.vault,
                                  "--jobs", "build_index", "--max-age-hours", "24")
        self.assertEqual(code, 1)
        self.assertIn("0/1 jobs fresh", out)
        self.assertIn("72", err)

    def test_only_failed_runs_count_as_did_not_run(self):
        self.write_log(f"{stamp(1)}\tbuild_index\tdefects\t3 defects")
        code, _, err = run_tool("check_freshness.py", "--vault", self.vault, "--jobs", "build_index")
        self.assertEqual(code, 1)
        self.assertIn("did not run", err)
        self.assertIn("no healthy line", err)

    def test_malformed_lines_are_counted_not_swallowed(self):
        self.write_log(f"{stamp(1)}\tbuild_index\tok\t0 defects", "kaputte zeile ohne tabs")
        code, out, err = run_tool("check_freshness.py", "--vault", self.vault, "--jobs", "build_index")
        self.assertEqual(code, 1)
        self.assertIn("1 malformed", out)
        self.assertIn("malformed", err)

    def test_non_ascii_job_name_survives_the_subprocess_round_trip(self):
        self.write_log(f"{stamp(1)}\tbuild_index\tok\t0 defects")
        code, _, err = run_tool("check_freshness.py", "--vault", self.vault, "--jobs", "Zählung")
        self.assertEqual(code, 1)
        self.assertIn("Zählung", err)


if __name__ == "__main__":
    unittest.main(verbosity=1)
