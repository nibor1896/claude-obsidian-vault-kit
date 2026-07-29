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

# The category folders every project gets when it is created. Numeric prefixes exist for sort
# order only; 01 is deliberately unused, closing the gap would rename every index file.
CATEGORY_FOLDERS = [
    "00_Notes",
    "02_docs",
    "03_technical_docs",
    "04_feedback",
    "05_workflows",
    "06_tools",
]

# The one directory at the vault root that is written by a tool and is still not a project: it
# holds one note template per project. Named with a leading underscore so it sorts above the
# projects in Obsidian's file pane.
TEMPLATES_DIR = "_templates"

# Directories that are never notes and never walked. _templates belongs here for two reasons at
# once: without it the folder becomes a project with six category folders of its own, and the
# templates inside would be read as notes and go red for having no summary.
#
# `.claude` is the agent's own configuration, the same class as `.obsidian`, and it holds the
# `/vaultkit` command write_command.py writes. Measured 2026-07-29 before it was listed: writing
# that one file took check_links.py from 26 files scanned to 27, check_duplicates.py from 4 notes
# to 5 and from 6 pairs to 10, and the generator from 26 distinct filenames to 27. Nothing went
# red -- the vault simply began counting its own configuration as knowledge, which is worse,
# because every denominator it reports is then slightly wrong and nobody has a reason to look.
SKIP_DIRS = {".git", ".obsidian", ".claude", "__pycache__", ".trash", ".venv", "node_modules",
             TEMPLATES_DIR}

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


def template_name(project_name: str) -> str:
    """'TEMPLATE - <Project>.md' — one note template per project.

    Same shape as the index filenames on purpose: they sort together in the file pane, and
    the name says which project the template writes into its `project:` line.
    """
    return f"TEMPLATE - {project_name}.md"


def template_text(project_name: str) -> str:
    """The four fields every note actually carries -- not the whole contract.

    `{{title}}` and `{{date}}` are two of the three variables Obsidian's core Templates plugin
    knows -- the third is `{{time}}` and has no field here. So the title comes from the filename
    (the convention is that the filename carries the title) and the date fills itself. Only
    `project:` is written in, which is the one value a template can get right that a person
    retyping the block gets wrong.

    WHY `updated`, `issues`, `generator`, `retired` and `stale` ARE NOT HERE: they are
    situational -- set when something happened, not when a note is started. `generator:` is the
    one that must never sit in a template waiting to be filled: a note carrying it is declared
    derived, and a rebuild is then entitled to overwrite or delete it. Nothing is hidden by
    leaving them out -- Obsidian's "Add property" offers every field already used anywhere in the
    vault. The CONTRACT (SECTION 4) still defines all nine; the template is not the contract.
    """
    return (
        "---\n"
        'title: "{{title}}"\n'
        "summary:\n"
        f'project: "{project_name}"\n'
        "created: {{date}}\n"
        "---\n"
    )


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
