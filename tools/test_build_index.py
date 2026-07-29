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
from vault_paths import (
    CATEGORY_FOLDERS,
    RUN_LOG_RELPATH,
    category_index_name,
    project_index_name,
    root_index_name,
)


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

    def test_note_written_with_a_bom_keeps_its_frontmatter(self):
        """#12. Recipe for the failure without the fix: change the encoding in read_frontmatter
        back from utf-8-sig to utf-8 and rerun this file. Measured that way on this machine --
        exit 1 with three defects on mit-bom.md (no frontmatter block, missing title, missing
        summary) and the entry titled after its filename instead of its title.

        "﻿".isspace() is False, so a byte-order mark survives strip() and the opening
        '---' never matches. Windows editors write one by default.
        """
        write_note(self.project / "00_Notes" / "mit-bom.md", title="Mit BOM",
                   summary="Aus Notepad gespeichert.", bom=True)
        code, out, err = run_tool("build_index.py", "--vault", self.project)
        self.assertEqual(code, 0, err)
        self.assertIn("1 entries", out)
        text = self.index_text()
        self.assertIn("[[ProjektEins/00_Notes/mit-bom|Mit BOM]]", text)
        self.assertIn("Aus Notepad gespeichert.", text)

    def test_a_bom_does_not_hide_a_real_defect(self):
        """The other half: the fix must not turn the guard off for BOM'd files."""
        write_note(self.project / "00_Notes" / "bom-ohne-titel.md", title=None, bom=True)
        code, _, err = run_tool("build_index.py", "--vault", self.project)
        self.assertEqual(code, 1)
        self.assertIn("bom-ohne-titel.md", err)
        self.assertIn("title", err)

    # ------------------------------------------------------------ project: is advisory (#15)

    def test_project_disagreeing_with_the_folder_is_a_defect(self):
        """#15. Recipe for the failure without the fix: delete the `declared = ...` block from
        collect_entries in build_index.py and rerun this file. Measured that way on this machine
        -- 24 of 25 tests pass and this one fails with `AssertionError: 0 != 1`: the run exits 0,
        says nothing, and indexes the note under ProjektEins while its frontmatter goes on
        claiming Homelab. acceptance.py drops to 10/11 in the same state. The asymmetry is what
        made it hard to see: agreement behaved exactly the same, so the field looked like it
        worked.
        """
        write_note(self.project / "00_Notes" / "falsches-projekt.md",
                   title="Gehoert woandershin", project="Homelab")
        code, _, err = run_tool("build_index.py", "--vault", self.project)
        self.assertEqual(code, 1)
        self.assertIn("falsches-projekt.md", err)
        self.assertIn("Homelab", err)
        self.assertIn("ProjektEins", err)

    def test_project_matching_the_folder_is_silent(self):
        """A guard that fires on the agreeing case would make the field unusable."""
        write_note(self.project / "00_Notes" / "richtiges-projekt.md",
                   title="Gehoert hierher", project="ProjektEins")
        code, out, err = run_tool("build_index.py", "--vault", self.project)
        self.assertEqual(code, 0, err)
        self.assertNotIn("project", err)
        self.assertIn("1 entries", out)

    def test_a_missing_project_field_is_not_a_defect(self):
        """This is the promise the contract makes by writing `# optional` next to the field.

        Without this case, tightening the guard into a required field would go unnoticed --
        and 135 of the 339 notes in the vault this kit came from carry no `project:` at all.
        """
        write_note(self.project / "00_Notes" / "ohne-projekt.md", title="Kein Projektfeld")
        code, out, err = run_tool("build_index.py", "--vault", self.project)
        self.assertEqual(code, 0, err)
        self.assertNotIn("project", err)
        self.assertIn("1 entries", out)

    def test_a_quoted_project_value_compares_cleanly(self):
        """`project: "ProjektEins"` and `project: ProjektEins` are the same claim.

        _clean_scalar strips the quotes before anything compares them; without that, every
        quoted value in the vault -- which is how the contract writes them -- would be a defect.
        """
        path = self.project / "00_Notes" / "zitiert.md"
        path.write_text('---\ntitle: "Zitiert"\nsummary: "Wert in Anfuehrungszeichen."\n'
                        'project: "ProjektEins"\n---\n\nRumpf.\n', encoding="utf-8", newline="\n")
        code, out, err = run_tool("build_index.py", "--vault", self.project)
        self.assertEqual(code, 0, err)
        self.assertIn("1 entries", out)

    # ------------------------------------------------------- scaffolding and adoption (#6)

    def test_empty_project_folder_gets_its_categories(self):
        """Requirement 1 of #6: a project folder a user creates is empty and must not stay so."""
        fresh = self.vault / "ProjektNeu"
        fresh.mkdir()
        code, out, err = run_tool("build_index.py", "--vault", fresh)
        self.assertEqual(code, 0, err)
        for folder in CATEGORY_FOLDERS:
            self.assertTrue((fresh / folder).is_dir(), f"{folder} not created")
            self.assertTrue((fresh / folder / category_index_name("ProjektNeu", folder)).exists())
        self.assertIn("created", out)
        self.assertIn("ProjektNeu/00_Notes", out)

    def test_hand_made_folder_is_adopted_and_indexed(self):
        """Requirement 2 of #6: it stays where it is and gets an index of its own."""
        (self.project / "Rechnungen").mkdir()
        write_note(self.project / "Rechnungen" / "eine-rechnung.md", title="Eine Rechnung")
        code, out, err = run_tool("build_index.py", "--vault", self.project)
        self.assertEqual(code, 0, err)
        self.assertTrue((self.project / "Rechnungen").is_dir(), "the folder was moved or removed")
        text = self.index_text("Rechnungen")
        self.assertIn("[[ProjektEins/Rechnungen/eine-rechnung|Eine Rechnung]]", text)
        self.assertIn("1 entries in 7 categories", out)

    def test_adoption_is_announced_and_logged(self):
        """Adopting silently is the old defect wearing a green exit code.

        A renamed 06_tools once dropped a real run from 21 categories to 20 with no message.
        Adoption keeps the notes indexed; the printed line is what makes a typo'd folder name
        visible at all.
        """
        (self.project / "06_werkzeuge").mkdir()
        write_note(self.project / "06_werkzeuge" / "verlorene-notiz.md", title="Verloren")
        code, out, err = run_tool("build_index.py", "--vault", self.project)
        self.assertEqual(code, 0, err)
        self.assertIn("adopted", out)
        self.assertIn("ProjektEins/06_werkzeuge", out)
        log = (self.vault / RUN_LOG_RELPATH).read_text(encoding="utf-8")
        self.assertIn("1 adopted", log)

    def test_skip_dirs_are_never_adopted(self):
        """__pycache__ under 06_tools is normal. As a category it would be indexed forever."""
        (self.project / "__pycache__").mkdir()
        (self.project / ".obsidian").mkdir()
        code, out, err = run_tool("build_index.py", "--vault", self.project)
        self.assertEqual(code, 0, err)
        self.assertNotIn("__pycache__", out)
        self.assertNotIn(".obsidian", out)
        self.assertFalse((self.project / "__pycache__" / "INDEX - ProjektEins __pycache__.md").exists())

    def test_second_run_after_adoption_creates_nothing_new(self):
        (self.project / "Rechnungen").mkdir()
        run_tool("build_index.py", "--vault", self.project)
        before = {p: p.read_bytes() for p in self.project.rglob("INDEX - *.md")}
        code, out, err = run_tool("build_index.py", "--vault", self.project)
        after = {p: p.read_bytes() for p in self.project.rglob("INDEX - *.md")}
        self.assertEqual(code, 0, err)
        self.assertEqual(before, after)
        self.assertNotIn("created", out)   # nothing was missing the second time
        self.assertIn("adopted", out)      # but the folder is still worth naming

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
