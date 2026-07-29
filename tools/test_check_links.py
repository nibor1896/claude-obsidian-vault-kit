"""Suite for check_links.py."""

import shutil
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from _testkit import make_vault, run_tool, write_note


class CheckLinksTest(unittest.TestCase):
    def setUp(self):
        self.vault = make_vault(("ProjektEins",))
        self.notes = self.vault / "ProjektEins" / "00_Notes"

    def tearDown(self):
        shutil.rmtree(self.vault.parent, ignore_errors=True)

    def append(self, path, text):
        with open(path, "a", encoding="utf-8", newline="\n") as fh:
            fh.write(text + "\n")

    # ------------------------------------------------------------------ control

    def test_healthy_control(self):
        target = write_note(self.notes / "ziel.md")
        source = write_note(self.notes / "quelle.md")
        self.append(source, "Siehe [[ProjektEins/00_Notes/ziel|Ziel]].")
        code, out, err = run_tool("check_links.py", "--vault", self.vault)
        self.assertEqual(code, 0, err)
        self.assertIn("1/1 wikilinks resolve", out)
        self.assertTrue(target.exists())

    def test_denominator_is_always_printed(self):
        write_note(self.notes / "allein.md")
        code, out, _ = run_tool("check_links.py", "--vault", self.vault)
        self.assertEqual(code, 0)
        self.assertIn("0/0 wikilinks resolve", out)
        self.assertIn("files scanned", out)

    # ------------------------------------------------------------ failure modes

    def test_broken_link_is_red_with_a_denominator(self):
        source = write_note(self.notes / "quelle.md")
        self.append(source, "Siehe [[gibt-es-nicht]].")
        code, out, err = run_tool("check_links.py", "--vault", self.vault)
        self.assertEqual(code, 1)
        self.assertIn("gibt-es-nicht", err)
        self.assertIn("0/1 wikilinks resolve", out)

    def test_scanning_nothing_is_did_not_run_not_zero_broken(self):
        empty = Path(tempfile.mkdtemp(prefix="vaultkit_empty_"))
        try:
            code, out, err = run_tool("check_links.py", "--vault", empty)
            self.assertEqual(code, 1)
            self.assertIn("did not run", err)
            self.assertNotIn("0 broken", out)
        finally:
            shutil.rmtree(empty, ignore_errors=True)

    def test_wikilink_inside_code_is_not_a_link(self):
        source = write_note(self.notes / "syntax-doku.md")
        self.append(source, "Schreibe `[[Projekt/Ordner/datei|Titel]]` in die Notiz.")
        self.append(source, "```\n[[auch-das-nicht]]\n```")
        code, out, err = run_tool("check_links.py", "--vault", self.vault)
        self.assertEqual(code, 0, err)
        self.assertIn("0/0 wikilinks resolve", out)

    def test_a_bom_does_not_break_fence_detection_on_the_first_line(self):
        """#12, the narrowest of the four. Recipe without the fix: put encoding="utf-8" back
        in the read in main().

        FENCE anchors at ^\\s* and a byte-order mark is not \\s, so a note that OPENS with a
        code fence loses fence detection on line 1: the fence never closes either, and the
        wikilink inside it is reported broken. The note is right and the guard is wrong.
        """
        source = self.notes / "syntax-doku-mit-bom.md"
        source.write_text("```\n[[nur-ein-beispiel]]\n```\n", encoding="utf-8-sig", newline="\n")
        code, out, err = run_tool("check_links.py", "--vault", self.vault)
        self.assertEqual(code, 0, err)
        self.assertIn("0/0 wikilinks resolve", out)

    def test_non_ascii_target_resolves(self):
        write_note(self.notes / "Übergröße.md")
        source = write_note(self.notes / "quelle.md")
        self.append(source, "Siehe [[Übergröße]].")
        code, out, err = run_tool("check_links.py", "--vault", self.vault)
        self.assertEqual(code, 0, err)
        self.assertIn("1/1 wikilinks resolve", out)

    def test_non_ascii_defect_survives_the_subprocess_round_trip(self):
        source = write_note(self.notes / "Ärgernis.md")
        self.append(source, "Siehe [[fehlt-natürlich]].")
        code, _, err = run_tool("check_links.py", "--vault", self.vault)
        self.assertEqual(code, 1)
        self.assertIn("Ärgernis.md", err)
        self.assertIn("fehlt-natürlich", err)

    def test_escaped_alias_pipe_in_a_table_still_resolves(self):
        write_note(self.notes / "ziel.md")
        source = write_note(self.notes / "tabelle.md")
        self.append(source, "| Was | Wo |\n|---|---|\n| Ziel | [[ziel\\|Titel]] |")
        code, out, err = run_tool("check_links.py", "--vault", self.vault)
        self.assertEqual(code, 0, err)
        self.assertIn("1/1 wikilinks resolve", out)

    def test_escaped_pipe_does_not_hide_a_broken_target(self):
        source = write_note(self.notes / "tabelle.md")
        self.append(source, "| Was | Wo |\n|---|---|\n| Ziel | [[gibt-es-nicht\\|Titel]] |")
        code, out, err = run_tool("check_links.py", "--vault", self.vault)
        self.assertEqual(code, 1)
        self.assertIn("gibt-es-nicht", err)
        self.assertIn("0/1 wikilinks resolve", out)

    def test_alias_and_anchor_are_stripped_before_resolving(self):
        write_note(self.notes / "ziel.md")
        source = write_note(self.notes / "quelle.md")
        self.append(source, "Siehe [[ziel#Abschnitt|anderer Text]].")
        code, out, err = run_tool("check_links.py", "--vault", self.vault)
        self.assertEqual(code, 0, err)
        self.assertIn("1/1", out)


if __name__ == "__main__":
    unittest.main(verbosity=1)
