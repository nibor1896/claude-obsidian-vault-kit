"""Single source of truth for every generated filename and every path rule.

Spelling a generated filename a second time in another tool is how a guard ends up
reporting the index hub as "missing" while the hub sits right next to it. Every tool
imports from here instead.
"""

import sys

for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass

import re
from pathlib import Path

# The category folders every project gets. Numeric prefixes exist for sort order only.
CATEGORY_FOLDERS = [
    "00_Notes",
    "01_Issues",
    "02_docs",
    "03_technical_docs",
    "04_feedback",
    "05_workflows",
    "06_tools",
]

# Directories that are never notes and never walked.
SKIP_DIRS = {".git", ".obsidian", "__pycache__", ".trash", ".venv", "node_modules"}

# Characters Obsidian cannot carry inside a [[wikilink]] target.
FORBIDDEN_LINK_CHARS = set("#[]|^")

# Append-only log of every tool run, healthy ones included. Read by check_freshness.py.
RUN_LOG_RELPATH = Path("00_Global") / "06_tools" / "runs.log"


def force_utf8():
    """Re-export of the stdout/stderr fix so tests can assert it exists."""
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass


def category_label(folder_name: str) -> str:
    """'03_technical_docs' -> 'technical_docs'. The prefix is sort order, not meaning."""
    return re.sub(r"^\d+_", "", folder_name)


def root_index_name(vault_root) -> str:
    """'INDEX - <VaultName>.md'.

    The name is derived from a RESOLVED path on purpose: Path('.').name is the empty
    string, so `--root .` would write '# — Index' while `--root C:/.../Vault` writes
    '# Vault — Index'. Two correct invocations must not produce a diff against each other.
    """
    return f"INDEX - {Path(vault_root).resolve().name}.md"


def project_index_name(project_dir) -> str:
    """'INDEX - <ProjectName>.md' — the project hub."""
    return f"INDEX - {Path(project_dir).resolve().name}.md"


def category_index_name(project_name: str, folder_name: str) -> str:
    """'INDEX - <Project> <Category>.md'.

    Every project has identically named folders. Without the project in the filename the
    graph shows one node called 'INDEX - Issues' per project and the quick switcher
    becomes a coin toss.
    """
    return f"INDEX - {project_name} {category_label(folder_name)}.md"


def is_index_file(path) -> bool:
    return Path(path).name.startswith("INDEX - ")


def project_dirs(vault_root):
    """Every project directory directly under the vault root, sorted."""
    root = Path(vault_root).resolve()
    out = []
    for child in sorted(root.iterdir()):
        if not child.is_dir():
            continue
        if child.name in SKIP_DIRS or child.name.startswith("."):
            continue
        out.append(child)
    return out


def walk_markdown(root):
    """Every .md file under root, skipping SKIP_DIRS. Sorted, so output is stable."""
    root = Path(root).resolve()
    found = []
    for path in root.rglob("*.md"):
        if any(part in SKIP_DIRS for part in path.relative_to(root).parts[:-1]):
            continue
        found.append(path)
    return sorted(found)


def has_forbidden_chars(name: str) -> bool:
    return any(ch in FORBIDDEN_LINK_CHARS for ch in name)


def log_run(vault_root, job: str, status: str, detail: str = ""):
    """Append one line per run, healthy ones included.

    Silence must mean 'did not run', never 'ran and was fine'.
    """
    from datetime import datetime, timezone

    log_path = Path(vault_root).resolve() / RUN_LOG_RELPATH
    try:
        log_path.parent.mkdir(parents=True, exist_ok=True)
        stamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S+00:00")
        line = f"{stamp}\t{job}\t{status}\t{detail}\n"
        with open(log_path, "a", encoding="utf-8") as fh:
            fh.write(line)
    except OSError as exc:
        print(f"run log not written: {exc}", file=sys.stderr)
