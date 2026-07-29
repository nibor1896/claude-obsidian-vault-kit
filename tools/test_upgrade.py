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
        kit = kit_file(self.tmp / "kit.md", {"build_index.py": "print('old')"})
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


if __name__ == "__main__":
    unittest.main(verbosity=1)
