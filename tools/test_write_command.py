"""Suite for write_command.py.

The command file exists to answer three traps in the SECTION 8 chain, so the cases that matter
are not "a file appeared" but "the file answers them". `--vault` means a PROJECT after
build_index.py and the ROOT after check_links.py; getting that backwards is the failure the
command is written to prevent, and a test that only checks the file exists would pass over it.

THE DESTINATION IS THE USER'S OWN `~/.claude/commands/`, AND IT IS THE ONLY ONE. That is also
what makes this suite dangerous to write badly: run it against the real home folder and it edits
the setup of whoever runs it. Every case here redirects `Path.home()` into a throwaway folder via
`run_tool(home=...)`, so the tool takes its real path, writes for real, and touches nothing
outside the tempdir. Checking the path as a value only -- which is what this suite did while an
in-vault option still existed -- left the one destination that ships completely untested.
"""

import shutil
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from _testkit import make_vault, run_tool, write_note  # noqa: E402
from vault_paths import project_dirs  # noqa: E402

import write_command  # noqa: E402

COMMAND_RELPATH = Path(".claude") / "commands" / "vaultkit.md"


class WriteCommandTest(unittest.TestCase):
    def setUp(self):
        self.vault = make_vault(("ProjektEins", "ProjektZwei"))
        # A stand-in for the user's home folder, inside the same tempdir the vault lives in.
        self.home = self.vault.parent / "FakeHome"
        self.home.mkdir(parents=True, exist_ok=True)
        self.target = self.home / COMMAND_RELPATH

    def tearDown(self):
        shutil.rmtree(self.vault.parent, ignore_errors=True)

    def write(self, *extra):
        return run_tool("write_command.py", "--vault", self.vault, *extra, home=self.home)

    # ------------------------------------------------------------------ control

    def test_healthy_control_a_command_is_written_and_named(self):
        code, out, err = self.write()
        self.assertEqual(code, 0, err)
        self.assertTrue(self.target.is_file(), f"no command file: {out} {err}")
        self.assertIn("vaultkit.md", out, "it wrote a file outside the vault without saying so")

    def test_it_writes_into_the_home_folder_and_not_into_the_vault(self):
        """The destination is not a preference. A copy under the vault root would load only in a
        session started at that root, which is why the option was taken out again -- and why the
        vault must come back from this run with nothing added to it."""
        self.write()
        self.assertTrue(self.target.is_file())
        self.assertFalse((self.vault / COMMAND_RELPATH).exists(),
                         "a command was written into the vault, where it would not load")
        self.assertFalse((self.vault / ".claude").exists())

    def test_the_frontmatter_carries_a_description_and_nothing_else(self):
        """All five documented fields are optional. Every one that is set is one more thing to
        keep true, and a command needs exactly one of them to be findable.

        The marker lives on the first line of the BODY for this reason: YAML frontmatter has to
        start at byte zero, and a comment in front of it takes `description:` with it.
        """
        self.write()
        text = self.target.read_text(encoding="utf-8")
        self.assertTrue(text.startswith("---\n"), "something got in front of the frontmatter")
        block = text.split("---")[1]
        keys = [line.split(":")[0] for line in block.strip().splitlines() if ":" in line]
        self.assertEqual(keys, ["description"])
        self.assertNotIn(write_command.MARKER_PREFIX, block, "the marker is inside the frontmatter")

    # -------------------------------------------------------------- the traps

    def test_vault_means_a_project_for_the_generator_and_the_root_for_the_link_checker(self):
        """The trap the command exists for: one flag name, two meanings, three tools.

        check_links.py wants the vault root, build_index.py wants one project directory. A
        command that puts the same path after every `--vault` is wrong in two places out of
        three, and both wrong invocations exit non-zero at the user rather than here.
        """
        self.write("--shell", "powershell")
        root = write_command.show(self.vault, "powershell")
        lines = self.target.read_text(encoding="utf-8").splitlines()

        projects = project_dirs(self.vault)   # counted, never typed -- 00_Global is one of them
        generator = [line for line in lines if "build_index.py" in line and "--vault" in line]
        self.assertEqual(len(generator), len(projects),
                         "one build_index --vault line per project, no more and no fewer")
        for line in generator:
            self.assertNotIn(f"--vault {root}", line,
                             "the generator was handed the vault root, which it refuses")
        for project in projects:
            self.assertTrue(any(write_command.show(project, "powershell") in line
                                for line in generator), f"{project.name} has no index line")

        links = [line for line in lines if "check_links.py" in line]
        self.assertEqual(len(links), 1)
        self.assertIn(f"--vault {root}", links[0],
                      "the link checker was handed something narrower than the vault root")

    def test_the_sweep_uses_root_and_says_why(self):
        """`--vault` alone leaves the root index on yesterday's count, green and silent."""
        self.write("--shell", "powershell")
        text = self.target.read_text(encoding="utf-8")
        self.assertIn(f"--root {write_command.show(self.vault, 'powershell')}", text)
        self.assertIn("`--root`, not `--vault`", text)

    def test_the_tool_folder_is_written_as_a_full_path(self):
        """`06_tools/` resolves from the vault root and nowhere else."""
        self.write("--shell", "posix")
        text = self.target.read_text(encoding="utf-8")
        tools = (self.vault / "00_Global" / "06_tools").as_posix()
        self.assertIn(tools, text)
        for line in text.splitlines():
            if line.startswith("- `python "):
                self.assertIn(tools, line, f"a bare tool path slipped in: {line}")

    # ------------------------------------------------------------ failure modes

    def test_the_second_run_writes_nothing_and_says_nothing(self):
        """A command file is there to be edited. Silence on the second run is the whole promise:
        it means nothing was missing, and runs.log carries the run either way."""
        self.write()
        before = self.target.read_bytes()
        code, out, err = self.write()
        self.assertEqual(code, 0, err)
        self.assertEqual(out.strip(), "", "the second run reported work it did not do")
        self.assertEqual(self.target.read_bytes(), before)

    def test_a_foreign_command_of_the_same_name_is_named_and_goes_red(self):
        """The other half of "already there", and the half that must not be silent.

        In ~/.claude/commands/ the user may already have a /vaultkit of their own. Nothing is
        overwritten -- but nothing is written either, and a zero exit there would let the setup
        report the command as ready while the stranger keeps the name. Both directions are
        checked here, because the guard is only worth having if it can tell them apart.

        This is the case that could not be tested at all while it only ran against the vault
        copy: the collision it guards against happens in the home folder, by definition.
        """
        self.target.parent.mkdir(parents=True, exist_ok=True)
        self.target.write_text("---\ndescription: My own command\n---\n\nDo my thing.\n",
                               encoding="utf-8", newline="\n")
        mine = self.target.read_bytes()

        code, out, err = self.write()
        self.assertNotEqual(code, 0, "a foreign command was passed over silently")
        self.assertIn(str(self.target), out + err, "the path holding the name was not shown")
        self.assertEqual(self.target.read_bytes(), mine, "a foreign command was overwritten")

    def test_our_own_file_is_recognised_by_its_marker_not_by_its_path(self):
        """A vault that moved is still our file. Re-checking the path inside would call it a
        stranger and turn a working setup red for having been relocated."""
        self.write()
        text = self.target.read_text(encoding="utf-8")
        self.assertIn(write_command.MARKER_PREFIX, text)
        moved = text.replace(self.vault.as_posix(), "/somewhere/else/Vault")
        self.target.write_text(moved, encoding="utf-8", newline="\n")
        code, out, err = self.write()
        self.assertEqual(code, 0, err)
        self.assertEqual(out.strip(), "")
        self.assertEqual(self.target.read_text(encoding="utf-8"), moved)

    def test_a_hand_edited_command_survives_the_next_run(self):
        """One that comes back unchanged proves nothing unless it went in changed."""
        self.write()
        mine = self.target.read_text(encoding="utf-8") + "\n## 7 · My own step\n"
        self.target.write_text(mine, encoding="utf-8", newline="\n")
        code, _, err = self.write()
        self.assertEqual(code, 0, err)
        self.assertEqual(self.target.read_text(encoding="utf-8"), mine)

    def test_a_dot_claude_folder_inside_the_vault_stays_out_of_the_denominators(self):
        """Configuration is not knowledge, and a guard that counts it reports a wrong n/m.

        The command no longer lands in the vault, but a `.claude/` folder there is ordinary --
        the user may keep project settings beside their notes, and the setup itself is often
        started in such a folder. So the guards are held to skipping it, with a file written by
        hand rather than by the tool.

        Measured 2026-07-29 with `.claude` missing from SKIP_DIRS: one such file took
        check_links.py from 26 files scanned to 27, check_duplicates.py from 4 notes to 5 and
        from 6 compared pairs to 10, and the generator from 26 distinct filenames to 27. Nothing
        went red, which is exactly why it needs a test -- the numbers were quietly wrong and no
        run had a reason to mention it.

        Recipe without the fix: take ".claude" out of SKIP_DIRS in vault_paths.py and run this
        suite there; this case fails and no other does.
        """
        write_note(self.vault / "ProjektEins" / "00_Notes" / "eine-erkenntnis.md",
                   title="Eine Erkenntnis")
        run_tool("build_index.py", "--root", self.vault)
        before = [run_tool(script, "--vault", self.vault)[1]
                  for script in ("check_links.py", "check_duplicates.py")]

        intruder = self.vault / COMMAND_RELPATH
        intruder.parent.mkdir(parents=True, exist_ok=True)
        intruder.write_text("---\ndescription: Something the user keeps here\n---\n\nBody.\n",
                            encoding="utf-8", newline="\n")
        after = [run_tool(script, "--vault", self.vault)[1]
                 for script in ("check_links.py", "check_duplicates.py")]
        self.assertEqual(before, after,
                         "a file under .claude/ changed what the guards count as notes")

    def test_a_vault_without_projects_is_refused_not_written_empty(self):
        """A command listing no projects is a working file that does nothing. It means the wrong
        path was given, and that has to be said, not written out."""
        empty = self.vault.parent / "NotAVault"
        empty.mkdir()
        code, out, err = run_tool("write_command.py", "--vault", empty, home=self.home)
        self.assertNotEqual(code, 0, "an empty vault produced a command file")
        self.assertIn("no projects", out + err)
        self.assertFalse(self.target.exists())

    def test_there_is_exactly_one_destination_and_it_is_the_home_folder(self):
        """`target_path()` takes no argument on purpose. A parameter here would be the door back
        to an in-vault copy, and that copy is the thing that got removed -- it loads only in a
        session started at the vault root, which is not how anyone runs a sync command."""
        self.assertEqual(write_command.target_path(),
                         Path.home() / ".claude" / "commands" / "vaultkit.md")


if __name__ == "__main__":
    unittest.main(verbosity=1)
