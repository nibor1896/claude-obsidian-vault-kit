"""Suite for upgrade.py.

The failure that matters here is silence: an upgrade that reports "nothing to do" over a file
it could not read, or that writes without saying what it overwrote. Every case below is a
failure-mode fixture except test_healthy_control.
"""

import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

TOOLS = Path(__file__).resolve().parent


def kit_file(path, blocks, version="0123456789ab"):
    """A minimal kit file: a version stamp plus one fenced block per script."""
    parts = [f"<!-- kit-version: {version} -->", "", "# A kit", ""]
    for name, body in blocks.items():
        lang = "json" if name.endswith(".json") else "python"
        parts.append(f"### `{name}`\n\n```{lang}\n{body}\n```\n")
    Path(path).write_text("\n".join(parts), encoding="utf-8", newline="\n")
    return path


def run_upgrade(tools_dir, *args):
    """upgrade.py acts on its own directory, so it is copied into the sandbox and run there."""
    result = subprocess.run([sys.executable, str(tools_dir / "upgrade.py"), *[str(a) for a in args]],
                            capture_output=True, cwd=str(tools_dir))
    return (result.returncode,
            result.stdout.decode("utf-8", errors="replace"),
            result.stderr.decode("utf-8", errors="replace"))


class UpgradeTest(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="vaultkit_upgrade_"))
        self.tools = self.tmp / "06_tools"
        self.tools.mkdir()
        shutil.copy2(TOOLS / "upgrade.py", self.tools / "upgrade.py")
        (self.tools / "build_index.py").write_text("print('old')\n", encoding="utf-8", newline="\n")

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    # ------------------------------------------------------------------ control

    def test_healthy_control_reports_no_change(self):
        """Identical scripts AND a matching stamp: the only state with nothing to say.

        The `--stamp` line was added on 2026-07-30 with the #23 fix. Without it this fixture was
        a folder that had never been stamped at all -- `installed: unknown` -- and it passed,
        because the old code returned on `nothing to do` before ever comparing the two versions.
        That is the defect, sitting inside the healthy control: the case this test called healthy
        was one where the tool could not say which kit the folder came from.
        """
        kit = kit_file(self.tmp / "kit.md", {"build_index.py": "print('old')"})
        run_upgrade(self.tools, "--stamp", kit)
        code, out, err = run_upgrade(self.tools, kit)
        self.assertEqual(code, 0, err)
        self.assertIn("1 unchanged", out)
        self.assertIn("nothing to do", out)

    # ------------------------------------------------------------ failure modes

    def test_a_changed_file_is_named_before_anything_is_written(self):
        kit = kit_file(self.tmp / "kit.md", {"build_index.py": "print('new')"})
        code, out, _ = run_upgrade(self.tools, kit)
        self.assertEqual(code, 0)
        self.assertIn("overwrite  build_index.py", out)
        self.assertIn("nothing written", out)
        self.assertEqual((self.tools / "build_index.py").read_text(encoding="utf-8"),
                         "print('old')\n", "file changed without --apply")

    def test_apply_writes_and_records_the_version(self):
        kit = kit_file(self.tmp / "kit.md", {"build_index.py": "print('new')"}, version="abcdef012345")
        run_upgrade(self.tools, kit, "--apply")
        self.assertEqual((self.tools / "build_index.py").read_text(encoding="utf-8"), "print('new')\n")
        self.assertEqual((self.tools / "kit-version.txt").read_text(encoding="utf-8").strip(),
                         "abcdef012345")

    def test_stamp_records_the_version_without_writing_anything_else(self):
        """The first install's only writer. Nothing else puts a version beside a fresh folder.

        `--apply` above covers the second kit onwards. Until --stamp existed, the first one was
        covered by nobody: the contract told the agent to type the twelve characters by hand,
        and verify_setup's step 13 read back a value its own fixture had written.
        """
        kit = kit_file(self.tmp / "kit.md", {"build_index.py": "print('new')"},
                       version="0f1e2d3c4b5a")
        code, out, err = run_upgrade(self.tools, "--stamp", kit)
        self.assertEqual(code, 0, err)
        self.assertEqual((self.tools / "kit-version.txt").read_text(encoding="utf-8").strip(),
                         "0f1e2d3c4b5a")
        self.assertEqual((self.tools / "build_index.py").read_text(encoding="utf-8"),
                         "print('old')\n", "--stamp wrote a script file")

    def test_stamp_refuses_a_file_with_no_version_line(self):
        """`unversioned` would be compared against every future kit and never match."""
        kit = self.tmp / "old-kit.md"
        kit.write_text("### `build_index.py`\n\n```python\nprint('new')\n```\n",
                       encoding="utf-8", newline="\n")
        code, out, err = run_upgrade(self.tools, "--stamp", kit)
        self.assertNotEqual(code, 0, "a file with no stamp must not produce one")
        self.assertFalse((self.tools / "kit-version.txt").exists(),
                         "a refused stamp still landed on disk")
        self.assertIn("kit-version", out + err)

    def test_a_file_only_the_kit_has_is_reported_as_added(self):
        kit = kit_file(self.tmp / "kit.md",
                       {"build_index.py": "print('old')", "check_links.py": "print('new tool')"})
        code, out, _ = run_upgrade(self.tools, kit)
        self.assertEqual(code, 0)
        self.assertIn("add        check_links.py", out)

    def test_a_file_without_blocks_is_refused_not_reported_as_clean(self):
        empty = self.tmp / "not-a-kit.md"
        empty.write_text("# Just prose, no code blocks.\n", encoding="utf-8", newline="\n")
        code, out, err = run_upgrade(self.tools, empty)
        self.assertNotEqual(code, 0, "a file with no blocks must not read as up to date")
        self.assertIn("no script blocks", out + err)

    def test_an_unversioned_kit_says_so_rather_than_guessing(self):
        kit = self.tmp / "old-kit.md"
        kit.write_text("### `build_index.py`\n\n```python\nprint('new')\n```\n",
                       encoding="utf-8", newline="\n")
        code, out, _ = run_upgrade(self.tools, kit)
        self.assertEqual(code, 0)
        self.assertIn("unversioned", out)

    def test_non_ascii_content_survives_the_round_trip(self):
        body = "print('Übergröße')"
        kit = kit_file(self.tmp / "kit.md", {"build_index.py": body})
        run_upgrade(self.tools, kit, "--apply")
        self.assertIn("Übergröße", (self.tools / "build_index.py").read_text(encoding="utf-8"))

    # ------------------------------------------------- what a Windows editor leaves behind

    def test_a_file_with_a_bom_is_not_reported_as_changed(self):
        """The silent half of #22: a BOM does not raise, it just makes the comparison fail.

        The user opened the file in Notepad, or wrote it once with PowerShell 5.1's
        `Set-Content -Encoding utf8`. The bytes of the code are identical; the file gains a
        leading \\ufeff that `utf-8` keeps and `strip()` does not remove -- "\\ufeff".isspace()
        is False. classify() then lists an untouched file under `overwrite`, and the user is
        told they have a local edit they never made.

        Undo recipe, re-measured on this machine 2026-07-31: in upgrade.py's classify(), read the
        target with `encoding="utf-8"` again. test_upgrade 16/18 -- this case fails with
        `1 would be overwritten` where it expects `1 unchanged`, and the undecodable case goes
        with it, because dropping the replacement handler is part of the same reversal. The run
        stays exit 0 throughout, which is why nothing caught it before.
        """
        (self.tools / "build_index.py").write_text("print('old')\n",
                                                   encoding="utf-8-sig", newline="\n")
        kit = kit_file(self.tmp / "kit.md", {"build_index.py": "print('old')"})
        code, out, err = run_upgrade(self.tools, kit)
        self.assertEqual(code, 0, err)
        self.assertIn("1 unchanged", out)
        self.assertNotIn("overwrite", out)

    def test_an_undecodable_file_is_named_rather_than_crashing_the_run(self):
        """The loud half of #22, and the only one that ever raised.

        One invalid byte anywhere in the tool folder took the whole update down with a
        UnicodeDecodeError out of classify(), which names no file -- so the message pointed at
        nothing the user could act on, and the other twenty-one scripts went unexamined.
        `errors="replace"` turns it into an ordinary mismatch: the file is named under
        `overwrite`, which is exactly right, because overwriting it is the repair.

        Undo recipe, measured on this machine 2026-07-30: drop `errors="replace"` from
        classify(). This test fails with a non-zero exit and `UnicodeDecodeError` on stderr
        instead of the expected listing.
        """
        (self.tools / "build_index.py").write_bytes(b"print('\xff\xfe not utf-8')\n")
        kit = kit_file(self.tmp / "kit.md", {"build_index.py": "print('old')"})
        code, out, err = run_upgrade(self.tools, kit)
        self.assertEqual(code, 0, f"an unreadable byte stopped the run:\n{err}")
        self.assertIn("overwrite  build_index.py", out)
        self.assertNotIn("UnicodeDecodeError", err)

    # ------------------------------------- file operations that the environment refuses

    def test_a_kit_path_that_is_not_there_is_named_rather_than_traced(self):
        """The first thing the update path does, and a mistyped argument is the likeliest input.

        Verified by running it on this machine 2026-07-31: `upgrade.py <typo>.md` came back as a
        FileNotFoundError traceback out of read_kit(). A traceback on the opening move reads as
        "this tool is broken" rather than "that path is wrong", and it is the state a user is in
        when they are already trying to repair something.

        Exit 2 rather than 1 throughout this file means the environment refused an I/O
        operation; 1 stays what it was, "written, but it does not pass its own checks".

        Undo recipe: remove the try/except around read_text() in upgrade.py's read_kit(). This
        case then exits 1 with `Traceback (most recent call last)` on stderr.
        """
        code, out, err = run_upgrade(self.tools, self.tmp / "gibt-es-nicht.md")
        self.assertEqual(code, 2, out + err)
        self.assertNotIn("Traceback", err)
        self.assertIn("gibt-es-nicht.md", out + err)

    def test_a_stamp_path_that_is_not_there_is_named_rather_than_traced(self):
        """--stamp is the other entry point and had the same hole, in a read of its own."""
        code, out, err = run_upgrade(self.tools, "--stamp", self.tmp / "gibt-es-nicht.md")
        self.assertEqual(code, 2, out + err)
        self.assertNotIn("Traceback", err)
        self.assertIn("gibt-es-nicht.md", out + err)
        self.assertFalse((self.tools / "kit-version.txt").exists())

    def test_a_file_that_cannot_be_written_is_named_and_the_rest_still_land(self):
        """One refused target used to end --apply with a traceback naming the exception and not
        the file, and every script after it in the list went unwritten with nothing said either.

        The refused block here is one whose heading carries a directory that does not exist, so
        the write raises FileNotFoundError for every user on every platform -- no permissions
        involved, no exception for root. It sorts first among the added files, which is the half
        that matters: the ones behind it have to land anyway.

        The stamp is the other half. A folder that is part old and part new must not come out
        carrying a version claiming otherwise -- the same reason stamp() refuses to record
        "unversioned".

        Undo recipe: remove the try/except from the write loop in upgrade.py's main(). This case
        then exits 1 with a FileNotFoundError traceback, check_links.py is never written, and
        the assertions on the surviving file and on the absent stamp go with it.
        """
        kit = kit_file(self.tmp / "kit.md",
                       {"build_index.py": "print('new')",
                        "aaa_kein_ordner/neu.py": "x = 1",
                        "check_links.py": "print('tool')"},
                       version="abcdef012345")
        code, out, err = run_upgrade(self.tools, kit, "--apply")
        self.assertEqual(code, 2, out + err)
        self.assertNotIn("Traceback", err)
        self.assertIn("aaa_kein_ordner/neu.py", err)
        self.assertEqual((self.tools / "build_index.py").read_text(encoding="utf-8"),
                         "print('new')\n", "a file listed before the refusal was not written")
        self.assertTrue((self.tools / "check_links.py").exists(),
                        "the loop stopped at the first refusal instead of naming it and going on")
        self.assertFalse((self.tools / "kit-version.txt").exists(),
                         "a part-old, part-new folder was stamped as if the update had finished")

    # ------------------------------------- a newer kit whose scripts happen to be identical

    def test_a_newer_kit_with_identical_scripts_still_reports_the_stale_stamp(self):
        """#23, the empty cell: version differs, blocks do not.

        A release that only edited the contract or the SECTION 10 header ships new bytes and
        the same scripts. The old code returned on `nothing to do` before the --apply branch,
        so write_stamp() was unreachable on this path and the folder kept the previous version
        forever -- while reporting itself fully up to date, which is what hid it.

        Nothing is written here, because that promise holds without --apply. It is said.

        THE ASSERTIONS ARE ON THE SENTENCE, NOT ON THE HEX. Written the obvious way -- assert both
        version strings appear in the output -- this test passed against the broken code, because
        the header line `installed: aaaaaaaaaaaa · kit file: bbbbbbbbbbbb` already contains both
        and always did. It was caught by running the undo recipe rather than by reading it: only
        the --apply case below went red, and a recipe that moves one test when it claims two is
        the same defect this suite exists for, one level up.

        Undo recipe, re-measured on this machine 2026-07-31: replace the stamp comparison in
        upgrade.py's main() with `if False:`, which is what returning early amounts to.
        test_upgrade 15/18 -- this case, the unstamped one and the --apply one -- and
        verify_setup 13/14 at step 13. Before the assertions above were moved off the header
        line the same recipe moved exactly ONE test, and the difference between one and three
        is the whole reason this recipe gets run instead of reasoned about. Named rather than
        given as a fraction, because that older run cannot be repeated: the code it measured
        is gone, and a fraction carried forward would look like a number somebody still has.
        """
        run_upgrade(self.tools, "--stamp",
                    kit_file(self.tmp / "old.md", {"build_index.py": "print('old')"},
                             version="aaaaaaaaaaaa"))
        kit = kit_file(self.tmp / "kit.md", {"build_index.py": "print('old')"},
                       version="bbbbbbbbbbbb")
        code, out, err = run_upgrade(self.tools, kit)
        self.assertEqual(code, 0, err)
        self.assertIn("stamp still reads aaaaaaaaaaaa", out, "the stale stamp was not called out")
        self.assertIn("record bbbbbbbbbbbb", out, "the repair was not named")
        self.assertNotIn("nothing to do", out, "a folder on the wrong version was called done")
        self.assertEqual((self.tools / "kit-version.txt").read_text(encoding="utf-8").strip(),
                         "aaaaaaaaaaaa", "the stamp was rewritten without --apply")

    def test_apply_corrects_the_stamp_when_only_the_version_moved(self):
        """The other half: --apply has to actually fix what the report named."""
        run_upgrade(self.tools, "--stamp",
                    kit_file(self.tmp / "old.md", {"build_index.py": "print('old')"},
                             version="aaaaaaaaaaaa"))
        kit = kit_file(self.tmp / "kit.md", {"build_index.py": "print('old')"},
                       version="bbbbbbbbbbbb")
        code, out, err = run_upgrade(self.tools, kit, "--apply")
        self.assertEqual(code, 0, err)
        self.assertEqual((self.tools / "kit-version.txt").read_text(encoding="utf-8").strip(),
                         "bbbbbbbbbbbb")
        self.assertEqual((self.tools / "build_index.py").read_text(encoding="utf-8"),
                         "print('old')\n", "a script was rewritten over an identical block")

    def test_an_unstamped_folder_with_identical_scripts_is_told_it_has_no_stamp(self):
        """The same gap from the other end: no stamp at all, scripts already current.

        Found by the healthy control above when the #23 fix went in, not by design. A folder
        installed before `--stamp` existed, or by a setup that skipped that line, answers
        `installed: unknown` -- and on this path the old code returned before saying so. The
        repair is the same one word of output; `--apply` writes it.

        Asserted on the sentence rather than on the words, for the reason spelled out two tests
        up: `installed: unknown · kit file: dddddddddddd` is the header line, so both strings are
        present whether or not the tool ever compares them.
        """
        kit = kit_file(self.tmp / "kit.md", {"build_index.py": "print('old')"},
                       version="dddddddddddd")
        code, out, err = run_upgrade(self.tools, kit)
        self.assertEqual(code, 0, err)
        self.assertIn("stamp still reads unknown", out)
        self.assertIn("record dddddddddddd", out)
        self.assertNotIn("nothing to do", out)
        self.assertFalse((self.tools / "kit-version.txt").exists(),
                         "a stamp was written without --apply")

    def test_a_matching_stamp_and_identical_scripts_stay_quiet(self):
        """The healthy control for the two above.

        Without it they only prove the tool complains, not that it complains for a reason: a
        version comparison that fires when the versions agree would pass both of them and turn
        every run into an offer to fix what is already right.
        """
        kit = kit_file(self.tmp / "kit.md", {"build_index.py": "print('old')"},
                       version="cccccccccccc")
        run_upgrade(self.tools, "--stamp", kit)
        code, out, err = run_upgrade(self.tools, kit)
        self.assertEqual(code, 0, err)
        self.assertIn("nothing to do", out)
        self.assertNotIn("--apply", out, "a folder at the right version was offered a correction")


if __name__ == "__main__":
    unittest.main(verbosity=1)
