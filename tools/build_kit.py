"""Assemble the single-file kit: the setup contract plus every script, verbatim.

The user drags ONE file into a Claude conversation. Everything Claude needs is inside it, so
there is no folder to clone, no path to guess, and nothing for a setup to re-derive from a
description -- which is what produced a fresh crop of defects on every cold run.

    python build_kit.py            write the standalone file
    python build_kit.py --check    exit 1 if it is out of date (for the acceptance run)

The generated file is derived output. Edit the contract or the scripts, never the result.
"""

import argparse
import hashlib
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
CONTRACT = REPO / "src" / "contract.md"
README = REPO / "README.md"
TOOLS = REPO / "tools"
OUT = REPO / "claude-obsidian-vault-kit.md"

for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass

# Order matters for a human reading top to bottom: shared modules, then tools, then suites.
SHARED = ["vault_paths.py", "_testkit.py", "jobs.json"]
TOOLS_ORDER = ["build_index.py", "write_command.py", "check_links.py", "check_duplicates.py",
               "check_freshness.py", "count_tokens.py", "run_suites.py"]
DRIVERS = ["acceptance.py", "verify_setup.py", "upgrade.py"]


def delivered_suites():
    """The suites that ship: `test_X.py` where `X.py` is one of the scripts above.

    THE REPOSITORY HAS MORE SUITES THAN THE USER DOES, AND THAT IS NOT A DISAGREEMENT. The three
    lists above are maintained by hand; the suites used to be picked up by a bare
    `glob("test_*.py")`. So a suite written for a repo-side tool delivered *itself* into the
    user's folder, without anyone deciding to, and then sat there testing a tool that is not
    there. `test_build_kit.py` is the case that made this visible: build_kit.py is the generator,
    it is not in any list above, and it is not something a vault needs.

    So: a suite ships only with its tool. In this repository `run_suites.py` reports one more
    than the delivered file carries -- workshop, not product. **The `n/m suites` in the contract,
    in HEADER and in README.md describe the PRODUCT**, which is why check_prose_claims() counts
    this list and not the folder. Do not raise those numbers because the repo grew a suite.

    Undo recipes, both measured on this machine 2026-07-29:

      1. Write an empty `tools/test_dummy.py` with no `dummy.py` beside it. It must not appear in
         claude-obsidian-vault-kit.md and `--check` must stay green -- the counted number does
         not move. Delete the file afterwards.
      2. Drop `count_tokens.py` from TOOLS_ORDER. `test_count_tokens.py` leaves the delivery with
         it, the counted number falls by one, and `--check` exits 1 against prose that still
         states the old one -- in all three sources at once, which is what tells you a tool left
         rather than one sentence rotting.

    Both recipes are also `test_build_kit.py`, which is where they run on every acceptance pass.
    """
    shipped = set(SHARED + TOOLS_ORDER + DRIVERS)
    return [path.name for path in sorted(TOOLS.glob("test_*.py"))
            if path.name[len("test_"):] in shipped]


def delivered_files():
    """Every file SECTION 10 writes into the user's tool folder, in reading order.

    One list, asked by everything: the renderer, the round-trip verifier, the number the prose is
    held to, and the tree verify_setup.py builds. Before this existed there were three counters
    for one question and no run ever compared them.
    """
    return SHARED + TOOLS_ORDER + DRIVERS + delivered_suites()

