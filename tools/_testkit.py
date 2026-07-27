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

CATEGORY_FOLDERS = [
    "00_Notes",
    "01_Issues",
    "02_docs",
    "03_technical_docs",
    "04_feedback",
    "05_workflows",
    "06_tools",
]


def make_vault(projects=("ProjektEins",)):
    """A throwaway vault with the real folder tree. Caller deletes the returned tempdir."""
    tmp = Path(tempfile.mkdtemp(prefix="vaultkit_")) / "Vault"
    for project in projects:
        for folder in CATEGORY_FOLDERS:
            (tmp / project / folder).mkdir(parents=True, exist_ok=True)
    (tmp / "00_Global" / "06_tools").mkdir(parents=True, exist_ok=True)
    return tmp


def write_note(path, title="Ein Titel", summary="Eine Zusammenfassung.", **extra):
    """Write a note with frontmatter. Pass title=None or summary=None to omit the key."""
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
    path.write_text("\n".join(lines), encoding="utf-8", newline="\n")
    return path


def run_tool(script, *args, strip_io_encoding=True):
    """Run a tool as a real subprocess. Returns (returncode, stdout, stderr) as UTF-8 text.

    PYTHONIOENCODING is removed on purpose: the tools must force UTF-8 themselves, or the
    same suite goes green under PowerShell and red under Git Bash on one machine.
    """
    env = dict(os.environ)
    env["PYTHONPATH"] = str(TOOLS) + os.pathsep + env.get("PYTHONPATH", "")
    if strip_io_encoding:
        env.pop("PYTHONIOENCODING", None)
        env.pop("PYTHONUTF8", None)
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
