"""Every guard this vault runs, in one file: `vaultkit.py <subcommand> …`.

    vaultkit.py index      --root <VaultRoot> | --vault <Project>
    vaultkit.py links      --vault <VaultRoot>
    vaultkit.py duplicates --vault <VaultRoot>
    vaultkit.py freshness  --vault <VaultRoot>
    vaultkit.py tokens     <path> …
    vaultkit.py command    --vault <VaultRoot>

Each subcommand takes exactly the arguments the tool behind it always took and prints exactly
what it always printed. **The job names in `runs.log` do not move by a single byte** -- every
logging call passes a string literal, none of them changed, and `jobs.json` stays valid.

WHY ONE FILE (2026-07-31): a user's tool folder held twenty-two files, of which they were told
to run six. Every one of those was a separate block in the kit file a stranger drags into a
Claude conversation, and every block is context that conversation carries before it writes
anything. The measured cost of the split was never runtime -- it was the cold run.

The size was the open question and it is answered: a probe carrying this file's shape, 1683
lines and 68.6 KiB, went through a fresh session and came back byte-identical -- same sha256,
all 34 markers, no BOM, no CRLF. That is three times the largest block the old delivery had.

WHAT THIS FILE IS NOT ALLOWED TO SWALLOW. `upgrade.py` stays outside. If its own write breaks
off, it is the only tool left that can repeat the attempt, and folding it in here would make the
repair depend on the thing being repaired.

Read it in sections: the shared floor first -- every generated filename and the run log -- then
one section per subcommand, each opening with the tool's own documentation, unchanged from when
it was a file of its own. The register at the very end says which subcommand runs what.
"""

import sys

# BEFORE ANY WORK, AND BEFORE THE IMPORTS THAT WOULD SUCCEED ANYWAY (2026-07-31). The floor is
# 3.10 and it comes from exactly one thing: `Path.write_text(newline=…)`, used five times in
# this file. Below that version every one of those raises TypeError -- and it raises when the
# tool WRITES, not when it starts. For `index` that is after the whole note tree has been read
# and half the index rebuilt, with a message that says nothing about Python versions. A user
# would go looking at their notes.
#
# Checked here rather than in a function, because a function is something you can forget to call.
if sys.version_info < (3, 10):
    have = ".".join(str(part) for part in sys.version_info[:3])
    print(f"vaultkit.py needs Python 3.10 or newer; this is {have}. Nothing was read or "
          f"written. The floor is Path.write_text(newline=…), which every generated file goes "
          f"through -- on an older Python the first symptom would be a TypeError halfway "
          f"through a run, naming nothing that points here.", file=sys.stderr)
    # The literal, not EXIT_USAGE: this runs before the constants below are defined, and a
    # NameError here would replace the one message that explains what is wrong.
    raise SystemExit(2)

import argparse
import json
import re
from collections import defaultdict
from collections.abc import Callable
from datetime import date, datetime, timezone
from itertools import combinations
from pathlib import Path
from urllib.parse import quote

for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass

# The three verdicts, named once. Every subcommand returns one of them and `main()` hands it
# straight to the shell, so these are what a chain, a CI step or a `/vaultkit` run reads.
#
# THE MEANINGS, WRITTEN DOWN RATHER THAN INFERRED FROM EXAMPLES -- src/contract.md SECTION 6
# carries the same three sentences, because a user who has to derive them from thirty return
# statements will derive them differently:
#
#   0  clean. The check ran over a real population and found nothing wrong.
#   1  a defect, OR "did not run" -- the run could not reach a verdict. Both are "do not trust
#      this vault yet", and both are things the user fixes by changing notes or by running
#      something. `duplicates` is the one deliberate exception: too few notes to compare is the
#      normal state of a fresh vault, so it returns 0. That exception is in the contract.
#   2  the ARGUMENTS or the SOURCES are wrong, not the vault: an unknown subcommand, a path that
#      is not a directory, or two config lists that contradict each other. Nothing was measured,
#      so nothing about the vault is being claimed.
EXIT_OK = 0
EXIT_DEFECT = 1
EXIT_USAGE = 2

# THE ONE CONTRACT THAT CROSSES A FILE BOUNDARY, so it is the one thing here that is typed.
# `upgrade.py --prove` imports this module, reads COMMANDS and requires every `run` in it to be
# callable; that is the entire surface between the two delivered scripts. Everything else in
# this file has one caller a few hundred lines away, and a signature there states nothing two
# parties have to agree on.
#
# A handler takes the arguments left after the subcommand name -- `None` means "read sys.argv",
# the way argparse does it -- and returns one of the three exit codes above. Nothing else.
Handler = Callable[[list[str] | None], int]

# One entry per subcommand: what runs it, and the job name it writes into runs.log. `job` is
# `str | None`, and the None is a statement rather than a gap -- see the register at the end.
Command = dict[str, Handler | str | None]

# ---------------- shared: paths, names and the run log   (was vault_paths.py)
"""Single source of truth for every generated filename and every path rule.

Spelling a generated filename a second time in another tool is how a guard ends up
reporting the index hub as "missing" while the hub sits right next to it. Every tool
imports from here instead.
"""

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

# Append-only log of every tool run, healthy ones included. Read by `vaultkit.py freshness`.
RUN_LOG_RELPATH = Path("00_Global") / "06_tools" / "runs.log"


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


# The third outcome, spelled once. `pass` and `fail` are exit codes; this is the one a checker
# has to say in words, because "0 broken links" and "0 links looked at" are the same number.
#
# THE PHRASE IS LOAD-BEARING, NOT DECORATION. src/contract.md requires it, acceptance fixture 8
# greps for it, and four suites assert it. Changing the wording is a contract change and moves
# five sources at once -- which is exactly why it is a constant now and was four spellings
# before.
DID_NOT_RUN = "did not run"


def did_not_run(reason: str, stream=None) -> None:
    """Say that a check could not reach a verdict, and why. One wording, five callers.

    `stream` defaults to stderr, where every defect goes. `duplicates` passes stdout on purpose
    and is the only one that does: it is also the only caller that returns 0 afterwards -- too
    few notes to compare is the normal state of a fresh vault, not a defect -- so its line
    belongs with the denominators rather than with the failures. That asymmetry is asserted in
    two suites, one on `out` and three on `err`, so it cannot be tidied away by accident.

    `freshness` also says it once per job, in a different shape (`<job>: did not run — why`),
    and those two lines use DID_NOT_RUN directly rather than this function. MEASURED WHY THAT
    MATTERS, 2026-07-31: with the five headlines routed through here but those two still
    spelling the phrase out, acceptance stayed 12/12 when the wording was changed -- fixture 8
    was being satisfied by a per-job line, not by the headline it means to read. Consolidating
    five of seven spellings looks finished and leaves the guard reading the wrong one.
    """
    print(f"{DID_NOT_RUN}: {reason}", file=stream or sys.stderr)


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
        # newline="\n": the only writer in this kit that lacked it, so runs.log was the one
        # generated file whose line endings depended on the platform that wrote it. The reader
        # (the freshness check) opens in universal-newline mode and copes either way, which is
        # exactly why nothing went red over it -- a log half CRLF and half LF from two different
        # machines is a diff nobody can read, not a run that fails.
        with open(log_path, "a", encoding="utf-8", newline="\n") as fh:
            fh.write(line)
    except OSError as exc:
        print(f"run log not written: {exc}", file=sys.stderr)

# ----------------------------------- vaultkit.py index   (was build_index.py)
"""Generate the three-level index tree from note frontmatter.

    <VaultRoot>/INDEX - <VaultName>.md                   one line per project     --root
    <Project>/INDEX - <Project>.md                       one line per category    --vault <dir>
    <Project>/<Folder>/INDEX - <Project> <Category>.md   the entries themselves

Reads FRONTMATTER ONLY. There is no code path in this file that opens a note body, which
is the structural guarantee that prose can never leak into the index.

It also owns the shape of a project: a project folder that is missing category folders gets
them, and a folder the user made by hand becomes a category of its own. Both are printed --
they change the tree, and a run that changes the tree silently is the failure this whole
file exists to prevent. Neither is a defect.

Exit code is 0 only when every entry was clean. Otherwise each defect is printed as
"<filename>: <what is wrong>" on stderr and the exit code is non-zero.
"""

TITLE_MAX = 90
SUMMARY_MAX = 150

HEADER = """# {name} — Index

> Generated by `06_tools/vaultkit.py index` from note frontmatter.
> Do not edit by hand — changes belong in the note itself.
> As of: {today}
"""


class Defects:
    """Collects defects. A non-empty instance makes the run red."""

    def __init__(self):
        self.items = []
        self.skipped = 0

    def add(self, filename, message):
        self.items.append((str(filename), message))

    def report(self):
        for filename, message in self.items:
            print(f"{filename}: {message}", file=sys.stderr)

    def __len__(self):
        return len(self.items)


