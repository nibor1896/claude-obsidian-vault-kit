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
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
CONTRACT = REPO / "src" / "contract.md"
README = REPO / "README.md"
DOCS = REPO / "docs"
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

# Files that live in tools/ and are deliberately not delivered, name -> why. The reason is the
# entry: an exception without one cannot be told apart from a file somebody forgot to add.
REPO_ONLY = {
    "build_kit.py": "the generator itself -- it builds the kit, a vault does not have one",
    "test_build_kit.py": "the generator's suite; delivered_suites() ships a suite only with its "
                         "tool, and the tool it tests is not delivered either",
}

# Delivered scripts that ship without a `test_X.py`, name -> why. Exactly these three, and every
# new entry is a decision somebody has to defend in writing.
SUITE_EXEMPT = {
    "_testkit.py": "fixtures, not behaviour -- it has no assertions of its own, and every suite "
                   "that imports it fails the moment it stops working",
    "acceptance.py": "it IS a suite: twelve fixtures that each hand a guard bad input. A suite "
                     "for the suite would assert the same twelve facts one level up",
    "verify_setup.py": "the same, over the whole setup chain rather than one guard. Its fourteen "
                       "steps are its assertions",
}


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

    Undo recipes, both re-measured on this machine 2026-07-31:

      1. Write an empty `tools/test_dummy.py` with no `dummy.py` beside it AND declare it in
         REPO_ONLY. It must not appear in claude-obsidian-vault-kit.md and `--check` must stay
         green -- the counted number does not move. Delete both afterwards. (Without the
         REPO_ONLY line `--check` now goes red first, in check_delivery_lists(): since
         2026-07-31 a file in tools/ that no list mentions is itself the defect.)
      2. Drop `count_tokens.py` from TOOLS_ORDER and delete `tools/count_tokens.py` and
         `tools/test_count_tokens.py`. The counted number falls by one and `--check` exits 1
         against prose that still states the old one -- in all three sources at once, which is
         what tells you a tool left rather than one sentence rotting.

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


# Measured against src/contract.md and HEADER on 2026-07-30 BEFORE this check was written, because
# a pattern that cannot see its claim can never disagree with it -- which is how check_prose_claims()
# shipped green over a delivered file saying 99/99. Result: ten command lines in the contract and
# three in the header, covering all three spellings in use side by side --
# `python <VaultRoot>/00_Global/06_tools/x.py`, `python 06_tools/x.py`, `python <vault>/…/x.py`.
# `python --version` and `python -m compileall` carry no `.py` and are correctly not commands here.
COMMAND_RE = re.compile(r"python[3]?\s+(?:-\S+\s+)*(?:\S*[/\\])?([A-Za-z_][A-Za-z0-9_]*\.py)")


def chain_commands():
    """Every tool the prose actually tells the user to run, from both sources.

    NOT LIMITED TO SECTION 8, AND THAT CAME OUT OF THE MEASUREMENT. Counting by hand said nine
    lines, all inside SECTION 8; the pattern found ten. The tenth is `acceptance.py` at the top of
    SECTION 9, and a check scoped to SECTION 8 would have reported a tool the contract plainly
    invokes as never invoked. `verify_setup.py` runs the other way round -- it appears in the
    HEADER and literally nowhere in the contract -- so both sources have to be read as one chain.
    """
    return {name for _, text in prose_sources() for name in COMMAND_RE.findall(text)}


