<!-- kit-version: 6cd087d9fc96 -->
# Claude × Obsidian — Vault Kit

**What this file is:** a setup contract for Claude. Drop it into a Claude conversation and say
*"set this up for me"*. Claude will interview you first, then build a project-knowledge vault in
Obsidian with a **generated** index, a set of guards that refuse to lie to you, and a written
workflow you can hand to the next session.

**What it is not:** a finished vault. It contains no vault content — only the structure, the
contracts, and the rules that make the structure hold up over months.

**Why it exists.** Agent memory drifts. Chat scrollback disappears. Notes written by hand get an
index written by hand, which rots the moment someone is in a hurry. This kit fixes all three by
making one place the single source of truth, generating everything that can be generated, and
letting a check fail loudly instead of passing quietly.

---

## SECTION 0 — Instructions to Claude (read this before doing anything)

You are setting up a knowledge vault for the person who just handed you this file. Follow this
document in order. It is a contract, not a suggestion.

### Operating rules for this setup

1. **Speak the user's language.** This document is written in English. Conduct the entire setup
   dialog in whatever language the user writes to you in. Keep file names, frontmatter keys, CLI
   commands, and code in English regardless.
2. **Interview before you build.** Run SECTION 1 to completion. Do not create a folder, install
   software, or write a script before you have the answers you need. If an answer is missing and the
   next step depends on it, ask — do not assume.
   **Measuring the environment does not replace asking.** You may read the OS, shell, Python version
   and whether `git`/`gh` exist off disk instead of asking — say so when you do. You may not infer any
   answer that decides *what* gets written or *where*; SECTION 1 names those explicitly and none of
   them may be skipped, however obvious the disk makes them look.
3. **EVERY question goes through the structured question UI. Never as prose. No exceptions.**
   If your harness has a tool for asking the user questions with selectable options, that tool is the
   only way you are allowed to ask anything in SECTION 1 — not for one question, not for two, not for
   "just this quick one". A numbered list of questions inside a message is a violation even when it is
   short and even when it is polite.
   - **Fill the tool up.** Put as many of the round's questions into one call as the tool accepts
     (commonly four). Batching them is the behaviour that works — do not split a round into smaller
     pieces, and above all do not let a leftover question fall out into prose. There is no question
     count to stay under; the only limit is what the tool takes per call.
   - **Open-ended answers are asked the same way.** Project names, folder paths, an email address:
     put a concrete proposal as the first option, add the plausible alternatives, and let the free-text
     field take anything else. A path you propose is answered with one click. A path you request in
     prose costs a round trip and gets a partial answer.
   - **Never write "please answer all of these at once"**, and never continue a UI question with a
     prose follow-up in the same breath.
   - **If and only if your harness has no such tool**: ask exactly ONE question per message, and put
     nothing else in that message.
   Measured across three cold runs: rounds asked through the UI — four questions in a single call —
   were answered completely and immediately. The two runs that dropped into numbered prose questions
   were both abandoned by the user mid-setup. This is the most fragile part of the whole setup, which
   is why it is a rule and not a preference.
4. **Match the user's shell.** Ask which OS and shell they use, then emit commands in that syntax
   only. PowerShell has no `&&` and no `export`; POSIX shells have no `Get-ChildItem`. Mixing them
   costs the user a failed round trip every time.
5. **Never touch a path outside the vault and the tool folder** without saying which path and why,
   and waiting for a yes.
6. **The scripts are inside this file. Write them out; do not rewrite them.** SECTION 11 carries
   every tool, every suite and the three runners verbatim — measured on Windows 11 with Python 3.13
   under PowerShell 5.1 and Git Bash: **8/8 suites green, 10/10 acceptance checks and 10/10
   end-to-end setup steps, in ten consecutive runs under each shell.** Write each block to disk
   byte for byte. Retyping them from the contracts in SECTION 5 and SECTION 6 throws that
   measurement away and reintroduces the defects those sections describe — every one was found the
   expensive way. Change a shipped script only when the user's structure genuinely needs it, and
   then rerun the suites and `acceptance.py` before reporting anything.
   **Tell the user how to update later.** The header of this file carries a line like
   `<!-- kit-version: 435a3a2b532c -->`. It is a hash of the contract and every shipped script, so
   two copies with the same line are the same kit and a different line means something changed.
   Point them at `upgrade.py`, which is shipped alongside the other tools: given a newer kit file it
   lists what would be overwritten, writes nothing without `--apply`, and reruns the suites and the
   acceptance driver afterwards. Say this once during setup -- a user who does not know an update
   path exists will not go looking for one.
7. **The scripts do the mechanical work.** Do not hand-write an index, do not hand-count entries, do
   not eyeball whether links resolve. If a number can be measured, measure it with code. If it
   cannot, say "not measured".
8. **State every number's origin.** "12 of 14 links resolve, measured by `check_links.py`" — or
   nothing. Never present an estimate as a measurement.
9. **One task at a time, verified.** Finish and verify a step before starting the next. A half-built
   vault that reports success is worse than no vault.

### Deliverables at the end of setup

- The folder tree from SECTION 3, with real folders on disk.
- A generated index tree (SECTION 5) — root, project, category.
- The shipped `tools/` folder copied into the vault, suites and all.
- Optional: the GitHub issue mirror from SECTION 7.
- The four starting pages named in SECTION 9 — and **no other notes**. Nothing invented.
- Backup and git set up per SECTION 8.
- A verification run per SECTION 9, with its output shown to the user.
- **The acceptance test from SECTION 10, passed.** The setup is not finished until every guard has
  been shown to go red on deliberately bad input on this machine. Clean input proves nothing.

---

## SECTION 1 — Interview

**Read operating rule 3 again before you ask anything.** Every question below is asked through the
structured question UI, with options. Prose questions are not allowed here — not one, not two, not
"quickly". If you catch yourself typing "1." and "2." into a message, stop and use the tool.

**Batch each round into one call, as full as the tool allows.** There is no question count to stay
under. The failure mode is not "too many questions in one dialog" — it is a question that ends up
outside the dialog. Two cold runs died exactly there.

After each round, restate in **one line** what you now know, then ask the next. That is what lets the
user catch a wrong answer while it is still cheap to fix.

**What may be skipped, and what may not.** Skip a question only when it asks about a *prerequisite*
you can read off disk — OS, shell, Python version, whether `git` and `gh` exist — and then say out
loud which questions you skipped and what you measured.

**Never skip, never infer, no matter what the disk shows:**

- **1.1 — does the user already use Obsidian.** An installed app is not an answer. It says nothing
  about whether a vault exists, where it is, or whether the user wants you near it. Inferring "already
  uses Obsidian" from a present installation is how a setup ends up adapting a real vault nobody
  pointed you at.
- **1.2 — migration, new production vault, or test vault.**
- **1.3 — project names, and where their code lives.**
- **1.4 — whether a tracker gets mirrored, and which repos.** An authenticated `gh` is not consent.
  Finding credentials on the machine tells you the mirror is *possible*, not that it is wanted.
- **1.5 — the vault path, the backup, git, and whether a remote may be added.**
- **`user.email` — ask, even when an address is sitting right in front of you.** Your session
  context, another repo on the machine, a shell variable, a git credential store: **an address that
  is visible in your environment is not consent to publish it.** It goes into every commit forever,
  and the user may make that repo public later. One cold run took the operator's private mail address
  out of session context and set it without a word. Offer
  `<handle>@users.noreply.github.com` as the **first** clickable option, so the private-by-default
  answer is the cheap one.

The rule behind the list: **anything that decides what you write, or where, comes from the user's
mouth.** Reading the environment is measurement; deciding the destination is not.

### 1.1 Obsidian

**Ask this one out loud even if you can see Obsidian installed.** Say what you found — "I can see
Obsidian is installed" — and then ask anyway, because the installation answers a different question
than the one that matters here.

- **Do you already use Obsidian?** (yes / no / installed but unused)
- If **no**: *"Should I install it for you, or would you rather do it yourself?"* Offer both and
  wait. Never install without an explicit yes.
  - Install commands to offer, by platform:
    - Windows: `winget install Obsidian.Obsidian`
    - macOS: `brew install --cask obsidian`
    - Linux: flatpak `flatpak install flathub md.obsidian.Obsidian`, or the AppImage from
      obsidian.md
  - If the user prefers manual: give them the download page and wait for them to confirm it is
    installed before continuing.
- If **yes**: ask for the vault path. Whether that vault gets touched is decided in 1.2, not here —
  an existing vault plus a new production vault elsewhere is a normal answer. If 1.2 comes back as a
  migration, **read the existing structure before proposing anything**: list what is there, name what
  already matches this kit, and name what conflicts. Their existing structure wins over this document
  unless they say otherwise — a folder they use daily is worth more than a clean scheme they have to
  relearn.

### 1.2 What this setup is for

One question, three answers. Ask it in round one, next to 1.1.

```
What are we setting up?
  1  Production migration   an existing vault, adopted and brought in line
  2  New production vault    starts empty, this is the real one
  3  Test vault              throwaway, to look at and rearrange
```

- **1 — migration.** Go to the Appendix. Read what is there before proposing anything, show the user
  a two-column mapping of their folders to the roles in this kit, and get a yes before a single file
  moves.
- **2 and 3 build the same thing.** Same tree, same scripts, same starting pages. The difference is
  what happens around it: a test vault gets no backup and no remote, and the user is told it is
  disposable. Nothing is written differently because of this answer, so do not build a second copy of
  anything.
- **Whichever they pick, the structure is theirs to change.** After the tree exists, they open it in
  Obsidian, rename folders, drop categories, add their own. Then you **read the folders as they now
  are** and carry that through every project and every script config. Do not re-propose your original
  scheme. If they renamed `00_Notes` in one project only, say which reading you are taking —
  "everywhere" or "just there" — and get a yes. Silently applying it to one project leaves the vault
  inconsistent; silently applying it to all of them overrides a choice they may have made on purpose.

**Tell them what Obsidian will ask, before they start rearranging.** The moment they rename or move a
folder, Obsidian pops up *"Update internal links? This affects N links in N files."* Say in advance:
choose **"Don't update"**. The affected links live in generated index files, so letting Obsidian
rewrite them would hand-edit generated output — and the generator sets them correctly on its next run
anyway. Declining also makes that a real test instead of an assumption. Warning them afterwards is
worthless; the dialog is modal and they will have clicked it.

**Also warn about "Always update".** It is not a one-off answer, it writes a persistent setting into
that vault's `.obsidian/app.json`. Harmless here — the setting is per-vault, so a production vault
elsewhere is untouched — but say so, or they will assume they broke something they did not.


### 1.3 What is being documented

- **How many projects**, and what are their names? (One folder per project. The name becomes a
  folder name and appears in generated filenames — prefer no spaces, no `#`, `[`, `]`, `|`, `^`.)
- **Where does the code live** for each project? Absolute paths. May I read those repos, or is any
  of them off limits?
- **Is there a cross-project or "global" bucket** for things that belong to no single project
  (tooling, personal working rules, cross-cutting decisions)? Most people want one.

### 1.4 GitHub (optional — skip the whole of SECTION 7 if not)

- **Do you track work in GitHub issues?** If no, skip.
- **Which repos?** `owner/repo` for each.
- **Is the `gh` CLI installed and authenticated?** Verify with `gh auth status` rather than asking
  the user to trust their memory. If it is missing, offer the install command and wait.
- **Private repos?** Then the mirror on disk contains private content — confirm the user knows that
  before you write it anywhere synced or committed.

### 1.5 Where the vault lives, and how it survives

Four questions, one call:

- **The vault path.** Propose one and have it confirmed. It must sit inside the folder you were given.
- **Backup location.** Recommend a cloud-synced folder (OneDrive, Dropbox, iCloud Drive, Syncthing).
  Ask which one they use — and if a cloud folder exists on the machine but is out of bounds, say so
  rather than proposing it.
- **Git as well, and may a remote be added?** Recommend git: cloud sync knows file versions, git knows
  *states across all notes*. Neither replaces the other. "Yes to git" is not "yes to a remote" — if the
  vault will hold anything private, and a mirrored issue tracker usually does, the remote must be
  private, and that needs its own yes.
- **`user.name` and `user.email`** — ask for both, set them repo-locally, never `--global` (SECTION 8).
  Do not invent them and do not copy them from another repo on the machine. Offer a sensible default as
  the first option so it is one click.

### 1.6 Environment

- **OS and shell**, exactly. Every command you emit later depends on this.
- **Python 3.10+ available?** Check with `python --version` / `python3 --version`. The guard scripts
  are Python. If Python is absent, offer the install and wait.
- **Do you have agent memory / notes elsewhere** that should be imported (a `memory/` directory,
  scattered markdown, a Notion export)? If yes, ask for the path — but treat import as a *later*
  step, after the structure verifies clean.
---

## SECTION 2 — The doctrine (why the structure is shaped this way)

Tell the user these rules once, in plain language, and then hold to them for the rest of the setup.
They are the part that survives; the folder names are cosmetic by comparison.

1. **One insight, one file.** A note holds a single thing that is true. If a note needs the word
   "and" in its title, it is two notes.
2. **The filename carries the title, never just a number — and it is unique across the whole vault.**
   `ISSUE-42.md` tells nobody anything six weeks later. If a character is not legal in a filename,
   clean the title — do not drop it. A title that repeats in another project identifies nothing
   either: four files called `knowledge-transfer.md` are four indistinguishable nodes in the graph and
   a coin toss in the quick switcher. **Any file that exists once per project carries the project name
   in its filename.**

   **This is enforced by the index generator, not by a command someone has to remember.** It already
   walks every note, so it counts basenames while it does and reports a repeat as a defect with a
   non-zero exit (SECTION 5). A one-off check drifts out of use; a check on every run does not.
3. **The index is generated, never written.** The generator reads *frontmatter only* and has no
   access to note bodies. That is not an optimisation — it is the structural guarantee that prose can
   never leak into the index, because there is no code path by which it could.
4. **Generated folders are never hand-edited.** Anything a script rewrites on every run will eat
   your edit. Write upstream, read downstream.
5. **A degraded result makes the run red.** Missing `title:`, markdown debris in `summary:`, a
   wikilink pointing nowhere: shown *and* reported, with a non-zero exit code. Silent repair means
   the note stays broken and nobody finds out for months.
6. **No number without its denominator.** "0 broken links" is meaningless if the checker never found
   any files to check. Every check reports `n of m`, and refuses to report success when `m` is zero
   for an unexpected reason.
7. **A number written into a versioned file carries the command that reproduces it.** A comment
   stating a count is true the day it is written and unfalsifiable a month later. Put the one-liner
   that produces it right there, next to the number, so the next reader re-measures instead of
   quoting. A number with no reproduction path is how a config file ends up asserting something that
   stopped being true, with nobody able to tell.