# --------------------------------------------------------------------------- frontmatter


def read_frontmatter(path, defects):
    """Return the frontmatter mapping of a note, or None if it has none.

    Stops reading at the closing '---'. Body lines are never collected, never returned.
    """
    data = {}
    try:
        # utf-8-sig, not utf-8: a byte-order mark survives str.strip() -- "﻿".isspace()
        # is False -- so the opening '---' of a note written by a Windows editor fails this
        # test. The note then reads as having no frontmatter at all: its title and summary
        # are gone from the index and the run goes red over a file the user wrote correctly.
        # utf-8-sig drops a BOM if there is one and behaves like utf-8 if there is not.
        with open(path, "r", encoding="utf-8-sig", errors="replace") as fh:
            first = fh.readline()
            if first.strip() != "---":
                return None
            for line in fh:
                if line.strip() in ("---", "..."):
                    return data
                key, sep, value = line.partition(":")
                if not sep:
                    continue
                key = key.strip()
                if not key or key.startswith("#"):
                    continue
                data[key] = _clean_scalar(value)
    except OSError as exc:
        # An error branch that continues is a lost denominator: count it, print it.
        defects.skipped += 1
        defects.add(Path(path).name, f"unreadable ({exc})")
        return None
    # File ended before the closing '---'.
    defects.add(Path(path).name, "frontmatter block is not closed by '---'")
    return data


def _clean_scalar(value):
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
        return value[1:-1].strip()
    # An unquoted '#' starts a YAML comment. A quoted one (issues: "#12") never reaches here.
    value = re.split(r"\s+#", value, maxsplit=1)[0]
    return value.strip()


MARKDOWN_DEBRIS = re.compile(r"^\s*(?:>+\s*|#{1,6}\s+|[-*+]\s+|\d+\.\s+)")


def clean_summary(raw):
    """Return (cleaned, was_dirty). Debris in summary renders the index line as garbage."""
    text = raw
    dirty = False
    while True:
        stripped = MARKDOWN_DEBRIS.sub("", text)
        if stripped == text:
            break
        text = stripped
        dirty = True
    for marker in ("**", "__", "`"):
        if marker in text:
            text = text.replace(marker, "")
            dirty = True
    if "\n" in text or "\r" in text:
        text = re.sub(r"[\r\n]+", " ", text)
        dirty = True
    collapsed = re.sub(r"\s{2,}", " ", text).strip()
    if collapsed != text.strip():
        dirty = True
    return collapsed, dirty


def truncate(text, limit):
    if len(text) <= limit:
        return text
    return text[: limit - 1].rstrip() + "…"


# --------------------------------------------------------------------------- links


def link_to(vault_root, target_path, label, defects):
    """A [[wikilink]] where Obsidian can resolve one, a markdown link where it cannot.

    The link checker resolves [[...]] and deliberately does not resolve [text](path).
    So every fallback to a markdown link is a defect in the filename, not a workaround.
    """
    name = Path(target_path).name
    try:
        rel = Path(target_path).resolve().relative_to(Path(vault_root).resolve()).as_posix()
    except ValueError:
        # A junction or symlink inside the vault whose target resolves outside the root.
        # relative_to() raises there, and this used to leave the function as a traceback -- so
        # the run died before log_run() at the end of index_main(), which is the one outcome this kit
        # forbids: silence has to mean "did not run". There is no link to write either way (a
        # [[wikilink]] needs a vault-relative path and there is none), so the label goes in as
        # plain text and the defect line carries the reason.
        defects.add(name, "resolves outside the vault root — not linkable "
                          "(a junction or symlink pointing out of the vault?)")
        return label
    if has_forbidden_chars(name):
        defects.add(name, "filename contains one of # [ ] | ^ — cannot be wikilinked")
        return f"[{label}]({quote(rel)})"
    if not name.lower().endswith(".md"):
        # Obsidian does not index these; a [[tool.py]] would be permanently unresolved.
        return f"[{label}]({quote(rel)})"
    return f"[[{rel[:-3]}|{label}]]"


# --------------------------------------------------------------------------- entries


def collect_entries(vault_root, project_dir, folder_name, defects):
    """One entry dict per note in <project>/<folder>. Frontmatter only."""
    folder = Path(project_dir) / folder_name
    entries = []
    if not folder.is_dir():
        return entries
    # Resolved once, not per note: Path('.').name is the empty string, and every note in the
    # folder would then be reported as disagreeing with a project called "".
    project_name = Path(project_dir).resolve().name
    for path in sorted(folder.glob("*.md")):
        if is_index_file(path):
            continue
        fm = read_frontmatter(path, defects)
        name = path.name
        if fm is None:
            defects.add(name, "no frontmatter block")
            fm = {}

        title = fm.get("title", "").strip()
        if not title:
            defects.add(name, "missing 'title:' — index falls back to the filename")
            title = path.stem

        summary_raw = fm.get("summary", "").strip()
        if not summary_raw:
            defects.add(name, "missing 'summary:'")
        summary, dirty = clean_summary(summary_raw)
        if dirty:
            defects.add(name, "markdown debris in 'summary:' — stripped for the index")
        if summary and summary.strip().lower() == title.strip().lower():
            summary = ""

        # 'project:' is advisory -- the folder decides where a note is indexed, and nothing here
        # reads this field to place anything. Absent, it means nothing and stays silent. Present
        # and disagreeing, it is two sources claiming different things while only one of them
        # acts, which is the defect: the note is indexed under the folder and the frontmatter
        # says otherwise, forever, with no message. Compared exactly, case included -- the folder
        # name IS the project name and goes into every wikilink as it stands.
        declared = fm.get("project", "").strip()
        if declared and declared != project_name:
            defects.add(name, f"'project: {declared}' disagrees with the folder "
                              f"({project_name}) — the folder decides where a note is indexed")

        prefixes = []
        if fm.get("retired"):
            prefixes.append(f"[retired: {fm['retired']}]")
        if fm.get("stale"):
            prefixes.append(f"[stale since {fm['stale']}]")
        if prefixes:
            summary = " ".join(prefixes) + (f" {summary}" if summary else "")

        entries.append(
            {
                "path": path,
                "title": truncate(title, TITLE_MAX),
                "summary": truncate(summary, SUMMARY_MAX),
                "date": fm.get("updated") or fm.get("created") or "",
                "issues": fm.get("issues", ""),
                "generated": bool(fm.get("generator")),
            }
        )
    return entries


def entry_line(vault_root, entry, defects):
    parts = [f"- {link_to(vault_root, entry['path'], entry['title'], defects)}"]
    tail = []
    if entry["summary"]:
        tail.append(entry["summary"])
    if entry["date"]:
        tail.append(str(entry["date"]))
    if entry["issues"]:
        tail.append(str(entry["issues"]))
    if entry["generated"]:
        tail.append("generated")
    if tail:
        parts.append("— " + " · ".join(tail))
    return " ".join(parts)


# --------------------------------------------------------------------------- writing


def write_if_changed(path, content, defects):
    """Write only on a real change, so a rerun leaves `git status` empty.

    THE WRITE IS INSIDE A try, AND THAT IS THE WHOLE POINT (2026-07-31). It used to sit outside
    one, so a read-only or locked INDEX file -- a vault on OneDrive is not a theoretical case --
    raised PermissionError out of here and took the run down BEFORE log_run() at the end of
    index_main(). The result was half an index tree AND not one line in runs.log: not `defects`, not
    `did-not-run`, nothing at all. Silence is the one thing that has to keep meaning "did not
    run", and a crash on the way to the log turns it into a lie.

    Two try blocks, not one, and the split is deliberate: a file that cannot be READ may still be
    writable, and overwriting it is the repair. Merging them would turn that case into a defect
    and skip the write that would have fixed it.

    Measured on this machine 2026-07-31, on a copy of a real vault (491 .md), with `attrib +R` on
    `Horus-F5Tts-Onnx/00_Notes/INDEX - Horus-F5Tts-Onnx Notes.md` -- the third project of seven,
    so most of the tree comes before it:

      before   PermissionError traceback · 46 of 61 index files written · runs.log absent
      after    exit 1 · the filename on stderr · 61 of 61 written · `build_index defects` logged
      unlock   `attrib -R`, rerun: exit 0, tree complete
      again    third run writes nothing, `git status` stays empty

    The reset path is the point of quoting the numbers: `attrib -R` on the same file puts the
    copy back, so anyone can rerun this without guessing what state it left behind.
    """
    path = Path(path)
    try:
        if path.exists() and path.read_text(encoding="utf-8") == content:
            return False
    except OSError:
        # Unreadable, possibly writable. Fall through to the write, which is the repair.
        pass
    try:
        path.write_text(content, encoding="utf-8", newline="\n")
    except OSError as exc:
        defects.add(path.name, f"not written ({exc})")
        return False
    return True


