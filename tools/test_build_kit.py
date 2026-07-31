"""Suite for build_kit.py -- the guard that holds the prose to the numbers the code counts.

WHY THIS EXISTS (2026-07-29): build_kit.py checks every `n/m` in the contract, in the SECTION 10
header and in README.md against `len(FIXTURES)`, `len(STEPS)` and the count of `test_*.py`. It had
no suite of its own, and run_suites.py collects by `test_*.py`, so the acceptance run never touched
it -- the one guard nothing guarded. Its own docstring promised `--check` "for the acceptance run";
that run did not call it. Then a claim wrapped across a line end, the pattern stopped matching, and
zero matches read as agreement: the contract was set to `99/99`, rebuilt, `--check` exited 0, and
the delivered file said `99/99 end-to-end setup steps`.

Every case below runs the generator against a COPY of the repository, mutated in the temp
directory, never against the working tree. test_upgrade.py does the same for the same reason: a
tool that acts on its own folder cannot be tested honestly in that folder, and a suite that edits
tracked files leaves them edited when it crashes.

This suite is not delivered, and that is now a decision rather than an accident. build_kit.py is
the generator; a vault does not get one, so it does not get a suite for one either. The rule lives
in build_kit.delivered_suites(): a `test_X.py` ships only when `X.py` does. Until that rule
existed, a bare glob shipped every suite, and this file would have installed itself into every
user's tool folder to test a tool that is not there.
"""

import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent

sys.path.insert(0, str(HERE))

# Imported, never respelled: a second copy of the patterns in this file would go on passing while
# the real ones stopped matching, which is the exact defect this suite exists to catch.
import build_kit  # noqa: E402

# The repo files build_kit.py reads besides src/contract.md. The tool folder comes along whole:
# the guard imports acceptance and verify_setup to count fixtures and steps, and derives the
# delivered suites from what is in it.
SOURCES = ("README.md", "claude-obsidian-vault-kit.md")


def sandbox():
    """A throwaway copy of the repository, complete enough for build_kit.py to run in.

    `docs/` comes along since 2026-07-31: prose_sources() reads the pages for the command lines
    they hand the user, and a sandbox without them would make that guard check nothing while
    every case here still passed.
    """
    tmp = Path(tempfile.mkdtemp(prefix="vaultkit_buildkit_"))
    shutil.copytree(HERE, tmp / "tools", ignore=shutil.ignore_patterns("__pycache__"))
    shutil.copytree(REPO / "docs", tmp / "docs")
    (tmp / "src").mkdir()
    shutil.copy2(REPO / "src" / "contract.md", tmp / "src" / "contract.md")
    for name in SOURCES:
        shutil.copy2(REPO / name, tmp / name)
    return tmp


def run_build(tmp, *args):
    """build_kit.py inside a sandbox. Returns (returncode, stdout, stderr)."""
    result = subprocess.run([sys.executable, str(tmp / "tools" / "build_kit.py"), *args],
                            capture_output=True, cwd=str(tmp))
    return (result.returncode,
            result.stdout.decode("utf-8", errors="replace"),
            result.stderr.decode("utf-8", errors="replace"))


def run_check(tmp):
    return run_build(tmp, "--check")


def edit(tmp, relpath, fn):
    path = tmp / relpath
    path.write_text(fn(path.read_text(encoding="utf-8")), encoding="utf-8", newline="\n")


def falsify(text, pattern):
    """Turn the first `n/m <thing>` this pattern sees into `99/99 <thing>`."""
    return re.sub(pattern, lambda m: re.sub(r"^\d+/\d+", "99/99", m.group(0)), text, count=1)


def erase(text, pattern):
    """Remove every `n/m <thing>` this pattern sees, so the source states the claim nowhere."""
    return re.sub(pattern, "(the measurement used to be here)", text)


