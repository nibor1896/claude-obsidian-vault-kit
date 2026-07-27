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
3. **Match the user's shell.** Ask which OS and shell they use, then emit commands in that syntax
   only. PowerShell has no `&&` and no `export`; POSIX shells have no `Get-ChildItem`. Mixing them
   costs the user a failed round trip every time.
4. **Never touch a path outside the vault and the tool folder** without saying which path and why,
   and waiting for a yes.
5. **You write scripts; the scripts do the mechanical work.** Do not hand-write an index, do not
   hand-count entries, do not eyeball whether links resolve. If a number can be measured, measure it
   with code. If it cannot, say "not measured".
6. **State every number's origin.** "12 of 14 links resolve, measured by `check_links.py`" — or
   nothing. Never present an estimate as a measurement.
7. **One task at a time, verified.** Finish and verify a step before starting the next. A half-built
   vault that reports success is worse than no vault.

### Deliverables at the end of setup

- The folder tree from SECTION 3, with real folders on disk.
- A generated index tree (SECTION 5) — root, project, category.
- Guard scripts from SECTION 6, each with a matching `test_*.py` in the same commit.
- Optional: the GitHub issue mirror from SECTION 7.
- `05_workflows/knowledge-transfer.md` — the workflow, written in the user's own words.
- Backup and git set up per SECTION 8.
- A verification run per SECTION 9, with its output shown to the user.
- **The acceptance test from SECTION 10, passed.** The setup is not finished until every guard has
  been shown to go red on deliberately bad input on this machine. Clean input proves nothing.

---

## SECTION 1 — Interview

Ask these. Group them so the user answers a few at a time rather than facing a wall of questions.

**What may be skipped, and what may not.** Skip a question only when it asks about a *prerequisite*
you can read off disk — OS, shell, Python version, whether `git` and `gh` exist — and then say out
loud which questions you skipped and what you measured.

**Never skip, never infer, no matter what the disk shows:**

- **1.1 — does the user already use Obsidian.** An installed app is not an answer. It says nothing
  about whether a vault exists, where it is, or whether the user wants you near it. Inferring "already
  uses Obsidian" from a present installation is how a setup ends up adapting a real vault nobody
  pointed you at.
- **1.2 — test vault or straight to production.**
- **1.3 — project names, and where their code lives.**
- **1.4 — whether a tracker gets mirrored, and which repos.** An authenticated `gh` is not consent.
  Finding credentials on the machine tells you the mirror is *possible*, not that it is wanted.
- **1.5 — backup location and, separately, whether a remote may be added.**

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
- If **yes**: ask for the vault path, then **read the existing structure before proposing anything**.
  List what is there, name what already matches this kit, and name what conflicts. The user's
  existing structure wins over this document unless they say otherwise — a folder they already use
  daily is worth more than a clean scheme they have to relearn.

### 1.2 Test vault first?

Ask: **"Do you want a throwaway test vault first?"** Explain the two paths in one line each:

- **Test vault path:** you build the complete structure in a scratch folder. The user opens it in
  Obsidian, clicks through it, renames folders, drops sections, adds their own. They tell you when
  they are done. **You then read the resulting structure from disk and adopt it as the real spec** —
  folder names, order, which categories exist — and build the production vault from that. This is
  the recommended path for anyone who has not lived in a vault before.
- **Direct path:** you build straight into the real location.

If they choose the test vault:
- Put it somewhere obviously temporary and say the path out loud.
- When they report back, **read the folders as they now exist** — do not re-propose your original
  scheme. Diff it against SECTION 3, list every change they made, and confirm your reading with
  them in one short list before you build production.
- Delete the test vault only after they confirm production is good, and ask first.

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

- **Backup location.** Recommend a cloud-synced folder (OneDrive, Dropbox, iCloud Drive, Syncthing).
  Ask which one they use.
- **Git as well?** Recommend yes: cloud sync knows file versions, git knows *states across all
  notes*. Neither replaces the other.
