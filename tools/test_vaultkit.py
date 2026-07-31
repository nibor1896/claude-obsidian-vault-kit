"""Suite for vaultkit.py -- the one entry point every guard is reached through.

What can go wrong here is not arithmetic, it is routing: a subcommand that silently runs the
wrong tool, a register that disagrees with what the file can actually dispatch, or arguments
mangled on the way through. Each of those looks like a working vault right up to the moment
somebody reads a number that came from the wrong place.
"""

import shutil
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import vaultkit
from _testkit import make_vault, run_tool, write_note
from vaultkit import RUN_LOG_RELPATH, category_index_name


class VaultkitTest(unittest.TestCase):
    def setUp(self):
        self.vault = make_vault(("ProjektEins",))
        self.project = self.vault / "ProjektEins"

    def tearDown(self):
        shutil.rmtree(self.vault.parent, ignore_errors=True)

    # ------------------------------------------------------------------ control

    def test_healthy_control_index_through_the_dispatcher(self):
        """The whole point of the stage: `vaultkit.py index` does what `build_index.py` did."""
        write_note(self.project / "00_Notes" / "eine-erkenntnis.md",
                   title="Eine Erkenntnis", summary="Genau ein Satz.", created="2026-07-01")
        code, out, err = run_tool("vaultkit.py", "index", "--vault", self.project)
        self.assertEqual(code, 0, err)
        self.assertIn("1 entries in 6 categories", out)
        index = (self.project / "00_Notes"
                 / category_index_name("ProjektEins", "00_Notes")).read_text(encoding="utf-8")
        self.assertIn("[[ProjektEins/00_Notes/eine-erkenntnis|Eine Erkenntnis]]", index)

    # ------------------------------------------------------------ failure modes

    def test_no_subcommand_is_a_usage_error_not_a_silent_zero(self):
        """Exit 2 and the list of names. A bare invocation that returned 0 would read as a run."""
        code, out, err = run_tool("vaultkit.py")
        self.assertEqual(code, 2)
        self.assertIn("subcommand", out + err)

    def test_an_unknown_subcommand_is_named_and_refused(self):
        code, out, err = run_tool("vaultkit.py", "gibtsnicht")
        self.assertEqual(code, 2)
        self.assertIn("gibtsnicht", out + err)
        for known in ("index", "links", "duplicates", "freshness"):
            self.assertIn(known, out + err, "the refusal did not say what is available")

    def test_a_guards_own_exit_code_travels_out_through_the_dispatcher(self):
        """A dispatcher that swallowed a non-zero exit would turn every guard green.

        This is the failure that would be invisible from the inside: the tool still prints its
        defect, the chain still looks like it ran, and the verdict is gone.
        """
        write_note(self.project / "00_Notes" / "ohne-titel.md", title=None)
        code, _, err = run_tool("vaultkit.py", "index", "--vault", self.project)
        self.assertEqual(code, 1, "the guard's verdict did not survive the dispatch")
        self.assertIn("ohne-titel.md", err)

    def test_arguments_reach_the_tool_untouched(self):
        """`--root` and `--vault` mean different things, and only the tool below knows which.

        There is no shared parser on purpose. If one were ever added, this is the case that
        would catch it flattening the two into one meaning: `--root` writes the vault hub,
        `--vault` does not.
        """
        run_tool("vaultkit.py", "index", "--vault", self.project)
        self.assertEqual(list(self.vault.glob("INDEX - *.md")), [],
                         "--vault wrote the root index, so it was treated as --root")
        code, _, err = run_tool("vaultkit.py", "index", "--root", self.vault)
        self.assertEqual(code, 0, err)
        self.assertTrue(list(self.vault.glob("INDEX - *.md")), "--root wrote no root index")

    def test_the_job_name_in_the_run_log_does_not_move(self):
        """`runs.log` is read by the freshness check and by jobs.json, both of which speak the
        old names. If dispatching renamed a job, a watched job would silently stop being
        watched -- and `unclassified` deliberately does not change an exit code.
        """
        run_tool("vaultkit.py", "index", "--vault", self.project)
        log = (self.vault / RUN_LOG_RELPATH).read_text(encoding="utf-8")
        self.assertIn("\tbuild_index\t", log)
        self.assertNotIn("\tvaultkit\t", log)
        self.assertNotIn("\tindex\t", log)

    # ------------------------------------------------------------ the register

    def test_every_subcommand_in_the_register_can_actually_be_dispatched(self):
        """The register is what `freshness` and build_kit.py read to know what this file runs.

        A name in it with nothing callable behind it would be a promise nothing keeps, and it
        would be made to two other readers before anyone typed the subcommand.
        """
        self.assertTrue(vaultkit.COMMANDS, "the register is empty")
        for sub, spec in vaultkit.COMMANDS.items():
            self.assertTrue(callable(spec.get("run")), f"{sub} routes to nothing callable")
            self.assertIs(spec["run"], getattr(vaultkit, f"{sub}_main", None),
                          f"{sub} does not route to {sub}_main")
            # The typed part of the contract, checked as behaviour rather than trusted: a
            # handler takes the leftover arguments and returns an exit code. `upgrade.py
            # --prove` only asserts callable(); this is what says what calling it means.
            hints = getattr(spec["run"], "__annotations__", {})
            self.assertEqual(hints.get("return"), int, f"{sub}_main does not declare an exit code")
            self.assertIn("argv", hints, f"{sub}_main does not declare its argument")

    def test_the_register_sits_after_everything_it_describes(self):
        """It is the last thing in the file, and that makes it an all-or-nothing detector.

        A block that arrived truncated has no register, so the first subcommand fails at once
        with a NameError naming COMMANDS. Cut anywhere earlier and the file still compiles --
        it would simply lose a tool, quietly, which is the failure the kit is built against.
        """
        text = Path(vaultkit.__file__).read_text(encoding="utf-8")
        register = text.index("\nCOMMANDS: dict[str, Command] = {")
        self.assertGreater(register, text.index("\ndef main("),
                           "the register moved above the code it describes")
        after = text[register:]
        self.assertNotIn("\ndef ", after, "a function was added below the register")
        self.assertIn('if __name__ == "__main__":', after)

    def test_a_job_name_is_either_a_string_or_an_explicit_none(self):
        """`None` is a statement -- "reaches no verdict, never logs" -- not a missing value.

        `tokens` is the one, and it is also what excuses that subcommand from having to appear
        in any chain. Until 2026-07-31 the same statement lived in jobs.json's `not_invoked`
        under the old filename; it is made here now, where the fact is. An absent key would read
        as an oversight instead of a decision.
        """
        for sub, spec in vaultkit.COMMANDS.items():
            self.assertIn("job", spec, f"{sub} does not say whether it logs")
            self.assertTrue(spec["job"] is None or isinstance(spec["job"], str))
        self.assertIsNone(vaultkit.COMMANDS["tokens"]["job"])
        self.assertEqual(vaultkit.COMMANDS["index"]["job"], "build_index")


if __name__ == "__main__":
    unittest.main(verbosity=1)