def scaffold(project_dir, defects):
    """Create the category folders this project is missing. Returns the names created.

    A project folder a user makes in the file pane is empty. Leaving it that way means the
    user has to know the six names and type them correctly before anything they write is
    indexed -- so the run creates them instead, and says which ones it made.
    """
    created = []
    for folder_name in CATEGORY_FOLDERS:
        folder = project_dir / folder_name
        if folder.is_dir():
            continue
        try:
            folder.mkdir(parents=True, exist_ok=True)
        except OSError as exc:
            defects.add(f"{project_dir.name}/{folder_name}", f"category folder not created ({exc})")
            continue
        created.append(folder_name)
    return created


def project_categories(project_dir):
    """Every category of this project: the configured ones first, then the hand-made ones.

    CATEGORY_FOLDERS is what a project is *created* with, not the only thing it may hold.
    A folder the user adds themselves is a category they meant to have, so it is adopted and
    indexed like any other. Returns (folder_names, adopted_names).

    The alternative -- calling an unknown folder a defect -- was the behaviour up to here, and
    it made the run red for a user doing something the structure explicitly allows. What must
    not happen is the *silent* version: a renamed 06_tools once took a real run from 21
    categories to 20 with exit 0 and no message, and every note in it was simply gone from
    every index. Adoption keeps those notes indexed; index_main() prints the folder either way.
    """
    known = set(CATEGORY_FOLDERS)
    adopted = []
    for child in sorted(project_dir.iterdir()):
        if not child.is_dir() or child.name.startswith(".") or child.name in SKIP_DIRS:
            continue
        if child.name not in known:
            adopted.append(child.name)
    return CATEGORY_FOLDERS + adopted, adopted


def build_project(vault_root, project_dir, defects):
    """Write every category index plus the project hub.

    Returns (entries, categories, created, adopted) -- the last two are folder names, and index_main()
    prints them. A run that creates a folder and does not say so is a run that changed the tree
    behind the user's back.
    """
    project_dir = Path(project_dir).resolve()
    project_name = project_dir.name
    today = date.today().isoformat()
    total_entries = 0
    category_rows = []

    created = scaffold(project_dir, defects)
    folder_names, adopted = project_categories(project_dir)

    for folder_name in folder_names:
        folder = project_dir / folder_name
        if not folder.is_dir():
            continue
        entries = collect_entries(vault_root, project_dir, folder_name, defects)
        total_entries += len(entries)

        lines = [HEADER.format(name=f"{project_name} — {category_label(folder_name)}", today=today)]
        hub = project_dir / project_index_name(project_dir)
        lines.append(f"↑ {link_to(vault_root, hub, project_name, defects)}\n")
        if entries:
            for entry in entries:
                lines.append(entry_line(vault_root, entry, defects))
        else:
            lines.append("_No notes in this category yet._")
        lines.append("")
        lines.append(f"_{len(entries)} entries._")
        lines.append("")
        write_if_changed(folder / category_index_name(project_name, folder_name),
                         "\n".join(lines), defects)
        category_rows.append((folder_name, len(entries)))

    lines = [HEADER.format(name=project_name, today=today)]
    root_hub = Path(vault_root).resolve() / root_index_name(vault_root)
    lines.append(f"↑ {link_to(vault_root, root_hub, Path(vault_root).resolve().name, defects)}\n")
    for folder_name, count in category_rows:
        target = project_dir / folder_name / category_index_name(project_name, folder_name)
        label = category_label(folder_name)
        lines.append(f"- {link_to(vault_root, target, label, defects)} — {count} entries")
    lines.append("")
    lines.append(f"_{total_entries} entries in {len(category_rows)} categories._")
    lines.append("")
    write_if_changed(project_dir / project_index_name(project_dir), "\n".join(lines), defects)
    return total_entries, len(category_rows), created, adopted


def write_templates(vault_root, projects, defects):
    """One note template per project under <VaultRoot>/_templates/. Returns what it created.

    CREATED WHEN MISSING, NEVER OVERWRITTEN. A template exists to be edited -- a user adds the
    fields their vault actually uses -- and a tool that rewrites it on every run eats that edit
    without saying so. The doctrine rule that generated files are not hand-edited covers the
    index tree; _templates is deliberately not part of it, which is why it is written once and
    then left alone.

    THE SAME FAILURE MODE write_if_changed() HAD, AND THE SAME REPAIR. This runs at the very end
    of build_root(), so a read-only `_templates` folder raised OSError here and took the run down
    on the last step before log_run() -- a complete index tree, and still not one line in
    runs.log saying the run happened. A missing template is a defect, not a reason to lose the
    record of everything that did work.
    """
    folder = Path(vault_root).resolve() / TEMPLATES_DIR
    written = []
    for project in projects:
        target = folder / template_name(project.name)
        if target.exists():
            continue
        try:
            folder.mkdir(parents=True, exist_ok=True)
            target.write_text(template_text(project.name), encoding="utf-8", newline="\n")
        except OSError as exc:
            defects.add(target.name, f"note template not written ({exc})")
            continue
        written.append(target.name)
    return written


def build_root(vault_root, defects):
    vault_root = Path(vault_root).resolve()
    today = date.today().isoformat()
    lines = [HEADER.format(name=vault_root.name, today=today)]
    total_entries = 0
    total_categories = 0
    created_all = []
    adopted_all = []
    projects = project_dirs(vault_root)
    for project in projects:
        entries, categories, created, adopted = build_project(vault_root, project, defects)
        total_entries += entries
        total_categories += categories
        created_all += [f"{project.name}/{n}" for n in created]
        adopted_all += [f"{project.name}/{n}" for n in adopted]
        target = project / project_index_name(project)
        lines.append(
            f"- {link_to(vault_root, target, project.name, defects)} "
            f"— {entries} entries in {categories} categories"
        )
    lines.append("")
    lines.append(f"_{len(projects)} projects · {total_entries} entries in {total_categories} categories._")
    lines.append("")
    write_if_changed(vault_root / root_index_name(vault_root), "\n".join(lines), defects)
    templates = write_templates(vault_root, projects, defects)
    return len(projects), total_entries, total_categories, created_all, adopted_all, templates


# --------------------------------------------------------------------------- uniqueness


def check_unique_basenames(vault_root, defects):
    """Doctrine rule 2 needs code reading it, or it holds only while someone remembers it.

    The generator already walks every note, so it counts basenames while it does.
    """
    seen = defaultdict(list)
    for path in walk_markdown(vault_root):
        seen[path.name].append(path)
    for name, paths in sorted(seen.items()):
        if len(paths) > 1:
            where = ", ".join(sorted(p.parent.name for p in paths))
            defects.add(name, f"name used {len(paths)} times ({where})")
    return len(seen)


# --------------------------------------------------------------------------- main


def index_main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--root", help="vault root: writes the root index and every project below it")
    group.add_argument("--vault", help="one project directory: writes its category and hub indexes")
    args = parser.parse_args(argv)

    defects = Defects()

    if args.root:
        vault_root = Path(args.root).resolve()
        if not vault_root.is_dir():
            print(f"not a directory: {vault_root}", file=sys.stderr)
            return EXIT_USAGE
        projects, entries, categories, created, adopted, templates = build_root(vault_root, defects)
        names = check_unique_basenames(vault_root, defects)
        print(f"{entries} entries in {categories} categories · {projects} projects · {names} distinct filenames")
    else:
        project_dir = Path(args.vault).resolve()
        if not project_dir.is_dir():
            print(f"not a directory: {project_dir}", file=sys.stderr)
            return EXIT_USAGE
        vault_root = project_dir.parent
        entries, categories, created_names, adopted_names = build_project(vault_root, project_dir, defects)
        created = [f"{project_dir.name}/{n}" for n in created_names]
        adopted = [f"{project_dir.name}/{n}" for n in adopted_names]
        # Templates are written by the root run only: it is the one invocation that knows every
        # project, and _templates sits at the vault root, not inside a project.
        templates = []
        names = check_unique_basenames(vault_root, defects)
        print(f"{entries} entries in {categories} categories · {project_dir.name} · {names} distinct filenames")

    # Neither of these is a defect -- the run does exactly what the structure allows. Both change
    # or extend the tree, so both are said out loud. A typo'd folder name shows up here as a
    # category the user did not mean to have, which is the only warning that case ever gets.
    for name in created:
        print(f"  created  {name} — category folder was missing")
    for name in adopted:
        print(f"  adopted  {name} — folder made by hand, indexed as a category")
    for name in templates:
        print(f"  template {TEMPLATES_DIR}/{name} — note template written once; edit it freely, "
              f"no run overwrites it")

    if defects.skipped:
        print(f"skipped {defects.skipped} unreadable files", file=sys.stderr)

    status = "ok" if not defects else "defects"
    log_run(vault_root, "build_index", status,
            f"{len(defects)} defects · {len(created)} created · {len(adopted)} adopted · "
            f"{len(templates)} templates")

    if defects:
        defects.report()
        print(f"{len(defects)} defects", file=sys.stderr)
        return EXIT_DEFECT
    return EXIT_OK