def prose_sources():
    """Every text that tells a user what to type. README.md describes, it does not instruct.

    `docs/*.md` IS ON THIS LIST AND IS NOT ON check_prose_claims()'s (2026-07-31). The two
    functions ask different questions of a source, and only one of them can be asked of docs/:

      - This one asks "does every `python …x.py` name a tool that ships". A page telling a user
        to run something that is not in their folder is a page that wastes their time, and the
        docs are the only prose outside the contract that hands them command lines -- six of
        them today, in how-it-works.md and updating-and-templates.md.
      - check_prose_claims() asks "does every `n/m` match what the code counts", and it treats
        ZERO matches in a source as a defect, deliberately: a claim a pattern stopped seeing
        looks exactly like a claim that agrees. docs/ carries no `n/m` at all -- by choice, the
        pages describe rather than quote measurements -- so adding it there would fire
        "states no claim at all" on the first run and force a number into prose that is better
        off without one.

    So: commands yes, counts no. Written down because the obvious tidy-up is to pass the same
    list to both.
    """
    sources = [("src/contract.md", CONTRACT.read_text(encoding="utf-8")),
               ("tools/build_kit.py (SECTION 10 header)", HEADER)]
    pages = sorted(DOCS.glob("*.md"))
    if not pages:
        # Not a silent empty list. A docs folder that disappeared or moved would take this whole
        # guard with it and nothing would say so -- the same shape as the wrapped `n/m` claim
        # that made --check green over a delivered file saying 99/99.
        raise SystemExit(f"{DOCS}: no .md pages found -- the command lines the docs hand the "
                         f"user cannot be checked against what ships, and an unchecked source "
                         f"reads exactly like a source that agrees.")
    sources += [(f"docs/{page.name}", page.read_text(encoding="utf-8")) for page in pages]
    return tuple(sources)


def declared_uninvoked():
    """`not_invoked` out of tools/jobs.json: name -> why. Missing key means EMPTY, never a default.

    The same key check_freshness.py reads as its third classification, and deliberately the same
    file: "this tool is outside the chain on purpose" is one statement, and two structures holding
    it would eventually answer the same question two ways. jobs.json speaks stems throughout
    (`build_index`, not `build_index.py`), so the comparison below normalises rather than
    respelling the entries with a suffix the file has never used.

    A silent fall back to a built-in list is the defect this whole check is about, wearing green:
    it would classify tools on the strength of something nobody wrote down.
    """
    raw = json.loads((TOOLS / "jobs.json").read_text(encoding="utf-8-sig")).get("not_invoked") or {}
    return dict(raw) if isinstance(raw, dict) else {name: "" for name in raw}


def check_prose_chain():
    """Every command names a tool that ships, and every tool that ships is named or excused.

    WHY THIS EXISTS (#19, 2026-07-30): check_prose_claims() above guards three number patterns.
    Everything else in the contract is unguarded prose -- delete a command line from SECTION 8 and
    every run stays green. Four instances were on record, and two more were measured the day this
    was written: `verify_setup.py` appears in the contract zero times while its 14/14 is guarded in
    three places, and `count_tokens.py` sat in no chain and in no jobs.json list at all.

    The two directions fail differently:

      - A command naming a tool that does not ship is a line the user types and gets an error
        from. Cheap, no exceptions.
      - A shipped tool named by no command is a file sitting unexplained in their folder. This is
        the direction that needs an opt-out, and the opt-out is jobs.json's `not_invoked` rather
        than a new mechanism -- check_freshness.py already established the shape, down to the
        reason being mandatory text because JSON has no comments.

    Suites are covered by run_suites.py rather than listed one by one. That is a list comparison,
    not a semantic guess: run_suites.py collects exactly delivered_suites(), so if it ever leaves
    the chain, all nine go with it and this check says so on the same run.

    WHAT IT DOES NOT CHECK: the ORDER of the chain. That check_freshness.py must run first is a
    promise about meaning, not a list comparison -- guarding it here would build a second truth
    about the order, next to the contract's own.

    Undo recipes, each red on its own, all four measured on this machine 2026-07-30 --
    see test_build_kit.py, where each one runs against a copy in a temp directory:

      1. Delete `python 06_tools/check_freshness.py …` from SECTION 8. Exit 1,
         `check_freshness.py: ships, and no command line runs it`. This is the sentence from the
         issue body, as a test.
      2. Misspell a tool in SECTION 8 (`check_link.py`). Exit 1, `names check_link.py, which is
         not delivered`.
      3. Add a tool to TOOLS_ORDER without touching the contract or jobs.json. Exit 1 -- the case
         that actually happens the next time somebody writes a tool.
      4. Put a name in both the chain and `not_invoked`. Exit 2, no winner picked.
    """
    delivered = {name for name in delivered_files() if name.endswith(".py")}
    commanded = chain_commands()
    uninvoked = declared_uninvoked()

    # Direction 1, and it has no exceptions.
    ghosts = sorted(commanded - delivered)
    if ghosts:
        print(f"{OUT.name}: the prose tells the user to run something that is not delivered.\n"
              + "\n".join(f"  a command line names {name}, which is not delivered" for name in ghosts)
              + "\n  The user types it and gets an error. Either the tool left the delivery lists "
                "or the line has a typo.", file=sys.stderr)
        return 1

    # `run_suites.py` collecting them is the chain, so they are covered exactly as long as it is.
    if "run_suites.py" in commanded:
        delivered -= set(delivered_suites())

    both = sorted(name for name in delivered
                  if Path(name).stem in uninvoked and name in commanded)
    if both:
        print(f"{OUT.name}: classified twice.\n"
              + "\n".join(f"  {name}: a command line runs it, and jobs.json's not_invoked says "
                          f"nothing does — {uninvoked[Path(name).stem]!r}" for name in both)
              + "\n  No winner is picked: whichever lost would sit in the file doing nothing, and "
                "no run could show which of the two statements applies.", file=sys.stderr)
        return 2

    orphans = sorted(name for name in delivered
                     if name not in commanded and Path(name).stem not in uninvoked)
    if orphans:
        print(f"{OUT.name}: a delivered tool that no chain calls and nothing excuses.\n"
              + "\n".join(f"  {name}: ships, and no command line runs it" for name in orphans)
              + f"\n  Either add it to a chain in src/contract.md, or add it to `not_invoked` in "
                f"tools/jobs.json with the reason. A file in the user's tool folder that nothing "
                f"ever calls is one they cannot tell from a leftover.", file=sys.stderr)
        return 1
    return 0


