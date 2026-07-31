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
SHARED = ["jobs.json"]
TOOLS_ORDER = ["vaultkit.py"]
DRIVERS = ["upgrade.py"]

# Files that live in tools/ and are deliberately not delivered, name -> why.
#
# THIRTEEN OF THESE ARRIVED AT ONCE ON 2026-07-31, AND THE LIST IS THE POINT. The suites and the
# three drivers used to ship: a vault ran 126 unit tests over tools that had not changed since
# setup, every day, as step 6 of its own maintenance chain. They are release verification --
# they answer "does this code work", which is a question about the kit, asked once, in the
# repository, before anything is published. They are not maintenance, which is what the user's
# chain is for. Nothing here is deleted; it moved to the side of the line it belongs on.
#
# The reason per entry is not decoration: an exception without one cannot be told apart from a
# file somebody forgot to add, and check_delivery_lists() is what forces the move to be visible.
REPO_ONLY = {
    "build_kit.py": "the generator itself -- it builds the kit, a vault does not have one",
    "test_build_kit.py": "the generator's suite, and the tool it tests is not delivered either",
    "_testkit.py": "fixtures for the suites; with the suites in the repository it has no reader "
                   "in a vault",
    "run_suites.py": "the suite runner. With no suites delivered it would collect zero and say "
                     "so, forever",
    "acceptance.py": "release verification: it proves each guard goes RED on bad input. That is "
                     "a question about this kit, answered once before publishing, not something "
                     "a vault re-answers daily over code that has not changed",
    "verify_setup.py": "release verification over the whole setup chain, on a throwaway tree. "
                       "The user's own setup already ran that chain, on their tree, for real",
    "test_build_index.py": "suite for build_index.py -- release verification",
    "test_write_command.py": "suite for write_command.py -- release verification",
    "test_check_links.py": "suite for check_links.py -- release verification",
    "test_check_duplicates.py": "suite for check_duplicates.py -- release verification",
    "test_check_freshness.py": "suite for check_freshness.py -- release verification",
    "test_count_tokens.py": "suite for count_tokens.py -- release verification",
    "test_vault_paths.py": "suite for vault_paths.py -- release verification",
    "test_vaultkit.py": "suite for vaultkit.py -- release verification",
    "test_run_suites.py": "suite for run_suites.py, which is itself repo-only",
    "test_upgrade.py": "suite for upgrade.py -- release verification",
}

# Delivered scripts that have no `test_X.py` in the repository, name -> why. Empty since
# 2026-07-31: the two entries that were here, acceptance.py and verify_setup.py, are not
# delivered any more, so they need no exemption. An entry here is a decision to defend in
# writing, and there is currently nothing to defend.
SUITE_EXEMPT = {}


def repo_suites():
    """Every `test_*.py` in tools/. Not one of them is delivered any more.

    THE NUMBER IN THE PROSE CHANGED FRAME ON 2026-07-31, NOT MEANING. It used to count the
    suites the USER received, because the contract told them to run those suites as step 6 of
    their own maintenance chain. With the suites in the repository, `n/m suites green` is a
    statement about how this release was verified before it was published -- and the honest
    value for that is what `python tools/run_suites.py` prints in a clone, which is this folder,
    every suite in it, including the generator's own.

    Any narrower set would be a number no single command produces. That is the trap the whole
    prose guard exists to prevent: a figure nobody can reproduce is an assertion.

    Undo recipes, both re-measured on this machine 2026-07-31:

      1. Write an empty `tools/test_dummy.py` and declare it in REPO_ONLY. The counted number
         rises by one and `--check` exits 1 against prose stating the old one, in all three
         sources at once. Without the REPO_ONLY line it goes red one guard earlier, in
         check_delivery_lists(). Delete both afterwards.
      2. Delete `tools/count_tokens.py` and `tools/test_count_tokens.py` and drop
         `"count_tokens.py"` from TOOLS_ORDER. The counted number falls by one and `--check`
         exits 1 -- again in all three sources, which is what tells you a tool left rather than
         one sentence rotting.

    Both recipes are also `test_build_kit.py`, which is where they run on every acceptance pass.
    """
    return [path.name for path in sorted(TOOLS.glob("test_*.py"))]