8. **An error branch that continues is a lost denominator.** `except OSError: continue` inside a
   counting loop turns unreadable files into invisible ones: the count still prints, just over fewer
   items than it claims. Count skips explicitly and print them, or the run is a confident wrong
   answer rather than a failure.
9. **Every scheduled job logs every run, including the healthy ones.** Silence must mean "did not
   run", never "ran and was fine".
10. **A new tool ships with its `test_*.py` in the same commit.** A tool without a suite is invisible
    to the test runner — not red, *invisible*, which is worse.
11. **One commit per completed step.** A tool run is a commit. That is what makes a wrong move
    undoable.
12. **Nothing gets created outside the agreed structure.** If a context is missing — a folder for
    mockups, a place for meeting notes — ask the user whether to add one project-wide. Do not invent
    a folder in one project and leave the others inconsistent.

---

## SECTION 3 — Folder structure

Create this once per project. Every project gets the *same* folders, so a path is predictable
without looking.

```
<VaultRoot>/
├── INDEX - <VaultName>.md           generated — one line per project
├── 00_Global/                       optional: things belonging to no single project
│   └── (same subfolders as a project)
└── <ProjectName>/
    ├── INDEX - <ProjectName>.md     generated — one line per category
    ├── 00_Notes/                    insights with no ticket attached
    ├── 01_Issues/                   GENERATED mirror of the tracker (SECTION 7) — never hand-edit
    ├── 02_docs/                     product, project and decision documentation
    ├── 03_technical_docs/           the subsystem handbook — one page per subsystem
    ├── 04_feedback/                 working rules the user has given the agent
    ├── 05_workflows/                SOPs that apply to this project only
    └── 06_tools/                    scripts, plus this project's sources config
```

Rules for the tree:

- **The numeric prefixes exist for sort order only.** Keep them; they make Obsidian's file pane match
  the mental order.
- **Tools live in exactly one place.** Put the scripts under one project's `06_tools/` (or under
  `00_Global/06_tools/`) and have every other project supply only its own small config file. Two
  copies of a script means one of them is silently out of date.
- **Optional extras**, add only if the user has the need: `07_reports/` (one report per
  investigation), `08_issue_notes/` (hand-condensed notes about tickets, when the raw mirror is too
  long to read).
- If the user changed folder names in a test vault, **their names win** — carry them consistently
  into every project and into every script's config.

---

## SECTION 4 — Frontmatter contract

This is the interface between the notes and every script. Get it exactly right; everything
downstream reads it.

```yaml
---
title: "One line that states the insight"
summary: "One plain sentence. No markdown, no blockquote, no heading marks, no line breaks."
project: "<ProjectName>"
created: 2026-01-15
updated: 2026-02-03          # optional; the index prefers this over `created`
issues: "#12, #14"           # optional; plain text on purpose — see below
generator: "<source-file>"   # optional; presence means "the next rebuild overwrites this note"
retired: "<reason or date>"  # optional; the note is kept for history, not as current truth
stale: "2026-02-10"          # optional; source is newer than this condensation
---
```

Field semantics that matter:

- **`title` is required.** Without it the index falls back to the filename, which reads as
  `README` or `notes-2` in the list. That is a defect, and the index run must go red.
- **`summary` is required and must be plain.** If markdown debris ends up here — a leading `>`, a
  `#`, a `**` — the index line renders as garbage. The generator strips it, names the file, and
  exits non-zero.
- **`issues:` is deliberately not a wikilink.** A mention is a citation, not a membership. Making it
  a link pulls hundreds of note→ticket edges into the graph and turns it into a hairball. Membership
  is expressed once, in the tracker's own parent/child relation (SECTION 7).
- **`generator:` is the overwrite marker.** A note without it survives every rebuild — it is an
  original. A note with it is derived and replaceable. If a source document is deleted, retire it
  properly (remove the marker, drop the entry from the config) or the next run deletes the note with
  no replacement.

---

## SECTION 5 — The index generator (`build_index.py`)

Write this script. Contract, not code — implement it in Python 3.10+, standard library only.

### Behaviour

Three levels, because a single flat index becomes a star with hundreds of spokes and stops being
navigable at around 150 entries:

```
<VaultRoot>/INDEX - <VaultName>.md                   one line per project        --root
<Project>/INDEX - <Project>.md                       one line per category       --vault <dir>
<Project>/<Folder>/INDEX - <Project> <Category>.md   the entries themselves
```

- **Every index filename carries the name of what it indexes — at all three levels.** Every project
  has identically named folders, so without the project in the filename the graph shows five nodes
  called `INDEX - Issues` and the quick switcher becomes a coin toss.
- **This applies to the project and root hubs too, and that is easy to miss.** Naming them all
  `INDEX.md` produces one `INDEX` node per project plus one for the root — measured on a real vault:
  six files called `INDEX.md`, indistinguishable in the graph. The reasoning that forced the project
  name into the category filename does not stop one level up.
- **Read frontmatter only.** Never open a note body. This is the guarantee from SECTION 2.3.

### Entry line format

```
- [[Project/Folder/filename|Title]] — Summary · 2026-02-03 · #12 · generated
```

- Date is `updated`, else `created`. Trailing markers are appended only when present.
- **Wikilinks, not markdown links** — because the link checker (SECTION 6) resolves `[[...]]` and
  deliberately does not resolve `[text](path.md)`. An index built from unchecked links can rot
  invisibly.
- **Exception, by rule:** targets Obsidian does not index (`.py`, `.json`, other non-attachment
  types) keep a markdown link. A `[[tool.py]]` would be a permanently unresolved link.
- **Second exception:** a filename containing `#`, `[`, `]`, `|` or `^` cannot be wikilinked —
  Obsidian reads `#` as a heading anchor. Fall back to a markdown link so nothing is lost, print the
  offending filename on stderr, and **set the exit code**. That is a defect in the name, not a case
  to paper over.
- Truncate `title` to ~90 chars and `summary` to ~150, *after* applying warning prefixes, so a
  warning is never the first thing cut off.
- If `summary` merely repeats `title`, drop the summary — it adds nothing to a scan.
- `retired:` and `stale:` prepend a visible marker to the summary. A note whose source moved on must
  say so in the index, not only in its own frontmatter.

### Header of every generated file

```markdown
# <Name> — Index

> Generated by `06_tools/build_index.py` from note frontmatter.
> Do not edit by hand — changes belong in the note itself.
> As of: <YYYY-MM-DD>
```

### Two mechanics that produce output depending on how the script was called

Both were found by the acceptance test in SECTION 10, on a first real setup:

- **Derive every name from a resolved absolute path.** `Path(".").name` is the empty string, so
  `--root .` writes `# — Index` while `--root C:/…/Vault` writes `# Vault — Index`. Two correct
  invocations then produce a diff against each other, which is exactly the drift SECTION 9 forbids.
  Resolve first (`Path(p).resolve()`), then take `.name`.
- **A `[[wikilink]]` inside a code span or fenced block is not a link.** Obsidian does not resolve it,
  so the checker must not count it. Without this, every page that *documents* the wikilink syntax
  reports itself as broken — the prose is right and the checker is wrong, which is the worst way round
  because the instinct is to edit the note.
- **An escaped alias pipe, `[[note\|Title]]`, is a link.** In a Markdown table the pipe *must* be
  written `\|` or it ends the cell — that is Obsidian's own documented syntax, not a defect. A checker
  that splits on a bare `|` keeps the backslash in the target, resolves nothing, and reports a
  perfectly good link as broken: measured once as `61/62`, which then took `check_freshness` down with
  it. Unescape before splitting. Same failure mode as the code span above, same reason it costs so
  much: the note is right and the guard is wrong.

### Every generated filename comes from one function, and renaming one is not a one-line change

Two failures from doing this on a real vault, both cheap to avoid and expensive to find:

- **A filename used by more than one tool is computed in one place and imported.** Spelling it a
  second time in a freshness or hygiene check means that check reports the hub as *missing* for every
  project while the hub sits right next to it — a guard that fails loudly about the wrong thing is
  barely better than one that fails silently.
- **A generated file is linked to from other generated files, including backwards.** Each category
  index carries a back-link to its hub. Renaming the hub without following that link left 23 of 441
  wikilinks pointing nowhere. The link checker caught it; the test suite did not, because no test
  asserted the back-link. After any rename: grep the generator for every place it emits the old name,
  regenerate, **run the link checker**, and add the assertion the suite was missing.

### It also enforces unique filenames, because it is already walking every note

Count basenames while collecting frontmatter, and report any name used twice as a defect:

```
INDEX.md: name used 6 times (00_Global, ProjectA, ProjectB, …)
```

Doctrine rule 2 requires vault-wide unique filenames. That rule needs code reading it, or it holds
only as long as whoever is working remembers it. Read the paths as **bytes** from `git ls-files -z`
or by walking the tree — not from a shell pipeline, which differs per platform and breaks on names
containing non-ASCII (SECTION 6).

### It also reports a folder it walked past

The category list is configuration, and configuration goes stale the moment someone renames a folder
in the file pane. Walk the project's actual subfolders, compare them against the configured
categories, and report any folder that is not in the list as a defect with a non-zero exit:

```
ProjectB/06_werkzeuge: folder is not a configured category — nothing in it reaches an index
```

Measured on a first cold setup: renaming `06_tools` to `06_werkzeuge` in Obsidian took the run from
21 categories to 20 — **exit 0, no message on stderr, and the folder simply absent from every
index.** The index generator, the link checker and the duplicate check all reported green over it,
because none of them was asked what *should* have been there. SECTION 3 explicitly lets the user name
their own folders, which is exactly why the generator has to notice when they do.

The reverse case is the same defect: a configured category whose folder does not exist returns an
empty list today. Say so — `03_technical_docs: configured category has no folder` — rather than
counting it as zero clean entries.

### Exit code

`0` only when every entry was clean. Otherwise print each defect as `<filename>: <what is wrong>` on
stderr and exit non-zero. Report the totals as `n entries in m categories` so a zero has a
denominator.

---

## SECTION 6 — The guards

Each of these is a small script with one job, and each ships with a `test_*.py` in the same commit.
Every suite needs at least one **failure-mode fixture** *and* one **healthy control** — a test that
only ever sees good input cannot tell you the check still works.

| Script | Job | Must refuse |
|---|---|---|
| `build_index.py` | the index tree (SECTION 5) | a silent fallback on a degraded entry |
| `check_links.py` | every `[[wikilink]]` resolves to a file | reporting `0 broken` when it scanned 0 files |
| `check_duplicates.py` | notes whose content overlaps | being ignored — every hit gets a decision |
| `check_freshness.py` | age of the last **healthy** run of each scheduled job | treating "no log" as "fine" |
| `run_suites.py` | discovers and runs every `test_*.py` | reporting green when it collected zero suites |
| `count_tokens.py` | size of what was read, for cost | inventing a precision — output `exact` or `estimated` |

### The one rule all of them share

**Refuse a silent zero.** Every script prints numerator *and* denominator, and distinguishes three
outcomes explicitly: pass, fail, and *did not run*. A check that cannot tell "working" from "broken"
is not evidence.

### Force UTF-8 on stdout and stderr in every tool — first lines of every script

```python
import sys

for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass
```

**This is not cosmetic and it is not optional.** A child process inherits the console code page, which
differs per shell on the same machine — cp1252 under Git Bash, UTF-8 under PowerShell on Windows. A
defect message containing an umlaut then goes out as cp1252 while the reader decodes UTF-8, and the
suite dies in the reader thread. Measured on one machine: **the same six suites were 6/6 green under
PowerShell and 0/6 under Git Bash.** A guard whose verdict depends on which shell launched it is not
a guard.

**Do not "fix" this by restricting output to ASCII.** That is unreachable by construction: defect
messages name *filenames*, and filenames legitimately contain umlauts and accents. Forcing the
encoding is the fix; sanitising the content is a retreat that fails on the first non-ASCII note.

Every tool needs a test that asserts non-ASCII output survives a subprocess round trip — otherwise
this returns the moment someone adds a tool.

### Two more mechanics that break the rule quietly, both worth stating because they look like working code:

- **A skip that does not count itself.** `except OSError: continue` in a counting loop still prints a
  total — over fewer files than it names. Keep a `skipped` counter, print it, and treat a non-zero
  value as a defect rather than a footnote.
- **Paths that never reach the filesystem.** `git ls-files` *quotes* names containing non-ASCII, so
  feeding its plain output to `open()` fails on the quotation marks. Use `git ls-files -z`, split on
  `\0`, and pass bytes. Get this wrong and every note with an umlaut in its name silently leaves the
  denominator — which is exactly the class of file a knowledge vault is full of.

### `check_freshness.py` in particular

Any job on a schedule (task scheduler, cron, launchd) writes a line to an append-only log on **every
run, including the healthy ones**. `check_freshness.py` reads that log and reports the age of the
last healthy run per job, against a threshold the user sets. Without this, a scheduler that quietly
stopped firing looks identical to one that is fine.

Note for scheduled jobs on laptops: default task settings often include *do not start on battery*
and *do not catch up on missed runs*. That combination produces multi-hour gaps overnight that no
error message ever mentions. Tell the user this when you set up any schedule.

---

## SECTION 7 — Optional: mirror an issue tracker into the vault

Skip entirely if the user answered no in 1.4.

### The direction is one-way, and it is not negotiable

```
GitHub Issues  →  sync_issues.py  →  <Project>/01_Issues/*.md  →  read locally
     ↑
   writes go here only, via `gh issue comment` / `gh issue edit`
```

Every sync run **overwrites** the mirror. Anything typed into `01_Issues/` by hand is lost at the
next run, without warning. Say this to the user in exactly these terms, and repeat it in the
workflow file.

### `sync_issues.py` contract

- Fetch every issue **plus all comments** via `gh`, one file per issue:
  `<Project>/01_Issues/ISSUE-<N> - <Title>.md`.
- **Own the filenames.** Do not accept a tracker plugin's naming. Strip or replace `[`, `]`, `#`,
  `|`, `^` — a `[` in a filename breaks every wikilink pointing at it, and the graph loses the whole
  issue layer without a single error message.
- **Do not mangle the body.** Verify explicitly that code fences and backticks survive the round
  trip: count backticks in the API response, count them in the written file, and compare. A mirror
  that silently strips code snippets is worse than no mirror.
- **Membership comes from the tracker's own parent/child relation**, drawn as a wikilink in a
  `## Sub-Issues` section. A plain mention stays a plain link with no graph edge (SECTION 4).