HEADER = """
---

## SECTION 10 — The scripts, verbatim

Everything below is the finished implementation. **Write each block to disk exactly as it stands —
byte for byte, same filename — into the vault's tool folder** (`<VaultRoot>/00_Global/06_tools/`,
created in SECTION 3). Do not retype them from the contracts above, do not "improve" them while
copying, and do not skip the suites: they are the only reason the numbers in SECTION 0 mean
anything.

**Extract them; do not transcribe them.** The intended path is a short throwaway script that reads
this file, cuts each fenced block out by the filename in its heading, and writes it to the tool
folder. Both cold runs on 2026-07-30 wrote one independently, because nothing here said so — and a
silence where a method should be reads as "type it out". Sending every block back through the model
re-tokenises the whole of SECTION 10 and puts a paraphrase where a byte-for-byte copy was promised.
The extractor is scaffolding, not part of the vault: keep it outside the tool folder and delete it
when it has run.

**Then check three things, before running anything:**

- **Every `.py` file compiles** — `python -m compileall -q <VaultRoot>/00_Global/06_tools`. A block
  that arrived truncated fails here; without this check its first symptom is a suite failing for a
  reason that has nothing to do with the suite.
- **`jobs.json` parses** — it is the only non-Python block, so no compile step covers it.
- **No file carries a byte-order mark** — see below.

Measured on Windows 11, Python 3.13, under PowerShell 5.1 **and** Git Bash: 9/9 suites green,
12/12 acceptance checks correct, 14/14 end-to-end setup steps -- ten consecutive runs under each
shell. Copy them and that measurement still applies to what you handed the user. Rewrite them and
it does not.

**Write them as UTF-8 without a byte-order mark.** `Set-Content -Encoding utf8` under PowerShell 5.1
prepends a BOM, and a BOM in front of `import sys` is an invisible first character that some readers
choke on. Use your file-writing tool, or Python. This cost a full round on one setup, and the error
pointed at the wrong line.

After writing them, prove it on this machine before you report anything:

```
python <vault>/00_Global/06_tools/run_suites.py       expect 9/9 suites green
python <vault>/00_Global/06_tools/acceptance.py       expect 12/12 checks
python <vault>/00_Global/06_tools/verify_setup.py     expect 14/14 steps
```
"""


# Every "n/m <thing>" the prose is allowed to state, and the code that owns the m. The wording
# varies on purpose ("expect 11/11 checks", "11/11 acceptance checks"), so each pattern has to
# cover the phrasings actually in use -- a claim the pattern misses is a claim nothing counts.
#
# `\s+`, not a literal space, everywhere a word follows: prose wraps. `13/13` sat at the end of
# one line in src/contract.md with `end-to-end setup steps` on the next, and a pattern spelling
# that gap as " " saw no claim there at all -- which this file used to treat as agreement.
CLAIMS = ((r"(\d+)/\d+\s+suites", "suites"),
          (r"(\d+)/\d+\s+(?:acceptance\s+)?checks", "acceptance checks"),
          (r"(\d+)/\d+\s+(?:end-to-end\s+)?(?:setup\s+)?steps", "end-to-end setup steps"))


