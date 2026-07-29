"""Report the size of what was read, for cost.

Never invents a precision: every number is labelled `exact` or `estimated`. Without a real
tokenizer installed the token count is a chars/4 heuristic and says so on every line.
"""

import sys

for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass

import argparse
from pathlib import Path

from vault_paths import walk_markdown

CHARS_PER_TOKEN = 4.0


def tokenizer():
    """Return (name, callable) if a real tokenizer is importable, else (None, None)."""
    try:
        import tiktoken  # type: ignore

        enc = tiktoken.get_encoding("cl100k_base")
        return "tiktoken/cl100k_base", lambda s: len(enc.encode(s))
    except Exception:
        return None, None


def main(argv=None):
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
            return 2

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
        print("did not run: 0 files matched", file=sys.stderr)
        return 1

    source = name if name else f"chars/{CHARS_PER_TOKEN:g} heuristic"
    print(f"{tokens} tokens ({precision}, {source}) · {chars} chars · {len(files) - skipped}/{len(files)} files")
    if skipped:
        print(f"{skipped} files skipped — denominator incomplete", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