- Frontmatter per mirrored issue: `title`, `summary`, `project`, `created`, `updated`, `issues`,
  plus a state field. Set `stale:` when the source is newer than a hand-written condensation of it.
- Write a run line to the freshness log every time, healthy or not.
- Pull the issue category index afterwards so the index never lags the mirror.

### Rate limits and caching

The API caches. A comment posted seconds ago may not appear in the next read. When a response looks
one step behind reality, that is the likely cause — do not conclude the write failed. Note this in
the workflow file so the next session does not rediscover it.

---

## SECTION 8 — Backup, git, and the two failure modes

Set up **both**, and tell the user why neither replaces the other: cloud sync knows file versions but
has no notion of a coherent state across all notes; git knows states but lives on the same disk.

**Put the vault in its own folder, not in the folder you were started in.** If the agent's own config
directory (`.claude/`, `.cursor/`, whatever the harness uses) sits next to the notes, it lands in the
vault's history. A subfolder — `<workdir>/<VaultName>/` — keeps the two apart with no ignore rules to
maintain.

**A fresh machine usually has no git identity at all**, and `git commit` then fails with *"Author
identity unknown"* mid-setup. Check before the first commit and set it **repo-locally** — never
`--global`, which writes outside the folder the user gave you:

```bash
git -C <VaultRoot> config user.name  "<name the user gives you>"
git -C <VaultRoot> config user.email "<email the user gives you>"
```

Ask for both. Do not invent them, and do not copy them from another repo on the machine — an identity
appears in every commit forever, and if the vault ever gets a remote it becomes public.

```powershell
# Windows / PowerShell — one command per line, no chaining
cd <VaultRoot>
git init
git add .gitattributes .gitignore "INDEX - <VaultName>.md"
git commit -m "chore: initialise vault"
```

```bash
# macOS / Linux
cd <VaultRoot>
git init
git add .gitattributes .gitignore "INDEX - <VaultName>.md"
git commit -m "chore: initialise vault"
```

`.gitattributes`:

```gitattributes
# Store every file exactly as it is on disk. Normalising line endings rewrites notes nobody
# edited and buries real changes in whole-file diffs.
* -text
```

Without it, a checkout on another machine rewrites line endings on notes nobody touched, and the
first diff is hundreds of files wide.

**Obsidian itself is the most frequent trigger, and it does not need you to edit anything.** Opening
a note can be enough: measured on 2026-07-27, two notes that were only read came out as 56 and 105
fully rewritten lines with zero content change. Tell the user this before it happens, because
`git status` then shows notes as modified that nobody wrote, and a session that trusts that signal
commits someone else's file under its own message.

**The diagnostic to remember:** a note that shows as fully rewritten — same line count out and in,
e.g. `@@ -233,233 +233,233 @@` — has almost certainly only changed its line endings. Confirm before
concluding anything:

```bash
git diff --ignore-cr-at-eol -- path/to/note.md
```

Empty output means the content is byte-identical and only CR moved. Across the whole tree, the same
question is one command:

```bash
git diff --ignore-cr-at-eol --name-only     # empty = nothing but line endings moved
``` Then decide deliberately: commit
the flip (ends the churn if a tool keeps writing that way) or restore the previous endings (right if
it was a one-off and the repo has a dominant convention). Find out which before choosing — grep the
tools for a writer of that file. "A tool must be rewriting it" is a guess, and it was wrong the one
time it mattered.

`.gitignore`:

```gitignore
# Third-party code, reinstallable from Obsidian.
.obsidian/plugins/

# Obsidian UI state — changes on every pane opened and every slider dragged, says nothing about
# the knowledge. graph.json is the one people forget: it stores node and line size, zoom and force
# strengths, so merely LOOKING at the graph view produces a commit-worthy diff.
.obsidian/workspace.json
.obsidian/workspace-mobile.json
.obsidian/graph.json

# Append-only run log that every tool writes a line to. Tracked, it makes git status dirty after
# every check, and acceptance fixture 6 permanently noisy. check_freshness.py reads it off disk,
# not out of git. Leading **/ on purpose: 06_tools/runs.log anchors to the repo root and would
# never match 00_Global/06_tools/runs.log -- measured twice, on two different setups.
**/runs.log

# Throwaway fixtures from the acceptance run.
_acceptance/

**/__pycache__/
*.pyc
.trash/
```

The rest of `.obsidian/` is worth versioning — it is the vault's configuration (appearance, hotkeys,
core-plugin settings). UI state and vendored code are the exceptions, and the list above must name
them all: a comment saying "the rest is versioned" while one UI-state file is still tracked reads as
a decision when it is an oversight.

Two more things to tell the user:

- **Set the vault folder to "always keep on this device"** in the cloud client. Otherwise the client
  can dehydrate files into placeholders and scripts read empty content — which looks exactly like an
  empty vault, with no error.
- **Stage named paths, never `git add -A` or `git add .`** if there is any chance a second session or
  editor is working in the same folder. One working directory has one index; `-A` commits somebody
  else's half-finished work under your message.
- **The suite is green before you commit, and you say which suite and how many.** Do not rely on the
  user's own tooling to enforce this — they may have a pre-commit discipline of their own and they may
  have none at all. This kit carries the rule itself: run every `test_*.py`, report `n/m`, and confirm
  with `git ls-files` that the suites you just cited are tracked. A number whose suite is not in the
  repo cannot be re-run by anyone, which makes it an assertion rather than a measurement.

---

## SECTION 9 — Verify, then hand over

### Verification run — all of it, no exceptions

```bash
python 06_tools/build_index.py --vault <Project>     # once per project
python 06_tools/build_index.py --root  <VaultRoot>
python 06_tools/check_links.py --vault <VaultRoot>
python 06_tools/check_duplicates.py --vault <Project>
python 06_tools/run_suites.py
```

**`build_index.py` is not a read-only measurement — it writes.** Say so before running it, and check
`git status` first so its output is not mistaken for someone else's uncommitted work.

**Then run the index generator a second time and confirm the tree is still clean:**

```bash
python 06_tools/build_index.py --vault <Project>
git status --porcelain          # must be empty
```

A generator that produces fresh drift on every run is indistinguishable from a clean one after a
single pass, and it turns every later `git status` into noise nobody reads. One extra run settles it.

Then report to the user in exactly this shape:

```
Created:   <folders> · <n> projects · <n> categories
Index:     <n> entries in <m> categories        (exit 0 | defects: …)
Links:     <n>/<m> resolve
Duplicates: <n> flagged
Tests:     <n>/<m> suites green
Commit:    <hash>
Open:      <what is not done, AND what you did not measure>
```

Rules for that report:

- **"Synchronised" appears only when every check is clean.** Otherwise the line names what is
  broken. A success message that also appears on failure is not a message.
- **`Open:` lists what you did not measure**, not only what is unfinished. Unmeasured and working
  look identical from the outside — that is the entire reason for measuring.
- If nothing was transferred, write `nothing new`, not an empty success.

**Three items belong under `Open:` on every first setup, because they are always true and always get
forgotten:**

- **No Obsidian client has opened this vault yet.** Your link checker saying 39/39 is not the client
  saying 39/39. Whether the indexes render, whether the graph is usable, whether the app resolves the
  wikilinks: unverified until the user opens it. Say this in exactly those terms — it is the single
  most misleading gap, because everything measurable already passed.
- **The duplicate-detection threshold is uncalibrated.** On a vault with a handful of notes the number
  it reports is arithmetic, not evidence. Name the threshold, say it has never been checked against
  real volume, and revisit it once the vault has one.
- **No backup outside this folder, and no remote.** Mishandling is covered by git; disk loss is not.

### The starting content is this list, and nothing else

Left unspecified, a setup invents notes: one run produced eight, including demo notes and restatements
of these rules under names of its own choosing. Each of them was reasonable and no two runs would
produce the same set — which makes the vault's starting state a coin toss and the doctrine
unquotable, because nobody can say which page holds it.

**Create exactly these, in the user's language:**

| Page | Where | Holds |
|---|---|---|
| `the-rules-this-vault-runs-on.md` | global bucket, `03_technical_docs` | the doctrine from SECTION 2, in the user's own words |
| `tooling-<Bucket>.md` | global bucket, `03_technical_docs` | the tools table: what each guard does and what it refuses |
| `acceptance-test.md` | global bucket, `03_technical_docs` | the fixtures and required behaviour from SECTION 10, repeatable |
| `knowledge-transfer-<Project>.md` | each project, `05_workflows` | the workflow below, one per project |

If there is no global bucket, they go in the first project instead — and say so, so nobody hunts for
them later.

**Create no other notes.** No example notes, no demo content, no page restating a rule that already
has one. An empty category is correct on day one: it still gets its index file, which is what proves
the structure works. Acceptance fixtures live in the throwaway folder from SECTION 10 and are deleted
with it.

### Write the workflow file

Create `<Project>/05_workflows/knowledge-transfer-<Project>.md` containing: the goal in one sentence,
the inputs, the tools table, the command sequence for *this user's* shell, the expected output, and the
edge cases you hit during setup. This is what makes the vault survive you — the next session reads
this file instead of re-deriving the whole thing.

**The project name in that filename is not decoration.** One file per project all called
`knowledge-transfer.md` gives the graph four identical nodes and the quick switcher four identical
rows — see doctrine rule 2. Same for any other page you create once per project.

**Write what differs, link what does not — or the duplicate check will say so.** Filling the same
outline twice produces two pages that are mostly the same words: measured at 0.93 overlap on one
setup and flagged on another, both times correctly. Anything true for every project — the frontmatter
contract, the command sequence, what each guard refuses — belongs once in the global bucket's tooling
page, with a wikilink from each project page. What stays on the project page is what is only true
there: where its code lives, its decisions, its edge cases. Do this while writing them; fixing it
after the guard fires costs a rewrite and a second verification run.

**A wikilink in a table cell needs its pipe escaped: `[[note\|Title]]`.** These pages carry tables —
the tools table, the fixture table — and an unescaped alias pipe silently ends the cell, so the row
renders short and the link is gone. Obsidian documents `\|` as the way to write it; the link checker
resolves it (SECTION 5). Write it escaped, do not dodge the table.

### Tell the user how to use it from here on

- **New insight with no ticket** → a new file in `00_Notes/`, filename = the insight, frontmatter per
  SECTION 4. Then rerun `build_index.py`.
- **Insight tied to a ticket** → write it on the ticket via `gh`, let the sync bring it back. Never
  into `01_Issues/` by hand.
- **New subsystem or feature** → a page in `03_technical_docs/` in the same commit as the code.
  Numbers on that page are either measured or explicitly marked unmeasured.
- **Stuck on something?** Search `00_Notes/` first. A past procedure that already fits beats a new
  one you invent now.

---

## SECTION 10 — Acceptance test: prove the guards fail when they should

**Do not skip this, and do not report the setup as working before it passes.** Everything up to here
proves the scripts run on clean input. That is the half that cannot fail. A guard is only worth
having if it goes red on bad input, and the only way to know is to hand it bad input on *this*
machine — not to reason about the code you just wrote.

**Run the shipped driver. Do not write your own.**

```
python <vault>/00_Global/06_tools/acceptance.py
```

It builds a throwaway vault per fixture under the system temp directory, so it never touches the
user's notes, and it takes its verdict from process exit codes and files on disk — never from
parsing console output, which wraps at the terminal width and differs per shell. Expect
`10/10 checks behaved as specified`. Anything less is a defect in a script, not in the expectation.
`--repeat 10` runs ten full passes; use it after any change to a guard.

The table below is what the driver checks, and it is the specification a changed script must still
meet. Fixture 0 is the healthy control: a suite that only ever sees bad input is exactly as blind as
one that only ever sees good input.

| # | Fixture | Required behaviour | Fails how, if broken |
|---|---|---|---|
| 0 | a clean vault with two notes | every tool exits 0 with a denominator, and a second index run is byte-identical | a guard that is red on everything looks careful and proves nothing |
| 1 | note with no `title:` | index run exits **non-zero** and names the file on stderr | exits 0, filename appears as the entry title, nobody notices for months |
| 2 | note whose `summary:` starts with `>` or `#` | debris stripped, file named, exit non-zero | index line renders as `— > Living inventory …` |
| 3 | `[[wikilink]]` to a note that does not exist | link checker reports it, exit non-zero, **denominator > 0** | reports "0 broken" because it scanned nothing |
| 4 | note whose filename contains `#` | entry falls back to a markdown link, file named, exit non-zero | silent unresolvable wikilink |
| 5 | note whose filename contains a non-ASCII character (umlaut, accent) | it appears in the index and in the link count | it is silently absent from the denominator |
| 6 | nothing — run the index generator twice | second run leaves `git status` empty | every later `git status` is noise |
| 7 | point the suite runner at an empty directory | reports **"0 suites collected"** and does **not** say green | "all green" over zero tests |
| 8 | remove or blank a scheduled job's run log | freshness check says **"did not run"**, not "fine" | a scheduler that stopped is indistinguishable from a healthy one |
| 9 | a folder the config does not know — `<Project>/99_extra/` with one note in it | index run names the folder and exits **non-zero** | exit 0 and the folder is in no index; measured on a real setup, a renamed `06_tools` took the count from 21 categories to 20 without a word |

The driver leaves nothing behind — every fixture vault lives under the system temp directory and is
deleted in a `finally` block. After the run, `git status --porcelain` in the real vault must still be
empty; if it is not, something wrote outside the throwaway tree and that is the finding.

**Run the suites under every shell the user has**, not just the one you happen to be in. On Windows
that means PowerShell *and* Git Bash. This is where the encoding defect in SECTION 6 shows up, and it
is invisible from inside a single shell.

Report it like this, one line per check, and **name any check you did not run**:

```
Acceptance: 10/10 checks behaved as specified (9 red on bad input, 1 healthy control green)
            (or) 8/10 — #5 non-ASCII filename NOT caught, #9 not run
```

If a check does not behave as specified, the generated script is wrong — fix the script, not the
expectation. A guard that passes bad input is worse than no guard, because it will be cited as
evidence.

### Write the acceptance run into the vault, and repeat it after every script change

Two rules that make this a check rather than a ceremony:

- **The run belongs in the vault as `03_technical_docs/acceptance-test.md`**, with each fixture, the
  command, and the required behaviour — not only in the chat where it was performed. A one-off that
  lives in a conversation cannot be repeated by whoever inherits the vault.
- **Any change to a guard invalidates the last acceptance result.** Fixed a script after the run?
  Then the run is over and the number is no longer true — repeat all of it, not the affected check.
  Saying "10/10" after editing two tools is quoting a measurement of code that no longer exists.

---

## Appendix — Adapting an existing vault

If the user already has a vault (1.1 answered yes):

