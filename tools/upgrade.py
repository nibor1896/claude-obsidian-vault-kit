"""Update an installed tool folder from a newer kit file.

A vault that was set up months ago carries the scripts as they were that day. This reads a
newer `claude-obsidian-vault-kit.md`, extracts the scripts embedded in it, and reports what
would change. Nothing is written without `--apply`.

    python upgrade.py <path-to-kit.md>              show what would change
    python upgrade.py <path-to-kit.md> --apply      write the changes, then prove them
    python upgrade.py --stamp <path-to-kit.md>      record which kit installed this folder
    python upgrade.py --prove                       check this folder as it stands

`--apply` reads every file it wrote back, compares it against the block it came from, then
compiles the folder and parses `jobs.json` before reporting success. The suites that used to run
here live in the kit's repository now and ran against these exact bytes before the release; what
this checks is that they arrived whole.

`--stamp` is the other end of the same path: it writes `kit-version.txt` and `kit-manifest.txt`, so
a folder knows its own version and its own file list from the first install onwards instead of from
the first update.

Local edits are overwritten. They are listed first, by name, so that is a decision and not a
surprise.

A file the new kit no longer carries is REMOVED, and `kit-manifest.txt` is the only thing that
makes that safe: it is the list of what this kit delivered, so what the user wrote themselves is
never a candidate. Without a manifest nothing is removed and the run says why -- a folder installed
by an older kit has exactly one blind update cycle, and the run after it can act.
"""

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

TOOLS = Path(__file__).resolve().parent

# This file, by name. It is delivered like every other script, so a kit that stopped shipping it
# would list it for removal -- and the run would delete the only tool that can repeat itself.
SELF = Path(__file__).name

STAMP_NAME = "kit-version.txt"
MANIFEST_NAME = "kit-manifest.txt"

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
    try:
        text = Path(path).read_text(encoding="utf-8-sig")
    except OSError as exc:
        # THE FIRST THING THE UPDATE PATH DOES (2026-07-31). A mistyped kit path used to come
        # back as a FileNotFoundError traceback -- verified by running it -- and a traceback on
        # the opening move reads as "this tool is broken", not as "that argument is wrong".
        # Exit 2 throughout this file means the environment refused an I/O operation, which is
        # a different repair from exit 1 (written, but it does not pass its own checks).
        print(f"{path}: cannot be read ({exc})", file=sys.stderr)
        raise SystemExit(2)
    blocks = {name: body + "\n" for name, body in BLOCK_RE.findall(text)}
    if not blocks:
        raise SystemExit(f"{path}: no script blocks found -- is this a kit file?")
    version = VERSION_RE.search(text)
    return blocks, (version.group(1) if version else "unversioned")


def installed_version() -> str:
    """The version of the folder we are updating, if the kit that wrote it left one.

    ONE LINE, ONE VALUE, AND IT STAYS THAT WAY. Every upgrade.py already installed out there
    reads this whole file and compares it against twelve hex characters. The moment
    kit-version.txt gains a second line, every one of those prints a mangled `installed:` and
    never matches again -- at exactly the users an update path exists to rescue. That is why
    the file list went into kit-manifest.txt beside it and not in here: a new file is additive
    and breaks no old installation, a new line in this one breaks all of them.
    """
    stamp = TOOLS / STAMP_NAME
    if not stamp.exists():
        return "unknown"
    try:
        return stamp.read_text(encoding="utf-8-sig").strip()
    except OSError as exc:
        # Not "unknown": that is the answer for a folder nobody ever stamped, and reusing it
        # here would report a broken file as a normal first install.
        print(f"{STAMP_NAME}: cannot be read ({exc})", file=sys.stderr)
        return "unreadable"


def installed_files() -> list[str] | None:
    """The file list the kit that wrote this folder left behind, or None when there is none.

    NONE IS NOT THE EMPTY LIST, AND THE DIFFERENCE IS THE WHOLE SAFETY. Empty means "that kit
    delivered nothing", which is never true; None means "nothing here knows what it delivered",
    which is the honest state of every folder installed before this file existed. Removal reads
    that as: remove nothing, say so, and record a manifest on the way out. Guessing -- treating
    every .py in the folder as ours -- would delete the user's own tools on the first update.
    """
    manifest = TOOLS / MANIFEST_NAME
    if not manifest.exists():
        return None
    try:
        text = manifest.read_text(encoding="utf-8-sig")
    except OSError as exc:
        print(f"{MANIFEST_NAME}: cannot be read ({exc}) — nothing will be removed",
              file=sys.stderr)
        return None
    return [line.strip() for line in text.splitlines() if line.strip()]


