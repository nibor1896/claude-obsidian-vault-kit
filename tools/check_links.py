"""Check that every [[wikilink]] in the vault resolves to a file.

Reports numerator AND denominator, and distinguishes three outcomes: pass, fail, and
"did not run". A checker that scanned zero files must never report "0 broken".
"""

import sys

for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass

import argparse
import re
from collections import defaultdict
from pathlib import Path

from vault_paths import SKIP_DIRS, log_run, walk_markdown

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


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--vault", required=True, help="vault root")
    args = parser.parse_args(argv)

    vault_root = Path(args.vault).resolve()
    if not vault_root.is_dir():
        print(f"not a directory: {vault_root}", file=sys.stderr)
        return 2

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
        print(f"did not run: 0 of {len(files)} markdown files scanned", file=sys.stderr)
        log_run(vault_root, "check_links", "did-not-run", "0 files scanned")
        return 1

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
        return 1
    if skipped:
        print(f"{skipped} files skipped — denominator incomplete", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
