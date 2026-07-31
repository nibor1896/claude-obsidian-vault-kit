# How it works

The [README](../README.md) is the setup. This page is everything a reader wants *after* deciding to
try it: what the vault looks like, which rules carry it, what the machine needs, and how to check the
numbers yourself.

## What you end up with

- One folder per project, identical every time, so a path is predictable without looking.
- A three-level index — vault → project → category — **generated from note frontmatter only**. The
  generator has no access to note bodies, which is what structurally prevents prose from leaking into
  the index.
- Guard scripts that each refuse a silent zero: link resolution, duplicate detection, freshness of
  scheduled jobs, and a test runner that will not report green over zero collected suites.
- A note template per project, so the frontmatter header is filled in before you type anything.
- A `/vaultkit` slash command in `~/.claude/commands/`, carrying your vault's real paths, that runs
  the whole chain in the order that leaves nothing stale.
- A workflow document in your own words, so the next session reads it instead of re-deriving
  everything.

Two of those are quiet enough to miss when they work — the templates, and the version stamp that lets
a later kit tell you what an update would change. Both are written up for humans in
[updating-and-templates.md](updating-and-templates.md); the file you hand to Claude is written for
Claude.

## The part that actually matters

The folder names are cosmetic. These are not:

- **One insight, one file.** If a note's title needs the word "and", it is two notes.
- **The index is generated, never written.** Not an optimisation — a structural guarantee.
- **A degraded result makes the run red.** Missing `title:`, a wikilink pointing nowhere: reported,
  with a non-zero exit code. Silent repair means the note stays broken and nobody finds out.
- **No number without its denominator.** "0 broken links" is meaningless if the checker scanned zero
  files. Every check reports `n of m` and distinguishes pass, fail, and *did not run*.
- **A number written into a versioned file carries the command that reproduces it.** Otherwise it
  goes stale and gets quoted anyway.

Section 9 of the kit is an **acceptance test**: Claude has to feed each guard deliberately broken
input on your machine and show that it goes red. Clean input proves nothing, so the setup is not
reported as finished until that passes.

## Requirements

- Claude with file access to the folder you want the vault in
- Obsidian ([obsidian.md](https://obsidian.md)) — the kit offers to install it if you have not
- **Python 3.10+** for the guard scripts
- `git` — **recommended, not decorative.** Section 7 of the kit sets it up, `verify_setup.py` needs
  it, and the second half of every check is "the tree is still clean afterwards", which nothing else
  can answer. **GitHub is the optional part**, and a remote needs its own yes.
- Optional: a cloud-synced folder for backup — it knows file versions, git knows states across all
  notes, and neither replaces the other

**No third-party packages.** Every shipped tool imports the standard library and nothing else, so
there is no `pip install` and no `requirements.txt`. The single optional import is `tiktoken` in
`count_tokens.py`; without it that tool falls back to a character estimate and says so. No Obsidian
community plugin is required either — Templater was considered and deliberately dropped.

## Reproduce the numbers

The measurement quoted in the README describes **this repository**, not your vault, and it is
reproduced by cloning:

```
python tools/run_suites.py
python tools/acceptance.py --repeat 10
python tools/verify_setup.py --repeat 10
```

**Those three are not in your vault, on purpose.** They test the tools; your tools do not change
after setup, so a vault re-running them daily would re-answer a settled question about code nobody
touched. What your vault runs is the guard chain over your notes, which do change:

```
python <vault>/00_Global/06_tools/check_freshness.py --vault <vault>
python <vault>/00_Global/06_tools/build_index.py --root <vault>
python <vault>/00_Global/06_tools/check_links.py --vault <vault>
python <vault>/00_Global/06_tools/check_duplicates.py --vault <vault>
```

What a setup does check on your machine is that the blocks arrived whole:
`python -m compileall -q <vault>/00_Global/06_tools`, and that `jobs.json` parses. A block truncated
at a fence fails there; nothing else would notice it until a guard broke for an unrelated-looking
reason.

The exact counts live in `README.md` on purpose: `build_kit.py --check` reads that file and fails the
build if a number there disagrees with what the code counts. This page deliberately carries no `n/m`
of its own — see below.

## What is and is not covered by a check

Since 2026-07-31 `check_prose_chain()` **does** read these pages: every `python …x.py` line here is
compared against the files in `tools/`, so a misspelled tool name fails the build. What it does not
do is check the sentences around them.

`check_prose_claims()`, which holds every `n/m` to what the code counts, deliberately does **not**
read this page. It treats a source with zero matches as a defect — a claim a pattern stopped seeing
looks exactly like a claim that agrees — so putting these pages on that list would demand a number
in prose that reads better without one. That is why every measured figure stays in `README.md`, and
why a wrong *sentence* here still has to be caught by reading.

## Platforms

**Measured on Windows 11**, Python 3.13, under PowerShell 5.1 and Git Bash. That is the only
combination the quoted numbers describe.

**Not verified on macOS.** The `brew` path is plausible but has never been exercised. Reports from a
Mac are the most useful thing you can open an issue about.

**Linux was verified once, on the kit as it stood before the current rewrite** — Ubuntu under WSL2
with Python 3.14 and git 2.53: a cold run built the vault, every suite green, every acceptance
fixture and every setup step passing, every wikilink resolving, no drift on the second index run.
The counts that run reported are left out on purpose — they belong to a smaller kit, and a bare
count sitting in a paragraph of history gets quoted as a current measurement sooner or later. That
run measured code that has since changed (the tracker is gone, projects are scaffolded, every reader
is `utf-8-sig`), so it is history, not a current claim. One shell only — WSL ships bash, so the
PowerShell/Git-Bash comparison that catches encoding defects was not available there. `flatpak` and a
desktop Obsidian were not part of it.

## Before publishing a change

Cold-run it. A throwaway folder, a *fresh* Claude session with none of the authoring context, the
file dropped in, and naive answers — "don't know", "I don't understand that question". That is the
only test that finds wording which is only clear to whoever wrote it.
