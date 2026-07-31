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


def write_manifest(tools_dir, names):
    """The file list a kit leaves beside its stamp. Written by `--stamp` and by `--apply`."""
    (Path(tools_dir) / "kit-manifest.txt").write_text(
        "".join(f"{n}\n" for n in sorted(names)), encoding="utf-8", newline="\n")


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

    def test_stamp_records_the_version_without_touching_a_script(self):
        """The first install's only writer. Nothing else puts a version beside a fresh folder.

        `--apply` above covers the second kit onwards. Until --stamp existed, the first one was
        covered by nobody: the contract told the agent to type the twelve characters by hand,
        and verify_setup's step 13 read back a value its own fixture had written.

        It writes kit-manifest.txt as well -- covered on its own further down. What is asserted
        here is the other half: neither of those two files is a script, and no script moves.
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
        self.assertFalse((self.tools / "kit-manifest.txt").exists(),
                         "a refused stamp still recorded a file list, which would then be "
                         "trusted for removal against a version nobody knows")
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
        target with `encoding="utf-8"` again. test_upgrade 32/34 -- this case fails with
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

    # --------------------------------- a file the new kit no longer carries (the manifest)

    def test_a_file_the_new_kit_no_longer_carries_is_removed(self):
        """Without this the whole delivery can shrink and the user's folder never does.

        `classify()` returned three lists -- same, changed, added -- so a script that left the
        kit simply stayed on disk forever. That is not cosmetic: `run_suites.py` collects suites
        with a bare `sorted(tools.glob("test_*.py"))`, so an orphaned `test_x.py` whose tool is
        gone gets collected too. Measured directly on this machine 2026-07-31 -- one orphaned
        suite in an otherwise empty tool folder gives `0/1 suites green`, exit 1, with
        ModuleNotFoundError in the listing. The user's vault then reports red for good over a
        tool that no longer exists, and nothing in their folder explains why.

        Undo recipe, measured on this machine 2026-07-31: force `removed = []` in upgrade.py's
        classify(), replacing the conditional expression. test_upgrade 29/34 -- this case, the
        cached-bytecode one, the already-gone one and the dry-run listing. The orphan then sits
        in the folder after --apply, which is the state before this change and the reason for it.
        """
        (self.tools / "test_alt.py").write_text("raise SystemExit(0)\n",
                                                encoding="utf-8", newline="\n")
        write_manifest(self.tools, ["build_index.py", "test_alt.py"])
        kit = kit_file(self.tmp / "kit.md", {"build_index.py": "print('new')"},
                       version="abcdef012345")

        code, out, err = run_upgrade(self.tools, kit, "--apply")
        self.assertIn("remove     test_alt.py", out)
        self.assertFalse((self.tools / "test_alt.py").exists(),
                         f"the orphan survived the update:\n{out}\n{err}")
        self.assertEqual((self.tools / "build_index.py").read_text(encoding="utf-8"),
                         "print('new')\n")
        self.assertEqual((self.tools / "kit-manifest.txt").read_text(encoding="utf-8"),
                         "build_index.py\n", "the manifest still lists the file it just removed")

    def test_a_file_the_kit_never_delivered_is_never_removed(self):
        """The user's own tools live in the same folder, and this is what keeps them there.

        The subtraction is `manifest - blocks`, never `folder - blocks`. A tool the user wrote,
        a `runs.log`, a `jobs.json` they extended by hand: none of them are in the manifest, so
        none of them are candidates. Get this wrong once and an update deletes work this kit
        never wrote and cannot restore.

        Undo recipe, measured on this machine 2026-07-31: in classify(), take `removed` from the
        folder instead of the manifest --
        `sorted(p.name for p in TOOLS.glob("*.py") if p.name not in blocks and p.name != SELF)`.
        test_upgrade 31/34. Three cases move, and they are worth reading together: this one
        (the user's files are deleted), the no-manifest one (a folder that must not be touched
        at all is touched) and the already-gone one (the manifest stops driving anything). The
        folder and the manifest answer different questions, and the recipe makes the run answer
        the wrong one everywhere at once.
        """
        (self.tools / "test_eigene_suite.py").write_text("# mine, not the kit's\n",
                                                  encoding="utf-8", newline="\n")
        (self.tools / "eigenes_werkzeug.py").write_text("# also mine\n",
                                                        encoding="utf-8", newline="\n")
        write_manifest(self.tools, ["build_index.py"])
        kit = kit_file(self.tmp / "kit.md", {"build_index.py": "print('new')"},
                       version="abcdef012345")

        code, out, err = run_upgrade(self.tools, kit, "--apply")
        self.assertTrue((self.tools / "test_eigene_suite.py").is_file(),
                        f"a file the kit never delivered was removed:\n{out}\n{err}")
        self.assertTrue((self.tools / "eigenes_werkzeug.py").is_file(),
                        f"a file the kit never delivered was removed:\n{out}\n{err}")
        self.assertIn("0 would be removed", out)
        self.assertNotIn("  remove     ", out)

    def test_upgrade_itself_is_never_removed(self):
        """A kit that stops shipping upgrade.py must not take the repair tool with it.

        It is delivered like every other script, so it is in the manifest, so the plain
        subtraction would list it -- and the run would delete the only thing that can be run
        again after a failed update. Named as its own case because the guard is one comparison
        that reads like a detail.
        """
        write_manifest(self.tools, ["build_index.py", "upgrade.py"])
        kit = kit_file(self.tmp / "kit.md", {"build_index.py": "print('new')"},
                       version="abcdef012345")

        code, out, err = run_upgrade(self.tools, kit, "--apply")
        self.assertTrue((self.tools / "upgrade.py").is_file(),
                        f"the updater deleted itself:\n{out}\n{err}")
        self.assertNotIn("remove     upgrade.py", out)

    def test_without_a_manifest_nothing_is_removed_and_the_run_says_why(self):
        """A folder installed by an older kit has no file list, and guessing is not allowed.

        Every folder installed before the manifest existed is in this state. The tool cannot
        know what that older kit delivered, so it removes nothing, prints the reason, and
        records a manifest on the way out. Exactly one update cycle is blind; the one after it
        can act. Silence here would be the worst of the three options -- it looks identical to
        "there was nothing to remove".
        """
        (self.tools / "test_alt.py").write_text("raise SystemExit(0)\n",
                                                encoding="utf-8", newline="\n")
        kit = kit_file(self.tmp / "kit.md", {"build_index.py": "print('new')"},
                       version="abcdef012345")

        code, out, err = run_upgrade(self.tools, kit)
        self.assertIn("0 would be removed", out)
        self.assertIn("kit-manifest.txt", out)
        self.assertTrue((self.tools / "test_alt.py").is_file())
        self.assertFalse((self.tools / "kit-manifest.txt").exists(),
                         "a manifest was written without --apply")

        run_upgrade(self.tools, kit, "--apply")
        self.assertEqual((self.tools / "kit-manifest.txt").read_text(encoding="utf-8"),
                         "build_index.py\n",
                         "the blind cycle did not end -- the next update is blind too")

    def test_a_dry_run_names_what_would_be_removed_and_removes_nothing(self):
        """"Nothing is written without --apply" has to cover deleting, or it is half a promise."""
        (self.tools / "test_alt.py").write_text("raise SystemExit(0)\n",
                                                encoding="utf-8", newline="\n")
        write_manifest(self.tools, ["build_index.py", "test_alt.py"])
        kit = kit_file(self.tmp / "kit.md", {"build_index.py": "print('old')"},
                       version="abcdef012345")

        code, out, err = run_upgrade(self.tools, kit)
        self.assertEqual(code, 0, out + err)
        self.assertIn("1 would be removed", out)
        self.assertIn("remove     test_alt.py", out)
        self.assertIn("nothing removed", out)
        self.assertTrue((self.tools / "test_alt.py").is_file(),
                        "a dry run deleted a file")

    def test_the_cached_bytecode_of_a_removed_file_goes_with_it(self):
        """A .pyc with no .py beside it is something a user finds and cannot explain.

        Hygiene rather than correctness -- Python 3 will not import a __pycache__ entry whose
        source is gone -- but a folder this kit maintains should not leave debris it created.
        """
        (self.tools / "test_alt.py").write_text("raise SystemExit(0)\n",
                                                encoding="utf-8", newline="\n")
        cache = self.tools / "__pycache__"
        cache.mkdir()
        stale = cache / "test_alt.cpython-313.pyc"
        stale.write_bytes(b"not really bytecode")
        (cache / "build_index.cpython-313.pyc").write_bytes(b"stays")
        write_manifest(self.tools, ["build_index.py", "test_alt.py"])
        kit = kit_file(self.tmp / "kit.md", {"build_index.py": "print('new')"},
                       version="abcdef012345")

        run_upgrade(self.tools, kit, "--apply")
        self.assertFalse(stale.exists(), "the cached bytecode outlived its source")
        self.assertTrue((cache / "build_index.cpython-313.pyc").is_file(),
                        "the sweep took a cache entry whose source is still delivered")

    def test_a_manifest_naming_a_file_that_is_already_gone_still_completes(self):
        """The half-state an update leaves if it dies between the delete and the manifest write.

        Constructed directly rather than by killing a run: a manifest listing a file that is not
        on disk IS that state, and building it this way is deterministic on every platform.

        The next run has to walk over it -- `unlink(missing_ok=True)` is the no-op that lets it
        -- rewrite the manifest and finish. Without that, the folder would stay half-updated
        forever, because the stale manifest is also the only record that says something is
        missing.
        """
        write_manifest(self.tools, ["build_index.py", "test_schon_weg.py"])
        self.assertFalse((self.tools / "test_schon_weg.py").exists())
        kit = kit_file(self.tmp / "kit.md", {"build_index.py": "print('new')"},
                       version="abcdef012345")

        code, out, err = run_upgrade(self.tools, kit, "--apply")
        self.assertIn("already gone", out)
        self.assertNotIn("Traceback", err)
        self.assertEqual((self.tools / "kit-manifest.txt").read_text(encoding="utf-8"),
                         "build_index.py\n",
                         "the manifest still names a file nothing will ever look for again")
        self.assertEqual((self.tools / "kit-version.txt").read_text(encoding="utf-8").strip(),
                         "abcdef012345")

    def test_nothing_is_removed_when_a_write_in_the_same_run_was_refused(self):
        """Abort before deleting: the folder still has everything it started with.

        A run that deleted a script to make room for one that never landed is the single state
        the write-then-read-then-delete order exists to prevent. The refused write is a block
        whose heading carries a directory that does not exist, so it fails for every user on
        every platform, no permissions involved.

        The stamp did not move either, which is the other half: nothing tells the next run the
        work is done, so it recomputes the identical plan.
        """
        (self.tools / "test_alt.py").write_text("raise SystemExit(0)\n",
                                                encoding="utf-8", newline="\n")
        write_manifest(self.tools, ["build_index.py", "test_alt.py"])
        kit = kit_file(self.tmp / "kit.md",
                       {"build_index.py": "print('new')", "aaa_kein_ordner/neu.py": "x = 1"},
                       version="abcdef012345")

        code, out, err = run_upgrade(self.tools, kit, "--apply")
        self.assertEqual(code, 2, out + err)
        self.assertTrue((self.tools / "test_alt.py").is_file(),
                        "a file was deleted although a write in the same run was refused")
        self.assertFalse((self.tools / "kit-version.txt").exists(),
                         "the run stamped a folder it had not finished")
        self.assertEqual((self.tools / "kit-manifest.txt").read_text(encoding="utf-8"),
                         "build_index.py\ntest_alt.py\n",
                         "the manifest moved on a run that did not finish")

    def test_a_file_that_cannot_be_removed_keeps_the_manifest_where_it_is(self):
        """The manifest must never say a file is gone while it is still there.

        If it did, the name would drop out of the list and nothing would ever try again -- the
        leftover becomes permanent and invisible in one step. So a refused removal fails the run
        and leaves the old manifest, which is what makes the next --apply retry it.

        The fixture is a directory where the file belongs: `unlink()` raises for every user on
        every platform.
        """
        (self.tools / "test_alt.py").mkdir()
        write_manifest(self.tools, ["build_index.py", "test_alt.py"])
        kit = kit_file(self.tmp / "kit.md", {"build_index.py": "print('new')"},
                       version="abcdef012345")

        code, out, err = run_upgrade(self.tools, kit, "--apply")
        self.assertEqual(code, 2, out + err)
        self.assertNotIn("Traceback", err)
        self.assertIn("test_alt.py", err)
        self.assertEqual((self.tools / "kit-manifest.txt").read_text(encoding="utf-8"),
                         "build_index.py\ntest_alt.py\n",
                         "the manifest dropped a name whose file is still on disk")
        self.assertFalse((self.tools / "kit-version.txt").exists(),
                         "the run stamped a folder it had not finished")

    def test_stamp_records_the_file_list_as_well_as_the_version(self):
        """The first install's only writer, and it has to record both or the first update is blind.

        The kit file in the user's hand already lists everything it delivers, one fenced block
        per file. Waiting for the first `--apply` to write that down would cost every fresh
        install one update cycle in which nothing can be removed.
        """
        kit = kit_file(self.tmp / "kit.md",
                       {"build_index.py": "print('old')", "check_links.py": "print('tool')"},
                       version="0f1e2d3c4b5a")
        code, out, err = run_upgrade(self.tools, "--stamp", kit)
        self.assertEqual(code, 0, out + err)
        self.assertEqual((self.tools / "kit-manifest.txt").read_text(encoding="utf-8"),
                         "build_index.py\ncheck_links.py\n")
        self.assertIn("kit-manifest.txt", out)

    def test_a_kit_file_with_no_blocks_records_no_file_list(self):
        """An empty delivery is not the same statement as no delivery.

        A stand-in kit file -- a fragment, a stamp carrier -- has no blocks. Recording an empty
        manifest from it would say "this kit brought no files", and every file in the folder
        would then look like the user's own forever. It leaves the manifest alone instead.
        """
        kit = self.tmp / "nur-ein-stempel.md"
        kit.write_text("<!-- kit-version: 0f1e2d3c4b5a -->\n\n# Kit\n",
                       encoding="utf-8", newline="\n")
        code, out, err = run_upgrade(self.tools, "--stamp", kit)
        self.assertEqual(code, 0, out + err)
        self.assertEqual((self.tools / "kit-version.txt").read_text(encoding="utf-8").strip(),
                         "0f1e2d3c4b5a")
        self.assertFalse((self.tools / "kit-manifest.txt").exists(),
                         "a kit with no blocks recorded an empty delivery")

    # ------------------------------------- checking a folder that has no suites in it

    def test_prove_checks_the_folder_as_it_stands(self):
        """`--prove` is what replaced running the suites here, and it has to be usable alone.

        The suites moved to the kit's repository, so a folder can no longer show that its guards
        go red on bad input. What it can still show is that every script is whole -- it compiles
        -- and that the one non-Python file parses. A truncated write lands there, and so does a
        block that never arrived.
        """
        # A real tool folder always has one -- it is a delivered block -- and --prove is right to
        # insist. The sandbox is otherwise the two files setUp writes.
        (self.tools / "jobs.json").write_text('{"jobs": []}\n', encoding="utf-8", newline="\n")
        code, out, err = run_upgrade(self.tools, "--prove")
        self.assertEqual(code, 0, out + err)
        self.assertIn("compiles", out)
        self.assertIn("jobs.json", out + err)

    def test_prove_goes_red_on_a_script_that_does_not_compile(self):
        """The healthy control above proves it runs; this proves it can tell working from broken.

        Undo recipe: drop the returncode check from prove()'s compileall branch. This case then
        exits 0 over a folder holding a file Python cannot read.
        """
        (self.tools / "jobs.json").write_text('{"jobs": []}\n', encoding="utf-8", newline="\n")
        (self.tools / "kaputt.py").write_text("def (\n", encoding="utf-8", newline="\n")
        code, out, err = run_upgrade(self.tools, "--prove")
        self.assertNotEqual(code, 0, f"a folder with a broken script passed:\n{out}\n{err}")
        self.assertIn("FAIL", out + err)
        self.assertIn("compiles", out + err)

    def test_the_post_write_checks_run_from_the_code_that_was_just_written(self):
        """upgrade.py rewrites itself, and the running process keeps the code it started with.

        Measured on this machine 2026-07-31, crossing the release that moved the suites out of
        the delivery: the folder came out exactly right -- nine files, thirteen correctly removed
        -- and the run ended with `FAIL run_suites.py`, `FAIL acceptance.py` and
        "restore it from git", because the OLD prove() went looking for the two files the new kit
        had just correctly deleted. The worst possible advice, on a healthy folder.

        The fixture is a stub upgrade.py that prints a marker for any argument. If the marker is
        in the output, the checks were run by the code on disk rather than by the code in memory
        -- which is the whole claim.
        """
        stub = 'import sys\nprint("STUB PROVE MARKER")\nsys.exit(0)\n'
        kit = kit_file(self.tmp / "kit.md", {"upgrade.py": stub}, version="abcdef012345")
        code, out, err = run_upgrade(self.tools, kit, "--apply")
        self.assertEqual(code, 0, out + err)
        self.assertIn("STUB PROVE MARKER", out,
                      "the checks ran from the code in memory, not from the file just written")

    def test_an_updated_upgrade_without_prove_is_named_rather_than_called_broken(self):
        """Moving backwards to a kit older than `--prove` must not read as a failed update.

        argparse exits 2 with "unrecognized arguments" there. Treating that as a broken folder
        would tell a user to restore from git over an update that did exactly what it said.
        """
        stub = ('import sys\nprint("unrecognized arguments: --prove", file=sys.stderr)\n'
                'sys.exit(2)\n')
        kit = kit_file(self.tmp / "kit.md", {"upgrade.py": stub}, version="abcdef012345")
        code, out, err = run_upgrade(self.tools, kit, "--apply")
        self.assertEqual(code, 0, f"an older updater read as a broken folder:\n{out}\n{err}")
        self.assertIn("without --prove", err)
        self.assertIn("Nothing is wrong", err)

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

    def test_the_stamp_is_the_last_thing_written(self):
        """The stamp is what a later run reads to decide it is done, so it goes last on every
        path -- inside write_stamp() too, where the manifest is written before it.

        Written earlier, a run that died in between would tell the next one the work is
        finished while the folder is half old, and nothing would ever recompute the plan.

        The manifest path is a directory here, so the write fails for every user on every
        platform, no permissions involved. What is asserted is the order: the script landed,
        and the stamp did not.
        """
        (self.tools / "kit-manifest.txt").mkdir()
        kit = kit_file(self.tmp / "kit.md", {"build_index.py": "print('new')"},
                       version="abcdef012345")

        code, out, err = run_upgrade(self.tools, kit, "--apply")
        self.assertEqual(code, 2, out + err)
        self.assertNotIn("Traceback", err)
        self.assertEqual((self.tools / "build_index.py").read_text(encoding="utf-8"),
                         "print('new')\n", "the write did not happen before the stamp attempt")
        self.assertFalse((self.tools / "kit-version.txt").exists(),
                         "the stamp was written even though the manifest before it failed")

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

        Undo recipe, re-measured on this machine 2026-07-31: force `stale_stamp = False` in
        upgrade.py's main(), which is what returning early amounted to.
        test_upgrade 31/34 -- this case, the unstamped one and the --apply one -- and
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