def write_stamp(version: str, files: list[str] | None = None):
    """The one place kit-version.txt and kit-manifest.txt are spelled. Every writer comes here.

    THE MANIFEST GOES FIRST AND THE STAMP LAST, INSIDE THIS FUNCTION TOO. The stamp is what a
    later run compares against to decide it has nothing to do, so it is the last thing written
    on every path: if anything before it fails, the next run recomputes the same plan and comes
    through. Written first, it would tell the next run the work is done while the work is not.

    `files=None` leaves the manifest alone -- for the paths that wrote no scripts and have no
    new delivery to record.

    Returns the kit-version.txt path on success and None when either write failed, having said
    why on stderr. Callers act on the None: a run that could not record what it did must not
    report a version it did not write.
    """
    if files is not None:
        manifest = TOOLS / MANIFEST_NAME
        try:
            manifest.write_text("".join(f"{name}\n" for name in sorted(files)),
                                encoding="utf-8", newline="\n")
        except OSError as exc:
            print(f"{MANIFEST_NAME}: not written ({exc})", file=sys.stderr)
            return None
    target = TOOLS / STAMP_NAME
    try:
        target.write_text(version + "\n", encoding="utf-8", newline="\n")
    except OSError as exc:
        print(f"{target.name}: not written ({exc})", file=sys.stderr)
        return None
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

    IT WRITES THE MANIFEST TOO, AND THAT IS WHAT ENDS THE BLIND CYCLE. The kit file in the
    user's hand already lists everything it delivers, one fenced block per file. Recording that
    at install time means the FIRST update can already remove what a newer kit drops -- wait for
    the first `--apply` to write it and every fresh install spends one update cycle unable to
    remove anything. A kit file with no blocks (a stand-in, a fragment) leaves the manifest
    alone rather than recording an empty delivery, which would read as "this kit brought no
    files" and make every file in the folder look like the user's own.
    """
    try:
        text = Path(kit_path).read_text(encoding="utf-8-sig")
    except OSError as exc:
        # Same reasoning as read_kit(): --stamp is the other entry point, and a mistyped path
        # here produced the same traceback.
        print(f"{kit_path}: cannot be read ({exc})", file=sys.stderr)
        return 2
    found = VERSION_RE.search(text)
    if not found:
        print(f"{kit_path}: no `<!-- kit-version: … -->` line — nothing to stamp. An unstamped "
              f"file cannot say which kit this folder came from, and a guessed value is worse "
              f"than none.", file=sys.stderr)
        return 1
    delivered = sorted(name for name, _ in BLOCK_RE.findall(text))
    target = write_stamp(found.group(1), delivered or None)
    if target is None:
        return 2
    print(f"wrote {target.name}: {found.group(1)}")
    if delivered:
        print(f"wrote {MANIFEST_NAME}: {len(delivered)} files this kit delivers")
    return 0


def classify(blocks: dict[str, str],
             delivered: list[str] | None) -> tuple[list[str], list[str], list[str], list[str]]:
    """Compare each embedded block against the file on disk, and the manifest against the blocks.

    ANNOTATED BECAUSE IT RETURNS FOUR LISTS OF THE SAME TYPE. Three of them used to come back
    unannotated and a caller unpacking them in the wrong order would still run -- silently
    overwriting the files it meant to leave alone. The annotation is the only thing between a
    future fourth list and that.

    `removed` is the manifest minus the new kit's blocks. Not the folder minus the blocks: the
    user's own tools live in that folder too, and the difference between those two subtractions
    is whether an update deletes work nobody in this kit ever wrote. `delivered is None` means
    no manifest, and then the answer is the empty list, never a guess.

    A name that is in the manifest, gone from the new kit AND already gone from disk stays in
    the list on purpose. That is the state an update leaves behind when it dies between the
    delete and the manifest write, and keeping it there is what makes the next run finish the
    job -- the unlink is a no-op, the manifest gets rewritten, and the folder stops being
    half-updated. Filtering it out here would leave that manifest stale forever.

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

    Undo recipes, both re-measured on this machine 2026-07-31, and they are not symmetric:

      - Set the encoding back to `utf-8` (dropping errors= with it): test_upgrade 32/34. BOTH
        cases go red, because `utf-8` without a replacement handler raises on the bad byte too.
      - Keep `utf-8-sig` and drop only `errors="replace"`: test_upgrade 33/34, and only
        `test_an_undecodable_file_is_named_rather_than_crashing_the_run` moves. That asymmetry is
        the measurement worth keeping -- it shows the BOM half and the crash half are two defects
        sharing one line, and fixing either alone leaves the other.
    """
    same, changed, added = [], [], []
    for name, body in sorted(blocks.items()):
        target = TOOLS / name
        if not target.exists():
            added.append(name)
            continue
        try:
            current = target.read_text(encoding="utf-8-sig", errors="replace")
        except OSError as exc:
            # Unreadable is not "same". Overwriting is the repair for anything that cannot be
            # compared, so it is named under `overwrite` rather than taking the run down.
            print(f"{name}: cannot be read ({exc}) — listed for overwrite", file=sys.stderr)
            changed.append(name)
            continue
        if current.replace("\r\n", "\n") == body:
            same.append(name)
        else:
            changed.append(name)
    removed = [] if delivered is None else sorted(
        name for name in set(delivered) if name not in blocks and name != SELF)
    return same, changed, added, removed


def write_file(name: str, body: str) -> bool:
    """Write one script through a temp file and a single replace. True when it landed.

    ATOMIC BECAUSE THIS FILE REWRITES ITSELF. upgrade.py is delivered like every other script,
    so nearly every update overwrites the tool that is running. A write interrupted halfway
    through leaves a truncated repair tool, and the one thing a user needs at that moment is
    the ability to run it again. `replace()` is atomic on the same filesystem: the target is
    either the old script or the new one, never half of either.

    The temp file is inert if a crash leaves one behind -- it ends in `.upgrade-tmp`, so
    `run_suites.py`'s `test_*.py` glob and `check_freshness.py`'s `*.py` glob both skip it, and
    the next successful run writes over it.
    """
    target = TOOLS / name
    tmp = target.with_name(target.name + ".upgrade-tmp")
    try:
        tmp.write_text(body, encoding="utf-8", newline="\n")
        tmp.replace(target)
    except OSError as exc:
        print(f"{name}: not written ({exc})", file=sys.stderr)
        try:
            tmp.unlink(missing_ok=True)
        except OSError:
            pass
        return False
    return True


def reads_back(name: str, body: str) -> bool:
    """Read a file we just wrote and compare it against the block it came from.

    This runs over every written file BEFORE anything is deleted. A folder that lost a script
    to make room for one that did not land is the single state this order exists to prevent,
    and the check is cheap next to what it guards.

    `newline=""` turns off newline translation, so this compares what landed rather than what a
    reader would make of it. CRLF is then normalised exactly the way classify() does it, because
    a sync client that rewrote the line endings has not corrupted anything.
    """
    try:
        written = (TOOLS / name).read_text(encoding="utf-8", newline="")
    except OSError as exc:
        print(f"{name}: written, but could not be read back ({exc})", file=sys.stderr)
        return False
    return written.replace("\r\n", "\n") == body


def remove_file(name: str) -> bool:
    """Delete one file this kit delivered and no longer does, plus its cached bytecode.

    `missing_ok=True` is not politeness. It is what makes a half-finished update finishable: a
    run that deleted the file and then died before rewriting the manifest leaves that name in
    the list, and the next run has to be able to walk over it without failing.

    The `__pycache__` sweep is hygiene, not correctness -- Python 3 will not import a cached
    entry whose source is gone. A `.pyc` with no `.py` beside it is still something a user
    finds in a listing and cannot explain, so it goes.
    """
    try:
        (TOOLS / name).unlink(missing_ok=True)
    except OSError as exc:
        print(f"{name}: not removed ({exc})", file=sys.stderr)
        return False
    cache = TOOLS / "__pycache__"
    if cache.is_dir():
        stem = Path(name).stem
        for stale in list(cache.glob(f"{stem}.pyc")) + list(cache.glob(f"{stem}.*.pyc")):
            try:
                stale.unlink()
            except OSError:
                pass
    return True


def prove():
    """What can still be proven about the folder we just wrote, on this machine.

    IT USED TO RUN THE SUITES AND THE ACCEPTANCE DRIVER, AND THEY ARE NOT HERE ANY MORE
    (2026-07-31). Both moved to the kit's repository, where they run over these exact bytes
    before a release is published. Pretending otherwise would mean shipping 126 unit tests into
    every vault so that an update could re-answer a question about code that did not change
    between two kit files.

    SAY WHAT THAT COSTS, BECAUSE IT IS A REAL LOSS: after an update this folder can no longer
    show that its guards go RED on bad input. That claim now rests on the release, and on the
    byte comparison in classify() plus the read-back in --apply, which together say the files
    here are the files the kit shipped. What is left to check locally is that they are whole:
    every script compiles, and the one non-Python file parses. A truncated write and a block
    that never arrived both land here.
    """
    ok = True
    result = subprocess.run([sys.executable, "-m", "compileall", "-q", str(TOOLS)],
                            capture_output=True, cwd=str(TOOLS))
    detail = (result.stdout + result.stderr).decode("utf-8", errors="replace").strip()
    state = "ok  " if result.returncode == 0 else "FAIL"
    print(f"  {state} every .py compiles{'' if result.returncode == 0 else ': ' + detail[:200]}")
    ok = ok and result.returncode == 0

    config = TOOLS / "jobs.json"
    try:
        json.loads(config.read_text(encoding="utf-8-sig"))
        print(f"  ok   {config.name} parses")
    except (OSError, ValueError) as exc:
        print(f"  FAIL {config.name}: {exc}")
        ok = False
    return ok


def prove_from_disk() -> bool:
    """Run the checks from the upgrade.py that is now ON DISK, not the one in memory.

    THIS FILE REWRITES ITSELF AND THE RUNNING PROCESS KEEPS THE OLD CODE (2026-07-31). Python
    read this module before the write; everything called afterwards is the previous version.
    Measured on this machine while crossing the release that moved the suites out of the
    delivery: the folder came out exactly right -- 9 files, 13 correctly removed, every check
    green -- and the run ended with `FAIL run_suites.py`, `FAIL acceptance.py` and
    "restore it from git", because the old prove() went looking for the two files the new kit
    had just correctly deleted. The worst possible advice, on a healthy folder.

    So when this file is one of the files written, the checks run in a fresh process, which
    loads the new code. When it is not, the code in memory IS the code on disk and there is
    nothing to re-exec for.

    A kit older than this one has no `--prove`, and argparse then exits 2 with "unrecognized
    arguments". That is named rather than reported as a broken folder -- it means the update
    moved backwards, not that anything is wrong.
    """
    result = subprocess.run([sys.executable, str(TOOLS / SELF), "--prove"],
                            capture_output=True, cwd=str(TOOLS))
    out = result.stdout.decode("utf-8", errors="replace").rstrip()
    err = result.stderr.decode("utf-8", errors="replace").rstrip()
    if out:
        print(out)
    if result.returncode == 2 and "unrecognized arguments" in err:
        print("  ??   the kit you moved to has an upgrade.py without --prove, so the folder "
              "could not be checked from the new code. Nothing is wrong with what was written.",
              file=sys.stderr)
        return True
    if err:
        print(err, file=sys.stderr)
    return result.returncode == 0


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("kit", nargs="?", help="path to a newer claude-obsidian-vault-kit.md")
    parser.add_argument("--apply", action="store_true", help="write the changes")
    parser.add_argument("--stamp", metavar="KITFILE",
                        help="write kit-version.txt from KITFILE's stamp line and do nothing else")
    parser.add_argument("--prove", action="store_true",
                        help="check this tool folder as it stands -- every script compiles and "
                             "jobs.json parses -- and do nothing else")
    args = parser.parse_args(argv)

    if args.prove:
        return 0 if prove() else 1
    if args.stamp:
        return stamp(args.stamp)
    if not args.kit:
        parser.error("give a kit file to compare against, or --stamp <kitfile> to record one")

    blocks, new_version = read_kit(args.kit)
    delivered = installed_files()
    same, changed, added, removed = classify(blocks, delivered)
    installed = installed_version()

    print(f"installed: {installed} · kit file: {new_version}")
    print(f"{len(same)} unchanged · {len(changed)} would be overwritten · {len(added)} new · "
          f"{len(removed)} would be removed")
    for name in changed:
        print(f"  overwrite  {name}")
    for name in added:
        print(f"  add        {name}")
    for name in removed:
        note = "" if (TOOLS / name).exists() else "  — already gone; the manifest still lists it"
        print(f"  remove     {name}{note}")
    if delivered is None:
        print(f"  no {MANIFEST_NAME} beside the stamp, so nothing is removed. This folder was "
              f"installed by a kit that left no file list, and guessing which files are the "
              f"kit's would put the user's own tools at risk. Applying this kit records one, "
              f"and the update after it can remove what a newer kit drops.")

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
    #
    # A MISSING MANIFEST IS THE SECOND REASON THIS BRANCH CANNOT JUST SAY "nothing to do"
    # (2026-07-31). A folder whose scripts are all current and whose stamp already matches can
    # still be one that no kit ever left a file list beside -- and if this path returned there,
    # it would never get one, so the blind cycle would never end. `--apply` records it.
    if not changed and not added and not removed:
        stale_stamp = new_version != "unversioned" and installed != new_version
        if stale_stamp or delivered is None:
            if args.apply:
                if write_stamp(new_version, sorted(blocks)) is None:
                    return 2
                if stale_stamp:
                    print(f"every script is already current · stamp corrected: "
                          f"{installed} → {new_version}")
                else:
                    print(f"every script is already current · {MANIFEST_NAME} recorded, so the "
                          f"next update can remove what a newer kit drops")
            elif stale_stamp:
                print(f"every script is already current, but the stamp still reads {installed}. "
                      f"Re-run with --apply to record {new_version}.")
            else:
                print(f"every script is already current, but there is no {MANIFEST_NAME} beside "
                      f"the stamp. Re-run with --apply to record one.")
            return 0
        print("nothing to do.")
        return 0
    if not args.apply:
        what = "write and remove these files" if removed else "write these files"
        print(f"\nnothing written, nothing removed. Re-run with --apply to {what}.")
        return 0

    # PER FILE, AND THE LOOP DOES NOT STOP AT THE FIRST REFUSAL (2026-07-31). One unwritable
    # target used to end the run with a traceback that named the exception and not the file, and
    # every script after it in the list went unwritten with nothing said about them either. Now
    # each failure is named and the rest still land: a folder that got 20 of 22 files and knows
    # which two it is missing can be repaired; one that stopped somewhere unnamed cannot.
    #
    # THE ORDER BELOW IS THE IDEMPOTENCE, AND IT IS NOT NEGOTIABLE: write, read back, abort on a
    # mismatch BEFORE anything is deleted, delete, manifest, stamp, prove. Every step before the
    # stamp is repeatable, and the stamp is what a later run reads to decide it is done -- so it
    # goes last on every path. Move it earlier and a run that died in the middle tells the next
    # one the work is finished while the folder is half old.
    refused = []
    for name in changed + added:
        if not write_file(name, blocks[name]):
            refused.append(name)
    if refused:
        # No stamp, no manifest. kit-version.txt naming a version this folder does not carry is
        # the same wrong-answer-in-right-answer's-clothes that stamp() refuses "unversioned" for.
        print(f"\n{len(changed) + len(added) - len(refused)} of {len(changed) + len(added)} files "
              f"written · {len(refused)} refused: {', '.join(refused)}\n"
              f"Nothing was removed and {STAMP_NAME} was NOT updated -- the folder is part old, "
              f"part new, and a stamp would claim otherwise. Fix the cause and re-run --apply.",
              file=sys.stderr)
        return 2

    mismatched = [name for name in changed + added if not reads_back(name, blocks[name])]
    if mismatched:
        print(f"\n{len(mismatched)} file(s) do not read back as the kit wrote them: "
              f"{', '.join(mismatched)}\n"
              f"Nothing was removed and nothing was stamped, so this folder still has every "
              f"file it started with. Re-run --apply once the cause is fixed.", file=sys.stderr)
        return 2

    kept = [name for name in removed if not remove_file(name)]
    if kept:
        # Same reasoning as a refused write: the manifest must not claim a file is gone while it
        # is still there, or nothing will ever try again.
        print(f"\n{len(kept)} file(s) could not be removed: {', '.join(kept)}\n"
              f"{MANIFEST_NAME} was NOT updated, so the next --apply tries them again.",
              file=sys.stderr)
        return 2

    if write_stamp(new_version, sorted(blocks)) is None:
        print("the scripts are current, the stamp is not -- re-run --apply once it can be written.",
              file=sys.stderr)
        return 2
    written = len(changed) + len(added)
    print(f"\nwrote {written} files, removed {len(removed)}. Proving them:")
    checked = prove_from_disk() if SELF in changed + added else prove()
    if not checked:
        print("the updated folder does not pass its own checks -- restore it from git.",
              file=sys.stderr)
        return 1
    print(f"updated to {new_version} · every script compiles and jobs.json parses.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
