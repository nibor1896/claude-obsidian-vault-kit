"""Flag notes whose content overlaps, so one insight does not end up living in two files.

Every hit gets a decision: a flagged pair makes the run red. Ignoring it is not an option
the tool offers.

The threshold is a knob, not a truth. On a vault with a handful of notes the number this
prints is arithmetic, not evidence — recalibrate once there is real volume:

    python check_duplicates.py --vault <dir> --threshold 0.75
"""

import sys

for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass

import argparse
import re
from itertools import combinations
from pathlib import Path

from vault_paths import is_index_file, log_run, walk_markdown

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


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--vault", required=True, help="vault root or a single project directory")
    parser.add_argument("--threshold", type=float, default=DEFAULT_THRESHOLD)
    args = parser.parse_args(argv)

    root = Path(args.vault).resolve()
    if not root.is_dir():
        print(f"not a directory: {root}", file=sys.stderr)
        return 2

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
        print(
            f"did not run: {len(comparable)} comparable notes — "
            f"a pair needs two (threshold {args.threshold})"
        )
        log_run(root, "check_duplicates", "did-not-run", f"{len(comparable)} notes")
        return 0

    print(
        f"{len(flagged)} pairs flagged of {len(pairs)} compared · "
        f"{len(comparable)} notes · threshold {args.threshold} · {skipped} skipped"
    )
    log_run(root, "check_duplicates", "ok" if not flagged else "defects", f"{len(flagged)} flagged")

    if flagged:
        for a, b, score in sorted(flagged, key=lambda t: -t[2]):
            print(f"{a.name}: {score:.2f} overlap with {b.name}", file=sys.stderr)
        print(f"{len(flagged)} duplicate pairs need a decision", file=sys.stderr)
        return 1
    if skipped:
        print(f"{skipped} files skipped — denominator incomplete", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
