"""Suite for check_duplicates.py."""

import shutil
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from _testkit import make_vault, run_tool, write_note

SAME_BODY = (
    "Der Index wird erzeugt und niemals von Hand geschrieben. "
    "Der Generator liest ausschließlich das Frontmatter und niemals den Fließtext. "
    "Das ist keine Optimierung sondern die strukturelle Garantie."
)
OTHER_BODY = (
    "Ein Zeitplan der still aufgehört hat sieht genauso aus wie einer der läuft. "
    "Deshalb schreibt jeder Lauf eine Zeile ins Protokoll, auch der gesunde."
)


def note_with_body(path, body, title="Ein Titel", bom=False):
    write_note(path, title=title, bom=bom)
    with open(path, "a", encoding="utf-8", newline="\n") as fh:
        fh.write(body + "\n")
    return path


class CheckDuplicatesTest(unittest.TestCase):
    def setUp(self):
        self.vault = make_vault(("ProjektEins",))
        self.notes = self.vault / "ProjektEins" / "00_Notes"

    def tearDown(self):
        shutil.rmtree(self.vault.parent, ignore_errors=True)

    # ------------------------------------------------------------------ control

    def test_healthy_control(self):
        note_with_body(self.notes / "eins.md", SAME_BODY, title="Eins")
        note_with_body(self.notes / "zwei.md", OTHER_BODY, title="Zwei")
        code, out, err = run_tool("check_duplicates.py", "--vault", self.vault)
        self.assertEqual(code, 0, err)
        self.assertIn("0 pairs flagged of 1 compared", out)

    # ------------------------------------------------------------ failure modes

    def test_overlapping_notes_are_flagged_and_red(self):
        note_with_body(self.notes / "eins.md", SAME_BODY, title="Eins")
        note_with_body(self.notes / "kopie.md", SAME_BODY, title="Kopie")
        code, out, err = run_tool("check_duplicates.py", "--vault", self.vault)
        self.assertEqual(code, 1)
        self.assertIn("1 pairs flagged of 1 compared", out)
        self.assertIn("kopie.md", err)

    def test_one_note_is_did_not_run(self):
        note_with_body(self.notes / "eins.md", SAME_BODY)
        code, out, err = run_tool("check_duplicates.py", "--vault", self.vault)
        self.assertEqual(code, 0, err)
        self.assertIn("did not run", out)
        self.assertIn("1 comparable notes", out)

    def test_threshold_is_printed_with_every_result(self):
        note_with_body(self.notes / "eins.md", SAME_BODY, title="Eins")
        note_with_body(self.notes / "zwei.md", OTHER_BODY, title="Zwei")
        _, out, _ = run_tool("check_duplicates.py", "--vault", self.vault, "--threshold", "0.9")
        self.assertIn("threshold 0.9", out)

    def test_a_bom_does_not_hide_a_duplicate(self):
        """#12. Recipe without the fix: put encoding="utf-8" back in body_shingles.

        A BOM makes startswith("---") false, so the frontmatter is compared as body text and
        its words dilute the overlap. Two byte-identical bodies then score below 1.0 instead
        of at it.

        The threshold is raised to 0.9 on purpose. At the default 0.75 this exact pair still
        scores just above the line and the test passes without the fix -- measured that way
        on this machine, which is the only reason the number is here.
        """
        note_with_body(self.notes / "eins.md", SAME_BODY, title="Eins")
        note_with_body(self.notes / "kopie.md", SAME_BODY, title="Kopie", bom=True)
        code, out, err = run_tool("check_duplicates.py", "--vault", self.vault,
                                  "--threshold", "0.9")
        self.assertEqual(code, 1, out)
        self.assertIn("1 pairs flagged of 1 compared", out)
        self.assertIn("kopie.md", err)

    def test_non_ascii_filename_survives_the_subprocess_round_trip(self):
        note_with_body(self.notes / "Übergröße.md", SAME_BODY, title="Eins")
        note_with_body(self.notes / "Ärgernis.md", SAME_BODY, title="Zwei")
        code, _, err = run_tool("check_duplicates.py", "--vault", self.vault)
        self.assertEqual(code, 1)
        self.assertIn("Übergröße.md", err + "")
        self.assertIn("Ärgernis.md", err)


if __name__ == "__main__":
    unittest.main(verbosity=1)