# ------------------------------- vaultkit.py command   (was write_command.py)
"""Write a `/vaultkit` slash command for Claude Code, with this vault's real paths already in it.

The verification chain in SECTION 8 is six commands with three traps in them, and every one of
the three was hit on a real run:

  1. `--vault` means two different things. `links` wants the vault ROOT, `index` wants ONE
     PROJECT, `duplicates` takes either. Typing the same path after every `--vault` is wrong in
     two places out of three -- and folding the guards into one `vaultkit.py` did not remove
     that, it only put the collision inside one file. Each subcommand keeps its own parser.
  2. The tool folder is `<VaultRoot>/00_Global/06_tools/`, not `06_tools/`. A relative prefix is
     an invitation to run it from a directory where it does not resolve.
  3. `--root`, not `--vault`, for the sweep. Rerunning only `--vault` after adding a note leaves
     the root index on yesterday's count -- green, silent, and wrong. Measured on a cold run:
     one added note left the root index reading 5 entries against a vault holding 6.

There is a fourth thing the file gets right and a typed chain cannot: ORDER. `freshness` stands
first, because every other step appends an `ok` line and a freshness check measured after them
reports the side effect of its own chain as health.

A command file removes all three by spelling out the answers once, per vault, with the paths
filled in. It is a convenience for Claude Code and nothing depends on it: the workflow page in
`05_workflows` carries the same chain in prose for anyone working in a browser.

    python vaultkit.py command --vault <VaultRoot> --shell powershell
    python vaultkit.py command --vault <VaultRoot> --shell posix

THE DESTINATION IS ALWAYS `~/.claude/commands/vaultkit.md`, AND THERE IS NO OPTION. An in-vault
copy under `<VaultRoot>/.claude/commands/` was offered once and taken out again: it fires only in
a session started at the vault root, and a sync command that demands a particular working
directory is not one anybody uses. The file holds absolute paths, so it needs no cwd at all.

CREATED WHEN MISSING, NEVER OVERWRITTEN, same as the note templates. A command file is there to
be edited -- the user adds their own steps -- and a tool that rewrites it every run eats that
edit without saying so.

TWO KINDS OF "IT IS ALREADY THERE", AND THEY GET OPPOSITE ANSWERS. A file this tool wrote before
is not news: nothing is printed, exit 0, exactly like the note templates. A file it did NOT write
is a stranger holding the name -- most likely in `~/.claude/commands/`, where a `/vaultkit` of the
user's own may already live. That case is named on stderr and exits non-zero, because a silent
zero would let the setup report `/vaultkit` as ready while the user's own command still owns the
name. A quiet non-write that looks like success is the most expensive failure class this kit has
on record.

The two are told apart by the marker line the generated file carries, never by mtime and never by
a state file beside it: both of those answer "when", and the question is "whose".

Undo recipe for that guard, re-measured on this machine 2026-07-29 after the stranger case was
added: copy tools/ somewhere, make the `if target.exists():` block in command_main() unreachable,
and run the three drivers there. Re-measured on this machine 2026-07-31 --
test_write_command 10/14, acceptance 11/12, verify_setup 14/15. The four cases that move are the
hand-edited file, the second silent run, the marker check and the foreign file: the whole of what
this guard promises, from four directions.
"""

TOOLS = Path(__file__).resolve().parent
sys.path.insert(0, str(TOOLS))

for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass


COMMAND_NAME = "vaultkit"

DESCRIPTION = ("Rebuild this vault's index and run every guard, in the order that leaves "
               "nothing stale")

# How a run tells its own file from a stranger's with the same name. Deliberately not a state
# file and not an mtime heuristic: both answer "when", and the question is "whose".
#
# It sits on the first line of the BODY, not of the file. YAML frontmatter has to start at byte
# zero -- a comment in front of it and `description:` is either lost or the command does not load
# at all. That was not measured here, and a marker that breaks the thing it marks is not a marker.
MARKER_PREFIX = "<!-- vaultkit:"


def marker(vault_root):
    return f"{MARKER_PREFIX} {Path(vault_root).resolve().as_posix()} -->"


def written_by_us(path):
    """True when this file came out of this tool. The vault path inside is informative only --
    a vault that moved is still our file, and re-checking the path would call it a stranger."""
    try:
        head = path.read_text(encoding="utf-8-sig")[:2000]
    except OSError:
        return False
    return MARKER_PREFIX in head


def show(path, shell):
    """A path as the user's own shell writes it.

    Cosmetic, and deliberately so: Python takes forward slashes on Windows too, so nothing here
    breaks if it is wrong. It is done because a command file that spells paths in a foreign
    syntax reads as though it were meant for someone else's machine.
    """
    text = Path(path).as_posix() if shell == "posix" else str(Path(path)).replace("/", "\\")
    return f'"{text}"'


def command_text(vault_root, projects, shell):
    vault_root = Path(vault_root).resolve()
    tools = vault_root / "00_Global" / "06_tools"

    # ONE ENTRY POINT, SPELLED ONCE. Every step below is `vaultkit.py <sub>`, so the chain the
    # user reads has one path in it instead of six -- and a step that named a tool the delivery
    # no longer carries cannot happen by editing five lines and forgetting the sixth. It did:
    # this file went on emitting a "Run the suites" step with `run_suites.py` after that tool
    # left the delivery, and nothing read this text, so no run said so.
    kit = show(tools / "vaultkit.py", shell)

    root = show(vault_root, shell)
    lines = [
        "---",
        f"description: {DESCRIPTION}",
        "---",
        "",
        marker(vault_root),
        "",
        f"Synchronise the Obsidian vault at {root} completely. Its tools are in "
        f"{show(tools, shell)} — the full path, because `06_tools/` alone resolves only from the "
        f"vault root and nowhere else.",
        "",
        "Run every step below, in this order, and report what each one printed — with its "
        "numbers. Name any step you did not run; an unmeasured step and a passing one look "
        "identical from the outside.",
        "",
        "**Before you start:** the index steps write. Say so, and check `git status` first, so "
        "their output is not mistaken for someone else's uncommitted work.",
        "",
        "## 1 · Read the run log before anything writes to it",
        "",
        "**First, and the order is the whole point.** Every step below appends an `ok` line to "
        "the run log. Measured after them, this check sees the side effect of the very chain it "
        "belongs to and reports the jobs as fresh — including one that stopped firing a week "
        "ago.",
        "",
        "**Red here is a report, never a reason to stop.** It judges the past; the rest of this "
        "chain produces the present. Carry its numbers into the report and run the other steps "
        "either way.",
        "",
        f"- `python {kit} freshness --vault {root}`",
        "",
        "## 2 · Index each project",
        "",
        "`--vault` here means ONE PROJECT DIRECTORY, not the vault root. One line per project:",
        "",
    ]
    for project in projects:
        lines.append(f"- `python {kit} index --vault {show(project, shell)}`")
    lines += [
        "",
        "## 3 · Index the vault root",
        "",
        "`--root`, not `--vault`. This is the one invocation that walks every project *and* "
        "writes the root hub. Running only step 1 after adding a note leaves the root index "
        "holding yesterday's entry count, with no message and a green exit — measured on a cold "
        "run: one added note left it reading `5 entries` against a vault holding 6.",
        "",
        f"- `python {kit} index --root {root}`",
        "",
        "## 4 · Check the links",
        "",
        "`--vault` here means THE VAULT ROOT — the same flag, the other meaning. The project "
        "hubs link back to the root index, so anything narrower reports a broken link that is "
        "not broken:",
        "",
        f"- `python {kit} links --vault {root}`",
        "",
        "## 5 · Check for duplicates",
        "",
        "`--vault` here takes either the root or a single project:",
        "",
        f"- `python {kit} duplicates --vault {root}`",
        "",
        "## 6 · Prove the second run changes nothing",
        "",
        "A generator that drifts on every run is indistinguishable from a clean one after a "
        "single pass, and it turns every later `git status` into noise nobody reads.",
        "",
        f"- `python {kit} index --root {root}`",
    ]
    # The git line is written only into a vault that has a repository. SECTION 7 recommends git
    # and step 2 of verify_setup requires it, but a user may still have declined -- and a command
    # that ends in a line failing every single time teaches them to skip the last step.
    #
    # IT SAID "must print nothing" UNTIL 2026-07-31, AND THAT IS STRICTER THAN THE CONTRACT. The
    # contract's own block says `# no generated file may appear here` and then spells out two
    # things that legitimately do appear: `?? .obsidian/` once the app has been opened, and notes
    # the user wrote with the index entries now pointing at them. Drift is a changed
    # `INDEX - *.md` WITHOUT a new note. Measured on the cold run of 2026-07-31: step 6 showed
    # three changed index files, correctly, and a reader holding only this command file would
    # have reported a defect that was not one.
    #
    # KNOWN GAP, deliberately left for its own round: check_generated_command() in build_kit.py
    # renders against REPO/"not-a-real-vault", a path with no .git, so it only ever sees the
    # else-branch below and cannot read this line at all. Closing it means rendering against a
    # path WITH a .git, which is a guard rebuild, not a text fix.
    if (vault_root / ".git").is_dir():
        lines.append(f"- `git -C {root} status --porcelain`  — no `INDEX - *.md` may appear "
                     f"without a note having been added. `?? .obsidian/` and notes you wrote "
                     f"yourself, with the index entries pointing at them, are not drift.")
    else:
        lines.append("- Compare the index files before and after by hand: this vault has no git "
                     "repository, so there is nothing that can answer the question for you. "
                     "Setting one up (see the workflow page) makes this one command.")
    lines += [
        "",
        "## Report",
        "",
        "One line per step, each with its denominator. `Open:` lists what you did **not** "
        "measure, not only what is unfinished.",
        "",
    ]
    return "\n".join(lines)