def delivered_files():
    """Every file SECTION 10 writes into the user's tool folder, in reading order.

    One list, asked by everything: the renderer, the round-trip verifier and the tree
    verify_setup.py builds. Before this existed there were three counters for one question and
    no run ever compared them.
    """
    return SHARED + TOOLS_ORDER + DRIVERS

HEADER = """
---

## SECTION 10 — The scripts, verbatim

Everything below is the finished implementation. **Write each block to disk exactly as it stands —
byte for byte, same filename — into the vault's tool folder** (`<VaultRoot>/00_Global/06_tools/`,
created in SECTION 3). Do not retype them from the contracts above and do not "improve" them while
copying.

**The suites are not here, and that is deliberate.** They live in the kit's repository and were run
there before this file was published — over exactly these bytes. A vault does not re-run unit tests
over code that has not changed since setup; it runs the guards in SECTION 8 over notes that change
every day. What you have to prove on this machine is that the blocks arrived intact, which is the
three checks below.

**Extract them; do not transcribe them.** The intended path is a short throwaway script that reads
this file, cuts each fenced block out by the filename in its heading, and writes it to the tool
folder. Both cold runs on 2026-07-30 wrote one independently, because nothing here said so — and a
silence where a method should be reads as "type it out". Sending every block back through the model
re-tokenises the whole of SECTION 10 and puts a paraphrase where a byte-for-byte copy was promised.
The extractor is scaffolding, not part of the vault: keep it outside the tool folder and delete it
when it has run.

**Then run this one command, before running anything else:**

```
python <VaultRoot>/00_Global/06_tools/upgrade.py --prove
```

It compiles every block, parses `jobs.json`, and checks that `vaultkit.py` arrived whole. **The
third of those is the one you cannot do by compiling.** Measured on 2026-07-31: a `vaultkit.py` cut
short — anywhere — still compiles, still imports, and still exits 0 when you run it, having done
nothing, because the cut takes its entry point with it. Nothing inside that file can catch that;
whatever you put at its end goes with the same cut. `upgrade.py` is a separate block, so it can.

**Write them as UTF-8 without a byte-order mark** — see below.

**How this release was verified, in its own repository, before this file existed:** on Windows 11,
Python 3.13, under PowerShell 5.1 **and** Git Bash — 11/11 suites green, 12/12 acceptance checks
correct, 15/15 end-to-end setup steps, ten consecutive runs under each shell, against these exact
bytes. Copy them and that measurement still applies to what you handed the user. Rewrite them and it
does not, and nothing in their folder can tell them.

**Write them as UTF-8 without a byte-order mark.** `Set-Content -Encoding utf8` under PowerShell 5.1
prepends a BOM, and a BOM in front of `import sys` is an invisible first character that some readers
choke on. Use your file-writing tool, or Python. This cost a full round on one setup, and the error
pointed at the wrong line.
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
    # repo_suites(), i.e. the folder: since 2026-07-31 no suite is delivered, so `n/m suites` is
    # a statement about how this release was verified rather than about the user's folder -- and
    # the only honest value for that is what `python tools/run_suites.py` prints in a clone.
    counted = {"suites": len(repo_suites()),
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

# The same line, one word further along. Since the guards are reached as `vaultkit.py <sub>`,
# the filename alone stopped being the unit: it is one name for six tools, so a subcommand that
# nothing ever calls would sit inside a file the chain plainly runs and no check would see it.
SUBCOMMAND_RE = re.compile(
    r"python[3]?\s+(?:-\S+\s+)*(?:\S*[/\\])?vaultkit\.py\s+([a-z_]+)")


def dispatch_register():
    """`COMMANDS` out of vaultkit.py: subcommand -> the function that runs it, and its job name.

    Imported rather than respelled. A second copy of this mapping would answer "what can this
    kit run" one way here and another way in the tool, and the guard would go on passing while
    the two drifted -- which is the shape of every defect check_prose_chain() exists for.
    """
    sys.path.insert(0, str(TOOLS))
    import vaultkit
    return vaultkit.COMMANDS


def chain_commands():
    """Every tool the prose actually tells the user to run, from both sources.

    NOT LIMITED TO SECTION 8, AND THAT CAME OUT OF THE MEASUREMENT. Counting by hand said nine
    lines, all inside SECTION 8; the pattern found ten -- the tenth sat at the top of SECTION 9,
    and a check scoped to SECTION 8 would have reported a tool the contract plainly invoked as
    never invoked. `verify_setup.py` runs the other way round -- it appears in the HEADER and
    literally nowhere in the contract -- so both sources have to be read as one chain.

    THE NUMBER AND THE EXAMPLE BOTH MOVED (2026-07-31, re-measured here). That tenth line was
    `acceptance.py` at the top of SECTION 9. It is gone: the driver is REPO_ONLY since E3, and
    src/contract.md now carries no command line for it at all -- the only pages that name it are
    docs/, where naming a repo-only tool is how the release verification gets described, and the
    docs branch below allows exactly that. The scoping argument is unchanged, and the reason to
    read both sources is now `verify_setup.py` alone.

    Do not read this docstring for a current count -- that is what rotted. Read it off the run:
    `python -c "import build_kit; print(sorted(build_kit.chain_commands()))"`.
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

    `_`-prefixed keys are dropped, the same rule vaultkit.py's _mapping() applies, for the same
    reason: JSON has no comments, so `_comment` carries them, and it is not the name of a tool.
    Harmless here today -- no delivered file is called `_comment.py`, so a phantom entry excuses
    nothing that exists -- and filtered anyway, because the two readers of one file disagreeing
    about what counts as an entry is the shape this whole check exists to catch.
    """
    raw = json.loads((TOOLS / "jobs.json").read_text(encoding="utf-8-sig")).get("not_invoked") or {}
    if isinstance(raw, dict):
        return {name: reason for name, reason in raw.items() if not name.startswith("_")}
    return {name: "" for name in raw if not name.startswith("_")}


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

    # Direction 1, and it is strict where the reader is Claude and looser where the reader is a
    # human (2026-07-31). src/contract.md and the SECTION 10 header are instructions carried out
    # on the user's machine: a name there that is not in their folder is a command they type and
    # an error they get, no exceptions. docs/ describes the PROJECT, and since the suites moved
    # to the repository the honest thing for those pages to say is how the release was verified
    # -- which means naming tools that exist in tools/ and are deliberately not delivered.
    # Forbidding that would push the text into README.md to satisfy a check, which is the guard
    # shaping the prose instead of reading it.
    #
    # What both directions still refuse is a name that is nowhere: a typo, or a tool that left.
    ghosts, docs_ghosts = [], []
    for label, text in prose_sources():
        unknown = set(COMMAND_RE.findall(text)) - delivered
        if label.startswith("docs/"):
            docs_ghosts += [(label, name) for name in sorted(unknown - set(REPO_ONLY))]
        else:
            ghosts += [(label, name) for name in sorted(unknown)]
    if ghosts:
        print(f"{OUT.name}: the prose tells the user to run something that is not delivered.\n"
              + "\n".join(f"  {label} names {name}, which is not delivered"
                          for label, name in ghosts)
              + "\n  The user types it and gets an error. Either the tool left the delivery lists "
                "or the line has a typo.", file=sys.stderr)
        return 1
    if docs_ghosts:
        print(f"{OUT.name}: a docs page names a file that exists nowhere in tools/.\n"
              + "\n".join(f"  {label} names {name}, which is neither delivered nor repo-only"
                          for label, name in docs_ghosts)
              + "\n  A page may name a repo-only tool -- that is how the release verification is "
                "described. It may not name a file that does not exist.", file=sys.stderr)
        return 1

    # Subcommands, and they are checked in both directions for the same reasons the filenames
    # are. A name the prose invents is a line the user types and gets an error from; a
    # subcommand nothing calls is a tool sitting inside a file that IS called, which is the one
    # way a delivered guard can now go unnoticed. The way out is the same `not_invoked` in
    # jobs.json, read through the module the subcommand runs -- no second mechanism.
    register = dispatch_register()
    named_subs = {sub for _, text in prose_sources() for sub in SUBCOMMAND_RE.findall(text)}
    invented = sorted(named_subs - set(register))
    if invented:
        print(f"{OUT.name}: the prose names a vaultkit.py subcommand that does not exist.\n"
              + "\n".join(f"  vaultkit.py {sub}: no such subcommand" for sub in invented)
              + f"\n  Known: {', '.join(sorted(register))}. Either the register lost it or the "
                f"line has a typo.", file=sys.stderr)
        return 1
    # THE EXCUSE MOVED FROM jobs.json TO THE REGISTER (2026-07-31), and it is the same statement
    # in the place the fact lives. A subcommand carrying `job: None` reaches no verdict and never
    # logs, so there is nothing a chain could act on and nothing that could be late -- which is
    # exactly the reason `not_invoked` used to carry for `count_tokens`. With one file there are
    # no module filenames left to key that list by, and a second mechanism spelled by hand is
    # what this whole check exists to prevent.
    silent_subs = sorted(sub for sub, spec in register.items()
                         if sub not in named_subs and spec["job"])
    if silent_subs:
        print(f"{OUT.name}: a subcommand that ships and no chain calls.\n"
              + "\n".join(f"  vaultkit.py {sub}: logs as {register[sub]['job']!r}, and no "
                          f"command line names it" for sub in silent_subs)
              + "\n  A filename no longer tells you this: one file carries every guard, so an "
                "uncalled one hides inside a file the chain does run. Add it to a chain in "
                "src/contract.md -- or, if it genuinely reaches no verdict, give it `job: None` "
                "in the register with the reason beside it.", file=sys.stderr)
        return 1

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


def check_every_delivered_tool_has_a_suite():
    """Every delivered tool has a `test_X.py` IN THE REPOSITORY.

    THE RULE CHANGED SHAPE ON 2026-07-31, NOT STRENGTH. It used to read "every delivered tool
    ships with its suite", and that sentence stopped being checkable the moment no suite is
    delivered -- left as it was it would have fired eight times over a delivery that is exactly
    right. What still matters, and matters more now, is that nothing goes out untested: the user
    can no longer run a suite over their copy, so the only place that question is ever answered
    is here, before publishing.

    So the lookup moved from delivered_files() to the folder. SUITE_EXEMPT shrank to nothing in
    the same move: acceptance.py and verify_setup.py needed an exemption while they were
    delivered, and they are not delivered any more.

    Undo recipe: move `tools/test_count_tokens.py` OUT of tools/. `--check` exits 1 with
    `count_tokens.py: delivered, and there is no tools/test_count_tokens.py`. Move it back. A
    rename inside the folder measures something else -- check_delivery_lists() runs first and
    reports the renamed file as unaccounted for.
    """
    delivered = [name for name in delivered_files() if name.endswith(".py")]
    naked = sorted(name for name in delivered
                   if name not in SUITE_EXEMPT and not (TOOLS / f"test_{name}").is_file())
    if naked:
        print(f"{OUT.name}: a delivered tool has no suite in this repository.\n"
              + "\n".join(f"  {name}: delivered, and there is no tools/test_{name}"
                          for name in naked)
              + "\n  The user cannot run a suite over their copy any more, so this is the only "
                "place the question is ever asked. Write the suite, or add the tool to "
                "SUITE_EXEMPT in build_kit.py with the reason it does not need one.",
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
    import vaultkit

    try:
        config = json.loads((TOOLS / "jobs.json").read_text(encoding="utf-8-sig"))
    except (OSError, ValueError) as exc:
        print(f"{OUT.name}: tools/jobs.json cannot be read as JSON ({exc}). It is the only "
              f"non-Python block in the kit, so no compile step covers it.", file=sys.stderr)
        return 1

    # `_comment` is prose for the reader of the file and has no counterpart in code. It is
    # dropped rather than compared, in both mappings, so a sentence can be improved without
    # failing a build over it.
    def stated(key):
        raw = config.get(key)
        return ({k: v for k, v in raw.items() if k != "_comment"}
                if isinstance(raw, dict) else raw)

    pairs = (("jobs", stated("jobs"), vaultkit.DEFAULT_JOBS),
             ("on_demand", stated("on_demand"), vaultkit.DEFAULT_ON_DEMAND),
             ("not_invoked", stated("not_invoked"), vaultkit.DEFAULT_NOT_INVOKED))
    wrong = [f"  {key}: jobs.json says {shipped!r}, vaultkit.py says {code!r}"
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
    """Every logging label is a job name the register declares.

    THE RULE CHANGED ITS ANCHOR ON 2026-07-31, NOT ITS PURPOSE. It used to read "the label equals
    the stem of the file it is written in", and that was checkable while one file meant one job.
    With every guard inside `vaultkit.py` there is one filename for six jobs, so the old rule
    would have fired five times over labels that are exactly right. The register at the end of
    vaultkit.py states which job each subcommand logs under, so the register is the anchor now --
    and it is the same object `freshness` takes its population from, so the two cannot drift.

    THE WHOLE FAILURE CLASS IS SILENT, WHICH IS WHY IT NEEDS A BUILD-TIME CHECK. `freshness`
    matches log lines against the declared job names. A label that drifts puts BOTH names into
    `unclassified` -- the job nobody logged, and the label nobody declared -- and `unclassified`
    deliberately does not change the exit code. So a typo here costs a watched job its watching
    and prints two lines nothing acts on.

    Suites are skipped: they log under other jobs' names on purpose, as fixtures.

    Undo recipe: change the label in vaultkit.py's index run to `"build_indexx"`. `--check` exits
    1 with `vaultkit.py: logs as "build_indexx", which no subcommand declares`. Change it back.
    """
    declared = {spec["job"] for spec in dispatch_register().values() if spec["job"]}
    wrong = []
    for name in delivered_files():
        if not name.endswith(".py") or name.startswith("test_"):
            continue
        for label in LOG_CALL_RE.findall((TOOLS / name).read_text(encoding="utf-8")):
            if label not in declared:
                wrong.append(f'  {name}: logs as "{label}", which no subcommand declares')
    if wrong:
        print(f"{OUT.name}: a run log label is not a job any subcommand declares.\n"
              + "\n".join(sorted(set(wrong)))
              + f"\n  Declared: {', '.join(sorted(declared))}. `freshness` takes its population "
                f"from that register, so an undeclared label lands in `unclassified` -- and "
                f"unclassified does not change an exit code. The job stops being watched and no "
                f"run goes red over it.", file=sys.stderr)
        return 1
    unused = sorted(job for job in declared
                    if not any(job in LOG_CALL_RE.findall((TOOLS / n).read_text(encoding="utf-8"))
                               for n in delivered_files()
                               if n.endswith(".py") and not n.startswith("test_")))
    if unused:
        print(f"{OUT.name}: the register declares a job nothing ever logs.\n"
              + "\n".join(f"  {job}: declared in COMMANDS, and no code writes that label"
                          for job in unused)
              + "\n  `freshness` would then watch for a line that can never appear and report "
                "the job as stale forever, on a vault where nothing is wrong.", file=sys.stderr)
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


def check_generated_command():
    """The `/vaultkit` chain write_command.py emits, held to the same rule as the contract.

    WHY THIS EXISTS (2026-07-31): the delivered file the user reads most often is not in this
    repository at all -- it is generated into `~/.claude/commands/vaultkit.md` at setup. Every
    prose guard reads Markdown sources; this text is a Python f-string, so none of them saw it.
    Measured the day this was written: it had gone on emitting a step
    `## 6 · Run the suites` with `python …/run_suites.py` for a full release after that tool
    left the delivery. A user following their own maintenance command would have typed a line
    that cannot work, and no run anywhere was red about it.

    Rendered rather than pattern-matched over the source: what has to be right is the text the
    user gets, and a check reading the f-strings instead would pass over any name assembled at
    runtime.

    IT FOLLOWED THE TEXT WHEN THE TEXT MOVED (2026-07-31). `command_text()` used to live in
    write_command.py and lives in vaultkit.py now. A guard that kept importing the old module
    would have died with an ImportError -- loud, and therefore fine. The dangerous version is the
    one that keeps *running* and checks nothing, so what this asks for is the function by name,
    and it fails saying so if the function is not where it looked.

    Undo recipe: put `run_suites.py` back into command_text()'s step list. `--check` exits 1
    with `the /vaultkit chain names run_suites.py, which is not delivered`.
    """
    sys.path.insert(0, str(TOOLS))
    import vaultkit

    if not hasattr(vaultkit, "command_text"):
        print(f"{OUT.name}: vaultkit.py has no command_text(), so the /vaultkit chain this kit "
              f"generates is not checked by anything. It moved once already; if it moved again, "
              f"point this guard at it rather than letting the guard pass over nothing.",
              file=sys.stderr)
        return 1

    # A vault that does not exist and is never touched: command_text() only formats paths.
    text = vaultkit.command_text(REPO / "not-a-real-vault", [], "posix")
    delivered = {name for name in delivered_files() if name.endswith(".py")}
    register = dispatch_register()

    ghosts = sorted(set(COMMAND_RE.findall(text)) - delivered)
    if ghosts:
        print(f"{OUT.name}: the /vaultkit chain tells the user to run something undelivered.\n"
              + "\n".join(f"  the /vaultkit chain names {name}, which is not delivered"
                          for name in ghosts)
              + "\n  That file is generated into the user's own commands folder at setup, so a "
                "stale line there is one they type every time they sync.", file=sys.stderr)
        return 1
    invented = sorted(set(SUBCOMMAND_RE.findall(text)) - set(register))
    if invented:
        print(f"{OUT.name}: the /vaultkit chain names a subcommand that does not exist.\n"
              + "\n".join(f"  vaultkit.py {sub}: no such subcommand" for sub in invented)
              + f"\n  Known: {', '.join(sorted(register))}.", file=sys.stderr)
        return 1
    return 0


def all_guards():
    """Every build-time check, in the order a failure is cheapest to act on.

    Delivery first: check_prose_claims() imports acceptance and verify_setup, so a list naming a
    file that is not there has to be caught before anything tries to import from that folder.
    """
    return (check_delivery_lists() or check_every_delivered_tool_has_a_suite()
            or check_jobs_config_matches_code() or check_log_labels()
            or check_stream_reconfigure() or check_prose_claims() or check_prose_chain()
            or check_generated_command())


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
    parts.append("---\n\n*Generated by `tools/build_kit.py`. Edit the sources, never this file.*\n"
                 "*Source and newest published copy: "
                 "https://github.com/nibor1896/claude-obsidian-vault-kit*\n"
                 "*Compare the `kit-version` at the top against the published file to see whether "
                 "this copy is current.*\n")
    body = "\n".join(parts)
    return f"<!-- kit-version: {source_version(body)} -->{body}"


BLOCK_RE = re.compile(r"^### `([^`]+)`\n\n```(?:python|json)\n(.*?)\n```", re.S | re.M)


def verify():
    """Extract the scripts back out of the deliverable and check what came out.

    Everything else in this repo tests the sources. This tests the artefact the user actually
    receives -- a fence that swallowed a line, a block that never made it in, an embedded copy
    that drifted from tools/. None of those are visible from the source side.

    IT USED TO RUN THE SUITES FROM THE EXTRACTED FOLDER, AND SINCE 2026-07-31 IT CANNOT: they
    are not in the deliverable any more. What replaces them is not a weaker version of the same
    check, it is the same claim reached differently:

      - Every extracted block is compared byte for byte against tools/, and that already happens
        above. So "the delivered bytes are the repository's bytes" is established here.
      - `python tools/run_suites.py` runs those same repository bytes, in the repository.

    Those two together say exactly what running the suites from the extracted folder said. What
    this function still has to add is the part byte-equality does NOT cover: that the extracted
    file is a whole Python file rather than a truncated one that happens to match a truncated
    source, and that the one non-Python block parses. So: compileall over the folder, and
    json.loads over jobs.json -- the same two checks SECTION 10 now tells the setup to run.
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

        result = subprocess.run([sys.executable, "-m", "compileall", "-q", str(work)],
                                capture_output=True)
        if result.returncode != 0:
            print(f"{OUT.name}: an extracted block does not compile\n"
                  f"{result.stdout.decode('utf-8', errors='replace')}\n"
                  f"{result.stderr.decode('utf-8', errors='replace')}", file=sys.stderr)
            return 1
        print(f"  ok   every extracted .py compiles")
        try:
            json.loads((work / "jobs.json").read_text(encoding="utf-8-sig"))
        except (OSError, ValueError) as exc:
            print(f"{OUT.name}: the extracted jobs.json does not parse ({exc}). It is the only "
                  f"non-Python block, so compileall does not cover it.", file=sys.stderr)
            return 1
        print(f"  ok   the extracted jobs.json parses")
    finally:
        shutil.rmtree(work.parent, ignore_errors=True)
    failed = all_guards()
    if failed:
        return failed
    print(f"{OUT.name}: {len(blocks)} blocks extract, match tools/, compile and parse · "
          f"tools/ and the delivery lists agree · every delivered tool has a suite in this "
          f"repository · jobs.json matches its copy in code · every log label matches its file · "
          f"every runnable script fixes its streams · every count in the text matches the code · "
          f"no stale stamp quoted in the prose · every command names a file that exists, and "
          f"every delivered tool is called or excused")
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
