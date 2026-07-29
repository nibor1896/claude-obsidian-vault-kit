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
    """A throwaway copy of the repository, complete enough for build_kit.py to run in."""
    tmp = Path(tempfile.mkdtemp(prefix="vaultkit_buildkit_"))
    shutil.copytree(HERE, tmp / "tools", ignore=shutil.ignore_patterns("__pycache__"))
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

    def test_a_suite_whose_tool_is_not_delivered_does_not_deliver_itself(self):
        """Three lists governed one question and none of them knew the others.

        SHARED/TOOLS_ORDER/DRIVERS are maintained by hand; the suites used to be picked up by a
        bare glob. So writing `test_anything.py` in this folder shipped it to every user, whether
        or not the tool it tests goes with it -- a permanent prop in their `n/m`, testing
        something their vault does not have. This file is that case: it tests the generator.
        """
        (self.tmp / "tools" / "test_dummy.py").write_text(
            "print('a suite for a tool nobody ships')\n", encoding="utf-8", newline="\n")
        before = (self.tmp / "claude-obsidian-vault-kit.md").read_text(encoding="utf-8")

        code, out, err = run_check(self.tmp)
        self.assertEqual(code, 0, f"an undelivered suite moved the counted number:\n{out}\n{err}")

        code, out, err = run_build(self.tmp)
        self.assertEqual(code, 0, err)
        after = (self.tmp / "claude-obsidian-vault-kit.md").read_text(encoding="utf-8")
        self.assertNotIn("test_dummy.py", after, "a suite delivered itself")
        self.assertEqual(before, after, "the delivered file changed over a file nobody ships")

    def test_a_tool_leaving_the_delivery_takes_its_suite_and_the_count_with_it(self):
        """The other direction, and the one that has to be loud.

        Dropping a tool from the delivery silently drops its suite too. The number the user is
        promised then describes a folder that no longer exists, so the prose has to go red --
        in every source at once, which is what says "the tool left" rather than "the prose rotted".
        """
        edit(self.tmp, "tools/build_kit.py", lambda t: t.replace('"count_tokens.py", ', "", 1))
        code, out, err = run_check(self.tmp)
        self.assertNotEqual(code, 0, f"a shrunken delivery passed: {out}")
        # Counted from the delivery list, never typed: this number moves whenever a tool does.
        self.assertIn(f"counted {len(build_kit.delivered_suites()) - 1}", err)
        for source in ("src/contract.md", "tools/build_kit.py", "README.md"):
            self.assertIn(source, err, "only some sources noticed the tool leaving")

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