def target_path():
    """Always the user's own commands folder. No parameter, because there is no second answer.

    Taking a vault root here would keep the door open for an in-vault copy, and that copy is
    exactly what was removed: it loads only in a session started at the vault root.
    """
    return Path.home() / ".claude" / "commands" / f"{COMMAND_NAME}.md"


def command_main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--vault", required=True, help="vault root")
    parser.add_argument("--shell", choices=("powershell", "posix"), default="powershell",
                        help="the syntax the paths are written in")
    args = parser.parse_args(argv)

    vault_root = Path(args.vault).resolve()
    if not vault_root.is_dir():
        print(f"not a directory: {vault_root}", file=sys.stderr)
        return EXIT_USAGE

    target = target_path()
    projects = project_dirs(vault_root)
    if not projects:
        # Not a silent skip: a vault with no projects means the wrong path was given, and a
        # command file listing no projects would be a working file that does nothing.
        print(f"no projects under {vault_root} — nothing to write a command for", file=sys.stderr)
        return EXIT_DEFECT

    if target.exists():
        if written_by_us(target):
            # Ours from a previous run, possibly hand-edited since. Nothing to say.
            log_run(vault_root, "write_command", "ok", f"{target} already ours · nothing written")
            return EXIT_OK
        # Someone else's file under the name we wanted. Nothing is overwritten and nothing is
        # written either -- and a silent zero here is the most expensive answer in this kit,
        # because the setup would report /vaultkit as ready while the user's own command still
        # holds the name.
        print(f"{target} already exists and was not written by this kit — nothing written.\n"
              f"  It carries no `{MARKER_PREFIX} … -->` line, so it is your own command of the "
              f"same name, and it keeps the name.\n"
              f"  Rename or remove your own file and run this again; there is no second location "
              f"to fall back to, because a command anywhere else would not load.",
              file=sys.stderr)
        log_run(vault_root, "write_command", "blocked", f"{target} held by a foreign command")
        return EXIT_DEFECT

    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(command_text(vault_root, projects, args.shell),
                      encoding="utf-8", newline="\n")
    print(f"wrote {target} — /{COMMAND_NAME} covers {len(projects)} projects; "
          f"edit it freely, no run overwrites it")
    log_run(vault_root, "write_command", "ok", f"{target} written · {len(projects)} projects")
    return EXIT_OK

# ----------------------------------- vaultkit.py links   (was check_links.py)
"""Check that every [[wikilink]] in the vault resolves to a file.

Reports numerator AND denominator, and distinguishes three outcomes: pass, fail, and
"did not run". A checker that scanned zero files must never report "0 broken".
"""

WIKILINK = re.compile(r"\[\[([^\[\]]+)\]\]")
FENCE = re.compile(r"^\s*(```|~~~)")
INLINE_CODE = re.compile(r"`+[^`]*`+")

# Extensions Obsidian resolves in a wikilink besides .md.
ATTACHMENT_SUFFIXES = {
    ".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp", ".bmp",
    ".pdf", ".canvas", ".mp3", ".wav", ".m4a", ".ogg", ".flac",
    ".mp4", ".webm", ".mov",
}


def linkable_files(vault_root):
    """basename/relpath (lowercased, with and without .md) -> file, for resolution."""
    root = Path(vault_root).resolve()
    table = defaultdict(list)
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        rel = path.relative_to(root)
        if any(part in SKIP_DIRS for part in rel.parts[:-1]):
            continue
        suffix = path.suffix.lower()
        if suffix != ".md" and suffix not in ATTACHMENT_SUFFIXES:
            continue
        rel_posix = rel.as_posix().lower()
        table[rel_posix].append(path)
        table[path.name.lower()].append(path)
        if suffix == ".md":
            table[rel_posix[:-3]].append(path)
            table[path.stem.lower()].append(path)
    return table


def strip_code(text):
    """Remove fenced blocks and inline code spans.

    A [[wikilink]] inside a code span is not a link — Obsidian does not resolve it, so a
    page that *documents* the syntax must not report itself as broken.
    """
    out = []
    in_fence = False
    fence_marker = None
    for line in text.splitlines():
        match = FENCE.match(line)
        if match:
            if not in_fence:
                in_fence = True
                fence_marker = match.group(1)
            elif line.strip().startswith(fence_marker):
                in_fence = False
                fence_marker = None
            out.append("")
            continue
        if in_fence:
            out.append("")
            continue
        out.append(INLINE_CODE.sub("", line))
    return "\n".join(out)


def link_targets(text):
    """Every wikilink target in the text, alias and anchor stripped."""
    targets = []
    for raw in WIKILINK.findall(strip_code(text)):
        # Inside a Markdown table the alias pipe must be written `\|` — that is Obsidian's
        # own documented syntax, not a defect. Unescape before splitting, or a link the app
        # resolves fine is reported broken and the writer edits a correct note.
        target = raw.replace("\\|", "|").split("|", 1)[0]
        target = target.split("#", 1)[0]
        target = target.split("^", 1)[0]
        target = target.strip()
        if target:
            targets.append((target, raw))
    return targets


def links_main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--vault", required=True, help="vault root")
    args = parser.parse_args(argv)

    vault_root = Path(args.vault).resolve()
    if not vault_root.is_dir():
        print(f"not a directory: {vault_root}", file=sys.stderr)
        return EXIT_USAGE

    table = linkable_files(vault_root)
    files = walk_markdown(vault_root)
    scanned = 0
    skipped = 0
    total = 0
    broken = []

    for path in files:
        try:
            # utf-8-sig: FENCE anchors at ^\s* and a byte-order mark is not \s, so a note that
            # opens with a code fence loses fence detection on its first line. Every wikilink
            # inside that block is then reported broken -- the note is right, the guard is
            # wrong, and that is the expensive way round.
            text = path.read_text(encoding="utf-8-sig", errors="replace")
        except OSError as exc:
            # Count the skip explicitly. A silent skip is a lost denominator.
            skipped += 1
            print(f"{path.name}: unreadable ({exc})", file=sys.stderr)
            continue
        scanned += 1
        for target, raw in link_targets(text):
            total += 1
            key = target.lower().lstrip("./")
            if key not in table:
                broken.append((path, raw))

    if scanned == 0:
        did_not_run(f"0 of {len(files)} markdown files scanned")
        log_run(vault_root, "check_links", "did-not-run", "0 files scanned")
        return EXIT_DEFECT

    resolved = total - len(broken)
    print(f"{resolved}/{total} wikilinks resolve · {scanned} files scanned · {skipped} skipped")

    status = "ok" if not broken and not skipped else "defects"
    log_run(vault_root, "check_links", status, f"{resolved}/{total} resolve")

    if broken:
        for path, raw in broken:
            # Path relative to the vault, not the bare filename: every project has an
            # INDEX and a knowledge-transfer page, so a name alone does not say which one.
            print(f"{path.relative_to(vault_root).as_posix()}: [[{raw}]] resolves to nothing",
                  file=sys.stderr)
        print(f"{len(broken)} broken wikilinks", file=sys.stderr)
        return EXIT_DEFECT
    if skipped:
        print(f"{skipped} files skipped — denominator incomplete", file=sys.stderr)
        return EXIT_DEFECT
    return EXIT_OK

# ------------------------- vaultkit.py duplicates   (was check_duplicates.py)
"""Flag notes whose content overlaps, so one insight does not end up living in two files.

Every hit gets a decision: a flagged pair makes the run red. Ignoring it is not an option
the tool offers.

The threshold is a knob, not a truth. On a vault with a handful of notes the number this
prints is arithmetic, not evidence — recalibrate once there is real volume:

    python vaultkit.py duplicates --vault <dir> --threshold 0.75
"""