1. **Read before you propose.** List every existing folder and note count. Show the user what you
   found.
2. **Map, do not migrate blindly.** Produce a two-column mapping — their folder → the role it plays
   in this kit — and get it confirmed before a single file moves.
3. **Never bulk-move files without git in place first.** Commit the untouched state, then move, so
   one command undoes a wrong call.
4. **Add frontmatter incrementally.** Notes without `title:` will show as defects. That list *is*
   the backlog — work it down, do not silence the check to make it green.
5. **Leave their conventions alone where they conflict harmlessly.** This kit's value is in
   SECTION 2, not in the exact digits in front of the folder names.

---

*This kit describes structure and rules only. It contains no project data.*

---

## SECTION 11 — The scripts, verbatim

Everything below is the finished implementation. **Write each block to disk exactly as it stands —
byte for byte, same filename — into the vault's tool folder** (`<VaultRoot>/00_Global/06_tools/`,
created in SECTION 3). Do not retype them from the contracts above, do not "improve" them while
copying, and do not skip the suites: they are the only reason the numbers in SECTION 0 mean
anything.

Measured on Windows 11, Python 3.13, under PowerShell 5.1 **and** Git Bash: 8/8 suites green,
10/10 acceptance checks correct, 10/10 end-to-end setup steps -- ten consecutive runs under each
shell. Copy them and that measurement still applies to what you handed the user. Rewrite them and
it does not.

**Write them as UTF-8 without a byte-order mark.** `Set-Content -Encoding utf8` under PowerShell 5.1
prepends a BOM, and a BOM in front of `import sys` is an invisible first character that some readers
choke on. Use your file-writing tool, or Python. This cost a full round on one setup, and the error
pointed at the wrong line.

After writing them, prove it on this machine before you report anything:

```
python <vault>/00_Global/06_tools/run_suites.py       expect 8/8 suites green
python <vault>/00_Global/06_tools/acceptance.py       expect 10/10 checks
python <vault>/00_Global/06_tools/verify_setup.py     expect 10/10 steps
```

#### Shared

### `vault_paths.py`

```python
"""Single source of truth for every generated filename and every path rule.

Spelling a generated filename a second time in another tool is how a guard ends up
reporting the index hub as "missing" while the hub sits right next to it. Every tool
imports from here instead.
"""

import sys

for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass

import re
from pathlib import Path

# The category folders every project gets. Numeric prefixes exist for sort order only.
CATEGORY_FOLDERS = [
    "00_Notes",
    "01_Issues",
    "02_docs",
    "03_technical_docs",
    "04_feedback",
    "05_workflows",
    "06_tools",
]

# Directories that are never notes and never walked.
SKIP_DIRS = {".git", ".obsidian", "__pycache__", ".trash", ".venv", "node_modules"}

# Characters Obsidian cannot carry inside a [[wikilink]] target.
FORBIDDEN_LINK_CHARS = set("#[]|^")

# Append-only log of every tool run, healthy ones included. Read by check_freshness.py.
RUN_LOG_RELPATH = Path("00_Global") / "06_tools" / "runs.log"


def force_utf8():
    """Re-export of the stdout/stderr fix so tests can assert it exists."""
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass


def category_label(folder_name: str) -> str:
    """'03_technical_docs' -> 'technical_docs'. The prefix is sort order, not meaning."""
    return re.sub(r"^\d+_", "", folder_name)


def root_index_name(vault_root) -> str:
    """'INDEX - <VaultName>.md'.

    The name is derived from a RESOLVED path on purpose: Path('.').name is the empty
    string, so `--root .` would write '# — Index' while `--root C:/.../Vault` writes
    '# Vault — Index'. Two correct invocations must not produce a diff against each other.
    """
    return f"INDEX - {Path(vault_root).resolve().name}.md"


def project_index_name(project_dir) -> str:
    """'INDEX - <ProjectName>.md' — the project hub."""
    return f"INDEX - {Path(project_dir).resolve().name}.md"


def category_index_name(project_name: str, folder_name: str) -> str:
    """'INDEX - <Project> <Category>.md'.

    Every project has identically named folders. Without the project in the filename the
    graph shows one node called 'INDEX - Issues' per project and the quick switcher
    becomes a coin toss.
    """
    return f"INDEX - {project_name} {category_label(folder_name)}.md"


def is_index_file(path) -> bool:
    return Path(path).name.startswith("INDEX - ")


def project_dirs(vault_root):
    """Every project directory directly under the vault root, sorted."""
    root = Path(vault_root).resolve()
    out = []
    for child in sorted(root.iterdir()):
        if not child.is_dir():
            continue
        if child.name in SKIP_DIRS or child.name.startswith("."):
            continue
        out.append(child)
    return out


def walk_markdown(root):
    """Every .md file under root, skipping SKIP_DIRS. Sorted, so output is stable."""
    root = Path(root).resolve()
    found = []
    for path in root.rglob("*.md"):
        if any(part in SKIP_DIRS for part in path.relative_to(root).parts[:-1]):
            continue
        found.append(path)
    return sorted(found)


def has_forbidden_chars(name: str) -> bool:
    return any(ch in FORBIDDEN_LINK_CHARS for ch in name)


def log_run(vault_root, job: str, status: str, detail: str = ""):
    """Append one line per run, healthy ones included.

    Silence must mean 'did not run', never 'ran and was fine'.
    """
    from datetime import datetime, timezone

    log_path = Path(vault_root).resolve() / RUN_LOG_RELPATH
    try:
        log_path.parent.mkdir(parents=True, exist_ok=True)
        stamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S+00:00")
        line = f"{stamp}\t{job}\t{status}\t{detail}\n"
        with open(log_path, "a", encoding="utf-8") as fh:
            fh.write(line)
    except OSError as exc:
        print(f"run log not written: {exc}", file=sys.stderr)
```

### `_testkit.py`

```python
"""Shared fixtures for the tool suites.

Deliberately NOT named test_*.py: run_suites.py collects by that glob and a helper module
with no tests would be counted as a green suite.
"""

import os
import subprocess
import sys
import tempfile
from pathlib import Path

TOOLS = Path(__file__).resolve().parent

CATEGORY_FOLDERS = [
    "00_Notes",
    "01_Issues",
    "02_docs",
    "03_technical_docs",
    "04_feedback",
    "05_workflows",
    "06_tools",
]


def make_vault(projects=("ProjektEins",)):
    """A throwaway vault with the real folder tree. Caller deletes the returned tempdir."""
    tmp = Path(tempfile.mkdtemp(prefix="vaultkit_")) / "Vault"
    for project in projects:
        for folder in CATEGORY_FOLDERS:
            (tmp / project / folder).mkdir(parents=True, exist_ok=True)
    (tmp / "00_Global" / "06_tools").mkdir(parents=True, exist_ok=True)
    return tmp


def write_note(path, title="Ein Titel", summary="Eine Zusammenfassung.", **extra):
    """Write a note with frontmatter. Pass title=None or summary=None to omit the key."""
    lines = ["---"]
    if title is not None:
        lines.append(f'title: "{title}"')
    if summary is not None:
        lines.append(f'summary: "{summary}"')
    for key, value in extra.items():
        lines.append(f'{key}: "{value}"')
    lines += ["---", "", "Body text that the index generator must never read.", ""]
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8", newline="\n")
    return path


def run_tool(script, *args, strip_io_encoding=True):
    """Run a tool as a real subprocess. Returns (returncode, stdout, stderr) as UTF-8 text.

    PYTHONIOENCODING is removed on purpose: the tools must force UTF-8 themselves, or the
    same suite goes green under PowerShell and red under Git Bash on one machine.
    """
    env = dict(os.environ)
    env["PYTHONPATH"] = str(TOOLS) + os.pathsep + env.get("PYTHONPATH", "")
    if strip_io_encoding:
        env.pop("PYTHONIOENCODING", None)
        env.pop("PYTHONUTF8", None)
    result = subprocess.run(
        [sys.executable, str(TOOLS / script), *[str(a) for a in args]],
        cwd=str(TOOLS),
        env=env,
        capture_output=True,
    )
    return (
        result.returncode,
        result.stdout.decode("utf-8", errors="replace"),
        result.stderr.decode("utf-8", errors="replace"),
    )
```

### `jobs.json`

```json
{
  "_comment": "Jobs that must show a healthy run in runs.log. Verify with: python check_freshness.py --vault <VaultRoot>",
  "jobs": ["build_index", "check_links"]
}
```

#### Tools

### `build_index.py`

```python
"""Generate the three-level index tree from note frontmatter.

    <VaultRoot>/INDEX - <VaultName>.md                   one line per project     --root
    <Project>/INDEX - <Project>.md                       one line per category    --vault <dir>
    <Project>/<Folder>/INDEX - <Project> <Category>.md   the entries themselves

Reads FRONTMATTER ONLY. There is no code path in this file that opens a note body, which
is the structural guarantee that prose can never leak into the index.

Exit code is 0 only when every entry was clean. Otherwise each defect is printed as
"<filename>: <what is wrong>" on stderr and the exit code is non-zero.
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
from datetime import date
from pathlib import Path
from urllib.parse import quote

from vault_paths import (
    CATEGORY_FOLDERS,
    SKIP_DIRS,
    category_index_name,
    category_label,
    has_forbidden_chars,
    is_index_file,
    log_run,
    project_dirs,
    project_index_name,
    root_index_name,
    walk_markdown,
)

TITLE_MAX = 90
SUMMARY_MAX = 150

HEADER = """# {name} — Index

> Generated by `06_tools/build_index.py` from note frontmatter.
> Do not edit by hand — changes belong in the note itself.
> As of: {today}
"""


class Defects:
    """Collects defects. A non-empty instance makes the run red."""

    def __init__(self):
        self.items = []
        self.skipped = 0

    def add(self, filename, message):
        self.items.append((str(filename), message))

    def report(self):
        for filename, message in self.items:
            print(f"{filename}: {message}", file=sys.stderr)

    def __len__(self):
        return len(self.items)


# --------------------------------------------------------------------------- frontmatter


def read_frontmatter(path, defects):
    """Return the frontmatter mapping of a note, or None if it has none.

    Stops reading at the closing '---'. Body lines are never collected, never returned.
    """
    data = {}
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as fh:
            first = fh.readline()
            if first.strip() != "---":
                return None
            for line in fh:
                if line.strip() in ("---", "..."):
                    return data
                key, sep, value = line.partition(":")
                if not sep:
                    continue
                key = key.strip()
                if not key or key.startswith("#"):
                    continue
                data[key] = _clean_scalar(value)
    except OSError as exc:
        # An error branch that continues is a lost denominator: count it, print it.
        defects.skipped += 1
        defects.add(Path(path).name, f"unreadable ({exc})")
        return None
    # File ended before the closing '---'.
    defects.add(Path(path).name, "frontmatter block is not closed by '---'")
    return data


def _clean_scalar(value):
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
        return value[1:-1].strip()
    # An unquoted '#' starts a YAML comment. A quoted one (issues: "#12") never reaches here.
    value = re.split(r"\s+#", value, maxsplit=1)[0]
    return value.strip()


MARKDOWN_DEBRIS = re.compile(r"^\s*(?:>+\s*|#{1,6}\s+|[-*+]\s+|\d+\.\s+)")


def clean_summary(raw):
    """Return (cleaned, was_dirty). Debris in summary renders the index line as garbage."""
    text = raw
    dirty = False
    while True:
        stripped = MARKDOWN_DEBRIS.sub("", text)
        if stripped == text:
            break
        text = stripped
        dirty = True
    for marker in ("**", "__", "`"):
        if marker in text:
            text = text.replace(marker, "")
            dirty = True
    if "\n" in text or "\r" in text:
        text = re.sub(r"[\r\n]+", " ", text)
        dirty = True
    collapsed = re.sub(r"\s{2,}", " ", text).strip()
    if collapsed != text.strip():
        dirty = True
    return collapsed, dirty


def truncate(text, limit):
    if len(text) <= limit:
        return text
    return text[: limit - 1].rstrip() + "…"


# --------------------------------------------------------------------------- links


def link_to(vault_root, target_path, label, defects):
    """A [[wikilink]] where Obsidian can resolve one, a markdown link where it cannot.

    The link checker resolves [[...]] and deliberately does not resolve [text](path).
    So every fallback to a markdown link is a defect in the filename, not a workaround.
    """
    rel = Path(target_path).resolve().relative_to(Path(vault_root).resolve()).as_posix()
    name = Path(target_path).name
    if has_forbidden_chars(name):
        defects.add(name, "filename contains one of # [ ] | ^ — cannot be wikilinked")
        return f"[{label}]({quote(rel)})"
    if not name.lower().endswith(".md"):
        # Obsidian does not index these; a [[tool.py]] would be permanently unresolved.
        return f"[{label}]({quote(rel)})"
    return f"[[{rel[:-3]}|{label}]]"


# --------------------------------------------------------------------------- entries


def collect_entries(vault_root, project_dir, folder_name, defects):
    """One entry dict per note in <project>/<folder>. Frontmatter only."""
    folder = Path(project_dir) / folder_name
    entries = []
    if not folder.is_dir():
        return entries
    for path in sorted(folder.glob("*.md")):
        if is_index_file(path):
            continue
        fm = read_frontmatter(path, defects)
        name = path.name
        if fm is None:
            defects.add(name, "no frontmatter block")
            fm = {}

        title = fm.get("title", "").strip()
        if not title:
            defects.add(name, "missing 'title:' — index falls back to the filename")
            title = path.stem

        summary_raw = fm.get("summary", "").strip()
        if not summary_raw:
            defects.add(name, "missing 'summary:'")
        summary, dirty = clean_summary(summary_raw)
        if dirty:
            defects.add(name, "markdown debris in 'summary:' — stripped for the index")
        if summary and summary.strip().lower() == title.strip().lower():
            summary = ""

        prefixes = []
        if fm.get("retired"):
            prefixes.append(f"[retired: {fm['retired']}]")
        if fm.get("stale"):
            prefixes.append(f"[stale since {fm['stale']}]")
        if prefixes:
            summary = " ".join(prefixes) + (f" {summary}" if summary else "")

        entries.append(
            {
                "path": path,
                "title": truncate(title, TITLE_MAX),
                "summary": truncate(summary, SUMMARY_MAX),
                "date": fm.get("updated") or fm.get("created") or "",
                "issues": fm.get("issues", ""),
                "generated": bool(fm.get("generator")),
            }
        )
    return entries


