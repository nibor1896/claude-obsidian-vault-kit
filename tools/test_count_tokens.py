"""Suite for count_tokens.py — the tool that must never invent a precision."""

import shutil
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from _testkit import make_vault, run_tool, write_note


class CountTokensTest(unittest.TestCase):
    def setUp(self):
        self.vault = make_vault(("ProjektEins",))
        self.notes = self.vault / "ProjektEins" / "00_Notes"

    def tearDown(self):
        shutil.rmtree(self.vault.parent, ignore_errors=True)

    def test_healthy_control_labels_its_precision(self):
        write_note(self.notes / "eins.md")
        code, out, err = run_tool("vaultkit.py", "tokens", self.vault)
        self.assertEqual(code, 0, err)
        self.assertTrue("estimated" in out or "exact" in out, out)
        self.assertIn("chars", out)
        self.assertIn("1/1 files", out)

    def test_missing_path_is_red(self):
        code, _, err = run_tool("vaultkit.py", "tokens", self.vault / "gibt-es-nicht")
        self.assertEqual(code, 2)
        self.assertIn("not found", err)

    def test_empty_directory_is_did_not_run(self):
        code, _, err = run_tool("vaultkit.py", "tokens", self.notes)
        self.assertEqual(code, 1)
        self.assertIn("did not run", err)

    def test_non_ascii_file_is_counted(self):
        write_note(self.notes / "Übergröße.md", title="Umlaut", summary="Ärger.")
        code, out, err = run_tool("vaultkit.py", "tokens", self.vault)
        self.assertEqual(code, 0, err)
        self.assertIn("1/1 files", out)


if __name__ == "__main__":
    unittest.main(verbosity=1)