DEFAULT_THRESHOLD = 0.75
SHINGLE = 5
WORD = re.compile(r"[^\W\d_]+", re.UNICODE)


def body_shingles(path):
    """Word 5-grams of the note body. Frontmatter is skipped — it is metadata, not content."""
    # utf-8-sig: a BOM makes startswith("---") false, the frontmatter is then compared as if
    # it were body text, and its words dilute the overlap. Measured on this machine: an
    # identical-body pair went 1 flagged of 6 compared without a BOM to 0 of 6 with one.
    text = path.read_text(encoding="utf-8-sig", errors="replace")
    if text.startswith("---"):
        parts = text.split("\n---", 2)
        if len(parts) >= 2:
            text = parts[-1]
    words = [w.lower() for w in WORD.findall(text)]
    if len(words) < SHINGLE:
        return {tuple(words)} if words else set()
    return {tuple(words[i : i + SHINGLE]) for i in range(len(words) - SHINGLE + 1)}


def jaccard(a, b):
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def duplicates_main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--vault", required=True, help="vault root or a single project directory")
    parser.add_argument("--threshold", type=float, default=DEFAULT_THRESHOLD)
    args = parser.parse_args(argv)

    root = Path(args.vault).resolve()
    if not root.is_dir():
        print(f"not a directory: {root}", file=sys.stderr)
        return EXIT_USAGE

    notes = [p for p in walk_markdown(root) if not is_index_file(p)]
    shingles = {}
    skipped = 0
    for path in notes:
        try:
            shingles[path] = body_shingles(path)
        except OSError as exc:
            skipped += 1
            print(f"{path.name}: unreadable ({exc})", file=sys.stderr)

    comparable = list(shingles)
    pairs = list(combinations(comparable, 2))
    flagged = [
        (a, b, jaccard(shingles[a], shingles[b]))
        for a, b in pairs
        if jaccard(shingles[a], shingles[b]) >= args.threshold
    ]

    if len(comparable) < 2:
        did_not_run(f"{len(comparable)} comparable notes — a pair needs two "
                    f"(threshold {args.threshold})", sys.stdout)
        log_run(root, "check_duplicates", "did-not-run", f"{len(comparable)} notes")
        return EXIT_OK

    print(
        f"{len(flagged)} pairs flagged of {len(pairs)} compared · "
        f"{len(comparable)} notes · threshold {args.threshold} · {skipped} skipped"
    )
    log_run(root, "check_duplicates", "ok" if not flagged else "defects", f"{len(flagged)} flagged")

    if flagged:
        for a, b, score in sorted(flagged, key=lambda t: -t[2]):
            print(f"{a.name}: {score:.2f} overlap with {b.name}", file=sys.stderr)
        print(f"{len(flagged)} duplicate pairs need a decision", file=sys.stderr)
        return EXIT_DEFECT
    if skipped:
        print(f"{skipped} files skipped — denominator incomplete", file=sys.stderr)
        return EXIT_DEFECT
    return EXIT_OK

# --------------------------- vaultkit.py freshness   (was check_freshness.py)
"""Report the age of the last HEALTHY run of each expected job.

Without this, a scheduler that quietly stopped firing looks identical to one that is fine.
"no log" is reported as "did not run" — never as "fine".

Log format, one line per run, appended by every tool (see vault_paths.log_run):

    2026-07-27T09:15:00+00:00	build_index	ok	0 defects

LOGGING AND BEING WATCHED ARE TWO DIFFERENT THINGS, AND jobs.json CARRIES THE LISTS. Every tool
writes a line; only a tool that runs on a schedule can be *late*. Put the on-demand ones under an
age limit and the report is red every single day, which is the fastest way to get the whole check
switched off. So `jobs` is what must be fresh, `on_demand` is what logs and is never late,
`not_invoked` is what no chain calls at all, and a name in none of them is reported as
unclassified rather than assumed into one of them.

THE UNCLASSIFIED LIST IS READ FROM THE FOLDER, NOT ONLY FROM THE LOG. A tool that no chain calls
never writes a line, and a population derived from the log alone therefore cannot see the one
thing this report is for -- the check confirms its own silence. Measured 2026-07-30: `0
unclassified` over a folder holding a tool in neither list.

This tool logs itself and stands in `on_demand`. Without its own line, "the freshness check runs in
the chain" is a claim about a command file: delete the step and it looks exactly like a check that
runs and finds nothing. Watching itself would be the regress -- logging is not watching, and that
separation is the whole point.

RUN IT FIRST, BEFORE ANYTHING ELSE IN THE CHAIN. Every other tool appends an `ok` line, so a run
measured afterwards sees the side effect of the chain it is part of and reports fresh over a job
that died a week ago.
"""

DEFAULT_MAX_AGE_HOURS = 24.0
HEALTHY = {"ok"}

# Spelled again rather than imported from upgrade.py, AND THE DIRECTION IS THE WHOLE REASON.
# upgrade.py is the repair tool: it has to run on a folder where this file is truncated, missing
# or unparseable, which is why it imports nothing from here except the register, inside --prove,
# inside a try. An import the other way round -- this file reaching into upgrade.py for one
# string -- would put the thing being repaired on the repair tool's import path and invert the
# failure domain for the sake of eleven characters. upgrade.py states the same trade over its own
# copies of BLOCK_RE and the reconfigure block; this is that reasoning, mirrored.
STAMP_NAME = "kit-version.txt"

# Where a newer kit file comes from. No network call is made -- see the note on the display
# below; this is a place to look, printed for a human.
KIT_HOME = "github.com/nibor1896/claude-obsidian-vault-kit"

# How old an installation gets before the run mentions it. A line printed on EVERY run is read
# for about a week and skimmed forever after, which makes it worth less than no line at all; one
# that appears after two months is read. Sixty days is a choice, not a measurement -- nothing has
# been run long enough to say what interval a person actually notices.
STAMP_AGE_DAYS = 60.0


DEFAULT_JOBS = ["build_index", "check_links"]

# Tools that log but deliberately have no age limit, name -> why. Kept in step with the shipped
# jobs.json, and used only when no config file exists at all.
#
# THE REASON PER ENTRY IS NOT DECORATION: an exception without one is indistinguishable from an
# oversight, and JSON has no comments, so the value carries it.
DEFAULT_ON_DEMAND = {
    "check_duplicates": "runs in the verification chain and by hand, never on a schedule",
    "write_command": "runs once during setup, and again only if the command file is gone",
    "check_freshness": "this job itself -- logged, never watched: an age limit on the watcher "
                       "is a regress",
}

# The third classification: it logs, and no chain calls it. EMPTY SINCE 2026-07-31, and the
# structure stays for the user's own tools. All three entries that were here described FILES
# rather than jobs: `vault_paths` and `_testkit` were modules and are not files any more, and
# `count_tokens` is excused by the register at the end of this file instead -- it carries no job
# name, which is the same statement made where the fact lives rather than in a second place.
#
# A user's own logging script still belongs here, with its reason: JSON has no comments, so the
# value carries it, and an exception without one cannot be told from an oversight. Kept in step
# with the shipped jobs.json -- build_kit.py refuses a build where the two disagree.
DEFAULT_NOT_INVOKED = {}


def tool_folder(vault_root):
    """The one folder both the config and the population come out of.

    Derived from RUN_LOG_RELPATH rather than spelled again: a population read from one folder and
    a classification read from another would disagree without either being wrong.
    """
    return Path(vault_root).resolve() / RUN_LOG_RELPATH.parent


def loggable_tools(vault_root):
    """(names of jobs that can ever appear in the log, files that could not be read).

    WHY THE POPULATION IS NOT SIMPLY EVERY `.py` IN THE FOLDER (2026-07-30): a tool that never
    logs cannot appear in the log by construction, so asking whether it is watched has no answer
    that would change anything -- `upgrade.py` runs, reaches a verdict, and never logs. Naming it
    on every single run would put a permanent line above the one line that means something, which
    is the fastest way to get this report skimmed instead of read.

    Measured on this machine 2026-07-30, when this function was written: five of the shipped
    tools logged -- build_index, check_links, check_duplicates, write_command, check_freshness --
    and those five were exactly the five in jobs.json. So the honest population is "can it log",
    and the check that follows is "has anyone said which list it belongs to".

    HALF OF IT IS NOW READ, NOT GUESSED (2026-07-31). It used to take every stem in the folder
    whose file text mentioned the logging call. That was a guess with two known faults, and the
    merge into one file turned both fatal: `vault_paths.py` showed up because it DEFINED the
    call and needed a `not_invoked` entry as a patch, a tool that forgot to log was invisible by
    construction -- and with every guard in `vaultkit.py`, the guess now yields exactly one stem,
    `vaultkit`, which is no job's name at all. Every job would read as unclassified forever.

    So the kit's own jobs come from COMMANDS at the end of this file, which states them instead
    of inferring them. The folder scan stays for the user's OWN tools: a script they wrote that
    logs is still a job that can go stale, and nothing here knows about it in advance. This file
    is skipped by name in that scan, because the register already answered for it.

    Suites are excluded structurally, not by taste: `test_X.py` is not a job, and one that
    exercised the logging call would otherwise ask to be classified as a scheduled job.
    """
    names = {spec["job"] for spec in COMMANDS.values() if spec["job"]}
    folder = tool_folder(vault_root)
    if not folder.is_dir():
        return names, 0
    unreadable = 0
    for path in sorted(folder.glob("*.py")):
        if path.name.startswith("test_") or path.name == Path(__file__).name:
            continue
        try:
            text = path.read_text(encoding="utf-8-sig", errors="replace")
        except OSError:
            # Counted and printed, never a silent continue: a skip that does not count itself
            # still prints a total, over fewer files than it names.
            unreadable += 1
            continue
        if "log_run(" in text:
            names.add(path.stem)
    return names, unreadable