- If they want git: **public or private remote?** If the vault will hold anything private —
  and a mirrored issue tracker usually does — the remote must be private. Say this explicitly and
  get a yes before you add any remote.

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
2. **The filename carries the title, never just a number.** `ISSUE-42.md` tells nobody anything six
   weeks later. If a character is not legal in a filename, clean the title — do not drop it.
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
├── INDEX.md                         generated — one line per project
├── 00_Global/                       optional: things belonging to no single project
│   └── (same subfolders as a project)
└── <ProjectName>/
    ├── INDEX.md                     generated — one line per category
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
<VaultRoot>/INDEX.md                                 one line per project        --root
<Project>/INDEX.md                                   one line per category       --vault <dir>
<Project>/<Folder>/INDEX - <Project> <Category>.md   the entries themselves
```

- **The category index filename carries the project name.** Every project has identically named
  folders; without the project in the filename the graph shows five nodes called `INDEX - Issues`
  and the quick switcher becomes a coin toss.
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

Two mechanics that break this rule quietly, both worth stating because they look like working code:

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

```powershell
# Windows / PowerShell — one command per line, no chaining
cd <VaultRoot>
git init
git add .gitattributes .gitignore INDEX.md
git commit -m "chore: initialise vault"
```

```bash
# macOS / Linux
cd <VaultRoot>
git init
git add .gitattributes .gitignore INDEX.md
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

**The diagnostic to remember:** a note that shows as fully rewritten — same line count out and in,
e.g. `@@ -233,233 +233,233 @@` — has almost certainly only changed its line endings. Confirm before
concluding anything:

```bash
git diff --ignore-cr-at-eol -- path/to/note.md
```

Empty output means the content is byte-identical and only CR moved. Then decide deliberately: commit
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

### Write the workflow file

Create `<Project>/05_workflows/knowledge-transfer.md` containing: the goal in one sentence, the
inputs, the tools table, the command sequence for *this user's* shell, the expected output, and the
edge cases you hit during setup. This is what makes the vault survive you — the next session reads
this file instead of re-deriving the whole thing.

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

Create the fixtures in a throwaway folder inside the vault, run the checks, then delete the folder
and confirm the tree is clean again. Show the user the result of every line.

| # | Fixture you create | Required behaviour | Fails how, if broken |
|---|---|---|---|
| 1 | note with no `title:` | index run exits **non-zero** and names the file on stderr | exits 0, filename appears as the entry title, nobody notices for months |
| 2 | note whose `summary:` starts with `>` or `#` | debris stripped, file named, exit non-zero | index line renders as `— > Living inventory …` |
| 3 | `[[wikilink]]` to a note that does not exist | link checker reports it, exit non-zero, **denominator > 0** | reports "0 broken" because it scanned nothing |
| 4 | note whose filename contains `#` | entry falls back to a markdown link, file named, exit non-zero | silent unresolvable wikilink |
| 5 | note whose filename contains a non-ASCII character (umlaut, accent) | it appears in the index and in the link count | it is silently absent from the denominator |
| 6 | nothing — run the index generator twice | second run leaves `git status` empty | every later `git status` is noise |
| 7 | point the suite runner at an empty directory | reports **"0 suites collected"** and does **not** say green | "all green" over zero tests |
| 8 | remove or blank a scheduled job's run log | freshness check says **"did not run"**, not "fine" | a scheduler that stopped is indistinguishable from a healthy one |

```bash
# after the run, in this order
rm -r <vault>/_acceptance          # or the platform equivalent
python 06_tools/build_index.py --vault <Project>
git status --porcelain             # must be empty again
```

Report it like this, one line per check, and **name any check you did not run**:

```
Acceptance: 8/8 guards went red on bad input
            (or) 6/8 — #5 non-ASCII filename NOT caught, #8 not run
```

If a check does not behave as specified, the generated script is wrong — fix the script, not the
expectation. A guard that passes bad input is worse than no guard, because it will be cited as
evidence.

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
