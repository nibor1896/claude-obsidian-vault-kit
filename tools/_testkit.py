"""Shared fixtures for the tool suites.

Deliberately NOT named test_*.py: run_suites.py collects by that glob and a helper module
with no tests would be counted as a green suite.
"""

import os
import subprocess
import sys
import tempfile
from pathlib import Path

TOOLS = Path(__file__).resolve().parent

# Imported, never respelled. A second copy of this list makes the fixtures agree with a tree
# the tools no longer build, and every suite stays green while doing it.
sys.path.insert(0, str(TOOLS))
from vaultkit import CATEGORY_FOLDERS  # noqa: E402


def make_vault(projects=("ProjektEins",)):
    """A throwaway vault with the real folder tree. Caller deletes the returned tempdir."""
    tmp = Path(tempfile.mkdtemp(prefix="vaultkit_")) / "Vault"
    for project in projects:
        for folder in CATEGORY_FOLDERS:
            (tmp / project / folder).mkdir(parents=True, exist_ok=True)
    (tmp / "00_Global" / "06_tools").mkdir(parents=True, exist_ok=True)
    return tmp


def write_note(path, title="Ein Titel", summary="Eine Zusammenfassung.", bom=False, **extra):
    """Write a note with frontmatter. Pass title=None or summary=None to omit the key.

    bom=True writes UTF-8 *with* a byte-order mark -- what Notepad and PowerShell 5.1's
    `Set-Content -Encoding utf8` produce, and what a user creating a note outside Obsidian
    on Windows gets by default.
    """
    lines = ["---"]
    if title is not None:
        lines.append(f'title: "{title}"')
    if summary is not None:
        lines.append(f'summary: "{summary}"')
    for key, value in extra.items():
        lines.append(f'{key}: "{value}"')
    lines += ["---", "", "Body text that the index generator must never read.", ""]
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8-sig" if bom else "utf-8", newline="\n")
    return path


def run_tool(script, *args, strip_io_encoding=True, home=None):
    """Run a tool as a real subprocess. Returns (returncode, stdout, stderr) as UTF-8 text.

    PYTHONIOENCODING is removed on purpose: the tools must force UTF-8 themselves, or the
    same suite goes green under PowerShell and red under Git Bash on one machine.

    `home` redirects what `Path.home()` resolves to inside the subprocess, which is the only way
    to test a tool that writes into the user's own config folder without writing into it. Both
    variables are set because Python reads USERPROFILE on Windows and HOME elsewhere; setting one
    on the wrong platform is a no-op that silently leaves the real folder in play.
    """
    env = dict(os.environ)
    env["PYTHONPATH"] = str(TOOLS) + os.pathsep + env.get("PYTHONPATH", "")
    if strip_io_encoding:
        env.pop("PYTHONIOENCODING", None)
        env.pop("PYTHONUTF8", None)
    if home is not None:
        env["USERPROFILE"] = str(home)
        env["HOME"] = str(home)
        env.pop("HOMEDRIVE", None)
        env.pop("HOMEPATH", None)
    result = subprocess.run(
        [sys.executable, str(TOOLS / script), *[str(a) for a in args]],
        cwd=str(TOOLS),
        env=env,
        capture_output=True,
    )
    return (
        result.returncode,
        result.stdout.decode("utf-8", errors="replace"),
        result.stderr.decode("utf-8", errors="replace"),
    )