def job_lists(vault_root):
    """(watched, on_demand, not_invoked) — read once, so they can never disagree about the fallback.

    No config file is normal -- a project-only run has none, and both defaults stand. A config
    that exists and cannot be read is not normal, and falling back to the default over it
    checks a job list the user never chose while printing nothing about it. utf-8-sig is how
    that used to happen: Notepad writes a BOM, json.loads raises, the except swallowed it.

    A config that exists and has no `on_demand` key gets an EMPTY on-demand list, not the
    default above. That is the same rule one line further: substituting a classification the
    user never made is the silent fallback this docstring is about. Empty is honest, and the
    unclassified line then names the tools instead of guessing at them.

    Either shape is accepted for `on_demand` and for `not_invoked`: the mapping that ships
    (name -> reason) or a bare list, which a user mirroring `jobs` will write. A list simply
    carries no reasons; refusing it would hard-fail an honest config over cosmetics.
    """
    config = tool_folder(vault_root) / "jobs.json"
    if not config.exists():
        return list(DEFAULT_JOBS), dict(DEFAULT_ON_DEMAND), dict(DEFAULT_NOT_INVOKED)
    try:
        data = json.loads(config.read_text(encoding="utf-8-sig"))
        watched = list(data["jobs"])
        return watched, _mapping(data, "on_demand"), _mapping(data, "not_invoked")
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print(f"{config}: unreadable ({exc}) — falling back to {DEFAULT_JOBS}", file=sys.stderr)
        return list(DEFAULT_JOBS), dict(DEFAULT_ON_DEMAND), dict(DEFAULT_NOT_INVOKED)


def _mapping(data, key):
    """One optional name->reason list out of a config that exists. Missing means EMPTY.

    Never the built-in default: a config the user wrote and a classification they never made must
    not be mixed, or the unclassified line reports against a list nobody chose. Same rule as the
    docstring above, applied to both optional keys instead of one.

    KEYS STARTING WITH `_` ARE NOT JOBS (2026-07-31). JSON has no comments, so the shipped
    jobs.json carries its explanations as `_comment` keys -- and the delivered file invites the
    user to do the same, since it is the only way to write down why an entry is there. Without
    this filter every fresh vault reported `1 not invoked` over the placeholder that says the
    list is empty: a count with no object behind it, printed on the one line whose whole purpose
    is naming things nobody classified. The key itself stays in jobs.json -- delete it and
    build_kit.py's --check goes red comparing None against {}.
    """
    raw = data.get(key) or {}
    if isinstance(raw, dict):
        return {name: reason for name, reason in raw.items() if not name.startswith("_")}
    return {name: "" for name in raw if not name.startswith("_")}


def parse_log(log_path):
    """(newest healthy per job, every job name seen, lines, malformed).

    `seen` covers failed runs too: a tool that only ever fails is still either classified or
    not, and leaving it out of that question would hide the tool that needs the decision most.
    """
    healthy = {}
    seen = set()
    malformed = 0
    lines = 0
    with open(log_path, "r", encoding="utf-8", errors="replace") as fh:
        for line in fh:
            if not line.strip():
                continue
            lines += 1
            parts = line.rstrip("\n").split("\t")
            if len(parts) < 3:
                malformed += 1
                continue
            stamp, job, status = parts[0], parts[1], parts[2]
            try:
                when = datetime.fromisoformat(stamp)
            except ValueError:
                malformed += 1
                continue
            seen.add(job)
            if when.tzinfo is None:
                when = when.replace(tzinfo=timezone.utc)
            if status not in HEALTHY:
                continue
            if job not in healthy or when > healthy[job]:
                healthy[job] = when
    return healthy, seen, lines, malformed


def installed_kit_note(vault_root, now):
    """Two lines naming the installed kit and where to compare it, or None. Never a network call.

    WHY THIS EXISTS: until 2026-07-31 a user holding only the delivered `.md` had no way inside
    the vault to learn that a newer kit might exist. `upgrade.py` has done the whole job for a
    while -- compare, list, apply -- but nothing ever pointed at it: the `/vaultkit` chain
    contains no occurrence of "version" or "upgrade", and the only mention anywhere was the
    footer of the delivered file, which nobody reads twice. The update path existed and had no
    entrance.

    WHY IT SAYS NOTHING ABOUT WHETHER A NEWER ONE EXISTS. Answering that means asking GitHub,
    and "GitHub is the optional part" is a promise this kit makes -- a vault that phones home to
    stay honest is a different product. So the line states what is locally measurable, which is
    what is installed and how old it is, and names the one place to look. The comparison is the
    user's, and it is one glance at line 1 of the published file.

    WHY IT IS IN freshness: this runs FIRST in the daily chain, it already reads ages against
    thresholds, and tool_folder() already resolves the folder the stamp lives in. No new path, no
    new tool, no new command.

    NOTHING IS PRINTED WHEN THE STAMP IS ABSENT OR NOT A STAMP -- the same rule upgrade.py
    applies to a missing manifest: never guess. A folder assembled by hand has no
    kit-version.txt, and a file holding something other than twelve hex characters is a question
    for `upgrade.py`, which reports it properly; inventing a version here would put a wrong
    answer where the whole point is a comparison.
    """
    stamp = tool_folder(vault_root) / STAMP_NAME
    try:
        version = stamp.read_text(encoding="utf-8-sig").strip()
        installed = datetime.fromtimestamp(stamp.stat().st_mtime, timezone.utc)
    except OSError:
        return None
    if not re.fullmatch(r"[0-9a-f]{12}", version):
        return None
    age_days = (now - installed).total_seconds() / 86400.0
    if age_days < STAMP_AGE_DAYS:
        return None
    return (f"  kit-version {version} · installed {age_days:.0f} days ago\n"
            f"  compare it against the kit-version on line 1 at {KIT_HOME}")