def check_prose_claims():
    """Every number and every version stamp in the prose, against the code that owns it.

    WHY ALL THREE, AND WHY README (2026-07-29): this checked `suites` only, and only across the
    contract and the SECTION 10 header. README.md sat at `11/11 end-to-end setup steps` for four
    hours after step 12 shipped, with `--check` green the whole time, because nothing looked at
    it. The counts are imported rather than re-derived: `len(FIXTURES)` and `len(STEPS)` are the
    same objects the drivers count for their own summary lines, so the guard cannot disagree with
    the run it claims to summarise.

    WHY ZERO MATCHES IS ITSELF A DEFECT (2026-07-29): the three patterns used to spell the gap
    between the number and the word as a literal space, and prose wraps. `13/13` ended a line in
    src/contract.md with `end-to-end setup steps` beginning the next, so that pattern matched
    nothing in the one file the user actually reads -- and no match read as no disagreement.
    Measured: contract set to `99/99`, rebuilt, `--check` exit 0, line 64 of the delivered file
    saying `99/99 end-to-end setup steps`. `\\s+` fixes the wrapping; the minimum-hit loop below
    fixes the class, because a pattern that stops seeing its claim can never disagree with it.

    Undo recipes -- the two runs that have to go red, each on its own:

      1. Set src/contract.md's step claim to `99/99`. `python tools/build_kit.py --check` prints
         `src/contract.md: says "99/99 end-to-end setup steps", counted 14` and exits 1. Before
         the `\\s+` change this printed nothing and exited 0. The trailing count is whatever
         `len(verify_setup.STEPS)` is on the day you run it -- read it off the run, do not carry
         it forward; it was quoted here as 13 for one commit after a step was added.
      2. Delete the word `steps` from README.md's measurement sentence (line 15). `--check` then
         prints `README.md: states no end-to-end setup steps claim at all` and exits 1.

    Known wart, and it is load-bearing: README.md's maintainer notes quote an older Linux run as
    history, not as a current claim, and this guard cannot tell the two apart -- so that
    paragraph carries no bare `n/m` at all. Rephrase history, never bump a measurement nobody
    repeated.
    """
    sys.path.insert(0, str(TOOLS))
    import acceptance
    import verify_setup
    # delivered_suites(), not the folder: the prose describes what the user receives, and this
    # repository carries suites for its own tools that no vault ever gets.
    counted = {"suites": len(delivered_suites()),
               "acceptance checks": len(acceptance.FIXTURES),
               "end-to-end setup steps": len(verify_setup.STEPS)}
    # Prose only. The embedded suites contain strings like "0/2 suites" as test data, and counting
    # those as claims makes the guard cry wolf on its own fixtures.
    sources = (("src/contract.md", CONTRACT.read_text(encoding="utf-8")),
               ("tools/build_kit.py", HEADER),
               ("README.md", README.read_text(encoding="utf-8")))

    wrong = []
    unseen = []
    for label, text in sources:
        for pattern, what in CLAIMS:
            found_any = False
            for found in re.finditer(pattern, text):
                found_any = True
                if int(found.group(1)) != counted[what]:
                    wrong.append(f'  {label}: says "{found.group(0)}", counted {counted[what]}')
            if not found_any:
                unseen.append(f"  {label}: states no {what} claim at all")
    if wrong:
        print(f"{OUT.name}: the prose states a number the code does not count.\n"
              + "\n".join(sorted(set(wrong)))
              + "\n  A number in prose goes stale the moment a suite, a fixture or a step is "
                "added -- this check exists because three of them shipped that way.",
              file=sys.stderr)
    if unseen:
        # Every source is a place the reader takes the measurement from, so every source has to
        # carry every claim. A missing one is either prose that dropped a promise or a pattern
        # that stopped seeing it, and both look exactly like agreement from here.
        print(f"{OUT.name}: a source no longer carries a claim the others do.\n"
              + "\n".join(sorted(set(unseen)))
              + "\n  Zero matches is not agreement. A wrapped line already turned one claim "
                "invisible once, and --check stayed green over a delivered file saying 99/99.",
              file=sys.stderr)
    if wrong or unseen:
        return 1

    # Same class of defect, one level nastier: a real hash quoted in the prose as an example.
    # The file then carries two kit-version lines, only one of them true, and a reader comparing
    # copies has no way to tell which. Write the example as an ellipsis.
    for label, text in sources:
        stale = re.findall(r"kit-version: ([0-9a-f]{12})", text)
        if stale:
            print(f"{OUT.name}: {label} quotes a literal kit-version {stale}. The stamp on line 1 "
                  f"is the only true one -- a second one goes stale on the next build and reads as "
                  f"if the copy were outdated. Use `<!-- kit-version: … -->`.", file=sys.stderr)
            return 1
    return 0


def block(name):
    text = (TOOLS / name).read_text(encoding="utf-8")
    lang = "json" if name.endswith(".json") else "python"
    return f"### `{name}`\n\n```{lang}\n{text.rstrip()}\n```\n"


def source_version(body):
    """Twelve hex digits over the delivered file itself, minus the stamp line.

    A date would answer "how old is this" and nothing else; two people with different files
    could still read the same date. Hashing the *sources* instead looked equivalent and was
    not: the SECTION 10 header lives in this script, so editing it changed what users receive
    while the version stayed put -- two different files claiming to be the same one. Hash what
    is shipped.
    """
    return hashlib.sha256(body.encode("utf-8")).hexdigest()[:12]


def render():
    contract = CONTRACT.read_text(encoding="utf-8").rstrip()
    parts = ["", contract, HEADER.rstrip(), ""]
    for group, title in ((SHARED, "Shared"), (TOOLS_ORDER, "Tools"), (DRIVERS, "Drivers")):
        parts.append(f"#### {title}\n")
        for name in group:
            parts.append(block(name))
    for name in delivered_suites():
        parts.append(block(name))
    parts.append("---\n\n*Generated by `tools/build_kit.py`. Edit the sources, never this file.*\n"
                 "*Source and newest published copy: "
                 "https://github.com/nibor1896/claude-obsidian-vault-kit*\n"
                 "*Compare the `kit-version` at the top against the published file to see whether "
                 "this copy is current.*\n")
    body = "\n".join(parts)
    return f"<!-- kit-version: {source_version(body)} -->{body}"