def entry_line(vault_root, entry, defects):
    parts = [f"- {link_to(vault_root, entry['path'], entry['title'], defects)}"]
    tail = []
    if entry["summary"]:
        tail.append(entry["summary"])
    if entry["date"]:
        tail.append(str(entry["date"]))
    if entry["issues"]:
        tail.append(str(entry["issues"]))
    if entry["generated"]:
        tail.append("generated")
    if tail:
        parts.append("— " + " · ".join(tail))
    return " ".join(parts)


# --------------------------------------------------------------------------- writing


def write_if_changed(path, content):
    """Write only on a real change, so a rerun leaves `git status` empty."""
    path = Path(path)
    try:
        if path.exists() and path.read_text(encoding="utf-8") == content:
            return False
    except OSError:
        pass
    path.write_text(content, encoding="utf-8", newline="\n")
    return True


def build_project(vault_root, project_dir, defects):
    """Write every category index plus the project hub. Returns (entries, categories)."""
    project_dir = Path(project_dir).resolve()
    project_name = project_dir.name
    today = date.today().isoformat()
    total_entries = 0
    category_rows = []

    for folder_name in CATEGORY_FOLDERS:
        folder = project_dir / folder_name
        if not folder.is_dir():
            continue
        entries = collect_entries(vault_root, project_dir, folder_name, defects)
        total_entries += len(entries)

        lines = [HEADER.format(name=f"{project_name} — {category_label(folder_name)}", today=today)]
        hub = project_dir / project_index_name(project_dir)
        lines.append(f"↑ {link_to(vault_root, hub, project_name, defects)}\n")
        if entries:
            for entry in entries:
                lines.append(entry_line(vault_root, entry, defects))
        else:
            lines.append("_No notes in this category yet._")
        lines.append("")
        lines.append(f"_{len(entries)} entries._")
        lines.append("")
        write_if_changed(folder / category_index_name(project_name, folder_name), "\n".join(lines))
        category_rows.append((folder_name, len(entries)))

    # A folder nobody configured is a folder nobody indexes. Renaming 06_tools in the file pane
    # once took a real run from 21 categories to 20 with exit 0 and no message -- the notes were
    # simply gone from every index. Say it instead.
    known = set(CATEGORY_FOLDERS)
    for child in sorted(project_dir.iterdir()):
        if not child.is_dir() or child.name.startswith("."):
            continue
        if child.name not in known:
            defects.add(f"{project_name}/{child.name}",
                        "folder is not a configured category - nothing in it reaches an index")

    lines = [HEADER.format(name=project_name, today=today)]
    root_hub = Path(vault_root).resolve() / root_index_name(vault_root)
    lines.append(f"↑ {link_to(vault_root, root_hub, Path(vault_root).resolve().name, defects)}\n")
    for folder_name, count in category_rows:
        target = project_dir / folder_name / category_index_name(project_name, folder_name)
        label = category_label(folder_name)
        lines.append(f"- {link_to(vault_root, target, label, defects)} — {count} entries")
    lines.append("")
    lines.append(f"_{total_entries} entries in {len(category_rows)} categories._")
    lines.append("")
    write_if_changed(project_dir / project_index_name(project_dir), "\n".join(lines))
    return total_entries, len(category_rows)


def build_root(vault_root, defects):
    vault_root = Path(vault_root).resolve()
    today = date.today().isoformat()
    lines = [HEADER.format(name=vault_root.name, today=today)]
    total_entries = 0
    total_categories = 0
    projects = project_dirs(vault_root)
    for project in projects:
        entries, categories = build_project(vault_root, project, defects)
        total_entries += entries
        total_categories += categories
        target = project / project_index_name(project)
        lines.append(
            f"- {link_to(vault_root, target, project.name, defects)} "
            f"— {entries} entries in {categories} categories"
        )
    lines.append("")
    lines.append(f"_{len(projects)} projects · {total_entries} entries in {total_categories} categories._")
    lines.append("")
    write_if_changed(vault_root / root_index_name(vault_root), "\n".join(lines))
    return len(projects), total_entries, total_categories


# --------------------------------------------------------------------------- uniqueness


def check_unique_basenames(vault_root, defects):
    """Doctrine rule 2 needs code reading it, or it holds only while someone remembers it.

    The generator already walks every note, so it counts basenames while it does.
    """
    seen = defaultdict(list)
    for path in walk_markdown(vault_root):
        seen[path.name].append(path)
    for name, paths in sorted(seen.items()):
        if len(paths) > 1:
            where = ", ".join(sorted(p.parent.name for p in paths))
            defects.add(name, f"name used {len(paths)} times ({where})")
    return len(seen)