def check_delivery_lists():
    """The folder and the three hand-kept lists have to agree, in both directions.

    WHY (2026-07-31): SHARED, TOOLS_ORDER and DRIVERS are typed by hand, and nothing compared
    them against tools/ at all. A new tool written and never added fell through in silence -- it
    simply was not in the kit, and no run said so. The other direction was worse only in where
    it surfaced: a list entry with no file behind it got as far as block(), which reads the file,
    so the first symptom was a bare FileNotFoundError out of the renderer, after the guard had
    already reported everything as fine.

    `not_invoked` in jobs.json is NOT an escape hatch here. That key answers "no chain calls it",
    which is a statement about a delivered file; this asks "is it delivered at all". A file can
    honestly be both delivered and uncalled -- count_tokens.py is -- and conflating the two would
    let a repo-only tool hide behind a jobs.json entry.

    Undo recipe: write an empty `tools/dummy.py`. `--check` exits 1 with
    `dummy.py: in tools/ and in no list`. Delete it afterwards.
    """
    on_disk = {path.name for path in TOOLS.iterdir()
               if path.is_file() and path.suffix in (".py", ".json")}
    accounted = set(delivered_files()) | set(REPO_ONLY)
    strays = sorted(on_disk - accounted)
    if strays:
        print(f"{OUT.name}: a file in tools/ that no list mentions.\n"
              + "\n".join(f"  {name}: in tools/ and in no list" for name in strays)
              + "\n  Add it to SHARED, TOOLS_ORDER or DRIVERS in build_kit.py if the user gets "
                "it, or to REPO_ONLY with the reason if they do not. A tool nobody listed is a "
                "tool that silently is not in the kit.", file=sys.stderr)
        return 1
    ghosts = sorted(name for name in accounted if not (TOOLS / name).is_file())
    if ghosts:
        print(f"{OUT.name}: a list names a file that is not there.\n"
              + "\n".join(f"  {name}: listed, and no such file in tools/" for name in ghosts)
              + "\n  Without this the first symptom is a FileNotFoundError out of the renderer, "
                "long after every check has reported the delivery as fine.", file=sys.stderr)
        return 1
    return 0


