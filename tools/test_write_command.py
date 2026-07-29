"""Suite for write_command.py.

The command file exists to answer three traps in the SECTION 8 chain, so the cases that matter
are not "a file appeared" but "the file answers them". `--vault` means a PROJECT after
build_index.py and the ROOT after check_links.py; getting that backwards is the failure the
command is written to prevent, and a test that only checks the file exists would pass over it.

Nothing here ever writes with `--target home`. That path is outside the vault -- it is the
machine's real Claude config -- and a suite that writes there to prove it can is a suite that
edits the user's setup. The home path is checked as a value, not as a side effect.
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
        self.target = self.vault / COMMAND_RELPATH

    def tearDown(self):
        shutil.rmtree(self.vault.parent, ignore_errors=True)

    def write(self, *extra):
        return run_tool("write_command.py", "--vault", self.vault, "--target", "vault", *extra)

    # ------------------------------------------------------------------ control

    def test_healthy_control_a_command_is_written_and_named(self):
        code, out, err = self.write()
        self.assertEqual(code, 0, err)
        self.assertTrue(self.target.is_file(), f"no command file: {out} {err}")
        self.assertIn("vaultkit.md", out, "it wrote a file outside the vault without saying so")

    def test_the_frontmatter_carries_a_description_and_nothing_else(self):
        """All five documented fields are optional. Every one that is set is one more thing to
        keep true, and a command needs exactly one of them to be findable."""
        self.write()
        text = self.target.read_text(encoding="utf-8")
        block = text.split("---")[1]
        keys = [line.split(":")[0] for line in block.strip().splitlines() if ":" in line]
        self.assertEqual(keys, ["description"])

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

    def test_a_hand_edited_command_survives_the_next_run(self):
        """One that comes back unchanged proves nothing unless it went in changed."""
        self.write()
        mine = self.target.read_text(encoding="utf-8") + "\n## 7 · My own step\n"
        self.target.write_text(mine, encoding="utf-8", newline="\n")
        code, _, err = self.write()
        self.assertEqual(code, 0, err)
        self.assertEqual(self.target.read_text(encoding="utf-8"), mine)

    def test_the_command_file_does_not_enter_the_note_denominators(self):
        """It is configuration, not knowledge, and a guard that counts it reports a wrong n/m.

        Measured 2026-07-29 with `.claude` missing from SKIP_DIRS: writing this one file took
        check_links.py from 26 files scanned to 27, check_duplicates.py from 4 notes to 5 and
        from 6 compared pairs to 10, and the generator from 26 distinct filenames to 27. Nothing
        went red, which is exactly why it needs a test -- the numbers were quietly wrong and no
        run had a reason to mention it.
        """
        write_note(self.vault / "ProjektEins" / "00_Notes" / "eine-erkenntnis.md",
                   title="Eine Erkenntnis")
        run_tool("build_index.py", "--root", self.vault)
        before = [run_tool(script, "--vault", self.vault)[1]
                  for script in ("check_links.py", "check_duplicates.py")]

        self.write()
        self.assertTrue(self.target.is_file())
        after = [run_tool(script, "--vault", self.vault)[1]
                 for script in ("check_links.py", "check_duplicates.py")]
        self.assertEqual(before, after,
                         "the command file changed what the guards count as notes")

    def test_a_vault_without_projects_is_refused_not_written_empty(self):
        """A command listing no projects is a working file that does nothing. It means the wrong
        path was given, and that has to be said, not written out."""
        empty = self.vault.parent / "NotAVault"
        empty.mkdir()
        code, out, err = run_tool("write_command.py", "--vault", empty, "--target", "vault")
        self.assertNotEqual(code, 0, "an empty vault produced a command file")
        self.assertIn("no projects", out + err)
        self.assertFalse((empty / COMMAND_RELPATH).exists())

    def test_the_home_target_is_outside_the_vault(self):
        """Checked as a value, never written. `~/.claude/commands/` is the real config folder of
        whoever runs this suite, and it is also why SECTION 1 has to ask before choosing it: the
        name collides silently with a command the user may already have."""
        home = write_command.target_path(self.vault, "home")
        self.assertEqual(home, Path.home() / ".claude" / "commands" / "vaultkit.md")
        self.assertNotEqual(home, write_command.target_path(self.vault, "vault"))
        self.assertFalse(str(home).startswith(str(self.vault)))


if __name__ == "__main__":
    unittest.main(verbosity=1)