BLOCK_RE = re.compile(r"^### `([^`]+)`\n\n```(?:python|json)\n(.*?)\n```", re.S | re.M)


def verify():
    """Extract the scripts back out of the deliverable and run them.

    Everything else in this repo tests the sources. This tests the artefact the user actually
    receives -- a fence that swallowed a line, a block that never made it in, an embedded copy
    that drifted from tools/. None of those are visible from the source side.
    """
    if not OUT.exists():
        print(f"{OUT.name}: missing -- run build_kit.py", file=sys.stderr)
        return 1
    blocks = BLOCK_RE.findall(OUT.read_text(encoding="utf-8"))
    expected = delivered_files()
    names = [n for n, _ in blocks]
    if names != expected:
        print(f"{OUT.name}: embedded {len(names)} blocks, expected {len(expected)}\n"
              f"  missing: {sorted(set(expected) - set(names))}\n"
              f"  extra:   {sorted(set(names) - set(expected))}", file=sys.stderr)
        return 1

    work = Path(tempfile.mkdtemp(prefix="vaultkit_roundtrip_")) / "06_tools"
    work.mkdir(parents=True)
    try:
        drifted = []
        for name, body in blocks:
            (work / name).write_text(body + "\n", encoding="utf-8", newline="\n")
            source = (TOOLS / name).read_text(encoding="utf-8").replace("\r\n", "\n").rstrip() + "\n"
            if source != (work / name).read_text(encoding="utf-8"):
                drifted.append(name)
        if drifted:
            print(f"{OUT.name}: embedded copy differs from tools/: {drifted}", file=sys.stderr)
            return 1

        # Substrings without counts on purpose. Exit 0 already means every check passed, and a
        # literal "10/10" here is a number in a second place that goes stale the moment a
        # fixture or a step is added -- which is the defect this file checks the prose for.
        for script, want in (("run_suites.py", "suites green"),
                             ("acceptance.py", "checks behaved as specified"),
                             ("verify_setup.py", "steps every time")):
            result = subprocess.run([sys.executable, str(work / script)],
                                    capture_output=True, cwd=str(work))
            out = result.stdout.decode("utf-8", errors="replace")
            if result.returncode != 0 or want not in out:
                print(f"{script} from the deliverable: exit {result.returncode}\n{out}\n"
                      f"{result.stderr.decode('utf-8', errors='replace')}", file=sys.stderr)
                return 1
            print(f"  ok   {script} runs from the deliverable")
    finally:
        shutil.rmtree(work.parent, ignore_errors=True)
    if check_prose_claims():
        return 1
    print(f"{OUT.name}: {len(blocks)} blocks extract, match tools/, and run green · "
          f"every count in the text matches the code · no stale stamp quoted in the prose")
    return 0


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true",
                        help="exit 1 when the standalone file does not match the sources")
    parser.add_argument("--verify", action="store_true",
                        help="extract the scripts back out of the deliverable and run them")
    args = parser.parse_args(argv)

    if args.verify:
        return verify()

    # Before writing, not after: a build that emits the file and *then* complains has already
    # produced the artefact someone will ship. Both paths pay for it -- --check is the cheap gate
    # the acceptance run uses, and the write path refuses to mint a deliverable that lies.
    if check_prose_claims():
        return 1

    rendered = render()
    if args.check:
        if not OUT.exists():
            print(f"{OUT.name}: missing -- run build_kit.py", file=sys.stderr)
            return 1
        current = OUT.read_text(encoding="utf-8")
        if current != rendered:
            print(f"{OUT.name}: out of date -- "
                  f"{hashlib.sha256(current.encode()).hexdigest()[:12]} on disk, "
                  f"{hashlib.sha256(rendered.encode()).hexdigest()[:12]} from sources",
                  file=sys.stderr)
            return 1
        print(f"{OUT.name}: up to date · {len(current.splitlines())} lines")
        return 0

    OUT.write_text(rendered, encoding="utf-8", newline="\n")
    kb = len(rendered.encode("utf-8")) / 1024
    print(f"{OUT.name}: {len(rendered.splitlines())} lines · {kb:.0f} KB · "
          f"{len(delivered_files())} files embedded")
    return 0


if __name__ == "__main__":
    sys.exit(main())