def check_suites_ship_with_their_tools():
    """The contract's rule, checked in the direction the contract states it.

    delivered_suites() already holds the converse -- a `test_X.py` ships only when `X.py` does --
    and that is what stops a repo-side suite installing itself into a vault. It says nothing
    about a tool arriving WITHOUT a suite, which is the direction SECTION 0 actually promises,
    and that direction was unguarded: measured 2026-07-31, acceptance.py and verify_setup.py had
    no suite and nothing had ever mentioned it.

    They are exempt now, in writing, with the reason each -- they are suites themselves. An
    exemption list is the honest form of "we thought about it"; silence is not.

    Undo recipe: move `tools/test_count_tokens.py` OUT of tools/. `--check` exits 1 with
    `count_tokens.py: delivered, and no test_count_tokens.py ships with it`. Move it back. A
    rename inside the folder measures something else -- check_delivery_lists() runs first and
    reports the renamed file as unaccounted for.
    """
    delivered = [name for name in delivered_files() if name.endswith(".py")]
    suites = set(delivered_suites())
    naked = sorted(name for name in delivered
                   if not name.startswith("test_")
                   and name not in SUITE_EXEMPT
                   and f"test_{name}" not in suites)
    if naked:
        print(f"{OUT.name}: a delivered tool ships without its suite.\n"
              + "\n".join(f"  {name}: delivered, and no test_{name} ships with it"
                          for name in naked)
              + "\n  SECTION 0 states this as a doctrine rule. Write the suite, or add the tool "
                "to SUITE_EXEMPT in build_kit.py with the reason it does not need one.",
              file=sys.stderr)
        return 1
    unused = sorted(name for name in SUITE_EXEMPT if name not in delivered)
    if unused:
        print(f"{OUT.name}: SUITE_EXEMPT excuses something that is not delivered.\n"
              + "\n".join(f"  {name}: exempt from having a suite, and not in the kit"
                          for name in unused)
              + "\n  An exemption nobody needs outlives the reason it was written for.",
              file=sys.stderr)
        return 1
    return 0


def check_jobs_config_matches_code():
    """tools/jobs.json against the copy of it inside check_freshness.py.

    The copy is deliberate and stays: a vault with no jobs.json still has to classify its tools,
    so the defaults live in code. What was missing is anything comparing the two. And the
    acceptance fixture that exercises check_freshness builds a vault WITHOUT a jobs.json, so it
    takes the default path every single time -- measured 2026-07-31: the suite tests the copy and
    has never once read the original.

    Compared as parsed structures, not as text: the file may be reformatted, the statement may
    not change.

    Undo recipe: change one word in any reason string in tools/jobs.json. `--check` exits 1 and
    names the key that disagrees. Put the word back.
    """
    sys.path.insert(0, str(TOOLS))
    import check_freshness

    try:
        config = json.loads((TOOLS / "jobs.json").read_text(encoding="utf-8-sig"))
    except (OSError, ValueError) as exc:
        print(f"{OUT.name}: tools/jobs.json cannot be read as JSON ({exc}). It is the only "
              f"non-Python block in the kit, so no compile step covers it.", file=sys.stderr)
        return 1

    pairs = (("jobs", config.get("jobs"), check_freshness.DEFAULT_JOBS),
             ("on_demand", config.get("on_demand"), check_freshness.DEFAULT_ON_DEMAND),
             ("not_invoked", config.get("not_invoked"), check_freshness.DEFAULT_NOT_INVOKED))
    wrong = [f"  {key}: jobs.json says {shipped!r}, check_freshness.py says {code!r}"
             for key, shipped, code in pairs if shipped != code]
    if wrong:
        print(f"{OUT.name}: the shipped jobs.json and its copy in code disagree.\n"
              + "\n".join(wrong)
              + "\n  The user gets the file; a vault without one gets the copy. Two answers to "
                "the same question, and which one a run uses depends on whether a file exists.",
              file=sys.stderr)
        return 1
    return 0


LOG_CALL_RE = re.compile(r"log_run\(\s*\w+\s*,\s*\"([^\"]*)\"")


