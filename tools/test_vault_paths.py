"""Suite for vault_paths.py — the module every generated filename comes from."""

import shutil
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from _testkit import make_vault
from vaultkit import (
    RUN_LOG_RELPATH,
    category_index_name,
    category_label,
    has_forbidden_chars,
    is_index_file,
    log_run,
    project_index_name,
    root_index_name,
)


class VaultPathsTest(unittest.TestCase):
    def test_root_index_name_resolves_before_taking_the_name(self):
        """Path('.').name is the empty string — `--root .` must not write '# — Index'."""
        expected = f"INDEX - {Path('.').resolve().name}.md"
        self.assertEqual(root_index_name("."), expected)
        self.assertNotEqual(root_index_name("."), "INDEX - .md")

    def test_every_index_name_carries_what_it_indexes(self):
        self.assertEqual(category_index_name("ProjektEins", "02_docs"), "INDEX - ProjektEins docs.md")
        self.assertEqual(project_index_name("C:/x/ProjektEins"), "INDEX - ProjektEins.md")
        self.assertNotEqual(project_index_name("C:/x/ProjektEins"), "INDEX.md")

    def test_category_label_strips_only_the_sort_prefix(self):
        self.assertEqual(category_label("03_technical_docs"), "technical_docs")
        self.assertEqual(category_label("00_Notes"), "Notes")
        self.assertEqual(category_label("Notes"), "Notes")

    def test_forbidden_chars(self):
        for name in ("a#b.md", "a[b].md", "a|b.md", "a^b.md"):
            self.assertTrue(has_forbidden_chars(name), name)
        self.assertFalse(has_forbidden_chars("Übergröße-für-Ärger.md"))

    def test_is_index_file(self):
        self.assertTrue(is_index_file("INDEX - ProjektEins Notes.md"))
        self.assertFalse(is_index_file("eine-erkenntnis.md"))

    def test_log_run_appends_a_line_per_run(self):
        vault = make_vault(("ProjektEins",))
        try:
            log_run(vault, "build_index", "ok", "0 defects")
            log_run(vault, "build_index", "defects", "2 defects")
            lines = (vault / RUN_LOG_RELPATH).read_text(encoding="utf-8").strip().splitlines()
            self.assertEqual(len(lines), 2)
            self.assertIn("\tbuild_index\tok\t", lines[0])
            self.assertIn("\tbuild_index\tdefects\t", lines[1])
        finally:
            shutil.rmtree(vault.parent, ignore_errors=True)


if __name__ == "__main__":
    unittest.main(verbosity=1)
