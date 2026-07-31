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
        code, out, err = run_tool("vaultkit.py", "duplicates", "--vault", self.vault)
        self.assertEqual(code, 0, err)
        self.assertIn("0 pairs flagged of 1 compared", out)

    # ------------------------------------------------------------ failure modes

    def test_overlapping_notes_are_flagged_and_red(self):
        note_with_body(self.notes / "eins.md", SAME_BODY, title="Eins")
        note_with_body(self.notes / "kopie.md", SAME_BODY, title="Kopie")
        code, out, err = run_tool("vaultkit.py", "duplicates", "--vault", self.vault)
        self.assertEqual(code, 1)
        self.assertIn("1 pairs flagged of 1 compared", out)
        self.assertIn("kopie.md", err)

    def test_one_note_is_did_not_run(self):
        note_with_body(self.notes / "eins.md", SAME_BODY)
        code, out, err = run_tool("vaultkit.py", "duplicates", "--vault", self.vault)
        self.assertEqual(code, 0, err)
        self.assertIn("did not run", out)
        self.assertIn("1 comparable notes", out)

    def test_threshold_is_printed_with_every_result(self):
        note_with_body(self.notes / "eins.md", SAME_BODY, title="Eins")
        note_with_body(self.notes / "zwei.md", OTHER_BODY, title="Zwei")
        _, out, _ = run_tool("vaultkit.py", "duplicates", "--vault", self.vault, "--threshold", "0.9")
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
        code, out, err = run_tool("vaultkit.py", "duplicates", "--vault", self.vault,
                                  "--threshold", "0.9")
        self.assertEqual(code, 1, out)
        self.assertIn("1 pairs flagged of 1 compared", out)
        self.assertIn("kopie.md", err)

    def test_non_ascii_filename_survives_the_subprocess_round_trip(self):
        note_with_body(self.notes / "Übergröße.md", SAME_BODY, title="Eins")
        note_with_body(self.notes / "Ärgernis.md", SAME_BODY, title="Zwei")
        code, _, err = run_tool("vaultkit.py", "duplicates", "--vault", self.vault)
        self.assertEqual(code, 1)
        self.assertIn("Übergröße.md", err + "")
        self.assertIn("Ärgernis.md", err)

    def test_a_root_run_leaves_exactly_one_run_log(self):
        """The run log belongs at the vault root, and a root run puts it nowhere else.

        `log_run` builds its path relative to the directory it was handed
        (`vault_paths.RUN_LOG_RELPATH`). SECTION 8 prescribed `--vault <Project>` until
        2026-07-30, so the chain wrote `<Project>/00_Global/06_tools/runs.log` — a folder the
        generator adopts as a category on its next pass. Measured on cold run 2: 21 categories
        became 24, exit 0, three `adopted` lines as the only signal. Nothing went red, because
        no run reads the contract's prose.

        Undo recipe: put `--vault <Project>` back on `src/contract.md:896`, then run this tool
        against `<vault>/ProjektEins` instead of the root. A second `00_Global` appears under the
        project and this check goes red. Without that line the number is not reproducible.
        """
        note_with_body(self.notes / "eins.md", SAME_BODY, title="Eins")
        note_with_body(self.notes / "zwei.md", OTHER_BODY, title="Zwei")
        code, _, err = run_tool("vaultkit.py", "duplicates", "--vault", self.vault)
        self.assertEqual(code, 0, err)

        logs = sorted(p.relative_to(self.vault).as_posix() for p in self.vault.rglob("runs.log"))
        self.assertEqual(logs, ["00_Global/06_tools/runs.log"], f"run logs found: {logs}")
        globals_ = sorted(p.relative_to(self.vault).as_posix()
                          for p in self.vault.rglob("00_Global") if p.is_dir())
        self.assertEqual(globals_, ["00_Global"], f"00_Global folders found: {globals_}")


if __name__ == "__main__":
    unittest.main(verbosity=1)