def check_log_labels():
    """Every log_run() label equals the stem of the file it is written in.

    THE WHOLE FAILURE CLASS IS SILENT, WHICH IS WHY IT NEEDS A BUILD-TIME CHECK. check_freshness
    matches log lines against tool names taken from the file stems. A label that drifts from its
    filename puts BOTH names into `unclassified` -- the job nobody logged, and the label nobody
    declared -- and `unclassified` deliberately does not change the exit code. So a typo here
    costs a watched job its watching and prints two lines nothing acts on.

    Suites are skipped: they call log_run() with other tools' names on purpose, as fixtures.
    vault_paths.py is skipped because it DEFINES log_run and names nothing.

    Undo recipe: change the label in build_index.py's log_run() call to `"build_indexx"`.
    `--check` exits 1 with `build_index.py: logs as "build_indexx"`. Change it back.
    """
    wrong = []
    for name in delivered_files():
        if not name.endswith(".py") or name.startswith("test_") or name == "vault_paths.py":
            continue
        stem = name[:-3]
        for label in LOG_CALL_RE.findall((TOOLS / name).read_text(encoding="utf-8")):
            if label != stem:
                wrong.append(f'  {name}: logs as "{label}", which is not "{stem}"')
    if wrong:
        print(f"{OUT.name}: a run log label does not match the file that writes it.\n"
              + "\n".join(sorted(set(wrong)))
              + "\n  check_freshness.py takes the population from the filenames, so both names "
                "land in `unclassified` -- and unclassified does not change an exit code. The "
                "job stops being watched and no run goes red over it.", file=sys.stderr)
        return 1
    return 0


RECONFIGURE = '_stream.reconfigure(encoding="utf-8", errors="replace")'


def check_stream_reconfigure():
    """Every delivered script you can RUN carries the stdout/stderr fix before its first print.

    A module you import does not need one -- it inherits whatever the caller set up -- so the
    scope is exactly "has an `if __name__ == '__main__':` guard and is not a suite". The suites
    are covered by run_suites.py, which sets PYTHONIOENCODING for the subprocesses it starts.

    The block is copied into each file rather than imported, and that stays: three of these do
    not import vault_paths at all, and in the rest it sits ABOVE the import so that an
    ImportError traceback lands on a reconfigured stderr. A vault path with an umlaut plus a
    cp1252 console otherwise produces a UnicodeEncodeError on top of the real error.

    Undo recipe: delete the four-line block from the top of count_tokens.py. `--check` exits 1
    with `count_tokens.py: runnable, and no stdout/stderr reconfigure`. Put it back.
    """
    missing = []
    for name in delivered_files():
        if not name.endswith(".py") or name.startswith("test_"):
            continue
        text = (TOOLS / name).read_text(encoding="utf-8")
        if 'if __name__ == "__main__":' not in text:
            continue
        if RECONFIGURE not in text:
            missing.append(f"  {name}: runnable, and no stdout/stderr reconfigure")
    if missing:
        print(f"{OUT.name}: a script that can be run does not fix its own streams.\n"
              + "\n".join(missing)
              + "\n  On a cp1252 console every non-ASCII filename it tries to print raises "
                "UnicodeEncodeError, and the traceback replaces the defect the tool was "
                "reporting. Copy the block from any other tool -- above the imports.",
              file=sys.stderr)
        return 1
    return 0


def all_guards():
    """Every build-time check, in the order a failure is cheapest to act on.

    Delivery first: check_prose_claims() imports acceptance and verify_setup, so a list naming a
    file that is not there has to be caught before anything tries to import from that folder.
    """
    return (check_delivery_lists() or check_suites_ship_with_their_tools()
            or check_jobs_config_matches_code() or check_log_labels()
            or check_stream_reconfigure() or check_prose_claims() or check_prose_chain())


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
    failed = all_guards()
    if failed:
        return failed
    print(f"{OUT.name}: {len(blocks)} blocks extract, match tools/, and run green · "
          f"tools/ and the delivery lists agree · every delivered tool has its suite or its "
          f"reason · jobs.json matches its copy in code · every log label matches its file · "
          f"every runnable script fixes its streams · every count in the text matches the code · "
          f"no stale stamp quoted in the prose · every command in the contract, the header and "
          f"docs/ names a delivered tool, and every delivered tool is called or excused")
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
    # Exit 2 travels: a name classified twice is a contradiction in the sources, not a stale
    # number, and flattening it to 1 would hide which of the two a reader has to go fix.
    failed = all_guards()
    if failed:
        return failed

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