# --------------------------------------------------------------------------- main


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--root", help="vault root: writes the root index and every project below it")
    group.add_argument("--vault", help="one project directory: writes its category and hub indexes")
    args = parser.parse_args(argv)

    defects = Defects()

    if args.root:
        vault_root = Path(args.root).resolve()
        if not vault_root.is_dir():
            print(f"not a directory: {vault_root}", file=sys.stderr)
            return 2
        projects, entries, categories = build_root(vault_root, defects)
        names = check_unique_basenames(vault_root, defects)
        print(f"{entries} entries in {categories} categories · {projects} projects · {names} distinct filenames")
    else:
        project_dir = Path(args.vault).resolve()
        if not project_dir.is_dir():
            print(f"not a directory: {project_dir}", file=sys.stderr)
            return 2
        vault_root = project_dir.parent
        entries, categories = build_project(vault_root, project_dir, defects)
        names = check_unique_basenames(vault_root, defects)
        print(f"{entries} entries in {categories} categories · {project_dir.name} · {names} distinct filenames")

    if defects.skipped:
        print(f"skipped {defects.skipped} unreadable files", file=sys.stderr)

    status = "ok" if not defects else "defects"
    log_run(vault_root, "build_index", status, f"{len(defects)} defects")

    if defects:
        defects.report()
        print(f"{len(defects)} defects", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

### `check_links.py`

```python
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
            text = path.read_text(encoding="utf-8", errors="replace")
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
            print(f"{path.name}: [[{raw}]] resolves to nothing", file=sys.stderr)
        print(f"{len(broken)} broken wikilinks", file=sys.stderr)
        return 1
    if skipped:
        print(f"{skipped} files skipped — denominator incomplete", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

### `check_duplicates.py`

```python
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
    text = path.read_text(encoding="utf-8", errors="replace")
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
```

### `check_freshness.py`

```python
"""Report the age of the last HEALTHY run of each expected job.

Without this, a scheduler that quietly stopped firing looks identical to one that is fine.
"no log" is reported as "did not run" — never as "fine".

Log format, one line per run, appended by every tool (see vault_paths.log_run):

    2026-07-27T09:15:00+00:00\tbuild_index\tok\t0 defects
"""

import sys

for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

from vault_paths import RUN_LOG_RELPATH

DEFAULT_MAX_AGE_HOURS = 24.0
HEALTHY = {"ok"}


def expected_jobs(vault_root):
    """Jobs that must have a healthy run. Configured per vault, defaulted here."""
    config = Path(vault_root).resolve() / "00_Global" / "06_tools" / "jobs.json"
    try:
        data = json.loads(config.read_text(encoding="utf-8"))
        return list(data["jobs"])
    except (OSError, ValueError, KeyError):
        return ["build_index", "check_links"]


def parse_log(log_path):
    """job -> newest healthy datetime. Malformed lines are counted, not swallowed."""
    healthy = {}
    malformed = 0
    lines = 0
    with open(log_path, "r", encoding="utf-8", errors="replace") as fh:
        for line in fh:
            if not line.strip():
                continue
            lines += 1
            parts = line.rstrip("\n").split("\t")
            if len(parts) < 3:
                malformed += 1
                continue
            stamp, job, status = parts[0], parts[1], parts[2]
            try:
                when = datetime.fromisoformat(stamp)
            except ValueError:
                malformed += 1
                continue
            if when.tzinfo is None:
                when = when.replace(tzinfo=timezone.utc)
            if status not in HEALTHY:
                continue
            if job not in healthy or when > healthy[job]:
                healthy[job] = when
    return healthy, lines, malformed


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--vault", required=True, help="vault root")
    parser.add_argument("--log", help="run log path (defaults to the vault's own)")
    parser.add_argument("--max-age-hours", type=float, default=DEFAULT_MAX_AGE_HOURS)
    parser.add_argument("--jobs", nargs="*", help="override the expected job list")
    args = parser.parse_args(argv)

    vault_root = Path(args.vault).resolve()
    log_path = Path(args.log).resolve() if args.log else vault_root / RUN_LOG_RELPATH
    jobs = args.jobs if args.jobs else expected_jobs(vault_root)

    if not jobs:
        print("did not run: no expected jobs configured", file=sys.stderr)
        return 1

    if not log_path.exists() or log_path.stat().st_size == 0:
        print(f"did not run: no run log at {log_path}", file=sys.stderr)
        for job in jobs:
            print(f"{job}: did not run — no log", file=sys.stderr)
        print(f"0/{len(jobs)} jobs have a healthy run", file=sys.stderr)
        return 1

    healthy, lines, malformed = parse_log(log_path)
    now = datetime.now(timezone.utc)
    fresh = []
    problems = []

    for job in jobs:
        when = healthy.get(job)
        if when is None:
            problems.append(f"{job}: did not run — no healthy line in {lines} log lines")
            continue
        age_h = (now - when).total_seconds() / 3600.0
        if age_h > args.max_age_hours:
            problems.append(f"{job}: last healthy run {age_h:.1f}h ago, threshold {args.max_age_hours}h")
        else:
            fresh.append((job, age_h))

    print(
        f"{len(fresh)}/{len(jobs)} jobs fresh · {lines} log lines · "
        f"{malformed} malformed · threshold {args.max_age_hours}h"
    )
    for job, age_h in fresh:
        print(f"  {job}: {age_h:.1f}h ago")

    if problems or malformed:
        for problem in problems:
            print(problem, file=sys.stderr)
        if malformed:
            print(f"{malformed} malformed log lines", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

### `count_tokens.py`

```python
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
            text = path.read_text(encoding="utf-8", errors="replace")
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
```

### `run_suites.py`

```python
"""Discover and run every test_*.py next to the tools.

Reports n/m. Zero suites collected is NOT green — a tool without a suite is invisible to
the runner, which is worse than red.
"""

import sys

for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass

import argparse
import os
import subprocess
from pathlib import Path


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tools", default=str(Path(__file__).resolve().parent), help="directory to scan")
    args = parser.parse_args(argv)

    tools = Path(args.tools).resolve()
    if not tools.is_dir():
        print(f"not a directory: {tools}", file=sys.stderr)
        return 2

    suites = sorted(tools.glob("test_*.py"))
    if not suites:
        print(f"0 suites collected in {tools} — not green, nothing ran", file=sys.stderr)
        return 1

    env = dict(os.environ)
    env["PYTHONPATH"] = str(tools) + os.pathsep + env.get("PYTHONPATH", "")
    env["PYTHONIOENCODING"] = "utf-8"

    passed = []
    failed = []
    for suite in suites:
        result = subprocess.run(
            [sys.executable, str(suite)],
            cwd=str(tools),
            env=env,
            capture_output=True,
        )
        out = (result.stdout + result.stderr).decode("utf-8", errors="replace")
        if result.returncode == 0:
            passed.append(suite.name)
        else:
            failed.append((suite.name, out.strip()))

    print(f"{len(passed)}/{len(suites)} suites green")
    for name in passed:
        print(f"  ok   {name}")
    for name, out in failed:
        print(f"  FAIL {name}", file=sys.stderr)
        for line in out.splitlines()[-15:]:
            print(f"       {line}", file=sys.stderr)

    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
```

#### Drivers

### `acceptance.py`

```python
"""Acceptance test: prove every guard goes red on bad input, on this machine.

Nine fixtures, each built in a throwaway vault under the system temp directory. The verdict
comes from process exit codes and from files on disk -- never from parsing console text, which
wraps at the terminal width and differs per shell.

    python acceptance.py            one pass
    python acceptance.py --repeat 10

Exit 0 only when all nine passed in every pass.
"""

import argparse
import shutil
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from _testkit import make_vault, run_tool, write_note
from vault_paths import category_index_name

for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass

PROJECT = "ProjektEins"


def index_text(project, folder="00_Notes"):
    path = project / folder / category_index_name(PROJECT, folder)
    return path.read_text(encoding="utf-8") if path.exists() else ""


def note(path, title, summary, created, body):
    """A note with its own body. The shared helper writes one body for every note, which is
    itself a duplicate pair once two of them exist."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        f'---\ntitle: "{title}"\nsummary: "{summary}"\ncreated: "{created}"\n---\n\n{body}\n',
        encoding="utf-8", newline="\n")
    return path


def build_both(vault, project):
    """Category and project indexes, then the root hub.

    Both invocations are needed before the link checker means anything: the project hub
    back-links to the root index, and --vault alone never writes it. Skipping --root leaves
    exactly one broken link, which makes an unrelated fixture pass for the wrong reason.
    """
    run_tool("build_index.py", "--vault", project)
    run_tool("build_index.py", "--root", vault)


def fixture_1_missing_title(vault, project):
    write_note(project / "00_Notes" / "ohne-titel.md", title=None)
    code, _, err = run_tool("build_index.py", "--vault", project)
    return code != 0 and "ohne-titel.md" in err


def fixture_2_summary_debris(vault, project):
    write_note(project / "00_Notes" / "debris.md", summary="> Ein Zitatrest")
    code, _, err = run_tool("build_index.py", "--vault", project)
    return code != 0 and "debris.md" in err and "— > Ein Zitatrest" not in index_text(project)


def fixture_3_dead_wikilink(vault, project):
    write_note(project / "00_Notes" / "toter-link.md")
    (project / "00_Notes" / "toter-link.md").write_text(
        '---\ntitle: "Toter Link"\nsummary: "Zeigt ins Leere."\n---\n\n'
        "[[gibt-es-nicht-im-vault]]\n", encoding="utf-8", newline="\n")
    build_both(vault, project)
    code, out, err = run_tool("check_links.py", "--vault", vault)
    scanned = any(ch.isdigit() for ch in out)
    return code != 0 and scanned and "toter-link.md" in (out + err)


def fixture_4_forbidden_filename(vault, project):
    write_note(project / "00_Notes" / "kaputt#name.md", title="Kaputter Name")
    code, _, err = run_tool("build_index.py", "--vault", project)
    text = index_text(project)
    return code != 0 and "kaputt#name.md" in err and "[Kaputter Name](" in text


def fixture_5_non_ascii_filename(vault, project):
    write_note(project / "00_Notes" / "Übergröße-Ärger.md", title="Umlaut-Notiz")
    code, out, err = run_tool("build_index.py", "--vault", project)
    if code != 0:
        return False
    if "Übergröße-Ärger" not in index_text(project):
        return False
    run_tool("build_index.py", "--root", vault)
    code2, out2, err2 = run_tool("check_links.py", "--vault", vault)
    return code2 == 0 and "0 files scanned" not in out2 and "Übergröße-Ärger" not in err2


def fixture_6_second_run_is_a_noop(vault, project):
    write_note(project / "00_Notes" / "stabil.md")
    run_tool("build_index.py", "--vault", project)
    before = {p.name: p.read_bytes() for p in project.rglob("INDEX - *.md")}
    run_tool("build_index.py", "--vault", project)
    after = {p.name: p.read_bytes() for p in project.rglob("INDEX - *.md")}
    return bool(before) and before == after


def fixture_7_empty_suite_dir(vault, project):
    empty = Path(tempfile.mkdtemp(prefix="vaultkit_empty_"))
    try:
        code, out, err = run_tool("run_suites.py", "--tools", empty)
        return code != 0 and "0 suites" in (out + err)
    finally:
        shutil.rmtree(empty, ignore_errors=True)


def fixture_8_freshness_without_log(vault, project):
    blank = vault / "leeres-protokoll.log"
    blank.write_text("", encoding="utf-8")
    code, out, err = run_tool("check_freshness.py", "--vault", vault, "--log", blank)
    return code != 0 and "did not run" in (out + err)


def fixture_9_unknown_folder(vault, project):
    (project / "99_extra").mkdir(exist_ok=True)
    write_note(project / "99_extra" / "verlorene-notiz.md", title="Verloren")
    code, _, err = run_tool("build_index.py", "--vault", project)
    return code != 0 and "99_extra" in err


def control_clean_vault_is_green(vault, project):
    """The healthy control: a suite that only ever sees bad input is as blind as one that
    only ever sees good input. Every tool must exit 0 on a clean tree, and say so with a
    denominator."""
    # Distinct bodies on purpose: two notes sharing the shared-fixture body are a genuine
    # duplicate pair, and check_duplicates is right to flag them.
    note(project / "00_Notes" / "eine-erkenntnis.md", "Eine Erkenntnis", "Genau ein Satz.",
         "2026-07-01", "Was an diesem Tag gemessen wurde und warum es zaehlt.")
    note(project / "03_technical_docs" / "ein-subsystem.md", "Ein Subsystem", "Handbuchseite.",
         "2026-07-02", "Wie das Teilsystem aufgebaut ist, Schnittstellen und Grenzen.")
    build_both(vault, project)

    for script in ("check_links.py", "check_duplicates.py"):
        code, out, err = run_tool(script, "--vault", vault)
        if code != 0 or not any(ch.isdigit() for ch in out + err):
            return False

    log = vault / "runs.log"
    log.write_text("", encoding="utf-8")
    code, out, err = run_tool("check_freshness.py", "--vault", vault, "--log", log)
    if code == 0:  # an empty log is not a healthy run, and must not read as one
        return False

    before = {p.name: p.read_bytes() for p in vault.rglob("INDEX - *.md")}
    build_both(vault, project)
    after = {p.name: p.read_bytes() for p in vault.rglob("INDEX - *.md")}
    return bool(before) and before == after


FIXTURES = [
    ("0 healthy control: clean vault is green and stable", control_clean_vault_is_green),
    ("1 note without title", fixture_1_missing_title),
    ("2 markdown debris in summary", fixture_2_summary_debris),
    ("3 dead wikilink", fixture_3_dead_wikilink),
    ("4 forbidden character in filename", fixture_4_forbidden_filename),
    ("5 non-ASCII filename stays in the denominator", fixture_5_non_ascii_filename),
    ("6 second index run changes nothing", fixture_6_second_run_is_a_noop),
    ("7 suite runner on an empty directory", fixture_7_empty_suite_dir),
    ("8 freshness check without a run log", fixture_8_freshness_without_log),
    ("9 folder that is not a configured category", fixture_9_unknown_folder),
]


def one_pass(verbose=True):
    """Every fixture gets its own vault, so one fixture cannot poison the next."""
    results = []
    for label, fn in FIXTURES:
        vault = make_vault((PROJECT,))
        try:
            try:
                ok = bool(fn(vault, vault / PROJECT))
            except Exception as exc:  # a crashing fixture is a failing fixture
                ok = False
                label = f"{label} [raised {type(exc).__name__}: {exc}]"
        finally:
            shutil.rmtree(vault.parent, ignore_errors=True)
        results.append((label, ok))
        if verbose:
            print(f"  {'ok  ' if ok else 'FAIL'} {label}")
    return results


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repeat", type=int, default=1, help="number of full passes")
    args = parser.parse_args(argv)

    failures = []
    for run in range(1, args.repeat + 1):
        if args.repeat > 1:
            print(f"--- pass {run}/{args.repeat} ---")
        for label, ok in one_pass():
            if not ok:
                failures.append((run, label))
        passed = len(FIXTURES) - sum(1 for r, _ in failures if r == run)
        print(f"{passed}/{len(FIXTURES)} checks behaved as specified — "
              f"9 guards red on bad input, 1 healthy control green (pass {run})")

    if failures:
        print(f"\n{len(failures)} failing fixture runs:", file=sys.stderr)
        for run, label in failures:
            print(f"  pass {run}: {label}", file=sys.stderr)
        return 1
    print(f"\n{args.repeat} pass(es), {len(FIXTURES)}/{len(FIXTURES)} every time.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

### `verify_setup.py`

```python
"""End-to-end verification of a complete setup, from empty folder to committed vault.

acceptance.py proves each guard reacts correctly to one bad input. This proves the whole
sequence a setup actually performs still works when the steps run in order on one tree:
folders, tools, notes, git, indexes, every check, the suites, the acceptance run, and a
second index run that must leave the tree byte-identical and `git status` empty.

    python verify_setup.py
    python verify_setup.py --repeat 10

Everything happens in a throwaway tree under the system temp directory. Exit 0 only when
every step passed in every pass.
"""

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
sys.path.insert(0, str(TOOLS))

for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass

CATEGORY_FOLDERS = ["00_Notes", "01_Issues", "02_docs", "03_technical_docs",
                    "04_feedback", "05_workflows", "06_tools"]
PROJECTS = ["ProjektEins", "ProjektZwei"]

NOTES = [
    ("00_Global", "03_technical_docs", "the-rules-this-vault-runs-on.md", "The rules this vault runs on",
     "Twelve rules and the frontmatter contract.",
     "Every note carries frontmatter. The index is generated and never hand written."),
    ("00_Global", "03_technical_docs", "tooling-00_Global.md", "Tooling",
     "What each guard refuses to do.",
     "A check that cannot tell working from broken is not evidence, so each one prints a denominator."),
    ("ProjektEins", "00_Notes", "knowledge-transfer-ProjektEins.md", "Knowledge transfer ProjektEins",
     "How to pick this project up.",
     "Where the code lives, which decisions are settled, and what the next session should read first."),
    ("ProjektZwei", "00_Notes", "knowledge-transfer-ProjektZwei.md", "Knowledge transfer ProjektZwei",
     "How to pick that project up.",
     "Open questions, the last measurement, and the reason the current approach was chosen."),
]


class Failed(Exception):
    pass


def run(cmd, cwd, expect_zero=True, label=""):
    env = dict(os.environ)
    env.pop("PYTHONIOENCODING", None)
    env.pop("PYTHONUTF8", None)
    result = subprocess.run([str(c) for c in cmd], cwd=str(cwd), env=env, capture_output=True)
    out = result.stdout.decode("utf-8", errors="replace")
    err = result.stderr.decode("utf-8", errors="replace")
    if expect_zero and result.returncode != 0:
        raise Failed(f"{label or cmd[1]} exited {result.returncode}\n{out}\n{err}")
    if not expect_zero and result.returncode == 0:
        raise Failed(f"{label or cmd[1]} exited 0 but had to fail\n{out}\n{err}")
    return result.returncode, out, err


def tool(vault, script, *args, expect_zero=True):
    return run([sys.executable, str(vault / "00_Global" / "06_tools" / script), *args],
               cwd=vault, expect_zero=expect_zero, label=script)


def write_note(path, title, summary, body):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(f'---\ntitle: "{title}"\nsummary: "{summary}"\ncreated: "2026-07-27"\n---\n\n{body}\n',
                    encoding="utf-8", newline="\n")


def build_vault(root):
    """Step 1-3: the folder tree, the shipped tools, the starting pages."""
    for project in ["00_Global"] + PROJECTS:
        for folder in CATEGORY_FOLDERS:
            (root / project / folder).mkdir(parents=True, exist_ok=True)
    dst = root / "00_Global" / "06_tools"
    for src in list(TOOLS.glob("*.py")) + [TOOLS / "jobs.json"]:
        shutil.copy2(src, dst / src.name)
    for project, folder, name, title, summary, body in NOTES:
        write_note(root / project / folder / name, title, summary, body)
    (root / ".gitignore").write_text(
        ".obsidian/plugins/\n.obsidian/workspace.json\n.obsidian/graph.json\n"
        "**/runs.log\n**/__pycache__/\n*.pyc\n_acceptance/\n",
        encoding="utf-8", newline="\n")


def git_setup(root):
    run(["git", "init", "-q"], cwd=root, label="git init")
    run(["git", "config", "user.name", "vaultkit-verify"], cwd=root, label="git config name")
    run(["git", "config", "user.email", "verify@localhost"], cwd=root, label="git config email")


def git_commit_all(root, message):
    run(["git", "add", "-A"], cwd=root, label="git add")
    run(["git", "commit", "-q", "-m", message], cwd=root, label="git commit")


def index_all(root):
    for project in ["00_Global"] + PROJECTS:
        tool(root, "build_index.py", "--vault", str(root / project))
    tool(root, "build_index.py", "--root", ".")


def snapshot(root):
    return {str(p.relative_to(root)): p.read_bytes() for p in sorted(root.rglob("INDEX - *.md"))}


STEPS = []


def step(name):
    def wrap(fn):
        STEPS.append((name, fn))
        return fn
    return wrap


@step("1 tree, tools and starting pages exist")
def _s1(root):
    build_vault(root)
    missing = [p for p in (root / "00_Global" / "06_tools" / "build_index.py",
                           root / "ProjektEins" / "00_Notes",
                           root / ".gitignore") if not p.exists()]
    if missing:
        raise Failed(f"missing after build: {missing}")


@step("2 git initialised and the untouched state committed")
def _s2(root):
    git_setup(root)
    git_commit_all(root, "chore: vault skeleton before any generated file")


@step("3 index generator writes all three levels")
def _s3(root):
    index_all(root)
    for project in ["00_Global"] + PROJECTS:
        hub = list((root / project).glob("INDEX - *.md"))
        if not hub:
            raise Failed(f"no project hub in {project}")
    if not list(root.glob("INDEX - *.md")):
        raise Failed("no root index")


@step("4 link checker green with a denominator")
def _s4(root):
    _, out, err = tool(root, "check_links.py", "--vault", ".")
    if "wikilinks resolve" not in out or not any(c.isdigit() for c in out):
        raise Failed(f"no denominator: {out!r} {err!r}")


@step("5 duplicate check green with a denominator")
def _s5(root):
    _, out, _ = tool(root, "check_duplicates.py", "--vault", ".")
    if "compared" not in out:
        raise Failed(f"no denominator: {out!r}")


@step("6 freshness sees the healthy runs the tools just logged")
def _s6(root):
    _, out, err = tool(root, "check_freshness.py", "--vault", ".")
    if "jobs fresh" not in (out + err):
        raise Failed(f"freshness did not report per-job freshness: {out!r} {err!r}")


@step("7 suites green")
def _s7(root):
    _, out, _ = tool(root, "run_suites.py")
    if "suites green" not in out:
        raise Failed(f"unexpected suite output: {out!r}")


@step("8 acceptance run correct")
def _s8(root):
    _, out, _ = tool(root, "acceptance.py")
    if "10/10" not in out:
        raise Failed(f"acceptance not 10/10: {out!r}")


@step("9 second index run is byte-identical")
def _s9(root):
    before = snapshot(root)
    index_all(root)
    after = snapshot(root)
    if not before:
        raise Failed("no index files to compare")
    changed = [k for k in before if before[k] != after.get(k)]
    if changed or set(before) != set(after):
        raise Failed(f"index churn: {changed or set(after) ^ set(before)}")


@step("10 working tree clean after committing the generated files")
def _s10(root):
    git_commit_all(root, "chore: generated indexes")
    index_all(root)
    _, out, _ = run(["git", "status", "--porcelain"], cwd=root, label="git status")
    if out.strip():
        raise Failed(f"tree not clean after a rerun:\n{out}")


def one_pass(verbose=True):
    root = Path(tempfile.mkdtemp(prefix="vaultkit_flow_")) / "Vault"
    root.mkdir(parents=True)
    failures = []
    try:
        for name, fn in STEPS:
            try:
                fn(root)
                ok, detail = True, ""
            except Failed as exc:
                ok, detail = False, str(exc)
            except Exception as exc:
                ok, detail = False, f"{type(exc).__name__}: {exc}"
            if verbose:
                print(f"  {'ok  ' if ok else 'FAIL'} {name}")
            if not ok:
                failures.append((name, detail))
                break  # later steps depend on this one; a cascade hides the cause
    finally:
        shutil.rmtree(root.parent, ignore_errors=True)
    return failures


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repeat", type=int, default=1)
    args = parser.parse_args(argv)

    all_failures = []
    for run_no in range(1, args.repeat + 1):
        if args.repeat > 1:
            print(f"--- pass {run_no}/{args.repeat} ---")
        failures = one_pass()
        print(f"{len(STEPS) - len(failures)}/{len(STEPS)} steps passed (pass {run_no})")
        all_failures += [(run_no, n, d) for n, d in failures]

    if all_failures:
        print(f"\n{len(all_failures)} failing steps:", file=sys.stderr)
        for run_no, name, detail in all_failures:
            print(f"  pass {run_no}: {name}\n    {detail}", file=sys.stderr)
        return 1
    print(f"\n{args.repeat} pass(es), {len(STEPS)}/{len(STEPS)} steps every time.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

### `upgrade.py`

```python
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
    for script, want in (("run_suites.py", "suites green"), ("acceptance.py", "10/10")):
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
```

### `test_build_index.py`

```python
"""Suite for build_index.py.

Every case here is a failure-mode fixture except test_healthy_control, which is the
control: a suite that only ever sees good input cannot tell you the check still works.
"""

import shutil
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from _testkit import make_vault, run_tool, write_note
from vault_paths import category_index_name, project_index_name, root_index_name


class BuildIndexTest(unittest.TestCase):
    def setUp(self):
        self.vault = make_vault(("ProjektEins",))
        self.project = self.vault / "ProjektEins"

    def tearDown(self):
        shutil.rmtree(self.vault.parent, ignore_errors=True)

    def index_text(self, folder="00_Notes"):
        path = self.project / folder / category_index_name("ProjektEins", folder)
        return path.read_text(encoding="utf-8")

    # ------------------------------------------------------------------ control

    def test_healthy_control(self):
        write_note(self.project / "00_Notes" / "eine-erkenntnis.md",
                   title="Eine Erkenntnis", summary="Genau ein Satz.", created="2026-07-01")
        code, out, err = run_tool("build_index.py", "--vault", self.project)
        self.assertEqual(code, 0, err)
        self.assertIn("1 entries in 7 categories", out)
        text = self.index_text()
        self.assertIn("[[ProjektEins/00_Notes/eine-erkenntnis|Eine Erkenntnis]]", text)
        self.assertIn("Genau ein Satz.", text)

    def test_empty_category_still_gets_an_index(self):
        code, _, err = run_tool("build_index.py", "--vault", self.project)
        self.assertEqual(code, 0, err)
        for folder in ("00_Notes", "01_Issues", "06_tools"):
            path = self.project / folder / category_index_name("ProjektEins", folder)
            self.assertTrue(path.exists(), f"{path} missing")

    # ------------------------------------------------------------ failure modes

    def test_missing_title_is_a_defect(self):
        write_note(self.project / "00_Notes" / "ohne-titel.md", title=None)
        code, _, err = run_tool("build_index.py", "--vault", self.project)
        self.assertEqual(code, 1)
        self.assertIn("ohne-titel.md", err)
        self.assertIn("title", err)

    def test_markdown_debris_in_summary_is_stripped_and_red(self):
        write_note(self.project / "00_Notes" / "debris.md", summary="> Ein Zitatrest")
        code, _, err = run_tool("build_index.py", "--vault", self.project)
        self.assertEqual(code, 1)
        self.assertIn("debris.md", err)
        self.assertNotIn("— > Ein Zitatrest", self.index_text())
        self.assertIn("Ein Zitatrest", self.index_text())

    def test_forbidden_filename_falls_back_to_markdown_link(self):
        write_note(self.project / "00_Notes" / "kaputt#name.md", title="Kaputter Name")
        code, _, err = run_tool("build_index.py", "--vault", self.project)
        self.assertEqual(code, 1)
        self.assertIn("kaputt#name.md", err)
        text = self.index_text()
        self.assertIn("[Kaputter Name](", text)
        self.assertNotIn("[[ProjektEins/00_Notes/kaputt#name", text)

    def test_non_ascii_filename_stays_in_the_denominator(self):
        write_note(self.project / "00_Notes" / "Übergröße-für-Ärger.md", title="Umlaut-Notiz")
        code, out, err = run_tool("build_index.py", "--vault", self.project)
        self.assertEqual(code, 0, err)
        self.assertIn("1 entries", out)
        self.assertIn("Übergröße-für-Ärger", self.index_text())

    def test_non_ascii_defect_survives_the_subprocess_round_trip(self):
        write_note(self.project / "00_Notes" / "Ärgernis-ohne-Titel.md", title=None)
        code, _, err = run_tool("build_index.py", "--vault", self.project)
        self.assertEqual(code, 1)
        self.assertIn("Ärgernis-ohne-Titel.md", err)

    def test_duplicate_basenames_are_a_defect(self):
        vault = make_vault(("ProjektEins", "ProjektZwei"))
        try:
            write_note(vault / "ProjektEins" / "00_Notes" / "gleich.md")
            write_note(vault / "ProjektZwei" / "00_Notes" / "gleich.md")
            code, _, err = run_tool("build_index.py", "--root", vault)
            self.assertEqual(code, 1)
            self.assertIn("gleich.md", err)
            self.assertIn("name used 2 times", err)
        finally:
            shutil.rmtree(vault.parent, ignore_errors=True)

    def test_unknown_folder_is_a_defect(self):
        """A renamed 06_tools once dropped a real run from 21 categories to 20, silently."""
        (self.project / "06_werkzeuge").mkdir()
        write_note(self.project / "06_werkzeuge" / "verlorene-notiz.md", title="Verloren")
        code, out, err = run_tool("build_index.py", "--vault", self.project)
        self.assertEqual(code, 1, out)
        self.assertIn("06_werkzeuge", err)

    def test_healthy_control_has_no_unknown_folder(self):
        code, out, err = run_tool("build_index.py", "--vault", self.project)
        self.assertEqual(code, 0, err)
        self.assertNotIn("not a configured category", err)

    # -------------------------------------------------------------- invariants

    def test_second_run_changes_nothing(self):
        write_note(self.project / "00_Notes" / "stabil.md")
        run_tool("build_index.py", "--vault", self.project)
        before = {p: p.read_bytes() for p in self.project.rglob("INDEX - *.md")}
        run_tool("build_index.py", "--vault", self.project)
        after = {p: p.read_bytes() for p in self.project.rglob("INDEX - *.md")}
        self.assertEqual(before, after)

    def test_category_index_backlinks_to_the_project_hub(self):
        """The rename that broke 23 of 441 links was a missing assertion, not a missing check."""
        run_tool("build_index.py", "--vault", self.project)
        hub_stem = project_index_name(self.project)[:-3]
        self.assertIn(f"[[ProjektEins/{hub_stem}|ProjektEins]]", self.index_text())

    def test_project_hub_backlinks_to_the_root_index(self):
        run_tool("build_index.py", "--root", self.vault)
        hub = self.project / project_index_name(self.project)
        root_stem = root_index_name(self.vault)[:-3]
        self.assertIn(f"[[{root_stem}|{self.vault.name}]]", hub.read_text(encoding="utf-8"))

    def test_root_index_is_named_after_the_resolved_vault(self):
        run_tool("build_index.py", "--root", self.vault)
        self.assertTrue((self.vault / root_index_name(self.vault)).exists())
        self.assertIn(f"# {self.vault.name} — Index",
                      (self.vault / root_index_name(self.vault)).read_text(encoding="utf-8"))

    def test_index_never_reads_the_note_body(self):
        write_note(self.project / "00_Notes" / "geheim.md", title="Titel", summary="Kurz.")
        run_tool("build_index.py", "--vault", self.project)
        self.assertNotIn("Body text that the index generator must never read",
                         self.index_text())

    def test_retired_and_stale_are_visible_in_the_index(self):
        write_note(self.project / "00_Notes" / "alt.md", title="Alte Wahrheit",
                   summary="War mal wahr.", retired="2026-06-01")
        write_note(self.project / "00_Notes" / "veraltet.md", title="Halbalt",
                   summary="Quelle ist neuer.", stale="2026-07-01")
        run_tool("build_index.py", "--vault", self.project)
        text = self.index_text()
        self.assertIn("[retired: 2026-06-01]", text)
        self.assertIn("[stale since 2026-07-01]", text)


if __name__ == "__main__":
    unittest.main(verbosity=1)
```

### `test_check_duplicates.py`

```python
"""Suite for check_duplicates.py."""

import shutil
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from _testkit import make_vault, run_tool, write_note

SAME_BODY = (
    "Der Index wird erzeugt und niemals von Hand geschrieben. "
    "Der Generator liest ausschließlich das Frontmatter und niemals den Fließtext. "
    "Das ist keine Optimierung sondern die strukturelle Garantie."
)
OTHER_BODY = (
    "Ein Zeitplan der still aufgehört hat sieht genauso aus wie einer der läuft. "
    "Deshalb schreibt jeder Lauf eine Zeile ins Protokoll, auch der gesunde."
)


def note_with_body(path, body, title="Ein Titel"):
    write_note(path, title=title)
    with open(path, "a", encoding="utf-8", newline="\n") as fh:
        fh.write(body + "\n")
    return path


class CheckDuplicatesTest(unittest.TestCase):
    def setUp(self):
        self.vault = make_vault(("ProjektEins",))
        self.notes = self.vault / "ProjektEins" / "00_Notes"

    def tearDown(self):
        shutil.rmtree(self.vault.parent, ignore_errors=True)

    # ------------------------------------------------------------------ control

    def test_healthy_control(self):
        note_with_body(self.notes / "eins.md", SAME_BODY, title="Eins")
        note_with_body(self.notes / "zwei.md", OTHER_BODY, title="Zwei")
        code, out, err = run_tool("check_duplicates.py", "--vault", self.vault)
        self.assertEqual(code, 0, err)
        self.assertIn("0 pairs flagged of 1 compared", out)

    # ------------------------------------------------------------ failure modes

    def test_overlapping_notes_are_flagged_and_red(self):
        note_with_body(self.notes / "eins.md", SAME_BODY, title="Eins")
        note_with_body(self.notes / "kopie.md", SAME_BODY, title="Kopie")
        code, out, err = run_tool("check_duplicates.py", "--vault", self.vault)
        self.assertEqual(code, 1)
        self.assertIn("1 pairs flagged of 1 compared", out)
        self.assertIn("kopie.md", err)

    def test_one_note_is_did_not_run(self):
        note_with_body(self.notes / "eins.md", SAME_BODY)
        code, out, err = run_tool("check_duplicates.py", "--vault", self.vault)
        self.assertEqual(code, 0, err)
        self.assertIn("did not run", out)
        self.assertIn("1 comparable notes", out)

    def test_threshold_is_printed_with_every_result(self):
        note_with_body(self.notes / "eins.md", SAME_BODY, title="Eins")
        note_with_body(self.notes / "zwei.md", OTHER_BODY, title="Zwei")
        _, out, _ = run_tool("check_duplicates.py", "--vault", self.vault, "--threshold", "0.9")
        self.assertIn("threshold 0.9", out)

    def test_non_ascii_filename_survives_the_subprocess_round_trip(self):
        note_with_body(self.notes / "Übergröße.md", SAME_BODY, title="Eins")
        note_with_body(self.notes / "Ärgernis.md", SAME_BODY, title="Zwei")
        code, _, err = run_tool("check_duplicates.py", "--vault", self.vault)
        self.assertEqual(code, 1)
        self.assertIn("Übergröße.md", err + "")
        self.assertIn("Ärgernis.md", err)


if __name__ == "__main__":
    unittest.main(verbosity=1)
```

### `test_check_freshness.py`

```python
"""Suite for check_freshness.py."""

import shutil
import sys
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from _testkit import make_vault, run_tool


def stamp(hours_ago):
    return (datetime.now(timezone.utc) - timedelta(hours=hours_ago)).strftime("%Y-%m-%dT%H:%M:%S+00:00")


class CheckFreshnessTest(unittest.TestCase):
    def setUp(self):
        self.vault = make_vault(("ProjektEins",))
        self.log = self.vault / "00_Global" / "06_tools" / "runs.log"

    def tearDown(self):
        shutil.rmtree(self.vault.parent, ignore_errors=True)

    def write_log(self, *lines):
        self.log.parent.mkdir(parents=True, exist_ok=True)
        self.log.write_text("\n".join(lines) + ("\n" if lines else ""), encoding="utf-8", newline="\n")

    # ------------------------------------------------------------------ control

    def test_healthy_control(self):
        self.write_log(f"{stamp(1)}\tbuild_index\tok\t0 defects")
        code, out, err = run_tool("check_freshness.py", "--vault", self.vault, "--jobs", "build_index")
        self.assertEqual(code, 0, err)
        self.assertIn("1/1 jobs fresh", out)

    # ------------------------------------------------------------ failure modes

    def test_missing_log_is_did_not_run_not_fine(self):
        code, out, err = run_tool("check_freshness.py", "--vault", self.vault, "--jobs", "build_index")
        self.assertEqual(code, 1)
        self.assertIn("did not run", err)
        self.assertNotIn("fresh", out)

    def test_blank_log_is_did_not_run(self):
        self.write_log()
        code, _, err = run_tool("check_freshness.py", "--vault", self.vault, "--jobs", "build_index")
        self.assertEqual(code, 1)
        self.assertIn("did not run", err)

    def test_stale_healthy_run_is_red(self):
        self.write_log(f"{stamp(72)}\tbuild_index\tok\t0 defects")
        code, out, err = run_tool("check_freshness.py", "--vault", self.vault,
                                  "--jobs", "build_index", "--max-age-hours", "24")
        self.assertEqual(code, 1)
        self.assertIn("0/1 jobs fresh", out)
        self.assertIn("72", err)

    def test_only_failed_runs_count_as_did_not_run(self):
        self.write_log(f"{stamp(1)}\tbuild_index\tdefects\t3 defects")
        code, _, err = run_tool("check_freshness.py", "--vault", self.vault, "--jobs", "build_index")
        self.assertEqual(code, 1)
        self.assertIn("did not run", err)
        self.assertIn("no healthy line", err)

    def test_malformed_lines_are_counted_not_swallowed(self):
        self.write_log(f"{stamp(1)}\tbuild_index\tok\t0 defects", "kaputte zeile ohne tabs")
        code, out, err = run_tool("check_freshness.py", "--vault", self.vault, "--jobs", "build_index")
        self.assertEqual(code, 1)
        self.assertIn("1 malformed", out)
        self.assertIn("malformed", err)

    def test_non_ascii_job_name_survives_the_subprocess_round_trip(self):
        self.write_log(f"{stamp(1)}\tbuild_index\tok\t0 defects")
        code, _, err = run_tool("check_freshness.py", "--vault", self.vault, "--jobs", "Zählung")
        self.assertEqual(code, 1)
        self.assertIn("Zählung", err)


if __name__ == "__main__":
    unittest.main(verbosity=1)
```

### `test_check_links.py`

```python
"""Suite for check_links.py."""

import shutil
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from _testkit import make_vault, run_tool, write_note


class CheckLinksTest(unittest.TestCase):
    def setUp(self):
        self.vault = make_vault(("ProjektEins",))
        self.notes = self.vault / "ProjektEins" / "00_Notes"

    def tearDown(self):
        shutil.rmtree(self.vault.parent, ignore_errors=True)

    def append(self, path, text):
        with open(path, "a", encoding="utf-8", newline="\n") as fh:
            fh.write(text + "\n")

    # ------------------------------------------------------------------ control

    def test_healthy_control(self):
        target = write_note(self.notes / "ziel.md")
        source = write_note(self.notes / "quelle.md")
        self.append(source, "Siehe [[ProjektEins/00_Notes/ziel|Ziel]].")
        code, out, err = run_tool("check_links.py", "--vault", self.vault)
        self.assertEqual(code, 0, err)
        self.assertIn("1/1 wikilinks resolve", out)
        self.assertTrue(target.exists())

    def test_denominator_is_always_printed(self):
        write_note(self.notes / "allein.md")
        code, out, _ = run_tool("check_links.py", "--vault", self.vault)
        self.assertEqual(code, 0)
        self.assertIn("0/0 wikilinks resolve", out)
        self.assertIn("files scanned", out)

    # ------------------------------------------------------------ failure modes

    def test_broken_link_is_red_with_a_denominator(self):
        source = write_note(self.notes / "quelle.md")
        self.append(source, "Siehe [[gibt-es-nicht]].")
        code, out, err = run_tool("check_links.py", "--vault", self.vault)
        self.assertEqual(code, 1)
        self.assertIn("gibt-es-nicht", err)
        self.assertIn("0/1 wikilinks resolve", out)

    def test_scanning_nothing_is_did_not_run_not_zero_broken(self):
        empty = Path(tempfile.mkdtemp(prefix="vaultkit_empty_"))
        try:
            code, out, err = run_tool("check_links.py", "--vault", empty)
            self.assertEqual(code, 1)
            self.assertIn("did not run", err)
            self.assertNotIn("0 broken", out)
        finally:
            shutil.rmtree(empty, ignore_errors=True)

    def test_wikilink_inside_code_is_not_a_link(self):
        source = write_note(self.notes / "syntax-doku.md")
        self.append(source, "Schreibe `[[Projekt/Ordner/datei|Titel]]` in die Notiz.")
        self.append(source, "```\n[[auch-das-nicht]]\n```")
        code, out, err = run_tool("check_links.py", "--vault", self.vault)
        self.assertEqual(code, 0, err)
        self.assertIn("0/0 wikilinks resolve", out)

    def test_non_ascii_target_resolves(self):
        write_note(self.notes / "Übergröße.md")
        source = write_note(self.notes / "quelle.md")
        self.append(source, "Siehe [[Übergröße]].")
        code, out, err = run_tool("check_links.py", "--vault", self.vault)
        self.assertEqual(code, 0, err)
        self.assertIn("1/1 wikilinks resolve", out)

    def test_non_ascii_defect_survives_the_subprocess_round_trip(self):
        source = write_note(self.notes / "Ärgernis.md")
        self.append(source, "Siehe [[fehlt-natürlich]].")
        code, _, err = run_tool("check_links.py", "--vault", self.vault)
        self.assertEqual(code, 1)
        self.assertIn("Ärgernis.md", err)
        self.assertIn("fehlt-natürlich", err)

    def test_escaped_alias_pipe_in_a_table_still_resolves(self):
        write_note(self.notes / "ziel.md")
        source = write_note(self.notes / "tabelle.md")
        self.append(source, "| Was | Wo |\n|---|---|\n| Ziel | [[ziel\\|Titel]] |")
        code, out, err = run_tool("check_links.py", "--vault", self.vault)
        self.assertEqual(code, 0, err)
        self.assertIn("1/1 wikilinks resolve", out)

    def test_escaped_pipe_does_not_hide_a_broken_target(self):
        source = write_note(self.notes / "tabelle.md")
        self.append(source, "| Was | Wo |\n|---|---|\n| Ziel | [[gibt-es-nicht\\|Titel]] |")
        code, out, err = run_tool("check_links.py", "--vault", self.vault)
        self.assertEqual(code, 1)
        self.assertIn("gibt-es-nicht", err)
        self.assertIn("0/1 wikilinks resolve", out)

    def test_alias_and_anchor_are_stripped_before_resolving(self):
        write_note(self.notes / "ziel.md")
        source = write_note(self.notes / "quelle.md")
        self.append(source, "Siehe [[ziel#Abschnitt|anderer Text]].")
        code, out, err = run_tool("check_links.py", "--vault", self.vault)
        self.assertEqual(code, 0, err)
        self.assertIn("1/1", out)


if __name__ == "__main__":
    unittest.main(verbosity=1)
```

### `test_count_tokens.py`

```python
"""Suite for count_tokens.py — the tool that must never invent a precision."""

import shutil
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from _testkit import make_vault, run_tool, write_note


class CountTokensTest(unittest.TestCase):
    def setUp(self):
        self.vault = make_vault(("ProjektEins",))
        self.notes = self.vault / "ProjektEins" / "00_Notes"

    def tearDown(self):
        shutil.rmtree(self.vault.parent, ignore_errors=True)

    def test_healthy_control_labels_its_precision(self):
        write_note(self.notes / "eins.md")
        code, out, err = run_tool("count_tokens.py", self.vault)
        self.assertEqual(code, 0, err)
        self.assertTrue("estimated" in out or "exact" in out, out)
        self.assertIn("chars", out)
        self.assertIn("1/1 files", out)

    def test_missing_path_is_red(self):
        code, _, err = run_tool("count_tokens.py", self.vault / "gibt-es-nicht")
        self.assertEqual(code, 2)
        self.assertIn("not found", err)

    def test_empty_directory_is_did_not_run(self):
        code, _, err = run_tool("count_tokens.py", self.notes)
        self.assertEqual(code, 1)
        self.assertIn("did not run", err)

    def test_non_ascii_file_is_counted(self):
        write_note(self.notes / "Übergröße.md", title="Umlaut", summary="Ärger.")
        code, out, err = run_tool("count_tokens.py", self.vault)
        self.assertEqual(code, 0, err)
        self.assertIn("1/1 files", out)


if __name__ == "__main__":
    unittest.main(verbosity=1)
```

### `test_run_suites.py`

```python
"""Suite for run_suites.py — the runner that must never report green over zero tests."""

import shutil
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from _testkit import run_tool

PASSING = "import sys\nprint('fine')\nsys.exit(0)\n"
FAILING = "import sys\nsys.stderr.write('kaputt\\n')\nsys.exit(1)\n"
NON_ASCII = "import sys\nsys.stderr.write('Ärgernis in der Suite\\n')\nsys.exit(1)\n"


class RunSuitesTest(unittest.TestCase):
    def setUp(self):
        self.dir = Path(tempfile.mkdtemp(prefix="vaultkit_suites_"))

    def tearDown(self):
        shutil.rmtree(self.dir, ignore_errors=True)

    def suite(self, name, body):
        path = self.dir / name
        path.write_text(body, encoding="utf-8", newline="\n")
        return path

    # ------------------------------------------------------------------ control

    def test_healthy_control(self):
        self.suite("test_a.py", PASSING)
        self.suite("test_b.py", PASSING)
        code, out, err = run_tool("run_suites.py", "--tools", self.dir)
        self.assertEqual(code, 0, err)
        self.assertIn("2/2 suites green", out)

    # ------------------------------------------------------------ failure modes

    def test_zero_suites_is_not_green(self):
        code, out, err = run_tool("run_suites.py", "--tools", self.dir)
        self.assertEqual(code, 1)
        self.assertIn("0 suites collected", err)
        self.assertNotIn("green", out)

    def test_a_failing_suite_makes_the_run_red(self):
        self.suite("test_a.py", PASSING)
        self.suite("test_b.py", FAILING)
        code, out, err = run_tool("run_suites.py", "--tools", self.dir)
        self.assertEqual(code, 1)
        self.assertIn("1/2 suites green", out)
        self.assertIn("test_b.py", err)

    def test_helper_modules_are_not_counted_as_suites(self):
        self.suite("_testkit.py", PASSING)
        code, _, err = run_tool("run_suites.py", "--tools", self.dir)
        self.assertEqual(code, 1)
        self.assertIn("0 suites collected", err)

    def test_non_ascii_suite_output_survives_the_subprocess_round_trip(self):
        self.suite("test_umlaut.py", NON_ASCII)
        code, _, err = run_tool("run_suites.py", "--tools", self.dir)
        self.assertEqual(code, 1)
        self.assertIn("Ärgernis in der Suite", err)


if __name__ == "__main__":
    unittest.main(verbosity=1)
```

### `test_upgrade.py`

```python
"""Suite for upgrade.py.

The failure that matters here is silence: an upgrade that reports "nothing to do" over a file
it could not read, or that writes without saying what it overwrote. Every case below is a
failure-mode fixture except test_healthy_control.
"""

import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

TOOLS = Path(__file__).resolve().parent


def kit_file(path, blocks, version="0123456789ab"):
    """A minimal kit file: a version stamp plus one fenced block per script."""
    parts = [f"<!-- kit-version: {version} -->", "", "# A kit", ""]
    for name, body in blocks.items():
        lang = "json" if name.endswith(".json") else "python"
        parts.append(f"### `{name}`\n\n```{lang}\n{body}\n```\n")
    Path(path).write_text("\n".join(parts), encoding="utf-8", newline="\n")
    return path


def run_upgrade(tools_dir, *args):
    """upgrade.py acts on its own directory, so it is copied into the sandbox and run there."""
    result = subprocess.run([sys.executable, str(tools_dir / "upgrade.py"), *[str(a) for a in args]],
                            capture_output=True, cwd=str(tools_dir))
    return (result.returncode,
            result.stdout.decode("utf-8", errors="replace"),
            result.stderr.decode("utf-8", errors="replace"))


class UpgradeTest(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="vaultkit_upgrade_"))
        self.tools = self.tmp / "06_tools"
        self.tools.mkdir()
        shutil.copy2(TOOLS / "upgrade.py", self.tools / "upgrade.py")
        (self.tools / "build_index.py").write_text("print('old')\n", encoding="utf-8", newline="\n")

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    # ------------------------------------------------------------------ control

    def test_healthy_control_reports_no_change(self):
        kit = kit_file(self.tmp / "kit.md", {"build_index.py": "print('old')"})
        code, out, err = run_upgrade(self.tools, kit)
        self.assertEqual(code, 0, err)
        self.assertIn("1 unchanged", out)
        self.assertIn("nothing to do", out)

    # ------------------------------------------------------------ failure modes

    def test_a_changed_file_is_named_before_anything_is_written(self):
        kit = kit_file(self.tmp / "kit.md", {"build_index.py": "print('new')"})
        code, out, _ = run_upgrade(self.tools, kit)
        self.assertEqual(code, 0)
        self.assertIn("overwrite  build_index.py", out)
        self.assertIn("nothing written", out)
        self.assertEqual((self.tools / "build_index.py").read_text(encoding="utf-8"),
                         "print('old')\n", "file changed without --apply")

    def test_apply_writes_and_records_the_version(self):
        kit = kit_file(self.tmp / "kit.md", {"build_index.py": "print('new')"}, version="abcdef012345")
        run_upgrade(self.tools, kit, "--apply")
        self.assertEqual((self.tools / "build_index.py").read_text(encoding="utf-8"), "print('new')\n")
        self.assertEqual((self.tools / "kit-version.txt").read_text(encoding="utf-8").strip(),
                         "abcdef012345")

    def test_a_file_only_the_kit_has_is_reported_as_added(self):
        kit = kit_file(self.tmp / "kit.md",
                       {"build_index.py": "print('old')", "check_links.py": "print('new tool')"})
        code, out, _ = run_upgrade(self.tools, kit)
        self.assertEqual(code, 0)
        self.assertIn("add        check_links.py", out)

    def test_a_file_without_blocks_is_refused_not_reported_as_clean(self):
        empty = self.tmp / "not-a-kit.md"
        empty.write_text("# Just prose, no code blocks.\n", encoding="utf-8", newline="\n")
        code, out, err = run_upgrade(self.tools, empty)
        self.assertNotEqual(code, 0, "a file with no blocks must not read as up to date")
        self.assertIn("no script blocks", out + err)

    def test_an_unversioned_kit_says_so_rather_than_guessing(self):
        kit = self.tmp / "old-kit.md"
        kit.write_text("### `build_index.py`\n\n```python\nprint('new')\n```\n",
                       encoding="utf-8", newline="\n")
        code, out, _ = run_upgrade(self.tools, kit)
        self.assertEqual(code, 0)
        self.assertIn("unversioned", out)

    def test_non_ascii_content_survives_the_round_trip(self):
        body = "print('Übergröße')"
        kit = kit_file(self.tmp / "kit.md", {"build_index.py": body})
        run_upgrade(self.tools, kit, "--apply")
        self.assertIn("Übergröße", (self.tools / "build_index.py").read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main(verbosity=1)
```

### `test_vault_paths.py`

```python
"""Suite for vault_paths.py — the module every generated filename comes from."""

import shutil
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from _testkit import make_vault
from vault_paths import (
    RUN_LOG_RELPATH,
    category_index_name,
    category_label,
    has_forbidden_chars,
    is_index_file,
    log_run,
    project_index_name,
    root_index_name,
)


class VaultPathsTest(unittest.TestCase):
    def test_root_index_name_resolves_before_taking_the_name(self):
        """Path('.').name is the empty string — `--root .` must not write '# — Index'."""
        expected = f"INDEX - {Path('.').resolve().name}.md"
        self.assertEqual(root_index_name("."), expected)
        self.assertNotEqual(root_index_name("."), "INDEX - .md")

    def test_every_index_name_carries_what_it_indexes(self):
        self.assertEqual(category_index_name("ProjektEins", "01_Issues"), "INDEX - ProjektEins Issues.md")
        self.assertEqual(project_index_name("C:/x/ProjektEins"), "INDEX - ProjektEins.md")
        self.assertNotEqual(project_index_name("C:/x/ProjektEins"), "INDEX.md")

    def test_category_label_strips_only_the_sort_prefix(self):
        self.assertEqual(category_label("03_technical_docs"), "technical_docs")
        self.assertEqual(category_label("00_Notes"), "Notes")
        self.assertEqual(category_label("Notes"), "Notes")

    def test_forbidden_chars(self):
        for name in ("a#b.md", "a[b].md", "a|b.md", "a^b.md"):
            self.assertTrue(has_forbidden_chars(name), name)
        self.assertFalse(has_forbidden_chars("Übergröße-für-Ärger.md"))

    def test_is_index_file(self):
        self.assertTrue(is_index_file("INDEX - ProjektEins Notes.md"))
        self.assertFalse(is_index_file("eine-erkenntnis.md"))

    def test_log_run_appends_a_line_per_run(self):
        vault = make_vault(("ProjektEins",))
        try:
            log_run(vault, "build_index", "ok", "0 defects")
            log_run(vault, "build_index", "defects", "2 defects")
            lines = (vault / RUN_LOG_RELPATH).read_text(encoding="utf-8").strip().splitlines()
            self.assertEqual(len(lines), 2)
            self.assertIn("\tbuild_index\tok\t", lines[0])
            self.assertIn("\tbuild_index\tdefects\t", lines[1])
        finally:
            shutil.rmtree(vault.parent, ignore_errors=True)


if __name__ == "__main__":
    unittest.main(verbosity=1)
```

---

*Generated by `tools/build_kit.py`. Edit the sources, never this file.*
*Compare the `kit-version` at the top against the published file to see whether this copy is current.*
