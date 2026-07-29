"""Suite for build_index.py.

Every case here is a failure-mode fixture except test_healthy_control, which is the
control: a suite that only ever sees good input cannot tell you the check still works.
"""

import shutil
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from _testkit import make_vault, run_tool, write_note
from vault_paths import category_index_name, project_index_name, root_index_name


class BuildIndexTest(unittest.TestCase):
    def setUp(self):
        self.vault = make_vault(("ProjektEins",))
        self.project = self.vault / "ProjektEins"

    def tearDown(self):
        shutil.rmtree(self.vault.parent, ignore_errors=True)

    def index_text(self, folder="00_Notes"):
        path = self.project / folder / category_index_name("ProjektEins", folder)
        return path.read_text(encoding="utf-8")

    # ------------------------------------------------------------------ control

    def test_healthy_control(self):
        write_note(self.project / "00_Notes" / "eine-erkenntnis.md",
                   title="Eine Erkenntnis", summary="Genau ein Satz.", created="2026-07-01")
        code, out, err = run_tool("build_index.py", "--vault", self.project)
        self.assertEqual(code, 0, err)
        self.assertIn("1 entries in 6 categories", out)
        text = self.index_text()
        self.assertIn("[[ProjektEins/00_Notes/eine-erkenntnis|Eine Erkenntnis]]", text)
        self.assertIn("Genau ein Satz.", text)

    def test_empty_category_still_gets_an_index(self):
        code, _, err = run_tool("build_index.py", "--vault", self.project)
        self.assertEqual(code, 0, err)
        for folder in ("00_Notes", "02_docs", "06_tools"):
            path = self.project / folder / category_index_name("ProjektEins", folder)
            self.assertTrue(path.exists(), f"{path} missing")

    # ------------------------------------------------------------ failure modes

    def test_missing_title_is_a_defect(self):
        write_note(self.project / "00_Notes" / "ohne-titel.md", title=None)
        code, _, err = run_tool("build_index.py", "--vault", self.project)
        self.assertEqual(code, 1)
        self.assertIn("ohne-titel.md", err)
        self.assertIn("title", err)

    def test_markdown_debris_in_summary_is_stripped_and_red(self):
        write_note(self.project / "00_Notes" / "debris.md", summary="> Ein Zitatrest")
        code, _, err = run_tool("build_index.py", "--vault", self.project)
        self.assertEqual(code, 1)
        self.assertIn("debris.md", err)
        self.assertNotIn("— > Ein Zitatrest", self.index_text())
        self.assertIn("Ein Zitatrest", self.index_text())

    def test_forbidden_filename_falls_back_to_markdown_link(self):
        write_note(self.project / "00_Notes" / "kaputt#name.md", title="Kaputter Name")
        code, _, err = run_tool("build_index.py", "--vault", self.project)
        self.assertEqual(code, 1)
        self.assertIn("kaputt#name.md", err)
        text = self.index_text()
        self.assertIn("[Kaputter Name](", text)
        self.assertNotIn("[[ProjektEins/00_Notes/kaputt#name", text)

    def test_non_ascii_filename_stays_in_the_denominator(self):
        write_note(self.project / "00_Notes" / "Übergröße-für-Ärger.md", title="Umlaut-Notiz")
        code, out, err = run_tool("build_index.py", "--vault", self.project)
        self.assertEqual(code, 0, err)
        self.assertIn("1 entries", out)
        self.assertIn("Übergröße-für-Ärger", self.index_text())

    def test_non_ascii_defect_survives_the_subprocess_round_trip(self):
        write_note(self.project / "00_Notes" / "Ärgernis-ohne-Titel.md", title=None)
        code, _, err = run_tool("build_index.py", "--vault", self.project)
        self.assertEqual(code, 1)
        self.assertIn("Ärgernis-ohne-Titel.md", err)

    def test_duplicate_basenames_are_a_defect(self):
        vault = make_vault(("ProjektEins", "ProjektZwei"))
        try:
            write_note(vault / "ProjektEins" / "00_Notes" / "gleich.md")
            write_note(vault / "ProjektZwei" / "00_Notes" / "gleich.md")
            code, _, err = run_tool("build_index.py", "--root", vault)
            self.assertEqual(code, 1)
            self.assertIn("gleich.md", err)
            self.assertIn("name used 2 times", err)
        finally:
            shutil.rmtree(vault.parent, ignore_errors=True)

    def test_unknown_folder_is_a_defect(self):
        """A renamed 06_tools once dropped a real run from 21 categories to 20, silently."""
        (self.project / "06_werkzeuge").mkdir()
        write_note(self.project / "06_werkzeuge" / "verlorene-notiz.md", title="Verloren")
        code, out, err = run_tool("build_index.py", "--vault", self.project)
        self.assertEqual(code, 1, out)
        self.assertIn("06_werkzeuge", err)

    def test_healthy_control_has_no_unknown_folder(self):
        code, out, err = run_tool("build_index.py", "--vault", self.project)
        self.assertEqual(code, 0, err)
        self.assertNotIn("not a configured category", err)

    # -------------------------------------------------------------- invariants

    def test_second_run_changes_nothing(self):
        write_note(self.project / "00_Notes" / "stabil.md")
        run_tool("build_index.py", "--vault", self.project)
        before = {p: p.read_bytes() for p in self.project.rglob("INDEX - *.md")}
        run_tool("build_index.py", "--vault", self.project)
        after = {p: p.read_bytes() for p in self.project.rglob("INDEX - *.md")}
        self.assertEqual(before, after)

    def test_category_index_backlinks_to_the_project_hub(self):
        """The rename that broke 23 of 441 links was a missing assertion, not a missing check."""
        run_tool("build_index.py", "--vault", self.project)
        hub_stem = project_index_name(self.project)[:-3]
        self.assertIn(f"[[ProjektEins/{hub_stem}|ProjektEins]]", self.index_text())

    def test_project_hub_backlinks_to_the_root_index(self):
        run_tool("build_index.py", "--root", self.vault)
        hub = self.project / project_index_name(self.project)
        root_stem = root_index_name(self.vault)[:-3]
        self.assertIn(f"[[{root_stem}|{self.vault.name}]]", hub.read_text(encoding="utf-8"))

    def test_root_index_is_named_after_the_resolved_vault(self):
        run_tool("build_index.py", "--root", self.vault)
        self.assertTrue((self.vault / root_index_name(self.vault)).exists())
        self.assertIn(f"# {self.vault.name} — Index",
                      (self.vault / root_index_name(self.vault)).read_text(encoding="utf-8"))

    def test_index_never_reads_the_note_body(self):
        write_note(self.project / "00_Notes" / "geheim.md", title="Titel", summary="Kurz.")
        run_tool("build_index.py", "--vault", self.project)
        self.assertNotIn("Body text that the index generator must never read",
                         self.index_text())

    def test_retired_and_stale_are_visible_in_the_index(self):
        write_note(self.project / "00_Notes" / "alt.md", title="Alte Wahrheit",
                   summary="War mal wahr.", retired="2026-06-01")
        write_note(self.project / "00_Notes" / "veraltet.md", title="Halbalt",
                   summary="Quelle ist neuer.", stale="2026-07-01")
        run_tool("build_index.py", "--vault", self.project)
        text = self.index_text()
        self.assertIn("[retired: 2026-06-01]", text)
        self.assertIn("[stale since 2026-07-01]", text)


if __name__ == "__main__":
    unittest.main(verbosity=1)