class BuildKitTest(unittest.TestCase):
    def setUp(self):
        self.tmp = sandbox()

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    # ------------------------------------------------------------------ control

    def test_healthy_control_an_untouched_copy_is_consistent(self):
        """The sandbox has to be faithful, or every failure below proves only that it is not."""
        code, out, err = run_check(self.tmp)
        self.assertEqual(code, 0, f"{out}\n{err}")
        self.assertIn("up to date", out)

    # ------------------------------------------------------------ failure modes

    def test_every_claim_in_the_contract_is_counted(self):
        """The contract is the file the user reads. A stale number there is the whole defect."""
        for pattern, what in build_kit.CLAIMS:
            with self.subTest(claim=what):
                tmp = sandbox()
                try:
                    edit(tmp, "src/contract.md", lambda t: falsify(t, pattern))
                    code, out, err = run_check(tmp)
                    self.assertNotEqual(code, 0, f"a wrong {what} count passed: {out}")
                    self.assertIn("src/contract.md", err, "the wrong source was named")
                    self.assertIn("99/99", err)
                finally:
                    shutil.rmtree(tmp, ignore_errors=True)

    def test_every_claim_in_the_readme_is_counted(self):
        """README.md carried `11/11 end-to-end setup steps` for four hours after step 12 shipped,
        with --check green the whole time, because the guard only looked at the contract."""
        for pattern, what in build_kit.CLAIMS:
            with self.subTest(claim=what):
                tmp = sandbox()
                try:
                    edit(tmp, "README.md", lambda t: falsify(t, pattern))
                    code, out, err = run_check(tmp)
                    self.assertNotEqual(code, 0, f"a wrong {what} count passed: {out}")
                    self.assertIn("README.md", err, "the wrong source was named")
                finally:
                    shutil.rmtree(tmp, ignore_errors=True)

    def test_a_claim_that_wraps_across_a_line_end_is_still_counted(self):
        """The measured defect, reproduced: `13/13` ended a line, `end-to-end setup steps` began
        the next, the pattern spelled that gap as a literal space, and no match read as no
        disagreement. --check exited 0 over a delivered file saying 99/99."""
        pattern = dict((w, p) for p, w in build_kit.CLAIMS)["end-to-end setup steps"]
        edit(self.tmp, "src/contract.md",
             lambda t: re.sub(pattern,
                              lambda m: re.sub(r"^\d+/\d+\s+", "99/99\n", m.group(0)), t, count=1))
        code, out, err = run_check(self.tmp)
        self.assertNotEqual(code, 0, f"a wrapped claim went unread: {out}")
        self.assertIn("src/contract.md", err)

    def test_a_wrapped_claim_that_agrees_is_not_reported_as_wrong(self):
        """The other half: a pattern loose enough to read a wrapped line must not read every
        wrapped line as a defect. Exit is still 1 here -- the bytes moved, so the delivered file
        is out of date -- but not for the reason under test."""
        pattern = dict((w, p) for p, w in build_kit.CLAIMS)["end-to-end setup steps"]
        edit(self.tmp, "src/contract.md",
             lambda t: re.sub(pattern, lambda m: m.group(0).replace(" ", "\n", 1), t, count=1))
        _, out, err = run_check(self.tmp)
        self.assertNotIn("the prose states a number the code does not count", out + err)

    def test_a_source_that_states_a_claim_nowhere_is_reported(self):
        """Zero matches is not agreement.

        This is the class the wrapped line belonged to, and the reason the wrap survived: the
        loop had nothing to say about a pattern that matched nothing. Either the prose dropped a
        promise or the pattern stopped seeing it, and from inside the guard those look identical
        -- so both are reported.
        """
        for source in ("src/contract.md", "README.md"):
            for pattern, what in build_kit.CLAIMS:
                with self.subTest(source=source, claim=what):
                    tmp = sandbox()
                    try:
                        edit(tmp, source, lambda t: erase(t, pattern))
                        code, out, err = run_check(tmp)
                        self.assertNotEqual(code, 0, f"a missing {what} claim passed: {out}")
                        self.assertIn(f"states no {what} claim at all", err)
                    finally:
                        shutil.rmtree(tmp, ignore_errors=True)

    # ------------------------------------------------------- what gets delivered

    def test_no_suite_is_delivered_at_all(self):
        """The invariant E3 exists to establish, pinned so nothing drifts back into it.

        Suites used to be collected by a bare glob and shipped alongside their tools, so a vault
        received 126 unit tests and ran them daily as step 6 of its own maintenance chain --
        over code that had not changed since setup. They are release verification: they answer
        "does this kit work", once, here, before publishing.

        Asserted over the artefact rather than over the list, because that is what a user gets.
        A `test_` block reappearing in SECTION 10 is the one thing this must never allow.
        """
        text = (self.tmp / "claude-obsidian-vault-kit.md").read_text(encoding="utf-8")
        embedded = [name for name, _ in build_kit.BLOCK_RE.findall(text)]
        self.assertTrue(embedded, "no blocks at all -- the fixture is broken, not the delivery")
        leaked = [name for name in embedded if name.startswith("test_")]
        self.assertEqual(leaked, [], "a suite is in the delivered file")
        for name in ("run_suites.py", "acceptance.py", "verify_setup.py", "_testkit.py"):
            self.assertNotIn(name, embedded, f"{name} is release verification and must stay here")
        self.assertEqual(embedded, build_kit.delivered_files(),
                         "the artefact and the delivery lists disagree")

    def test_a_tool_leaving_the_delivery_takes_its_suite_and_the_count_with_it(self):
        """The other direction, and the one that has to be loud.

        Dropping a tool from the delivery silently drops its suite too. The number the user is
        promised then describes a folder that no longer exists, so the prose has to go red --
        in every source at once, which is what says "the tool left" rather than "the prose rotted".

        The two files go with the list entry since 2026-07-31: check_delivery_lists() runs first
        and a tool left on disk in no list is its own defect now. Deleting them is also the more
        faithful fixture -- a tool that leaves the kit leaves the repository.
        """
        edit(self.tmp, "tools/build_kit.py", lambda t: t.replace('"count_tokens.py"', "", 1))
        edit(self.tmp, "tools/build_kit.py",
             lambda t: t.replace('    "test_count_tokens.py": "suite for count_tokens.py '
                                 '-- release verification",\n', "", 1))
        (self.tmp / "tools" / "count_tokens.py").unlink()
        (self.tmp / "tools" / "test_count_tokens.py").unlink()
        code, out, err = run_check(self.tmp)
        self.assertNotEqual(code, 0, f"a shrunken delivery passed: {out}\n{err}")
        # Counted from the folder, never typed: this number moves whenever a suite does.
        self.assertIn(f"counted {len(build_kit.repo_suites()) - 1}", err)
        for source in ("src/contract.md", "tools/build_kit.py", "README.md"):
            self.assertIn(source, err, "only some sources noticed the tool leaving")

    # ------------------------------------- the five build-time guards, one probe each
    #
    # Each case mutates exactly ONE thing and requires exit 1 on its own. Two broken things at
    # once can leave a check green -- the second failure short-circuits before the first is
    # reached, or the two cancel in the same comparison -- so nothing here is combined.

    def test_a_file_in_tools_that_no_list_mentions_is_refused(self):
        """Guard (a), the direction that used to fall through in silence.

        SHARED, TOOLS_ORDER and DRIVERS are typed by hand and nothing compared them against the
        folder. A tool written and never added simply was not in the kit, and no run said so.
        """
        (self.tmp / "tools" / "dummy.py").write_text("print('nobody listed me')\n",
                                                     encoding="utf-8", newline="\n")
        code, out, err = run_check(self.tmp)
        self.assertNotEqual(code, 0, f"an unlisted file passed: {out}")
        self.assertIn("dummy.py: in tools/ and in no list", err)
        self.assertIn("REPO_ONLY", err, "the message did not name the way out")

    def test_a_list_entry_with_no_file_behind_it_is_refused(self):
        """Guard (a), the other direction, and the one with a worse symptom.

        A name in a list with no file behind it got as far as block(), which opens the file. The
        first sign was a bare FileNotFoundError out of the renderer -- after every check had
        already reported the delivery as fine.
        """
        edit(self.tmp, "tools/build_kit.py",
             lambda t: t.replace('"count_tokens.py"]', '"count_tokens.py", "nie_geschrieben.py"]', 1))
        code, out, err = run_check(self.tmp)
        self.assertNotEqual(code, 0, f"a list entry with no file passed: {out}")
        self.assertIn("nie_geschrieben.py: listed, and no such file", err)
        self.assertNotIn("Traceback", err, "the renderer crashed instead of the guard reporting")

    def test_a_delivered_tool_without_its_suite_is_refused(self):
        """Guard (b). The contract states the rule in this direction; only the converse was held.

        delivered_suites() stops a repo-side suite shipping itself. Nothing stopped a tool
        arriving with no suite at all -- acceptance.py and verify_setup.py were in exactly that
        state, and they are exempt in writing now rather than by omission.
        """
        # Deleted rather than renamed inside tools/: a rename leaves an unaccounted file behind
        # and check_delivery_lists() would report that instead, which is a different subject.
        # Its REPO_ONLY line goes too -- since 2026-07-31 that list is checked for existence, so
        # leaving the entry behind would make the run red one guard earlier.
        (self.tmp / "tools" / "test_count_tokens.py").unlink()
        edit(self.tmp, "tools/build_kit.py",
             lambda t: t.replace('    "test_count_tokens.py": "suite for count_tokens.py '
                                 '-- release verification",\n', "", 1))
        code, out, err = run_check(self.tmp)
        self.assertNotEqual(code, 0, f"a tool without its suite passed: {out}\n{err}")
        self.assertIn("count_tokens.py: delivered, and there is no tools/test_count_tokens.py", err)

    def test_an_exemption_for_something_not_delivered_is_refused(self):
        """Guard (b), the other half: SUITE_EXEMPT must not outlive what it excuses.

        An exemption nobody needs reads as a decision somebody made about a file that is still
        there. Three entries today, each with its reason; a fourth has to be defended.
        """
        edit(self.tmp, "tools/build_kit.py",
             lambda t: t.replace("SUITE_EXEMPT = {}",
                                 'SUITE_EXEMPT = {"laengst_weg.py": "no reason left"}', 1))
        code, out, err = run_check(self.tmp)
        self.assertNotEqual(code, 0, f"a stale exemption passed: {out}")
        self.assertIn("laengst_weg.py: exempt from having a suite, and not in the kit", err)

    def test_jobs_json_drifting_from_its_copy_in_code_is_refused(self):
        """Guard (c). The suite has never once read the shipped file.

        check_freshness.py carries the same three lists as defaults, for a vault with no config.
        The acceptance fixture builds a vault WITHOUT a jobs.json, so it takes the default path
        every time -- measured 2026-07-31. Both statements existed, nothing compared them, and
        the one the user gets was the untested one.
        """
        edit(self.tmp, "tools/jobs.json",
             lambda t: t.replace("runs in the verification chain and by hand, never on a schedule",
                                 "runs whenever, honestly"))
        code, out, err = run_check(self.tmp)
        self.assertNotEqual(code, 0, f"a drifted jobs.json passed: {out}")
        self.assertIn("on_demand", err)
        self.assertIn("disagree", err)

    def test_a_log_label_that_does_not_match_its_file_is_refused(self):
        """Guard (d), and the whole failure class it covers is silent.

        check_freshness takes the population from the filenames. A label that drifts puts BOTH
        names into `unclassified` -- the job nobody logged and the label nobody declared -- and
        unclassified deliberately does not change the exit code. The job stops being watched and
        no run anywhere goes red about it.
        """
        edit(self.tmp, "tools/build_index.py",
             lambda t: t.replace('log_run(vault_root, "build_index"',
                                 'log_run(vault_root, "build_indexx"'))
        code, out, err = run_check(self.tmp)
        self.assertNotEqual(code, 0, f"a drifted log label passed: {out}")
        self.assertIn('build_index.py: logs as "build_indexx"', err)
        self.assertIn("unclassified", err, "the message did not say why it is silent otherwise")

    def test_a_runnable_script_without_the_stream_fix_is_refused(self):
        """Guard (e). The block is copied twelve times on purpose, so it can go missing once.

        Three of these files do not import vault_paths at all, and in the rest the block sits
        ABOVE the import so an ImportError traceback lands on a reconfigured stderr. That is why
        it is not factored out -- and why nothing would notice one copy disappearing.
        """
        edit(self.tmp, "tools/count_tokens.py",
             lambda t: t.replace('        _stream.reconfigure(encoding="utf-8", errors="replace")',
                                 "        pass"))
        code, out, err = run_check(self.tmp)
        self.assertNotEqual(code, 0, f"a script with no stream fix passed: {out}")
        self.assertIn("count_tokens.py: runnable, and no stdout/stderr reconfigure", err)

    def test_a_docs_page_naming_a_tool_that_does_not_ship_is_refused(self):
        """Guard (f). The docs hand the user six command lines and nothing read them.

        prose_sources() gained `docs/*.md`; check_prose_claims()'s own source list deliberately
        did NOT. The two ask different questions: this one asks whether every `python …x.py`
        names something the user has, and that one treats zero `n/m` matches in a source as a
        defect. docs/ carries no `n/m` by choice, so adding it there would fire
        "states no claim at all" on the first run and force a number into prose that reads
        better without one.
        """
        edit(self.tmp, "docs/how-it-works.md",
             lambda t: t.replace("06_tools/check_links.py", "06_tools/check_link.py"))
        code, out, err = run_check(self.tmp)
        self.assertNotEqual(code, 0, f"a docs page naming a missing tool passed: {out}")
        self.assertIn("check_link.py", err)
        self.assertIn("docs/how-it-works.md", err)

    def test_the_docs_are_not_read_for_number_claims(self):
        """The other half of guard (f), and the reason it is a half at all.

        If docs/ ever reached check_prose_claims()'s source list, the zero-matches branch would
        fire immediately -- that branch exists because a claim a pattern stopped seeing looks
        exactly like a claim that agrees. Asserted as a property of the pages rather than of the
        code: as long as they carry no `n/m`, the separation is load-bearing and someone tidying
        the two lists together will find out here rather than in a delivered file.
        """
        for page in sorted((self.tmp / "docs").glob("*.md")):
            text = page.read_text(encoding="utf-8")
            for pattern, what in build_kit.CLAIMS:
                self.assertEqual(
                    re.findall(pattern, text), [],
                    f"{page.name} now states a {what} claim. Either it belongs in "
                    f"check_prose_claims()'s sources -- and then every docs page needs every "
                    f"claim -- or the number belongs out of the page.")

    # ------------------------------------------- the chain, not the numbers in it (#19)

    def test_a_tool_whose_command_line_is_deleted_falls_out_of_the_chain(self):
        """The sentence from #19's body, as a test: "Delete a command line from SECTION 8 and
        every run stays green."

        check_prose_claims() guards three number patterns; the command lines carry no numbers, so
        nothing read them. The freshness step was added to SECTION 8 on 2026-07-30 and its removal
        would have gone unnoticed by every run in this repository.

        The mutation happens against a COPY in a temp directory, never the working tree -- a
        recipe someone runs by hand on src/contract.md leaves the contract edited when it crashes.

        Undo recipe: delete the `orphans` block from check_prose_chain(). This case and the
        TOOLS_ORDER one below go green with the tool missing from the chain, and --check exits 0
        over a contract that never mentions it.

        Since 2026-07-31 the docs pages are a chain source too, so the line has to go from both
        or the tool is still commanded. That is one statement -- "nothing tells the user to run
        it" -- written in the two places that tell the user anything, not two defects.
        """
        edit(self.tmp, "src/contract.md",
             lambda t: re.sub(r"^python 06_tools/check_freshness\.py.*\n", "", t, flags=re.M))
        edit(self.tmp, "docs/how-it-works.md",
             lambda t: re.sub(r"^python .*check_freshness\.py.*\n", "", t, flags=re.M))
        code, out, err = run_check(self.tmp)
        self.assertNotEqual(code, 0, f"a tool nothing runs passed: {out}")
        self.assertIn("check_freshness.py: ships, and no command line runs it", err)

    def test_a_misspelled_tool_in_a_command_line_is_refused(self):
        """Direction one, and the cheap half: the user types the line and gets an error.

        Undo recipe: delete the `ghosts` block from check_prose_chain(). The contract then tells
        the user to run a file that was never delivered, and every run stays green -- which is
        how `check_duplicates --vault <Project>` prescribed the call that created a ghost folder,
        found by a cold run rather than by a check.
        """
        edit(self.tmp, "src/contract.md",
             lambda t: t.replace("python 06_tools/check_links.py", "python 06_tools/check_link.py"))
        code, out, err = run_check(self.tmp)
        self.assertNotEqual(code, 0, f"a command naming a missing tool passed: {out}")
        self.assertIn("check_link.py", err)
        self.assertIn("not delivered", err)

    def test_a_new_tool_in_no_chain_and_no_list_is_refused(self):
        """The case that actually happens the next time somebody writes a tool.

        Both other directions need a mistake in existing text. This one needs only a addition
        that is correct in itself: the tool ships, its block is embedded, it runs -- and it sits
        in the user's folder with nothing ever calling it, indistinguishable from a leftover.
        `count_tokens.py` was in exactly this state on 2026-07-30 and no run said so.

        Undo recipe: same as the deleted-command case -- drop the `orphans` block.
        """
        (self.tmp / "tools" / "neues_werkzeug.py").write_text(
            'import sys\n\nfor _stream in (sys.stdout, sys.stderr):\n    try:\n'
            '        _stream.reconfigure(encoding="utf-8", errors="replace")\n'
            '    except (AttributeError, ValueError):\n        pass\n\n\n'
            'if __name__ == "__main__":\n    print("ships, and nothing calls it")\n',
            encoding="utf-8", newline="\n")
        # The stream block and the SUITE_EXEMPT line are here so this fixture keeps testing what
        # it says. Since 2026-07-31 a delivered script without either is refused by an earlier
        # guard, and the run would then be red about the fixture rather than about the chain.
        # Exempt rather than given a suite on purpose: a suite file would move the counted number
        # and make check_prose_claims() fire first instead.
        edit(self.tmp, "tools/build_kit.py",
             lambda t: t.replace("SUITE_EXEMPT = {}",
                                 'SUITE_EXEMPT = {"neues_werkzeug.py": "a fixture"}', 1))
        edit(self.tmp, "tools/build_kit.py",
             lambda t: t.replace('"count_tokens.py"]', '"count_tokens.py", "neues_werkzeug.py"]', 1))
        code, out, err = run_check(self.tmp)
        self.assertNotEqual(code, 0, f"an uncalled new tool passed: {out}")
        self.assertIn("neues_werkzeug.py: ships, and no command line runs it", err)
        self.assertIn("not_invoked", err, "the message did not name the way out")

    def test_a_tool_both_called_and_declared_uncalled_stops_with_exit_2(self):
        """Exit 2, and deliberately not a winner.

        Copied from check_freshness.py's watched/on-demand rule rather than invented: whichever
        statement lost would sit in the file doing nothing, and no run could show which of the two
        applies. The exit code is distinct from 1 on purpose -- a contradiction between two
        sources is a different repair from a stale line in one of them.

        Undo recipe: return 1 instead of 2 from the `both` block. This case is the only one that
        moves, and a reader then cannot tell the two repairs apart from the exit code.
        """
        # The same entry goes into jobs.json AND into check_freshness.py's copy of it. That is
        # one statement written in the two places the kit requires it, not two defects: since
        # 2026-07-31 check_jobs_config_matches_code() runs first, and editing only the file would
        # make this case red about the drift instead of about the contradiction.
        edit(self.tmp, "tools/jobs.json",
             lambda t: t.replace('"not_invoked": {',
                                 '"not_invoked": {\n    "check_links": "widerspruch",', 1))
        edit(self.tmp, "tools/check_freshness.py",
             lambda t: t.replace("DEFAULT_NOT_INVOKED = {",
                                 'DEFAULT_NOT_INVOKED = {\n    "check_links": "widerspruch",', 1))
        code, out, err = run_check(self.tmp)
        self.assertEqual(code, 2, f"a name classified twice did not stop the run: {out}\n{err}")
        self.assertIn("check_links.py", err)
        self.assertIn("classified twice", err)

    def test_the_section_10_header_no_longer_carries_a_command_line(self):
        """A pin over an absence, and the absence is what makes another test impossible.

        Until 2026-07-31 the header was the ONLY source naming `verify_setup.py` -- it appears
        in src/contract.md zero times, measured 2026-07-30 -- and that made it provable that
        check_prose_chain() reads the header and not just the contract. E3 took the suites and
        the drivers out of the delivery, so the header stopped telling anyone to run anything:
        it now says write the blocks, compile them, check the encoding. No `python x.py` at all.

        The header stays in prose_sources() so a line added later is checked like any other. This
        assertion is what tells you that day has arrived -- and on that day, write a real chain
        case for it instead of relaxing this one. Until then, the source that proves the chain
        reads more than the contract is `docs/`, in the misspelling case above.
        """
        self.assertEqual(
            build_kit.COMMAND_RE.findall(build_kit.HEADER), [],
            "the SECTION 10 header names a script to run again. That is allowed -- but nothing "
            "proves the chain check reads it any more, so add a case that removes the line and "
            "requires the tool to be reported as uninvoked.")

    def test_a_literal_version_stamp_in_the_prose_is_refused(self):
        """A second kit-version line in the text goes stale on the next build, and a reader
        comparing copies cannot tell which of the two is the real one."""
        edit(self.tmp, "src/contract.md",
             lambda t: t + "\n<!-- kit-version: 0123456789ab -->\n")
        code, out, err = run_check(self.tmp)
        self.assertNotEqual(code, 0, f"a quoted stamp passed: {out}")
        self.assertIn("0123456789ab", err)


if __name__ == "__main__":
    unittest.main(verbosity=1)
