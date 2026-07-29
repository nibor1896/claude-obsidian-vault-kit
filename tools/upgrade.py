"""Update an installed tool folder from a newer kit file.

A vault that was set up months ago carries the scripts as they were that day. This reads a
newer `claude-obsidian-vault-kit.md`, extracts the scripts embedded in it, and reports what
would change. Nothing is written without `--apply`.

    python upgrade.py <path-to-kit.md>              show what would change
    python upgrade.py <path-to-kit.md> --apply      write the changes, then prove them

`--apply` reruns the suites and the acceptance driver afterwards and fails loudly if either
goes red, because a tool folder that was updated but never re-proven is the state this kit
exists to prevent.

Local edits are overwritten. They are listed first, by name, so that is a decision and not a
surprise.
"""

import argparse
import re
import subprocess
import sys
from pathlib import Path

TOOLS = Path(__file__).resolve().parent

for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass

BLOCK_RE = re.compile(r"^### `([^`]+)`\n\n```(?:python|json)\n(.*?)\n```", re.S | re.M)
VERSION_RE = re.compile(r"^<!-- kit-version: ([0-9a-f]{12}) -->$", re.M)


def read_kit(path):
    text = Path(path).read_text(encoding="utf-8")
    blocks = {name: body + "\n" for name, body in BLOCK_RE.findall(text)}
    if not blocks:
        raise SystemExit(f"{path}: no script blocks found -- is this a kit file?")
    version = VERSION_RE.search(text)
    return blocks, (version.group(1) if version else "unversioned")


def installed_version():
    """The version of the folder we are updating, if the kit that wrote it left one."""
    stamp = TOOLS / "kit-version.txt"
    return stamp.read_text(encoding="utf-8").strip() if stamp.exists() else "unknown"


def classify(blocks):
    same, changed, added = [], [], []
    for name, body in sorted(blocks.items()):
        target = TOOLS / name
        if not target.exists():
            added.append(name)
        elif target.read_text(encoding="utf-8").replace("\r\n", "\n") == body:
            same.append(name)
        else:
            changed.append(name)
    return same, changed, added


def prove():
    """Suites and acceptance, from the folder we just wrote."""
    ok = True
    # No fixture count in the string: exit 0 already means every one behaved, and a literal
    # here goes stale the moment a fixture is added.
    for script, want in (("run_suites.py", "suites green"),
                         ("acceptance.py", "checks behaved as specified")):
        result = subprocess.run([sys.executable, str(TOOLS / script)],
                                capture_output=True, cwd=str(TOOLS))
        out = result.stdout.decode("utf-8", errors="replace")
        first = next((l for l in out.splitlines() if want.split()[0] in l), out.strip()[:80])
        state = "ok  " if result.returncode == 0 and want in out else "FAIL"
        print(f"  {state} {script}: {first}")
        ok = ok and state == "ok  "
    return ok


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("kit", help="path to a newer claude-obsidian-vault-kit.md")
    parser.add_argument("--apply", action="store_true", help="write the changes")
    args = parser.parse_args(argv)

    blocks, new_version = read_kit(args.kit)
    same, changed, added = classify(blocks)

    print(f"installed: {installed_version()} · kit file: {new_version}")
    print(f"{len(same)} unchanged · {len(changed)} would be overwritten · {len(added)} new")
    for name in changed:
        print(f"  overwrite  {name}")
    for name in added:
        print(f"  add        {name}")

    if not changed and not added:
        print("nothing to do.")
        return 0
    if not args.apply:
        print("\nnothing written. Re-run with --apply to write these files.")
        return 0

    for name in changed + added:
        (TOOLS / name).write_text(blocks[name], encoding="utf-8", newline="\n")
    (TOOLS / "kit-version.txt").write_text(new_version + "\n", encoding="utf-8", newline="\n")
    print(f"\nwrote {len(changed) + len(added)} files. Proving them:")
    if not prove():
        print("the updated folder does not pass its own checks -- restore it from git.",
              file=sys.stderr)
        return 1
    print(f"updated to {new_version}, suites and acceptance green.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
