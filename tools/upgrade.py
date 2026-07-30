"""Update an installed tool folder from a newer kit file.

A vault that was set up months ago carries the scripts as they were that day. This reads a
newer `claude-obsidian-vault-kit.md`, extracts the scripts embedded in it, and reports what
would change. Nothing is written without `--apply`.

    python upgrade.py <path-to-kit.md>              show what would change
    python upgrade.py <path-to-kit.md> --apply      write the changes, then prove them
    python upgrade.py --stamp <path-to-kit.md>      record which kit installed this folder

`--apply` reruns the suites and the acceptance driver afterwards and fails loudly if either
goes red, because a tool folder that was updated but never re-proven is the state this kit
exists to prevent.

`--stamp` is the other end of the same path: it writes `kit-version.txt` and nothing else, so a
folder knows its own version from the first install onwards instead of from the first update.

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
    # utf-8-sig: a downloaded kit file re-saved by a Windows editor starts with a BOM, and
    # VERSION_RE anchors at ^. The match then fails and the newer kit reads as "unversioned"
    # -- the one number the whole update path compares against.
    text = Path(path).read_text(encoding="utf-8-sig")
    blocks = {name: body + "\n" for name, body in BLOCK_RE.findall(text)}
    if not blocks:
        raise SystemExit(f"{path}: no script blocks found -- is this a kit file?")
    version = VERSION_RE.search(text)
    return blocks, (version.group(1) if version else "unversioned")


def installed_version():
    """The version of the folder we are updating, if the kit that wrote it left one."""
    stamp = TOOLS / "kit-version.txt"
    return stamp.read_text(encoding="utf-8-sig").strip() if stamp.exists() else "unknown"


def write_stamp(version):
    """The one place kit-version.txt is spelled. Both writers go through here."""
    target = TOOLS / "kit-version.txt"
    target.write_text(version + "\n", encoding="utf-8", newline="\n")
    return target


def stamp(kit_path):
    """Write kit-version.txt from the kit file's own stamp line. Nothing else, no --apply.

    WHY THIS IS A COMMAND AND NOT A SENTENCE IN THE CONTRACT (2026-07-29): SECTION 8 used to
    tell the agent to type twelve hex characters into a file, copied by eye from line 1 of the
    kit. Operating rule 7 of that same contract says the scripts do the mechanical work, and
    copying a value that already exists verbatim in a file on disk is the most mechanical work
    there is. It also left a hole: `--apply` below is the only other writer, so until a *second*
    kit ever shipped, nothing wrote the file and a fresh folder answered `installed: unknown` --
    the one question the whole update path exists to answer.

    A file with no stamp line is refused rather than recorded as "unversioned". That string
    would then be compared against every future kit forever and never match, which is a wrong
    answer wearing a right answer's clothes.
    """
    text = Path(kit_path).read_text(encoding="utf-8-sig")
    found = VERSION_RE.search(text)
    if not found:
        print(f"{kit_path}: no `<!-- kit-version: … -->` line — nothing to stamp. An unstamped "
              f"file cannot say which kit this folder came from, and a guessed value is worse "
              f"than none.", file=sys.stderr)
        return 1
    target = write_stamp(found.group(1))
    print(f"wrote {target.name}: {found.group(1)}")
    return 0


def classify(blocks):
    """Compare each embedded block against the file on disk.

    READ AS utf-8-sig AND errors="replace", AND BOTH HALVES ARE LOAD-BEARING (2026-07-30). The
    contract states this rule for every file the user might have touched (SECTION 6, "Read every
    file the user might have written as `utf-8-sig`, never `utf-8`") and this line was the one
    place in this file that broke it -- three other reads here already had it, so it read as an
    oversight rather than a decision.

    The two halves fail differently, which is why neither alone is enough:

      - A BOM does NOT raise. It decodes to \\ufeff, the comparison against the block fails, and
        the file is listed as `overwrite` -- an untouched file reported as a local edit. The user
        opened it in Notepad once; that is the whole cause. This is the silent half.
      - Only genuinely invalid UTF-8 raises, and then UnicodeDecodeError comes out of a helper
        with no filename in the message, taking the whole update down. `errors="replace"` turns
        that into a mismatch, so the file is named as `overwrite` and the run survives.

    Undo recipes, both measured on this machine 2026-07-30, and they are not symmetric:

      - Set the encoding back to `utf-8` (dropping errors= with it): test_upgrade 13/15. BOTH
        cases go red, because `utf-8` without a replacement handler raises on the bad byte too.
      - Keep `utf-8-sig` and drop only `errors="replace"`: test_upgrade 14/15, and only
        `test_an_undecodable_file_is_named_rather_than_crashing_the_run` moves. That asymmetry is
        the measurement worth keeping -- it shows the BOM half and the crash half are two defects
        sharing one line, and fixing either alone leaves the other.
    """
    same, changed, added = [], [], []
    for name, body in sorted(blocks.items()):
        target = TOOLS / name
        if not target.exists():
            added.append(name)
        elif target.read_text(encoding="utf-8-sig",
                              errors="replace").replace("\r\n", "\n") == body:
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
    parser.add_argument("kit", nargs="?", help="path to a newer claude-obsidian-vault-kit.md")
    parser.add_argument("--apply", action="store_true", help="write the changes")
    parser.add_argument("--stamp", metavar="KITFILE",
                        help="write kit-version.txt from KITFILE's stamp line and do nothing else")
    args = parser.parse_args(argv)

    if args.stamp:
        return stamp(args.stamp)
    if not args.kit:
        parser.error("give a kit file to compare against, or --stamp <kitfile> to record one")

    blocks, new_version = read_kit(args.kit)
    same, changed, added = classify(blocks)
    installed = installed_version()

    print(f"installed: {installed} · kit file: {new_version}")
    print(f"{len(same)} unchanged · {len(changed)} would be overwritten · {len(added)} new")
    for name in changed:
        print(f"  overwrite  {name}")
    for name in added:
        print(f"  add        {name}")

    # A NEWER KIT WHOSE SCRIPTS DID NOT CHANGE STILL MOVES THE VERSION (2026-07-30). The return
    # below used to sit in front of the --apply branch, so write_stamp() further down was
    # unreachable on this path: a release that only edited the contract or the SECTION 10 header
    # left the folder stamped with the version before it, forever. `installed:` then answered the
    # one question this whole path exists for with a number that was true yesterday -- and the
    # folder was fully up to date, which is what makes it hard to notice.
    #
    # Said either way, never done silently: without --apply this only reports the gap, because
    # "nothing is written without --apply" is the promise the rest of the file keeps. An
    # unversioned kit is not stamped from here for the same reason stamp() refuses it -- that
    # string would be compared against every future kit and never match.
    if not changed and not added:
        if new_version != "unversioned" and installed != new_version:
            if args.apply:
                write_stamp(new_version)
                print(f"every script is already current · stamp corrected: "
                      f"{installed} → {new_version}")
            else:
                print(f"every script is already current, but the stamp still reads {installed}. "
                      f"Re-run with --apply to record {new_version}.")
            return 0
        print("nothing to do.")
        return 0
    if not args.apply:
        print("\nnothing written. Re-run with --apply to write these files.")
        return 0

    for name in changed + added:
        (TOOLS / name).write_text(blocks[name], encoding="utf-8", newline="\n")
    write_stamp(new_version)
    print(f"\nwrote {len(changed) + len(added)} files. Proving them:")
    if not prove():
        print("the updated folder does not pass its own checks -- restore it from git.",
              file=sys.stderr)
        return 1
    print(f"updated to {new_version}, suites and acceptance green.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