def freshness_main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--vault", required=True, help="vault root")
    parser.add_argument("--log", help="run log path (defaults to the vault's own)")
    parser.add_argument("--max-age-hours", type=float, default=DEFAULT_MAX_AGE_HOURS)
    parser.add_argument("--jobs", nargs="*", help="override the expected job list")
    args = parser.parse_args(argv)

    vault_root = Path(args.vault).resolve()
    log_path = Path(args.log).resolve() if args.log else vault_root / RUN_LOG_RELPATH
    configured, on_demand, not_invoked = job_lists(vault_root)
    jobs = args.jobs if args.jobs else configured

    # Before any measurement, because the answer to "which list wins" is none of them. Letting one
    # win would be an invisible decision: the other entry would sit there doing nothing, and no
    # run could show which of the statements applies.
    #
    # The CONFIGURED list, not the effective one: the defect is in the file, so `--jobs` must not
    # be able to dodge it -- and `--jobs check_duplicates` is a deliberate one-off watch of an
    # on-demand tool, which is not a contradiction and must not be treated as one.
    #
    # Three lists since 2026-07-30, so every pair is checked rather than the one that used to
    # exist. `not_invoked` contradicts either of the others just as loudly: a tool cannot both be
    # called by no chain and be the thing a chain is watched for.
    clash = sorted({name for a, b in ((configured, on_demand), (configured, not_invoked),
                                      (set(on_demand), set(not_invoked)))
                    for name in set(a) & set(b)})
    if clash:
        print(f"{', '.join(clash)}: classified twice. Watched means it may be late, on demand "
              f"means it cannot be, not invoked means no chain calls it — a name belongs to "
              f"exactly one. Take it out of the others in {tool_folder(vault_root) / 'jobs.json'}.",
              file=sys.stderr)
        log_run(vault_root, "check_freshness", "did-not-run",
                f"{len(clash)} jobs in more than one list")
        return EXIT_USAGE

    if not jobs:
        did_not_run("no expected jobs configured")
        log_run(vault_root, "check_freshness", "did-not-run", "no expected jobs configured")
        return EXIT_DEFECT

    if not log_path.exists() or log_path.stat().st_size == 0:
        did_not_run(f"no run log at {log_path}")
        for job in jobs:
            print(f"{job}: {DID_NOT_RUN} — no log", file=sys.stderr)
        print(f"0/{len(jobs)} jobs have a healthy run", file=sys.stderr)
        log_run(vault_root, "check_freshness", "did-not-run", f"no run log at {log_path}")
        return EXIT_DEFECT

    healthy, seen, lines, malformed = parse_log(log_path)
    now = datetime.now(timezone.utc)
    fresh = []
    problems = []

    for job in jobs:
        when = healthy.get(job)
        if when is None:
            problems.append(f"{job}: {DID_NOT_RUN} — no healthy line in {lines} log lines")
            continue
        age_h = (now - when).total_seconds() / 3600.0
        if age_h > args.max_age_hours:
            problems.append(f"{job}: last healthy run {age_h:.1f}h ago, threshold {args.max_age_hours}h")
        else:
            fresh.append((job, age_h))

    # In no list. The only real signal at this point: somebody built a tool and nobody decided
    # whether it is watched. It does NOT change the exit code -- an unclassified tool has not
    # failed, and a chain that goes red the first time a user adds a tool of their own is one
    # they will stop running.
    # `configured` is subtracted as well as `jobs`, so a `--jobs` override does not turn the rest
    # of the user's own watch list into news.
    #
    # THE POPULATION IS THE FOLDER AS WELL AS THE LOG (2026-07-30, #24). It used to be `seen`
    # alone, and that made the check confirm its own silence: a tool no chain calls never writes
    # a line, and without a line it could not turn up as unclassified. Measured that day against
    # a fresh vault -- `0 unclassified` while count_tokens sat in the folder in neither list, the
    # one tool the report existed to name. The self-confirming shape is the point: the tools that
    # fall out of the chain are exactly the ones a log-derived population cannot see.
    on_disk, unreadable = loggable_tools(vault_root)
    unclassified = sorted((seen | on_disk) - set(jobs) - set(configured)
                          - set(on_demand) - set(not_invoked))

    print(
        f"{len(fresh)}/{len(jobs)} jobs fresh · {len(on_demand)} on demand · "
        f"{len(not_invoked)} not invoked · {len(unclassified)} unclassified · "
        f"{lines} log lines · {malformed} malformed · threshold {args.max_age_hours}h"
    )
    for job, age_h in fresh:
        print(f"  {job}: {age_h:.1f}h ago")
    if unclassified:
        print(f"  in none of the three lists: {', '.join(unclassified)}")
    # After the measurement, never instead of it: this says nothing about the vault's health and
    # must not read as a verdict. It also cannot change the exit code -- an old installation is
    # not a defect, and a chain that goes red because two months passed is one that gets skipped.
    kit_note = installed_kit_note(vault_root, now)
    if kit_note:
        print(kit_note)
    if unreadable:
        print(f"  {unreadable} file(s) in {tool_folder(vault_root)} could not be read, so they "
              f"are outside every count above", file=sys.stderr)

    status = "defects" if (problems or malformed) else "ok"
    log_run(vault_root, "check_freshness", status,
            f"{len(fresh)}/{len(jobs)} fresh · {len(unclassified)} unclassified")

    if problems or malformed:
        for problem in problems:
            print(problem, file=sys.stderr)
        if malformed:
            print(f"{malformed} malformed log lines", file=sys.stderr)
        return EXIT_DEFECT
    return EXIT_OK

# --------------------------------- vaultkit.py tokens   (was count_tokens.py)
"""Report the size of what was read, for cost.

Never invents a precision: every number is labelled `exact` or `estimated`. Without a real
tokenizer installed the token count is a chars/4 heuristic and says so on every line.
"""

CHARS_PER_TOKEN = 4.0


def tokenizer():
    """Return (name, callable) if a real tokenizer is importable, else (None, None)."""
    try:
        import tiktoken  # type: ignore

        enc = tiktoken.get_encoding("cl100k_base")
        return "tiktoken/cl100k_base", lambda s: len(enc.encode(s))
    except Exception:
        return None, None


def tokens_main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="+", help="files or directories")
    args = parser.parse_args(argv)

    name, encode = tokenizer()
    precision = "exact" if encode else "estimated"

    files = []
    for raw in args.paths:
        path = Path(raw).resolve()
        if path.is_dir():
            files.extend(walk_markdown(path))
        elif path.is_file():
            files.append(path)
        else:
            print(f"not found: {path}", file=sys.stderr)
            return EXIT_USAGE

    chars = 0
    tokens = 0
    skipped = 0
    for path in files:
        try:
            # utf-8-sig so a byte-order mark is not counted as a character of content.
            text = path.read_text(encoding="utf-8-sig", errors="replace")
        except OSError as exc:
            skipped += 1
            print(f"{path.name}: unreadable ({exc})", file=sys.stderr)
            continue
        chars += len(text)
        tokens += encode(text) if encode else int(len(text) / CHARS_PER_TOKEN)

    if not files:
        did_not_run("0 files matched")
        return EXIT_DEFECT

    source = name if name else f"chars/{CHARS_PER_TOKEN:g} heuristic"
    print(f"{tokens} tokens ({precision}, {source}) · {chars} chars · {len(files) - skipped}/{len(files)} files")
    if skipped:
        print(f"{skipped} files skipped — denominator incomplete", file=sys.stderr)
        return EXIT_DEFECT
    return EXIT_OK


def main(argv: list[str] | None = None) -> int:
    """Hand the remaining arguments to the subcommand's own parser, untouched.

    NO SHARED ARGUMENT PARSING, ON PURPOSE. `--vault` means one project directory after `index`
    and the vault root after `links`; `--root` exists only for `index`. That collision is the
    trap the `/vaultkit` command was written for, and folding the guards into one file did not
    remove it -- it only put it inside one file. A parser here that tried to unify the two would
    either pick a winner or invent a third spelling. Each subcommand keeps its own parser and its
    own `--help`, so what a user types is what the section above documents.
    """
    argv = list(sys.argv[1:] if argv is None else argv)
    if not argv or argv[0] in ("-h", "--help"):
        parser = argparse.ArgumentParser(prog="vaultkit.py", description=__doc__,
                                         formatter_class=argparse.RawDescriptionHelpFormatter)
        parser.add_argument("subcommand", choices=sorted(COMMANDS),
                            help="the guard to run; each has its own --help")
        parser.parse_args(argv)
        return EXIT_USAGE

    name, rest = argv[0], argv[1:]
    if name not in COMMANDS:
        print(f"vaultkit.py: no subcommand {name!r}. Known: {', '.join(sorted(COMMANDS))}",
              file=sys.stderr)
        return EXIT_USAGE
    return COMMANDS[name]["run"](rest)


# --------------------------------------------------------------------------- the register
#
# AT THE END OF THE FILE, AND THAT IS LOAD-BEARING THREE TIMES OVER.
#
# 1. It is where `freshness` takes its own population from. That population used to be a GUESS:
#    the folder was globbed for `*.py` and a stem taken when the text mentioned the logging call,
#    so `vault_paths.py` appeared because it DEFINED that call and needed a `not_invoked` entry
#    as a patch -- and a tool that forgot to log was invisible by construction. With one file
#    the guess has no meaning left at all: every job would come out as `vaultkit`. `job` below is
#    the answer instead, and `None` says "reaches no verdict, never logs" out loud.
# 2. It is what build_kit.py holds every logging literal to. The rule used to be "the label
#    equals the filename", and after the merge there is one filename for six jobs.
# 3. It is what `upgrade.py --prove` asks for to decide this file arrived whole -- and that
#    check lives THERE, in another block, because nothing here can do it. Measured on this
#    machine 2026-07-31, cutting this file twice, once just above this register and once
#    mid-file after a complete function: `compileall` exit 0, `import vaultkit` exit 0, and
#    `vaultkit.py index` exit 0 having done nothing at all. Both cuts take the entry point below
#    with them, so the script runs to the end of what arrived and reports success. Anything put
#    at the end to catch that goes with the same cut. One long block makes truncation quieter,
#    not louder, and the only reader that can tell is a separate file.
#
# The folder scan in `freshness` stays, for the user's OWN tools: this register describes what
# the kit brought, not what they wrote.

COMMANDS: dict[str, Command] = {
    "index": {"run": index_main, "job": "build_index"},
    "links": {"run": links_main, "job": "check_links"},
    "duplicates": {"run": duplicates_main, "job": "check_duplicates"},
    "freshness": {"run": freshness_main, "job": "check_freshness"},
    "command": {"run": command_main, "job": "write_command"},
    # No job: it reports a size and reaches no verdict, so nothing can be late and no chain has
    # anything to act on. That is also why no command line has to name it.
    "tokens": {"run": tokens_main, "job": None},
}


if __name__ == "__main__":
    raise SystemExit(main())
