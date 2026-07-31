<!-- kit-version: da3b9756915a -->
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
   and whether `git` exists off disk instead of asking — say so when you do. You may not infer any
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
   - **A proposal may only be built from what the user has already given you**: the paths in their
     instruction, their earlier answers in this interview, and this file. Nothing else. Listing a
     directory to find better options is a read of their machine, and rule 5 below governs it — name
     the path and the reason, wait for a yes, or do not read it. **If no proposal can be built
     without such a read, ask the question with no pre-filled first option.** An empty first option
     costs one round trip; an unannounced scan costs something you cannot give back. One cold run
     offered the user's three real repository names as option 3, read from `<home>/dev` — a path no
     instruction had named, and nothing in the output said a directory had been looked at.
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
   and waiting for a yes. **One exception, and it is the only one:**
   `~/.claude/commands/vaultkit.md`, written in SECTION 8. That file is part of this setup, not an
   extra — it is how the verification chain gets run from then on, and it works nowhere else. Name
   the path out loud before writing it, then write it. Do **not** turn it into a question: an offer
   with a "no" in it produces a vault whose own maintenance command does not exist. The tool never
   overwrites, so the only thing a yes could protect is a file it already refuses to touch.
6. **The scripts are inside this file. Write them out; do not rewrite them.** SECTION 10 carries
   every tool the vault runs, verbatim. **The suites and the verification drivers are not in it**
   — they live in the kit's repository, and they ran there over these exact bytes before this file
   was published: on Windows 11 with Python 3.13, under PowerShell 5.1 and Git Bash, **11/11 suites
   green, 12/12 acceptance checks and 15/15 end-to-end setup steps, in ten consecutive runs under
   each shell.** That is a statement about the release, not a chore for this machine: a vault does
   not re-run unit tests over code that has not changed since setup. Write each block to disk byte
   for byte. Retyping them from the contracts in SECTION 5 and SECTION 6 throws that measurement
   away and reintroduces the defects those sections describe — every one was found the expensive
   way. **Change a shipped script and the measurement no longer describes what the user has, and
   nothing in their folder can tell them so.** Say that out loud if you ever do it.
   **Tell the user how to update later.** The header of this file carries a line like
   `<!-- kit-version: … -->` (twelve hex characters). It is a hash of the contract and every shipped script, so
   two copies with the same line are the same kit and a different line means something changed.
   Point them at `upgrade.py`, which is shipped alongside the other tools: given a newer kit file it
   lists what would be overwritten, added and removed, writes nothing without `--apply`, and reads
   every file back before it compiles the folder. **Name where a newer file comes from** — the repository is in the
   last lines of this file; a user holding only the `.md` has no other way to find out that a newer
   one exists. Say this once during setup -- a user who does not know an update path exists will not
   go looking for one. The stamp `upgrade.py` compares against is written in SECTION 8.
7. **The scripts do the mechanical work.** Do not hand-write an index, do not hand-count entries, do
   not eyeball whether links resolve. If a number can be measured, measure it with code. If it
   cannot, say "not measured".
8. **State every number's origin.** "12 of 14 links resolve, measured by `vaultkit.py links`" — or
   nothing. Never present an estimate as a measurement.
9. **One task at a time, verified.** Finish and verify a step before starting the next. A half-built
   vault that reports success is worse than no vault.

### Deliverables at the end of setup

- The folder tree from SECTION 3, with real folders on disk.
- A generated index tree (SECTION 5) — root, project, category.
- Every block from SECTION 10 written into the vault's tool folder — the guards, `upgrade.py` and
  `jobs.json`. No suites: they are release verification and stay in the kit's repository.
- The four starting pages named in SECTION 8 — and **no other notes**. Nothing invented.
- Backup and git set up per SECTION 7.
- **A `/vaultkit` command in `~/.claude/commands/`**, with the path it went to shown to the user.
  If a command of that name was already there, it keeps the name: say so, and do not list
  `/vaultkit` as delivered.
- A verification run per SECTION 8, with its output shown to the user.
- **The acceptance test from SECTION 9, passed.** The setup is not finished until every guard has
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
you can read off disk — OS, shell, Python version, whether `git` exists — and then say out
loud which questions you skipped and what you measured.

**Never skip, never infer, no matter what the disk shows:**

- **1.1 — does the user already use Obsidian.** An installed app is not an answer. It says nothing
  about whether a vault exists, where it is, or whether the user wants you near it. Inferring "already
  uses Obsidian" from a present installation is how a setup ends up adapting a real vault nobody
  pointed you at.
- **1.2 — migration, new production vault, or test vault.**
- **1.3 — project names, and where their code lives.**
- **1.4 — the vault path, the backup, git, and whether a remote may be added.**
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

**Do not ask whether they want a global bucket.** `00_Global/` is always created — it is where the
tools go, and the scripts spell that path out. State it in the one-line summary after this round
("`00_Global/` will hold the tools and anything that belongs to no single project"), and move on.
This was a question until 2026-07-30, and the answer "no" was never honoured: the first tool run
recreated the folder through `log_run`, with exit 0 and no message. A question whose answer the code
overrules is worse than no question — it teaches the user that their answers do not decide anything.

### 1.4 Where the vault lives, and how it survives

Four questions, one call:

- **The vault path.** Propose one and have it confirmed. It must sit inside the folder you were given.
- **Backup location.** Recommend a cloud-synced folder (OneDrive, Dropbox, iCloud Drive, Syncthing).
  Ask which one they use — and if a cloud folder exists on the machine but is out of bounds, say so
  rather than proposing it.
- **Git as well, and may a remote be added?** Recommend git: cloud sync knows file versions, git knows
  *states across all notes*. Neither replaces the other. "Yes to git" is not "yes to a remote" — a
  vault of project knowledge holds things the user would not publish, so the remote must be private,
  and that needs its own yes.
- **`user.name` and `user.email`** — ask for both, set them repo-locally, never `--global` (SECTION 7).
  Do not invent them and do not copy them from another repo on the machine. Offer a sensible default as
  the first option so it is one click. **Both defaults are named, so neither is left to judgement:**
  - `user.email` → `<handle>@users.noreply.github.com` as the first clickable option. The rule and
    the reason are in 1.0 above.
  - `user.name` → **the handle you just used to build that address**, as option 1:
    `[1] <handle>  [2] a different name`, with free text for anything else. The two values may
    legitimately differ — a full name against a handle — which is why this stays a question and
    never becomes an assumption. What it must not be is a second blind typing: in both cold runs on
    2026-07-30 the operator typed the same string twice, because the question that already had the
    answer did not offer it. If no handle was given (the user chose a real address instead), there
    is no default here — ask it open.

### 1.5 Environment

- **OS and shell**, exactly. Every command you emit later depends on this.
- **Python 3.10+ available?** Check with `python --version` / `python3 --version`. The guard scripts
  are Python. If Python is absent, offer the install and wait.

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

Every project gets the *same* folders, so a path is predictable without looking. You create them
once during setup; after that the index generator creates any that are missing, including in a
project folder the user makes themselves later (SECTION 5).

```
<VaultRoot>/
├── INDEX - <VaultName>.md           generated — one line per project
├── 00_Global/                       ALWAYS created — the tools live here; see the note below
│   └── (same subfolders as a project)
└── <ProjectName>/
    ├── INDEX - <ProjectName>.md     generated — one line per category
    ├── 00_Notes/                    insights that belong to no larger document
    ├── 02_docs/                     product, project and decision documentation
    ├── 03_technical_docs/           the subsystem handbook — one page per subsystem
    ├── 04_feedback/                 working rules the user has given the agent
    ├── 05_workflows/                SOPs that apply to this project only
    └── 06_tools/                    scripts, plus this project's sources config
```

Rules for the tree:

- **The numeric prefixes exist for sort order only.** Keep them; they make Obsidian's file pane match
  the mental order. `01` is deliberately unused — closing the gap would rename every category index
  file in every project for no gain, and the prefix carries no meaning to close.
- **`00_Global/` is always created, and it is not a question.** The tools live in
  `00_Global/06_tools/`, and that path is not a preference — it is written into the scripts. The run
  log is `00_Global/06_tools/runs.log` (`vaultkit.RUN_LOG_RELPATH`), `vaultkit.py freshness` reads it
  there, `upgrade.py --stamp` writes `00_Global/06_tools/kit-version.txt`, and the `.gitignore`
  comment names the same path. Offering "no global folder" as a choice was worse than not asking:
  the first tool run recreated `00_Global/06_tools/` anyway, through `log_run`'s `mkdir(parents=True)`
  — exit 0, no message, against the user's stated answer. **Tell the user the folder is being created
  and what it is for; do not ask whether to create it.** Whether they also file *notes* there is
  entirely theirs — an empty `00_Global/00_Notes/` costs nothing.
- **Tools live in exactly one place.** Two copies of a script means one of them is silently out of
  date. Every other project supplies only its own small config file.
- **Optional extras**, add only if the user has the need: `07_reports/` (one report per
  investigation) is the common one. Any folder the user adds by hand becomes a category of its own
  on the next index run (SECTION 5) — they do not have to ask permission for a folder.
- If the user changed folder names in a test vault, **their names win** — carry them consistently
  into every project and into every script's config.
- **A directory at the vault root is a project, and the generator will treat it as one.** It gets
  the category folders and a hub index on the next run. Say this before the user parks an
  `attachments/` or a `_scratch/` next to their projects: it is not wrong, but they will get six
  folders inside it and the run will tell them it made them.
- **`_templates/` is the one exception, and it is the generator's own.** It sits at the vault root,
  holds one note template per project, and is never a project: no category folders, no hub index,
  and its files are not notes. That exemption is a line in `SKIP_DIRS`, not a special case in the
  index code — without it the folder gets six subfolders and the templates go red for having no
  `summary:`. See SECTION 5 for what is written and SECTION 8 for the one Obsidian setting.

---

## SECTION 4 — Frontmatter contract

This is the interface between the notes and every script. Get it exactly right; everything
downstream reads it.

```yaml
---
title: "One line that states the insight"
summary: "One plain sentence. No markdown, no blockquote, no heading marks, no line breaks."
project: "<ProjectName>"     # optional; must equal the containing project folder
created: 2026-01-15
updated: 2026-02-03          # optional; the index prefers this over `created`
issues: "#12, #14"           # optional; a plain-text citation, never a link — see below
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
- **`project:` is optional and advisory.** The folder a note sits in decides where it is indexed;
  no script reads this field to place anything. It exists so a human reading the file knows where it
  belongs without reconstructing the path. Leave it out and nothing happens — that is what optional
  means here. Write a value that disagrees with the project folder and the run goes red: not because
  the value is wrong, but because two sources claim different things and only one of them has any
  effect. The comparison is exact, case included — the folder name *is* the project name and goes
  into every wikilink as it stands, so a case difference breaks on case-sensitive filesystems.
- **`issues:` is optional, free text, and deliberately not a wikilink.** It exists so a note can cite
  a ticket number the user tracks somewhere else; this kit reads no tracker and writes none. Making
  it a link would pull hundreds of note→ticket edges into the graph and turn it into a hairball, and
  every one of them would be permanently unresolved — there is no note on the other end.
- **`generator:` is the overwrite marker.** A note without it survives every rebuild — it is an
  original. A note with it is derived and replaceable. If a source document is deleted, retire it
  properly (remove the marker, drop the entry from the config) or the next run deletes the note with
  no replacement.

---

## SECTION 5 — The index generator (`vaultkit.py index`)

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
  called `INDEX - docs` and the quick switcher becomes a coin toss.
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

> Generated by `06_tools/vaultkit.py index` from note frontmatter.
> Do not edit by hand — changes belong in the note itself.
> As of: <YYYY-MM-DD>
```

### Two mechanics that produce output depending on how the script was called

Both were found by the acceptance test in SECTION 9, on a first real setup:

- **Derive every name from a resolved absolute path.** `Path(".").name` is the empty string, so
  `--root .` writes `# — Index` while `--root C:/…/Vault` writes `# Vault — Index`. Two correct
  invocations then produce a diff against each other, which is exactly the drift SECTION 8 forbids.
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

### It owns the shape of a project: it scaffolds, it adopts, and it says so

The category list is what a project is **created** with, not the only thing it may hold. Two things
follow, and the generator does both on every run:

- **A project folder that is missing category folders gets them.** A user makes `<Project>/` in
  Obsidian's file pane and it is empty. Leaving it empty means they must know six folder names and
  spell them correctly before anything they write is indexed.
- **A folder the user made by hand becomes a category of its own** — it stays where it is, it gets
  its own `INDEX - <Project> <Folder>.md`, and its notes are in the count. SECTION 3 explicitly lets
  the user name their own folders; a generator that then calls one a defect is arguing with the
  document it implements.

**Neither is a defect, and neither is silent.** Print one line per folder created and one per folder
adopted, on stdout, and put the counts in the run log:

```
  created  ProjectB/03_technical_docs — category folder was missing
  adopted  ProjectB/06_werkzeuge — folder made by hand, indexed as a category
```

That line is the whole safeguard, so do not drop it as noise. Measured on a first cold setup:
renaming `06_tools` to `06_werkzeuge` in Obsidian took the run from 21 categories to 20 — **exit 0,
no message, and the folder simply absent from every index.** Adoption fixes the missing half of
that: the notes now reach an index. The printed line fixes the other half, and it is the only
warning a *mistyped* folder name will ever get — `00_Nots` is indistinguishable from a deliberate
new category except that the user reads the line and says "I did not mean that".

**Skip what is not a category.** `.git`, `.obsidian`, `__pycache__`, `.trash`, `.venv`,
`node_modules`, `_templates` and anything starting with a dot are never adopted. One `node_modules`
at project level would otherwise become a permanent category with an index file inside it.

### It also writes one note template per project, once

The `--root` run writes `<VaultRoot>/_templates/TEMPLATE - <Project>.md` for every project that has
none. The file carries the four fields of SECTION 4 that every note actually fills — not all nine:

```
---
title: "{{title}}"
summary:
project: "<Project>"
created: {{date}}
---
```

- **`{{title}}` and `{{date}}` are Obsidian's**, two of the three variables its core Templates
  plugin knows (the third, `{{time}}`, has no field here). The title therefore comes from the
  filename, which is where the title belongs anyway, and the date fills itself.
- **`project:` is written in, per file.** It is the one value a template can get right that a person
  retyping the block gets wrong — and getting it wrong is exactly what the guard in SECTION 4
  reports. One file per project is not redundancy; it is the only way to carry the project name,
  because Obsidian has no folder variable.
- **`updated:`, `issues:`, `generator:`, `retired:` and `stale:` are deliberately absent.** They are
  situational — set when something happened, not when a note is started. `generator:` is the one
  that must never sit in a template waiting to be filled: a note carrying it is declared derived,
  and a rebuild is then entitled to overwrite or delete it. Nothing is hidden by leaving them out,
  because Obsidian's *Add property* offers every field already in use anywhere in the vault. The
  contract in SECTION 4 still defines all nine — the template is not the contract.
- **Created when missing, never overwritten.** A template is there to be edited. A tool that rewrites
  it on every run eats the user's change silently, and the doctrine rule about not hand-editing
  generated files covers the index tree, not this folder.
- **Say what was written**, one line per template, like `created` and `adopted` above. A run that
  puts a file in the user's vault without a word is the defect this whole section exists to avoid.

A folder that cannot be created — permissions, a file of that name in the way — **is** a defect,
with the OS error attached. That is the one case here where the run goes red.

### Exit code

`0` only when every entry was clean. Otherwise print each defect as `<filename>: <what is wrong>` on
stderr and exit non-zero. Report the totals as `n entries in m categories` so a zero has a
denominator.

---

## SECTION 6 — The guards

Each of these is a small script with one job, and each has a `test_*.py` beside it **in the kit's
repository** — written in the same commit as the tool, and not delivered. Every suite needs at least
one **failure-mode fixture** *and* one **healthy control**; a test that only ever sees good input
cannot tell you the check still works.

| Script | Job | Must refuse |
|---|---|---|
| `vaultkit.py index` | the index tree (SECTION 5) | a silent fallback on a degraded entry |
| `vaultkit.py links` | every `[[wikilink]]` resolves to a file | reporting `0 broken` when it scanned 0 files |
| `vaultkit.py duplicates` | notes whose content overlaps | being ignored — every hit gets a decision |
| `vaultkit.py freshness` | age of the last **healthy** run of each scheduled job | treating "no log" as "fine", or a job listed as both watched and on-demand as watched |
| `vaultkit.py tokens` | size of what was read, for cost | inventing a precision — output `exact` or `estimated` |
| `vaultkit.py command` | the `/vaultkit` command, with this vault's real paths in it | overwriting a command the user has edited, or writing one without naming the path |

### The one rule all of them share

**Refuse a silent zero.** Every script prints numerator *and* denominator, and distinguishes three
outcomes explicitly: pass, fail, and *did not run*. A check that cannot tell "working" from "broken"
is not evidence.

The third one is a phrase, not an exit code, and it is spelled **`did not run: <why>`** — one
wording, from one constant, because a checker that scanned nothing and a checker that found nothing
print the same number otherwise.

### The three exit codes, and what each one claims

Both shipped scripts use these, and nothing else. Read them as claims about *what was measured*, not
as severity:

| | Meaning | What the user does |
|---|---|---|
| `0` | **Clean.** The check ran over a real population and found nothing wrong. | nothing |
| `1` | **A defect, or `did not run`.** Either it found something, or it could not reach a verdict. | fix a note, or run the thing that was missing |
| `2` | **The arguments or the sources are wrong, not the vault.** An unknown subcommand, a path that is not a directory, two config lists that contradict each other, a file operation the environment refused. **Nothing was measured, so nothing about the vault is being claimed.** | fix the command or the config |

**`1` covers two states on purpose.** "I found a broken link" and "I could not look" are both *do not
trust this vault yet*, and both are answered by the same next action: look at the output. Splitting
them would put the difference in a number instead of in the sentence that already carries it.

**One deliberate exception, and it is the kind that reads like a bug forever if nobody writes it
down.** `vaultkit.py duplicates` returns **`0`** when there are fewer than two comparable notes,
where `links` and `freshness` return `1` in their equivalent case. The reason is the first run of a
new vault: one note is not a failure, it is Tuesday. A guard that goes red on a brand-new vault
teaches its owner to ignore it in the first minute, and a check that gets ignored is worse than one
that does not exist.

Measured on 2026-07-31, flipping that one return to `1`: a fresh vault holding a single note goes
from exit `0` to exit `1` — **and `acceptance.py` stays at 12/12**, because its healthy-control
fixture has two notes. Nothing in this kit's own verification sees that decision, which is precisely
why it is stated here rather than left in the code to be discovered and "fixed".

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

### Read every file the user might have written as `utf-8-sig`, never `utf-8`

```python
text = path.read_text(encoding="utf-8-sig", errors="replace")
```

Windows editors — Notepad, and PowerShell 5.1's `Set-Content -Encoding utf8` — write a byte-order
mark by default. **`"﻿".isspace()` is `False` in Python, so a BOM survives `strip()`** and sits
in front of the first character of the file where nothing visible is. Reading as `utf-8` keeps it;
reading as `utf-8-sig` drops it if it is there and behaves identically if it is not. There is no
case where `utf-8` is the better choice for a file the user may have touched.

Every place that anchors on the *first* character breaks, and each one breaks quietly. Measured on
one machine, one note per case:

| What reads it | What the BOM does | What the user sees |
|---|---|---|
| the frontmatter reader's `first.strip() != "---"` | the block is not recognised at all | title and summary gone from the index, and the run goes **red over a correct note** |
| the duplicate check's `text.startswith("---")` | frontmatter is compared as body text | two identical bodies stop scoring as identical; a real duplicate goes unflagged |
| the link checker's `^\s*(```\|~~~)` fence match — a BOM is **not** `\s` | a note opening with a code fence loses fence detection, and the fence never closes | every wikilink documented inside that block reported broken; the note is right and the guard is wrong |
| `json.loads` on a config file | raises, and a bare `except` returns the default | the check measures a job list the user never configured, silently |

Two rules follow from that last row and they are cheap: **read config as `utf-8-sig` too**, and
**never let a config that exists but cannot be parsed fall back without printing why.** A missing
config falling back to a default is normal. A present one doing it is the same silent zero this
whole section is about.

### Two more mechanics that break the rule quietly, both worth stating because they look like working code:

- **A skip that does not count itself.** `except OSError: continue` in a counting loop still prints a
  total — over fewer files than it names. Keep a `skipped` counter, print it, and treat a non-zero
  value as a defect rather than a footnote.
- **Paths that never reach the filesystem.** `git ls-files` *quotes* names containing non-ASCII, so
  feeding its plain output to `open()` fails on the quotation marks. Use `git ls-files -z`, split on
  `\0`, and pass bytes. Get this wrong and every note with an umlaut in its name silently leaves the
  denominator — which is exactly the class of file a knowledge vault is full of.

### `vaultkit.py duplicates` in particular — the threshold is a knob nobody has turned yet

**The default is `0.75`, and it is unvalidated. Say so when you report the result.** It was chosen
as a plausible starting value, not derived from a measurement, and nothing since has tested it
against a body of notes large enough for the answer to mean anything. On the runs that exist it
reported `0 pairs flagged` across five and six notes — on that denominator almost any threshold
reports zero, so the run confirms the arithmetic and nothing else.

This is not a defect to fix before shipping; it is a number whose status has to travel with it. A
threshold that reads as tuned invites the opposite of what it deserves: the user takes `0 flagged`
as evidence that there are no duplicates, when it is evidence only that nothing crossed a line
nobody has placed.

**What would validate it**, so this is a measurement someone can actually run rather than a
disclaimer:

- A vault with **at least a few hundred notes** that a person knows well enough to judge.
- The check run **at several thresholds over the same notes** — 0.6, 0.7, 0.75, 0.8, 0.9 — with the
  flagged pairs recorded per threshold, not just the counts.
- Each flagged pair judged by hand: a real duplicate, or two notes that legitimately share
  boilerplate. **Both error directions are counted.** The interesting failure is not the pair it
  flags wrongly, it is the pair it misses, and a run that only counts hits cannot see those.
- The result written down **with its denominator and the vault it came from**. A threshold tuned on
  one person's writing is not a universal constant, and the next vault may want a different one.

Until that exists, `--threshold` is the honest interface: the number is exposed on the command line
precisely because it is not settled.

### `vaultkit.py freshness` in particular

Any job on a schedule (task scheduler, cron, launchd) writes a line to an append-only log on **every
run, including the healthy ones**. `vaultkit.py freshness` reads that log and reports the age of the
last healthy run per job, against a threshold the user sets. Without this, a scheduler that quietly
stopped firing looks identical to one that is fine.

**Logging and being watched are two different things, and `jobs.json` carries three lists.** Every
tool writes a line; only a tool that runs on a schedule can be *late*. Put the on-demand ones under
an age limit and the report is red every single day — which is the fastest way to get the whole
check switched off, and a check nobody runs is worth less than none. So `jobs` is what must be
fresh, `on_demand` is what logs and is never late, `not_invoked` is what no chain calls at all, and
each entry in the latter two carries its reason as its value, because JSON has no comments and an
exception without a reason is indistinguishable from an oversight.

Four consequences, and each one is a behaviour, not a preference:

- **A name in two of the lists stops the tool with exit 2.** Not "watched wins": that would be an
  invisible decision, with the other entry sitting there doing nothing and no run able to show
  which of the statements applies.
- **A name in none of them is reported, and does not change the exit code.** That line is the only
  real signal in this area — somebody built a tool and nobody decided whether it is watched.
  Turning it red would make the chain permanently red for every user who adds a tool of their own.
- **That report is read from the tool folder, not only from the run log.** A tool that no chain
  calls never writes a line, so a population taken from the log alone cannot contain the one thing
  the report exists to name — the check confirms its own silence, and the tools it cannot see are
  exactly the ones that fell out of the chain. Measured on one setup: `0 unclassified` over a
  folder holding a tool that was in no list at all. Only tools that *can* log are counted, because
  asking whether something that never logs is late has no answer that changes anything.
- **The check itself logs, and stands in `on_demand`.** Without its own line, "the freshness check
  runs in the chain" is a claim about a command file: delete the step and it looks exactly like a
  check that runs and finds nothing. Watching the watcher would be the regress; logging is not
  watching.

**It runs FIRST in any chain that also runs other tools** — see the verification run in SECTION 8.
Every other tool appends an `ok` line, so a freshness check measured afterwards sees the side effect
of the chain it belongs to and reports fresh over a job that died a week ago.

Note for scheduled jobs on laptops: default task settings often include *do not start on battery*
and *do not catch up on missed runs*. That combination produces multi-hour gaps overnight that no
error message ever mentions. Tell the user this when you set up any schedule.

---

## SECTION 7 — Backup, git, and the two failure modes

Set up **both**, and tell the user why neither replaces the other: cloud sync knows file versions but
has no notion of a coherent state across all notes; git knows states but lives on the same disk.

**Put the vault in its own folder, not in the folder you were started in.** If the agent's own config
directory (`.claude/`, `.cursor/`, whatever the harness uses) sits next to the notes, it lands in the
vault's history. A subfolder — `<workdir>/<VaultName>/` — keeps the two apart with no ignore rules to
maintain.

**Nothing this setup writes lands in a `.claude/` folder inside the vault.** The `/vaultkit`
command goes to the user's own `~/.claude/commands/`, outside the vault entirely. Such a folder may
still turn up here — the user keeps settings beside their notes, or the setup was started in one —
and none of it belongs in the history: sessions, settings and caches are the agent's state, not
project knowledge. The `.gitignore` below ignores the whole folder, the same way it handles the
volatile parts of `.obsidian/`.

**A fresh machine usually has no git identity at all**, and `git commit` then fails with *"Author
identity unknown"* mid-setup. Check before the first commit and set it **repo-locally** — never
`--global`, which writes outside the folder the user gave you:

```bash
git -C <VaultRoot> config user.name  "<name the user gives you>"
git -C <VaultRoot> config user.email "<email the user gives you>"
```

Ask for both. Do not invent them, and do not copy them from another repo on the machine — an identity
appears in every commit forever, and if the vault ever gets a remote it becomes public.

**Stage only what exists at this point.** `INDEX - <VaultName>.md` is *not* written yet — the
generator creates it in SECTION 8, several steps from here. Staging it makes `git add` fail with
*"did not match any files"*, and an agent that works around the error by running the generator early
has quietly reordered the setup. Measured on the cold run of 2026-07-30: the operator had to commit
in two stages to get past it. The tree and the notes are committed in SECTION 8, after the
verification run, where the index exists.

```powershell
# Windows / PowerShell — one command per line, no chaining
cd <VaultRoot>
git init
git add .gitattributes .gitignore
git commit -m "chore: initialise vault"
```

```bash
# macOS / Linux
cd <VaultRoot>
git init
git add .gitattributes .gitignore
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

# The agent's own folder, if one turns up here: sessions, settings and caches are its state, not
# project knowledge. Nothing this setup writes lives here -- the /vaultkit command goes to the
# user's own ~/.claude/commands/ -- so the whole folder is ignored, with no exception to maintain.
.claude/

# Append-only run log that every tool writes a line to. Tracked, it makes git status dirty after
# every check, and acceptance fixture 6 permanently noisy. The freshness check reads it off disk,
# not out of git. Leading **/ on purpose: 06_tools/runs.log anchors to the repo root and would
# never match 00_Global/06_tools/runs.log -- measured twice, on two different setups.
**/runs.log

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

## SECTION 8 — Verify, then hand over

### Stamp the tool folder with the version that wrote it

Before the verification run, run this once — it is a command, not a file you write:

```
python <VaultRoot>/00_Global/06_tools/upgrade.py --stamp <path to this kit file>
```

It writes

```
<VaultRoot>/00_Global/06_tools/kit-version.txt
<VaultRoot>/00_Global/06_tools/kit-manifest.txt
```

The first one's whole content is the twelve hex characters from the `<!-- kit-version: … -->`
comment on line 1 of this file, plus a newline. UTF-8, no BOM, nothing else in the file — no date,
no label, no sentence around it; `upgrade.py` reads the file and strips it, and anything else in
there becomes part of the version. **It stays one line forever**: every `upgrade.py` already
installed anywhere reads the whole file and compares it against twelve characters, so a second line
in it would break the update path at exactly the folders an update exists to rescue. That is why
the file list went into a second file beside it instead.

`kit-manifest.txt` is that list — one filename per line, sorted, every file this kit delivers. It is
what makes removal safe: a later kit that no longer carries a script can delete it, because the
manifest says this kit brought it. Anything **not** in that list is the user's own — their tools,
their `runs.log`, a `jobs.json` they extended — and is never a candidate for removal.

`--stamp` writes those two files and touches nothing else; it needs no `--apply`.

**Do not type those twelve characters yourself**, even though you can see them. They already exist
verbatim in a file on disk, which makes copying them mechanical work — operating rule 7. If the kit
file carries no stamp line, `--stamp` refuses instead of recording `unversioned`: that string would
be compared against every future kit and never match.

This is the value the entire update path compares against. `upgrade.py` prints
`installed: <version> · kit file: <version>`, and until this file exists it prints
`installed: unknown` — so a user cannot tell an outdated tool folder from a current one, which is
the one question the update path exists to answer. Nothing else writes it at setup time:
`upgrade.py` writes it again when it applies an update, i.e. from the *second* version onwards.

**A folder installed before manifests existed has exactly one blind update cycle**, and that is a
promise rather than a bug. Such a folder has no `kit-manifest.txt`, so nothing on the machine knows
what the older kit delivered — and guessing, by treating every script in the folder as the kit's,
would delete the user's own work on the first update. So the first `upgrade.py … --apply` there
removes nothing, says why in as many words, and records a manifest on its way out. The update after
it can remove what a newer kit drops. Say this to the user if their folder is in that state; a run
that removed nothing without explaining itself looks exactly like a run with nothing to remove.

### Write the `/vaultkit` command

**After git, and before the verification run.** The order matters and it is not cosmetic: the
generated file states whether this vault has a repository, because with one the last step is
`git status --porcelain` and without one it is a paragraph telling the user to compare index files
by hand. Write the command before `git init` from SECTION 7 has run and that paragraph is true for
about a minute, then wrong for the life of the vault — and nothing later reads the file again to
notice. Measured on a cold run: the command was written first and carried
*"this vault has no git repository"* into a vault that got one two minutes later.

The tool never overwrites, so if the order does slip, the fix is to delete the file it wrote and run
it again — not to edit it by hand.

Run this once:

```bash
python <VaultRoot>/00_Global/06_tools/vaultkit.py command --vault <VaultRoot> \
       --shell powershell|posix
```

It writes `~/.claude/commands/vaultkit.md` — the user's own commands folder, which is the only
destination and takes no flag — with this vault's real paths already in it, and prints the path it
wrote. **Show the user that line.**

**Announce it, do not ask.** The file lands outside the vault, which is why operating rule 5 names
this one path as its single exception: say where it goes and what it is for, then run the command.
A question with a "no" in it hands the user a vault whose maintenance command does not exist, and
nothing further down works around that. The tool never overwrites anything, so there is no damage a
yes would have prevented.

There is no in-vault alternative, and the reason belongs here so nobody re-adds one: a command
under `<VaultRoot>/.claude/commands/` loads only in a session started at that exact folder, and a
sync command that demands a particular working directory is not one anybody uses. This file carries
absolute paths, so it needs no working directory at all.

**Three outcomes, and only one of them is "done".** It prints a path and exits 0 — written. It
prints nothing and exits 0 — the file was already there and this kit wrote it, so it was left
alone, which is correct and is also *not* a fresh install. It prints a refusal and exits
**non-zero** — a command of that name exists that this kit did not write, most likely the user's
own; nothing was written and nothing was overwritten. **In that third case `/vaultkit` does not
exist for this vault. Say so plainly, tell them their own file keeps the name, and do not list it as
delivered.** There is nowhere else to put it, so the only ways out are their file or a rename.
A quiet non-write reported as success is the failure this kit has paid for most often.

The command exists because the chain below has three traps in it, and a chain typed from memory
hits them: `--vault` means one project after `index` and the vault root after `links`; the
tool folder is a full path, not `06_tools/`; and the sweep is `--root`.
**This is a Claude Code convenience, not a deliverable.** The workflow page in `05_workflows`
carries the same chain in prose, so a user working in a browser loses nothing.

### Verification run — all of it, no exceptions

```bash
python 06_tools/vaultkit.py freshness  --vault <VaultRoot>   # FIRST, and not as a formality
python 06_tools/vaultkit.py index      --vault <Project>     # once per project
python 06_tools/vaultkit.py index      --root  <VaultRoot>
python 06_tools/vaultkit.py links      --vault <VaultRoot>
python 06_tools/vaultkit.py duplicates --vault <VaultRoot>
```

**One file, one front door.** `vaultkit.py` carries every guard as a subcommand; each takes the
arguments it always took and prints what it always printed. **`--vault` still means two different
things** — one project directory after `index`, the vault root after `links` — and no shared parser
papers over that, because the collision is real and the `/vaultkit` command exists to spell it out.
Each subcommand has its own `--help`.

**There is no suite run in this chain, and that is deliberate.** The suites test the tools; the
tools have not changed since setup, and they were tested in the kit's repository before the release
that put them here. What changes every day is the notes, which is what every line above reads.

**The freshness check goes first because every line below it writes to the run log.** Measured
after them, it sees the side effect of this very chain and reports the jobs as fresh — including a
scheduled one that stopped firing a week ago. There is no reading of the order that puts it
anywhere else.

**Red there is a report, not a stop.** It judges the past; the rest of the chain produces the
present. Run every remaining step regardless, carry its numbers into the report below, and do not
fold its verdict into a line that claims the vault is in order — the two answer different questions.

**On the very first setup it is red, and that is correct.** No tool has ever run in this vault, so
the log holds no healthy line for `build_index` or `check_links` and the check reports `0/2`. Say
this out loud before you run it, or the user reads their brand-new vault as broken in its first
minute. Run the chain, then run `vaultkit.py freshness` once more at the end: it now reads the lines
this chain just wrote and reports `2/2`. Observed on the cold run of 2026-07-30 — `0/2` before,
`2/2` after, same vault, nothing repaired in between.

**`vaultkit.py index` is not a read-only measurement — it writes.** Say so before running it, and check
`git status` first so its output is not mistaken for someone else's uncommitted work.

**Then run the index generator a second time and confirm the tree is still clean:**

```bash
python 06_tools/vaultkit.py index --vault <Project>
git status --porcelain          # no generated file may appear here
```

A generator that produces fresh drift on every run is indistinguishable from a clean one after a
single pass, and it turns every later `git status` into noise nobody reads. One extra run settles it.

**What may legitimately appear, and what may not.** The check is about *generated* files: no
`INDEX - *.md` may show up. Two other things can, and neither is a defect:

- **`?? .obsidian/`**, once the user has opened the vault in Obsidian. The folder does not exist
  during setup and is created by the app on first launch. Most of it is worth versioning (see
  SECTION 7) — commit it and the line is gone.
- **Notes the user wrote themselves**, and the index entries that now point at them.

If an `INDEX - *.md` differs after the second run *without* a note having been added, that is real
drift and it stops here. Distinguish the two before reporting: `git diff` on the index file names
the entry that changed, and hashing the file before and after a third run separates "changed because
content changed" from "changes on every run". Both cases occurred on 2026-07-30; only the second
would be a defect.

Then report to the user in exactly this shape:

```
Created:   <folders> · <n> projects · <n> categories
Index:     <n> entries in <m> categories        (exit 0 | defects: …)
Links:     <n>/<m> resolve
Duplicates: <n> flagged
Freshness: <n>/<m> jobs fresh · <k> on demand · <u> unclassified
Commit:    <hash>
Open:      <what is not done, AND what you did not measure>
```

Rules for that report:

- **"Synchronised" appears only when every check is clean.** Otherwise the line names what is
  broken. A success message that also appears on failure is not a message.
- **`Freshness:` is its own line and is printed every time, denominators included** — also when
  everything is fresh, and also when the check went red. It never merges into a line claiming the
  vault is in order: that one is about the state this run just produced, and freshness is about the
  past that led up to it. Folding the two together makes a healthy vault look like proof that the
  scheduler is alive, which is the one thing it cannot show.
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
| `acceptance-test.md` | global bucket, `03_technical_docs` | the fixtures and required behaviour from SECTION 9, repeatable |
| `knowledge-transfer-<Project>.md` | each project, `05_workflows` | the workflow below, one per project |

If there is no global bucket, they go in the first project instead — and say so, so nobody hunts for
them later.

**Create no other notes.** No example notes, no demo content, no page restating a rule that already
has one. An empty category is correct on day one: it still gets its index file, which is what proves
the structure works. Acceptance fixtures live in the throwaway folder from SECTION 9 and are deleted
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

- **New insight that belongs to no larger document** → a new file in `00_Notes/`, filename = the
  insight, frontmatter per SECTION 4. Then rerun the generator — **with `--root <VaultRoot>`, which
  is the one invocation that covers everything.** `--root` walks every project and writes the root
  hub as well; `--vault <Project>` writes that project's indexes and *never* the root hub. Rerun
  only `--vault` after adding a note and the root index keeps yesterday's entry count, with no
  message and a green exit, until someone happens to run `--root`. Measured on a cold run: adding
  one note that way left the root index reading `5 entries` against a vault holding 6.
- **New subsystem or feature** → a page in `03_technical_docs/` in the same commit as the code.
  Numbers on that page are either measured or explicitly marked unmeasured.
- **Point them at the templates, and name the one setting that switches them on.** The generator
  writes `_templates/TEMPLATE - <Project>.md` per project (SECTION 5), but Obsidian does not find
  that folder by itself. Tell the user, once, in these words: *Settings → Core plugins → Templates →
  Template folder location* = `_templates`. After that, `Ctrl+P → Insert template` in a new note
  fills the frontmatter block, with the project name already correct.
  **Do not write `.obsidian/templates.json` for them — and not because it would fail.** It works,
  and it has now been measured three times against Obsidian **1.12.7**, most recently on
  2026-07-30 with a control probe: delete the file with Obsidian closed and the setting comes back
  **empty** on the next start; write it from outside and the setting is **live** on the start after
  that. The file Obsidian writes itself is 28 bytes — `{`, newline, two spaces,
  `"folder": "_templates"`, newline, `}` — UTF-8, LF, **no BOM, no trailing newline**; a byte-identical
  copy written from outside is read the same way. Three things remain untested: the same file *with*
  a BOM, writing it while Obsidian is running, and any other Obsidian version.
  The rule stands on the other reason: `.obsidian/` is the user's application state, and this kit
  does not write into it. Name the setting and let them make it. If they would rather have the
  file than click through Settings, that is theirs to write, with Obsidian closed — one line,
  no BOM: `{"folder": "_templates"}`.
- **Stuck on something?** Search `00_Notes/` first. A past procedure that already fits beats a new
  one you invent now.

---

## SECTION 9 — What each guard is specified to do, and how that was proven

**This section is not a task. It is the specification the shipped guards were held to before this
file was published, and it is here so a changed script can be measured against something.**

Everything a setup does proves the scripts run on clean input. That is the half that cannot fail. A
guard is only worth having if it goes **red on bad input**, and reasoning about the code is not
evidence — so the kit's repository carries `acceptance.py`, which hands each guard one deliberately
broken input and requires it to refuse. It ran before this release: **12/12 checks behaved as
specified**, on Windows 11 with Python 3.13, under PowerShell 5.1 and Git Bash, ten passes each.

**It is not in SECTION 10 and the user does not run it.** It builds and deletes throwaway vaults per
fixture; nothing about a user's notes changes what it measures, so re-running it on their machine
would re-answer a question about this kit's code with the same answer, daily. **If you change a
shipped script, the table below is what your change has to keep true — and you cannot check that
here.** Say so plainly rather than reporting a setup as verified.

The driver takes its verdict from process exit codes and files on disk. Console text wraps at the
terminal width and differs per shell, so **it never stands alone as evidence** — a fixture that only
greps stdout passes a tool which prints the right sentence and does the wrong thing. **Where the
message itself is the specified behaviour, the message is what gets checked** — in addition to the
exit code, never instead of it. Three kinds of row below are that case, and the third is easy to
forget:

- the ones that require the run to **name the file**,
- the ones that require it to **show a denominator**,
- and the ones that require a **particular phrase** — *"did not run"*, *"0 suites collected"*,
  *"adopted"* — **including the requirement to stay silent**, which is a claim about output that
  nothing but the output can settle.

"It is reported" is the requirement, and a guard that goes red without saying which file has not
met it. The driver reads output only where a row below asks it to; fixture 9 carries the reasoning
in its docstring. Anything short of `12/12 checks behaved as specified` is a defect in a script,
not in the expectation.

The table below is what the driver checks, and it is the specification a changed script must still
meet. **Fixtures 0, 9 and 11 require green; every other row requires red** — the healthy control, a
folder the structure allows, and a file the setup itself writes. A suite that only ever sees bad
input is exactly as blind as one that only ever sees good input. The driver counts the two kinds
from the fixture list rather than printing a fixed sentence, so a fixture that changes sides changes
the summary with it.

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
| 9 | a folder made by hand — `<Project>/99_extra/` with one note in it | folder survives, gets its own index containing the note, run exits **0** and **names it on stdout** | either half alone is the failure: red on a folder the structure allows, or green while the note reaches no index — measured on a real setup, a renamed `06_tools` took the count from 21 categories to 20 without a word |
| 10 | note with `project:` naming a different project than its folder, then the agreeing and the absent case | index run exits **non-zero** on the contradiction and names both values; **exit 0 and silent** when the field agrees or is missing | the field reads as if it placed the note, places nothing, and says nothing either way — measured on a real vault before the guard existed: 339 notes, 204 of them carrying `project:`, no run had ever compared one against its folder |
| 11 | run `vaultkit.py command` twice against a vault, hand-editing the command in between, then once more against a file of the same name it did not write | the file appears, spells `--root` and `--vault` as the two different things they are, the run **names it on stdout**; the second run writes nothing and **says nothing**; the foreign file is **named on stderr with a non-zero exit** and is not touched | a tool that writes into a config folder without naming it — the destination can be outside the vault, which is the one place operating rule 5 forbids anything quiet — or, worse, one that returns 0 over a command it never wrote, so the setup reports `/vaultkit` ready while someone else's file holds the name |

The driver leaves nothing behind — every fixture vault lives under the system temp directory and is
deleted in a `finally` block. It was run under **every shell**, not just one: on Windows that means
PowerShell *and* Git Bash, which is where the encoding defect in SECTION 6 shows up and is invisible
from inside a single shell.

### What this means for the vault you are setting up

- **Write the specification into the vault as `03_technical_docs/acceptance-test.md`** — the table
  above, each fixture and the behaviour it requires, plus the sentence that it was measured in the
  kit's repository rather than here. Whoever inherits the vault then knows what the guards promise
  and where that promise was tested. A specification that lives only in a conversation cannot be
  used by anyone.
- **If a guard is ever changed on this machine, the release measurement stops describing it.** There
  is no driver in the tool folder to re-run, so the honest report is "changed, and no longer covered
  by the measurement quoted in SECTION 0" — never a repeated number. Quoting a figure measured
  against code that no longer exists is the failure this whole section is written to prevent.
- **A guard that passes bad input is worse than no guard**, because it will be cited as evidence.
  Fix the script against the table; do not adjust the expectation.

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

#### Shared

### `jobs.json`

```json
{
  "_comment": "Three lists, and a name belongs to exactly one of them. \"jobs\" must show a healthy run inside the threshold -- these are the ones a dead scheduler would silently take with it. \"on_demand\" logs like everything else but is never late, because it runs when someone asks. \"not_invoked\" is not called by any chain at all, and the value says why. A name in two of them stops the tool with exit 2. A name in none is reported, never guessed at. Verify with: python vaultkit.py freshness --vault <VaultRoot>",
  "jobs": ["build_index", "check_links"],
  "on_demand": {
    "check_duplicates": "runs in the verification chain and by hand, never on a schedule",
    "write_command": "runs once during setup, and again only if the command file is gone",
    "check_freshness": "this job itself -- logged, never watched: an age limit on the watcher is a regress"
  },
  "not_invoked": {
    "_comment": "Empty since 2026-07-31, and the key stays for YOUR tools. Its three entries were vault_paths and _testkit -- modules, and neither is a file any more -- and count_tokens, which the register in vaultkit.py now excuses itself by carrying no job name. Put a tool of your own here when it logs but no chain calls it, with the reason: JSON has no comments, so the value is the reason."
  }
}
```

#### Tools

### `vaultkit.py`

```python
"""Every guard this vault runs, in one file: `vaultkit.py <subcommand> …`.

    vaultkit.py index      --root <VaultRoot> | --vault <Project>
    vaultkit.py links      --vault <VaultRoot>
    vaultkit.py duplicates --vault <VaultRoot>
    vaultkit.py freshness  --vault <VaultRoot>
    vaultkit.py tokens     <path> …
    vaultkit.py command    --vault <VaultRoot>

Each subcommand takes exactly the arguments the tool behind it always took and prints exactly
what it always printed. **The job names in `runs.log` do not move by a single byte** -- every
logging call passes a string literal, none of them changed, and `jobs.json` stays valid.

WHY ONE FILE (2026-07-31): a user's tool folder held twenty-two files, of which they were told
to run six. Every one of those was a separate block in the kit file a stranger drags into a
Claude conversation, and every block is context that conversation carries before it writes
anything. The measured cost of the split was never runtime -- it was the cold run.

The size was the open question and it is answered: a probe carrying this file's shape, 1683
lines and 68.6 KiB, went through a fresh session and came back byte-identical -- same sha256,
all 34 markers, no BOM, no CRLF. That is three times the largest block the old delivery had.

WHAT THIS FILE IS NOT ALLOWED TO SWALLOW. `upgrade.py` stays outside. If its own write breaks
off, it is the only tool left that can repeat the attempt, and folding it in here would make the
repair depend on the thing being repaired.

Read it in sections: the shared floor first -- every generated filename and the run log -- then
one section per subcommand, each opening with the tool's own documentation, unchanged from when
it was a file of its own. The register at the very end says which subcommand runs what.
"""

import sys

# BEFORE ANY WORK, AND BEFORE THE IMPORTS THAT WOULD SUCCEED ANYWAY (2026-07-31). The floor is
# 3.10 and it comes from exactly one thing: `Path.write_text(newline=…)`, used five times in
# this file. Below that version every one of those raises TypeError -- and it raises when the
# tool WRITES, not when it starts. For `index` that is after the whole note tree has been read
# and half the index rebuilt, with a message that says nothing about Python versions. A user
# would go looking at their notes.
#
# Checked here rather than in a function, because a function is something you can forget to call.
if sys.version_info < (3, 10):
    have = ".".join(str(part) for part in sys.version_info[:3])
    print(f"vaultkit.py needs Python 3.10 or newer; this is {have}. Nothing was read or "
          f"written. The floor is Path.write_text(newline=…), which every generated file goes "
          f"through -- on an older Python the first symptom would be a TypeError halfway "
          f"through a run, naming nothing that points here.", file=sys.stderr)
    # The literal, not EXIT_USAGE: this runs before the constants below are defined, and a
    # NameError here would replace the one message that explains what is wrong.
    raise SystemExit(2)

import argparse
import json
import re
from collections import defaultdict
from collections.abc import Callable
from datetime import date, datetime, timezone
from itertools import combinations
from pathlib import Path
from urllib.parse import quote

for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass

# The three verdicts, named once. Every subcommand returns one of them and `main()` hands it
# straight to the shell, so these are what a chain, a CI step or a `/vaultkit` run reads.
#
# THE MEANINGS, WRITTEN DOWN RATHER THAN INFERRED FROM EXAMPLES -- src/contract.md SECTION 6
# carries the same three sentences, because a user who has to derive them from thirty return
# statements will derive them differently:
#
#   0  clean. The check ran over a real population and found nothing wrong.
#   1  a defect, OR "did not run" -- the run could not reach a verdict. Both are "do not trust
#      this vault yet", and both are things the user fixes by changing notes or by running
#      something. `duplicates` is the one deliberate exception: too few notes to compare is the
#      normal state of a fresh vault, so it returns 0. That exception is in the contract.
#   2  the ARGUMENTS or the SOURCES are wrong, not the vault: an unknown subcommand, a path that
#      is not a directory, or two config lists that contradict each other. Nothing was measured,
#      so nothing about the vault is being claimed.
EXIT_OK = 0
EXIT_DEFECT = 1
EXIT_USAGE = 2

# THE ONE CONTRACT THAT CROSSES A FILE BOUNDARY, so it is the one thing here that is typed.
# `upgrade.py --prove` imports this module, reads COMMANDS and requires every `run` in it to be
# callable; that is the entire surface between the two delivered scripts. Everything else in
# this file has one caller a few hundred lines away, and a signature there states nothing two
# parties have to agree on.
#
# A handler takes the arguments left after the subcommand name -- `None` means "read sys.argv",
# the way argparse does it -- and returns one of the three exit codes above. Nothing else.
Handler = Callable[[list[str] | None], int]

# One entry per subcommand: what runs it, and the job name it writes into runs.log. `job` is
# `str | None`, and the None is a statement rather than a gap -- see the register at the end.
Command = dict[str, Handler | str | None]

# ---------------- shared: paths, names and the run log   (was vault_paths.py)
"""Single source of truth for every generated filename and every path rule.

Spelling a generated filename a second time in another tool is how a guard ends up
reporting the index hub as "missing" while the hub sits right next to it. Every tool
imports from here instead.
"""

# The category folders every project gets when it is created. Numeric prefixes exist for sort
# order only; 01 is deliberately unused, closing the gap would rename every index file.
CATEGORY_FOLDERS = [
    "00_Notes",
    "02_docs",
    "03_technical_docs",
    "04_feedback",
    "05_workflows",
    "06_tools",
]

# The one directory at the vault root that is written by a tool and is still not a project: it
# holds one note template per project. Named with a leading underscore so it sorts above the
# projects in Obsidian's file pane.
TEMPLATES_DIR = "_templates"

# Directories that are never notes and never walked. _templates belongs here for two reasons at
# once: without it the folder becomes a project with six category folders of its own, and the
# templates inside would be read as notes and go red for having no summary.
#
# `.claude` is the agent's own configuration, the same class as `.obsidian`, and it holds the
# `/vaultkit` command write_command.py writes. Measured 2026-07-29 before it was listed: writing
# that one file took check_links.py from 26 files scanned to 27, check_duplicates.py from 4 notes
# to 5 and from 6 pairs to 10, and the generator from 26 distinct filenames to 27. Nothing went
# red -- the vault simply began counting its own configuration as knowledge, which is worse,
# because every denominator it reports is then slightly wrong and nobody has a reason to look.
SKIP_DIRS = {".git", ".obsidian", ".claude", "__pycache__", ".trash", ".venv", "node_modules",
             TEMPLATES_DIR}

# Characters Obsidian cannot carry inside a [[wikilink]] target.
FORBIDDEN_LINK_CHARS = set("#[]|^")

# Append-only log of every tool run, healthy ones included. Read by check_freshness.py.
RUN_LOG_RELPATH = Path("00_Global") / "06_tools" / "runs.log"


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


def template_name(project_name: str) -> str:
    """'TEMPLATE - <Project>.md' — one note template per project.

    Same shape as the index filenames on purpose: they sort together in the file pane, and
    the name says which project the template writes into its `project:` line.
    """
    return f"TEMPLATE - {project_name}.md"


def template_text(project_name: str) -> str:
    """The four fields every note actually carries -- not the whole contract.

    `{{title}}` and `{{date}}` are two of the three variables Obsidian's core Templates plugin
    knows -- the third is `{{time}}` and has no field here. So the title comes from the filename
    (the convention is that the filename carries the title) and the date fills itself. Only
    `project:` is written in, which is the one value a template can get right that a person
    retyping the block gets wrong.

    WHY `updated`, `issues`, `generator`, `retired` and `stale` ARE NOT HERE: they are
    situational -- set when something happened, not when a note is started. `generator:` is the
    one that must never sit in a template waiting to be filled: a note carrying it is declared
    derived, and a rebuild is then entitled to overwrite or delete it. Nothing is hidden by
    leaving them out -- Obsidian's "Add property" offers every field already used anywhere in the
    vault. The CONTRACT (SECTION 4) still defines all nine; the template is not the contract.
    """
    return (
        "---\n"
        'title: "{{title}}"\n'
        "summary:\n"
        f'project: "{project_name}"\n'
        "created: {{date}}\n"
        "---\n"
    )


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


# The third outcome, spelled once. `pass` and `fail` are exit codes; this is the one a checker
# has to say in words, because "0 broken links" and "0 links looked at" are the same number.
#
# THE PHRASE IS LOAD-BEARING, NOT DECORATION. src/contract.md requires it, acceptance fixture 8
# greps for it, and four suites assert it. Changing the wording is a contract change and moves
# five sources at once -- which is exactly why it is a constant now and was four spellings
# before.
DID_NOT_RUN = "did not run"


def did_not_run(reason: str, stream=None) -> None:
    """Say that a check could not reach a verdict, and why. One wording, five callers.

    `stream` defaults to stderr, where every defect goes. `duplicates` passes stdout on purpose
    and is the only one that does: it is also the only caller that returns 0 afterwards -- too
    few notes to compare is the normal state of a fresh vault, not a defect -- so its line
    belongs with the denominators rather than with the failures. That asymmetry is asserted in
    two suites, one on `out` and three on `err`, so it cannot be tidied away by accident.

    `freshness` also says it once per job, in a different shape (`<job>: did not run — why`),
    and those two lines use DID_NOT_RUN directly rather than this function. MEASURED WHY THAT
    MATTERS, 2026-07-31: with the five headlines routed through here but those two still
    spelling the phrase out, acceptance stayed 12/12 when the wording was changed -- fixture 8
    was being satisfied by a per-job line, not by the headline it means to read. Consolidating
    five of seven spellings looks finished and leaves the guard reading the wrong one.
    """
    print(f"{DID_NOT_RUN}: {reason}", file=stream or sys.stderr)


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
        # newline="\n": the only writer in this kit that lacked it, so runs.log was the one
        # generated file whose line endings depended on the platform that wrote it. The reader
        # (check_freshness.py) opens in universal-newline mode and copes either way, which is
        # exactly why nothing went red over it -- a log half CRLF and half LF from two different
        # machines is a diff nobody can read, not a run that fails.
        with open(log_path, "a", encoding="utf-8", newline="\n") as fh:
            fh.write(line)
    except OSError as exc:
        print(f"run log not written: {exc}", file=sys.stderr)

# ----------------------------------- vaultkit.py index   (was build_index.py)
"""Generate the three-level index tree from note frontmatter.

    <VaultRoot>/INDEX - <VaultName>.md                   one line per project     --root
    <Project>/INDEX - <Project>.md                       one line per category    --vault <dir>
    <Project>/<Folder>/INDEX - <Project> <Category>.md   the entries themselves

Reads FRONTMATTER ONLY. There is no code path in this file that opens a note body, which
is the structural guarantee that prose can never leak into the index.

It also owns the shape of a project: a project folder that is missing category folders gets
them, and a folder the user made by hand becomes a category of its own. Both are printed --
they change the tree, and a run that changes the tree silently is the failure this whole
file exists to prevent. Neither is a defect.

Exit code is 0 only when every entry was clean. Otherwise each defect is printed as
"<filename>: <what is wrong>" on stderr and the exit code is non-zero.
"""

TITLE_MAX = 90
SUMMARY_MAX = 150

HEADER = """# {name} — Index

> Generated by `06_tools/vaultkit.py index` from note frontmatter.
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
        # utf-8-sig, not utf-8: a byte-order mark survives str.strip() -- "﻿".isspace()
        # is False -- so the opening '---' of a note written by a Windows editor fails this
        # test. The note then reads as having no frontmatter at all: its title and summary
        # are gone from the index and the run goes red over a file the user wrote correctly.
        # utf-8-sig drops a BOM if there is one and behaves like utf-8 if there is not.
        with open(path, "r", encoding="utf-8-sig", errors="replace") as fh:
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
    name = Path(target_path).name
    try:
        rel = Path(target_path).resolve().relative_to(Path(vault_root).resolve()).as_posix()
    except ValueError:
        # A junction or symlink inside the vault whose target resolves outside the root.
        # relative_to() raises there, and this used to leave the function as a traceback -- so
        # the run died before log_run() at the end of index_main(), which is the one outcome this kit
        # forbids: silence has to mean "did not run". There is no link to write either way (a
        # [[wikilink]] needs a vault-relative path and there is none), so the label goes in as
        # plain text and the defect line carries the reason.
        defects.add(name, "resolves outside the vault root — not linkable "
                          "(a junction or symlink pointing out of the vault?)")
        return label
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
    # Resolved once, not per note: Path('.').name is the empty string, and every note in the
    # folder would then be reported as disagreeing with a project called "".
    project_name = Path(project_dir).resolve().name
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

        # 'project:' is advisory -- the folder decides where a note is indexed, and nothing here
        # reads this field to place anything. Absent, it means nothing and stays silent. Present
        # and disagreeing, it is two sources claiming different things while only one of them
        # acts, which is the defect: the note is indexed under the folder and the frontmatter
        # says otherwise, forever, with no message. Compared exactly, case included -- the folder
        # name IS the project name and goes into every wikilink as it stands.
        declared = fm.get("project", "").strip()
        if declared and declared != project_name:
            defects.add(name, f"'project: {declared}' disagrees with the folder "
                              f"({project_name}) — the folder decides where a note is indexed")

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


def write_if_changed(path, content, defects):
    """Write only on a real change, so a rerun leaves `git status` empty.

    THE WRITE IS INSIDE A try, AND THAT IS THE WHOLE POINT (2026-07-31). It used to sit outside
    one, so a read-only or locked INDEX file -- a vault on OneDrive is not a theoretical case --
    raised PermissionError out of here and took the run down BEFORE log_run() at the end of
    index_main(). The result was half an index tree AND not one line in runs.log: not `defects`, not
    `did-not-run`, nothing at all. Silence is the one thing that has to keep meaning "did not
    run", and a crash on the way to the log turns it into a lie.

    Two try blocks, not one, and the split is deliberate: a file that cannot be READ may still be
    writable, and overwriting it is the repair. Merging them would turn that case into a defect
    and skip the write that would have fixed it.

    Measured on this machine 2026-07-31, on a copy of a real vault (491 .md), with `attrib +R` on
    `Horus-F5Tts-Onnx/00_Notes/INDEX - Horus-F5Tts-Onnx Notes.md` -- the third project of seven,
    so most of the tree comes before it:

      before   PermissionError traceback · 46 of 61 index files written · runs.log absent
      after    exit 1 · the filename on stderr · 61 of 61 written · `build_index defects` logged
      unlock   `attrib -R`, rerun: exit 0, tree complete
      again    third run writes nothing, `git status` stays empty

    The reset path is the point of quoting the numbers: `attrib -R` on the same file puts the
    copy back, so anyone can rerun this without guessing what state it left behind.
    """
    path = Path(path)
    try:
        if path.exists() and path.read_text(encoding="utf-8") == content:
            return False
    except OSError:
        # Unreadable, possibly writable. Fall through to the write, which is the repair.
        pass
    try:
        path.write_text(content, encoding="utf-8", newline="\n")
    except OSError as exc:
        defects.add(path.name, f"not written ({exc})")
        return False
    return True


def scaffold(project_dir, defects):
    """Create the category folders this project is missing. Returns the names created.

    A project folder a user makes in the file pane is empty. Leaving it that way means the
    user has to know the six names and type them correctly before anything they write is
    indexed -- so the run creates them instead, and says which ones it made.
    """
    created = []
    for folder_name in CATEGORY_FOLDERS:
        folder = project_dir / folder_name
        if folder.is_dir():
            continue
        try:
            folder.mkdir(parents=True, exist_ok=True)
        except OSError as exc:
            defects.add(f"{project_dir.name}/{folder_name}", f"category folder not created ({exc})")
            continue
        created.append(folder_name)
    return created


def project_categories(project_dir):
    """Every category of this project: the configured ones first, then the hand-made ones.

    CATEGORY_FOLDERS is what a project is *created* with, not the only thing it may hold.
    A folder the user adds themselves is a category they meant to have, so it is adopted and
    indexed like any other. Returns (folder_names, adopted_names).

    The alternative -- calling an unknown folder a defect -- was the behaviour up to here, and
    it made the run red for a user doing something the structure explicitly allows. What must
    not happen is the *silent* version: a renamed 06_tools once took a real run from 21
    categories to 20 with exit 0 and no message, and every note in it was simply gone from
    every index. Adoption keeps those notes indexed; index_main() prints the folder either way.
    """
    known = set(CATEGORY_FOLDERS)
    adopted = []
    for child in sorted(project_dir.iterdir()):
        if not child.is_dir() or child.name.startswith(".") or child.name in SKIP_DIRS:
            continue
        if child.name not in known:
            adopted.append(child.name)
    return CATEGORY_FOLDERS + adopted, adopted


def build_project(vault_root, project_dir, defects):
    """Write every category index plus the project hub.

    Returns (entries, categories, created, adopted) -- the last two are folder names, and index_main()
    prints them. A run that creates a folder and does not say so is a run that changed the tree
    behind the user's back.
    """
    project_dir = Path(project_dir).resolve()
    project_name = project_dir.name
    today = date.today().isoformat()
    total_entries = 0
    category_rows = []

    created = scaffold(project_dir, defects)
    folder_names, adopted = project_categories(project_dir)

    for folder_name in folder_names:
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
        write_if_changed(folder / category_index_name(project_name, folder_name),
                         "\n".join(lines), defects)
        category_rows.append((folder_name, len(entries)))

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
    write_if_changed(project_dir / project_index_name(project_dir), "\n".join(lines), defects)
    return total_entries, len(category_rows), created, adopted


def write_templates(vault_root, projects, defects):
    """One note template per project under <VaultRoot>/_templates/. Returns what it created.

    CREATED WHEN MISSING, NEVER OVERWRITTEN. A template exists to be edited -- a user adds the
    fields their vault actually uses -- and a tool that rewrites it on every run eats that edit
    without saying so. The doctrine rule that generated files are not hand-edited covers the
    index tree; _templates is deliberately not part of it, which is why it is written once and
    then left alone.

    THE SAME FAILURE MODE write_if_changed() HAD, AND THE SAME REPAIR. This runs at the very end
    of build_root(), so a read-only `_templates` folder raised OSError here and took the run down
    on the last step before log_run() -- a complete index tree, and still not one line in
    runs.log saying the run happened. A missing template is a defect, not a reason to lose the
    record of everything that did work.
    """
    folder = Path(vault_root).resolve() / TEMPLATES_DIR
    written = []
    for project in projects:
        target = folder / template_name(project.name)
        if target.exists():
            continue
        try:
            folder.mkdir(parents=True, exist_ok=True)
            target.write_text(template_text(project.name), encoding="utf-8", newline="\n")
        except OSError as exc:
            defects.add(target.name, f"note template not written ({exc})")
            continue
        written.append(target.name)
    return written


def build_root(vault_root, defects):
    vault_root = Path(vault_root).resolve()
    today = date.today().isoformat()
    lines = [HEADER.format(name=vault_root.name, today=today)]
    total_entries = 0
    total_categories = 0
    created_all = []
    adopted_all = []
    projects = project_dirs(vault_root)
    for project in projects:
        entries, categories, created, adopted = build_project(vault_root, project, defects)
        total_entries += entries
        total_categories += categories
        created_all += [f"{project.name}/{n}" for n in created]
        adopted_all += [f"{project.name}/{n}" for n in adopted]
        target = project / project_index_name(project)
        lines.append(
            f"- {link_to(vault_root, target, project.name, defects)} "
            f"— {entries} entries in {categories} categories"
        )
    lines.append("")
    lines.append(f"_{len(projects)} projects · {total_entries} entries in {total_categories} categories._")
    lines.append("")
    write_if_changed(vault_root / root_index_name(vault_root), "\n".join(lines), defects)
    templates = write_templates(vault_root, projects, defects)
    return len(projects), total_entries, total_categories, created_all, adopted_all, templates


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


def index_main(argv: list[str] | None = None) -> int:
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
            return EXIT_USAGE
        projects, entries, categories, created, adopted, templates = build_root(vault_root, defects)
        names = check_unique_basenames(vault_root, defects)
        print(f"{entries} entries in {categories} categories · {projects} projects · {names} distinct filenames")
    else:
        project_dir = Path(args.vault).resolve()
        if not project_dir.is_dir():
            print(f"not a directory: {project_dir}", file=sys.stderr)
            return EXIT_USAGE
        vault_root = project_dir.parent
        entries, categories, created_names, adopted_names = build_project(vault_root, project_dir, defects)
        created = [f"{project_dir.name}/{n}" for n in created_names]
        adopted = [f"{project_dir.name}/{n}" for n in adopted_names]
        # Templates are written by the root run only: it is the one invocation that knows every
        # project, and _templates sits at the vault root, not inside a project.
        templates = []
        names = check_unique_basenames(vault_root, defects)
        print(f"{entries} entries in {categories} categories · {project_dir.name} · {names} distinct filenames")

    # Neither of these is a defect -- the run does exactly what the structure allows. Both change
    # or extend the tree, so both are said out loud. A typo'd folder name shows up here as a
    # category the user did not mean to have, which is the only warning that case ever gets.
    for name in created:
        print(f"  created  {name} — category folder was missing")
    for name in adopted:
        print(f"  adopted  {name} — folder made by hand, indexed as a category")
    for name in templates:
        print(f"  template {TEMPLATES_DIR}/{name} — note template written once; edit it freely, "
              f"no run overwrites it")

    if defects.skipped:
        print(f"skipped {defects.skipped} unreadable files", file=sys.stderr)

    status = "ok" if not defects else "defects"
    log_run(vault_root, "build_index", status,
            f"{len(defects)} defects · {len(created)} created · {len(adopted)} adopted · "
            f"{len(templates)} templates")

    if defects:
        defects.report()
        print(f"{len(defects)} defects", file=sys.stderr)
        return EXIT_DEFECT
    return EXIT_OK

# ------------------------------- vaultkit.py command   (was write_command.py)
"""Write a `/vaultkit` slash command for Claude Code, with this vault's real paths already in it.

The verification chain in SECTION 8 is six commands with three traps in them, and every one of
the three was hit on a real run:

  1. `--vault` means two different things. `links` wants the vault ROOT, `index` wants ONE
     PROJECT, `duplicates` takes either. Typing the same path after every `--vault` is wrong in
     two places out of three -- and folding the guards into one `vaultkit.py` did not remove
     that, it only put the collision inside one file. Each subcommand keeps its own parser.
  2. The tool folder is `<VaultRoot>/00_Global/06_tools/`, not `06_tools/`. A relative prefix is
     an invitation to run it from a directory where it does not resolve.
  3. `--root`, not `--vault`, for the sweep. Rerunning only `--vault` after adding a note leaves
     the root index on yesterday's count -- green, silent, and wrong. Measured on a cold run:
     one added note left the root index reading 5 entries against a vault holding 6.

There is a fourth thing the file gets right and a typed chain cannot: ORDER. `freshness` stands
first, because every other step appends an `ok` line and a freshness check measured after them
reports the side effect of its own chain as health.

A command file removes all three by spelling out the answers once, per vault, with the paths
filled in. It is a convenience for Claude Code and nothing depends on it: the workflow page in
`05_workflows` carries the same chain in prose for anyone working in a browser.

    python write_command.py --vault <VaultRoot> --shell powershell
    python write_command.py --vault <VaultRoot> --shell posix

THE DESTINATION IS ALWAYS `~/.claude/commands/vaultkit.md`, AND THERE IS NO OPTION. An in-vault
copy under `<VaultRoot>/.claude/commands/` was offered once and taken out again: it fires only in
a session started at the vault root, and a sync command that demands a particular working
directory is not one anybody uses. The file holds absolute paths, so it needs no cwd at all.

CREATED WHEN MISSING, NEVER OVERWRITTEN, same as the note templates. A command file is there to
be edited -- the user adds their own steps -- and a tool that rewrites it every run eats that
edit without saying so.

TWO KINDS OF "IT IS ALREADY THERE", AND THEY GET OPPOSITE ANSWERS. A file this tool wrote before
is not news: nothing is printed, exit 0, exactly like the note templates. A file it did NOT write
is a stranger holding the name -- most likely in `~/.claude/commands/`, where a `/vaultkit` of the
user's own may already live. That case is named on stderr and exits non-zero, because a silent
zero would let the setup report `/vaultkit` as ready while the user's own command still owns the
name. A quiet non-write that looks like success is the most expensive failure class this kit has
on record.

The two are told apart by the marker line the generated file carries, never by mtime and never by
a state file beside it: both of those answer "when", and the question is "whose".

Undo recipe for that guard, re-measured on this machine 2026-07-29 after the stranger case was
added: copy tools/ somewhere, make the `if target.exists():` block in command_main() unreachable,
and run the three drivers there -- test_write_command 8/12, acceptance 11/12, verify_setup 14/15.
"""

TOOLS = Path(__file__).resolve().parent
sys.path.insert(0, str(TOOLS))

for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass


COMMAND_NAME = "vaultkit"

DESCRIPTION = ("Rebuild this vault's index and run every guard, in the order that leaves "
               "nothing stale")

# How a run tells its own file from a stranger's with the same name. Deliberately not a state
# file and not an mtime heuristic: both answer "when", and the question is "whose".
#
# It sits on the first line of the BODY, not of the file. YAML frontmatter has to start at byte
# zero -- a comment in front of it and `description:` is either lost or the command does not load
# at all. That was not measured here, and a marker that breaks the thing it marks is not a marker.
MARKER_PREFIX = "<!-- vaultkit:"


def marker(vault_root):
    return f"{MARKER_PREFIX} {Path(vault_root).resolve().as_posix()} -->"


def written_by_us(path):
    """True when this file came out of this tool. The vault path inside is informative only --
    a vault that moved is still our file, and re-checking the path would call it a stranger."""
    try:
        head = path.read_text(encoding="utf-8-sig")[:2000]
    except OSError:
        return False
    return MARKER_PREFIX in head


def show(path, shell):
    """A path as the user's own shell writes it.

    Cosmetic, and deliberately so: Python takes forward slashes on Windows too, so nothing here
    breaks if it is wrong. It is done because a command file that spells paths in a foreign
    syntax reads as though it were meant for someone else's machine.
    """
    text = Path(path).as_posix() if shell == "posix" else str(Path(path)).replace("/", "\\")
    return f'"{text}"'


def command_text(vault_root, projects, shell):
    vault_root = Path(vault_root).resolve()
    tools = vault_root / "00_Global" / "06_tools"

    # ONE ENTRY POINT, SPELLED ONCE. Every step below is `vaultkit.py <sub>`, so the chain the
    # user reads has one path in it instead of six -- and a step that named a tool the delivery
    # no longer carries cannot happen by editing five lines and forgetting the sixth. It did:
    # this file went on emitting a "Run the suites" step with `run_suites.py` after that tool
    # left the delivery, and nothing read this text, so no run said so.
    kit = show(tools / "vaultkit.py", shell)

    root = show(vault_root, shell)
    lines = [
        "---",
        f"description: {DESCRIPTION}",
        "---",
        "",
        marker(vault_root),
        "",
        f"Synchronise the Obsidian vault at {root} completely. Its tools are in "
        f"{show(tools, shell)} — the full path, because `06_tools/` alone resolves only from the "
        f"vault root and nowhere else.",
        "",
        "Run every step below, in this order, and report what each one printed — with its "
        "numbers. Name any step you did not run; an unmeasured step and a passing one look "
        "identical from the outside.",
        "",
        "**Before you start:** the index steps write. Say so, and check `git status` first, so "
        "their output is not mistaken for someone else's uncommitted work.",
        "",
        "## 1 · Read the run log before anything writes to it",
        "",
        "**First, and the order is the whole point.** Every step below appends an `ok` line to "
        "the run log. Measured after them, this check sees the side effect of the very chain it "
        "belongs to and reports the jobs as fresh — including one that stopped firing a week "
        "ago.",
        "",
        "**Red here is a report, never a reason to stop.** It judges the past; the rest of this "
        "chain produces the present. Carry its numbers into the report and run the other steps "
        "either way.",
        "",
        f"- `python {kit} freshness --vault {root}`",
        "",
        "## 2 · Index each project",
        "",
        "`--vault` here means ONE PROJECT DIRECTORY, not the vault root. One line per project:",
        "",
    ]
    for project in projects:
        lines.append(f"- `python {kit} index --vault {show(project, shell)}`")
    lines += [
        "",
        "## 3 · Index the vault root",
        "",
        "`--root`, not `--vault`. This is the one invocation that walks every project *and* "
        "writes the root hub. Running only step 1 after adding a note leaves the root index "
        "holding yesterday's entry count, with no message and a green exit — measured on a cold "
        "run: one added note left it reading `5 entries` against a vault holding 6.",
        "",
        f"- `python {kit} index --root {root}`",
        "",
        "## 4 · Check the links",
        "",
        "`--vault` here means THE VAULT ROOT — the same flag, the other meaning. The project "
        "hubs link back to the root index, so anything narrower reports a broken link that is "
        "not broken:",
        "",
        f"- `python {kit} links --vault {root}`",
        "",
        "## 5 · Check for duplicates",
        "",
        "`--vault` here takes either the root or a single project:",
        "",
        f"- `python {kit} duplicates --vault {root}`",
        "",
        "## 6 · Prove the second run changes nothing",
        "",
        "A generator that drifts on every run is indistinguishable from a clean one after a "
        "single pass, and it turns every later `git status` into noise nobody reads.",
        "",
        f"- `python {kit} index --root {root}`",
    ]
    # The git line is written only into a vault that has a repository. SECTION 7 recommends git
    # and step 2 of verify_setup requires it, but a user may still have declined -- and a command
    # that ends in a line failing every single time teaches them to skip the last step.
    if (vault_root / ".git").is_dir():
        lines.append(f"- `git -C {root} status --porcelain`  — must print nothing")
    else:
        lines.append("- Compare the index files before and after by hand: this vault has no git "
                     "repository, so there is nothing that can answer the question for you. "
                     "Setting one up (see the workflow page) makes this one command.")
    lines += [
        "",
        "## Report",
        "",
        "One line per step, each with its denominator. `Open:` lists what you did **not** "
        "measure, not only what is unfinished.",
        "",
    ]
    return "\n".join(lines)


def target_path():
    """Always the user's own commands folder. No parameter, because there is no second answer.

    Taking a vault root here would keep the door open for an in-vault copy, and that copy is
    exactly what was removed: it loads only in a session started at the vault root.
    """
    return Path.home() / ".claude" / "commands" / f"{COMMAND_NAME}.md"


def command_main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--vault", required=True, help="vault root")
    parser.add_argument("--shell", choices=("powershell", "posix"), default="powershell",
                        help="the syntax the paths are written in")
    args = parser.parse_args(argv)

    vault_root = Path(args.vault).resolve()
    if not vault_root.is_dir():
        print(f"not a directory: {vault_root}", file=sys.stderr)
        return EXIT_USAGE

    target = target_path()
    projects = project_dirs(vault_root)
    if not projects:
        # Not a silent skip: a vault with no projects means the wrong path was given, and a
        # command file listing no projects would be a working file that does nothing.
        print(f"no projects under {vault_root} — nothing to write a command for", file=sys.stderr)
        return EXIT_DEFECT

    if target.exists():
        if written_by_us(target):
            # Ours from a previous run, possibly hand-edited since. Nothing to say.
            log_run(vault_root, "write_command", "ok", f"{target} already ours · nothing written")
            return EXIT_OK
        # Someone else's file under the name we wanted. Nothing is overwritten and nothing is
        # written either -- and a silent zero here is the most expensive answer in this kit,
        # because the setup would report /vaultkit as ready while the user's own command still
        # holds the name.
        print(f"{target} already exists and was not written by this kit — nothing written.\n"
              f"  It carries no `{MARKER_PREFIX} … -->` line, so it is your own command of the "
              f"same name, and it keeps the name.\n"
              f"  Rename or remove your own file and run this again; there is no second location "
              f"to fall back to, because a command anywhere else would not load.",
              file=sys.stderr)
        log_run(vault_root, "write_command", "blocked", f"{target} held by a foreign command")
        return EXIT_DEFECT

    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(command_text(vault_root, projects, args.shell),
                      encoding="utf-8", newline="\n")
    print(f"wrote {target} — /{COMMAND_NAME} covers {len(projects)} projects; "
          f"edit it freely, no run overwrites it")
    log_run(vault_root, "write_command", "ok", f"{target} written · {len(projects)} projects")
    return EXIT_OK

# ----------------------------------- vaultkit.py links   (was check_links.py)
"""Check that every [[wikilink]] in the vault resolves to a file.

Reports numerator AND denominator, and distinguishes three outcomes: pass, fail, and
"did not run". A checker that scanned zero files must never report "0 broken".
"""

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


def links_main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--vault", required=True, help="vault root")
    args = parser.parse_args(argv)

    vault_root = Path(args.vault).resolve()
    if not vault_root.is_dir():
        print(f"not a directory: {vault_root}", file=sys.stderr)
        return EXIT_USAGE

    table = linkable_files(vault_root)
    files = walk_markdown(vault_root)
    scanned = 0
    skipped = 0
    total = 0
    broken = []

    for path in files:
        try:
            # utf-8-sig: FENCE anchors at ^\s* and a byte-order mark is not \s, so a note that
            # opens with a code fence loses fence detection on its first line. Every wikilink
            # inside that block is then reported broken -- the note is right, the guard is
            # wrong, and that is the expensive way round.
            text = path.read_text(encoding="utf-8-sig", errors="replace")
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
        did_not_run(f"0 of {len(files)} markdown files scanned")
        log_run(vault_root, "check_links", "did-not-run", "0 files scanned")
        return EXIT_DEFECT

    resolved = total - len(broken)
    print(f"{resolved}/{total} wikilinks resolve · {scanned} files scanned · {skipped} skipped")

    status = "ok" if not broken and not skipped else "defects"
    log_run(vault_root, "check_links", status, f"{resolved}/{total} resolve")

    if broken:
        for path, raw in broken:
            # Path relative to the vault, not the bare filename: every project has an
            # INDEX and a knowledge-transfer page, so a name alone does not say which one.
            print(f"{path.relative_to(vault_root).as_posix()}: [[{raw}]] resolves to nothing",
                  file=sys.stderr)
        print(f"{len(broken)} broken wikilinks", file=sys.stderr)
        return EXIT_DEFECT
    if skipped:
        print(f"{skipped} files skipped — denominator incomplete", file=sys.stderr)
        return EXIT_DEFECT
    return EXIT_OK

# ------------------------- vaultkit.py duplicates   (was check_duplicates.py)
"""Flag notes whose content overlaps, so one insight does not end up living in two files.

Every hit gets a decision: a flagged pair makes the run red. Ignoring it is not an option
the tool offers.

The threshold is a knob, not a truth. On a vault with a handful of notes the number this
prints is arithmetic, not evidence — recalibrate once there is real volume:

    python check_duplicates.py --vault <dir> --threshold 0.75
"""

DEFAULT_THRESHOLD = 0.75
SHINGLE = 5
WORD = re.compile(r"[^\W\d_]+", re.UNICODE)


def body_shingles(path):
    """Word 5-grams of the note body. Frontmatter is skipped — it is metadata, not content."""
    # utf-8-sig: a BOM makes startswith("---") false, the frontmatter is then compared as if
    # it were body text, and its words dilute the overlap. Measured on this machine: an
    # identical-body pair went 1 flagged of 6 compared without a BOM to 0 of 6 with one.
    text = path.read_text(encoding="utf-8-sig", errors="replace")
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


def duplicates_main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--vault", required=True, help="vault root or a single project directory")
    parser.add_argument("--threshold", type=float, default=DEFAULT_THRESHOLD)
    args = parser.parse_args(argv)

    root = Path(args.vault).resolve()
    if not root.is_dir():
        print(f"not a directory: {root}", file=sys.stderr)
        return EXIT_USAGE

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
        did_not_run(f"{len(comparable)} comparable notes — a pair needs two "
                    f"(threshold {args.threshold})", sys.stdout)
        log_run(root, "check_duplicates", "did-not-run", f"{len(comparable)} notes")
        return EXIT_OK

    print(
        f"{len(flagged)} pairs flagged of {len(pairs)} compared · "
        f"{len(comparable)} notes · threshold {args.threshold} · {skipped} skipped"
    )
    log_run(root, "check_duplicates", "ok" if not flagged else "defects", f"{len(flagged)} flagged")

    if flagged:
        for a, b, score in sorted(flagged, key=lambda t: -t[2]):
            print(f"{a.name}: {score:.2f} overlap with {b.name}", file=sys.stderr)
        print(f"{len(flagged)} duplicate pairs need a decision", file=sys.stderr)
        return EXIT_DEFECT
    if skipped:
        print(f"{skipped} files skipped — denominator incomplete", file=sys.stderr)
        return EXIT_DEFECT
    return EXIT_OK

# --------------------------- vaultkit.py freshness   (was check_freshness.py)
"""Report the age of the last HEALTHY run of each expected job.

Without this, a scheduler that quietly stopped firing looks identical to one that is fine.
"no log" is reported as "did not run" — never as "fine".

Log format, one line per run, appended by every tool (see vault_paths.log_run):

    2026-07-27T09:15:00+00:00	build_index	ok	0 defects

LOGGING AND BEING WATCHED ARE TWO DIFFERENT THINGS, AND jobs.json CARRIES THE LISTS. Every tool
writes a line; only a tool that runs on a schedule can be *late*. Put the on-demand ones under an
age limit and the report is red every single day, which is the fastest way to get the whole check
switched off. So `jobs` is what must be fresh, `on_demand` is what logs and is never late,
`not_invoked` is what no chain calls at all, and a name in none of them is reported as
unclassified rather than assumed into one of them.

THE UNCLASSIFIED LIST IS READ FROM THE FOLDER, NOT ONLY FROM THE LOG. A tool that no chain calls
never writes a line, and a population derived from the log alone therefore cannot see the one
thing this report is for -- the check confirms its own silence. Measured 2026-07-30: `0
unclassified` over a folder holding a tool in neither list.

This tool logs itself and stands in `on_demand`. Without its own line, "the freshness check runs in
the chain" is a claim about a command file: delete the step and it looks exactly like a check that
runs and finds nothing. Watching itself would be the regress -- logging is not watching, and that
separation is the whole point.

RUN IT FIRST, BEFORE ANYTHING ELSE IN THE CHAIN. Every other tool appends an `ok` line, so a run
measured afterwards sees the side effect of the chain it is part of and reports fresh over a job
that died a week ago.
"""

DEFAULT_MAX_AGE_HOURS = 24.0
HEALTHY = {"ok"}


DEFAULT_JOBS = ["build_index", "check_links"]

# Tools that log but deliberately have no age limit, name -> why. Kept in step with the shipped
# jobs.json, and used only when no config file exists at all.
#
# THE REASON PER ENTRY IS NOT DECORATION: an exception without one is indistinguishable from an
# oversight, and JSON has no comments, so the value carries it.
DEFAULT_ON_DEMAND = {
    "check_duplicates": "runs in the verification chain and by hand, never on a schedule",
    "write_command": "runs once during setup, and again only if the command file is gone",
    "check_freshness": "this job itself -- logged, never watched: an age limit on the watcher "
                       "is a regress",
}

# The third classification: it logs, and no chain calls it. EMPTY SINCE 2026-07-31, and the
# structure stays for the user's own tools. All three entries that were here described FILES
# rather than jobs: `vault_paths` and `_testkit` were modules and are not files any more, and
# `count_tokens` is excused by the register at the end of this file instead -- it carries no job
# name, which is the same statement made where the fact lives rather than in a second place.
#
# A user's own logging script still belongs here, with its reason: JSON has no comments, so the
# value carries it, and an exception without one cannot be told from an oversight. Kept in step
# with the shipped jobs.json -- build_kit.py refuses a build where the two disagree.
DEFAULT_NOT_INVOKED = {}


def tool_folder(vault_root):
    """The one folder both the config and the population come out of.

    Derived from RUN_LOG_RELPATH rather than spelled again: a population read from one folder and
    a classification read from another would disagree without either being wrong.
    """
    return Path(vault_root).resolve() / RUN_LOG_RELPATH.parent


def loggable_tools(vault_root):
    """(names of jobs that can ever appear in the log, files that could not be read).

    WHY THE POPULATION IS NOT SIMPLY EVERY `.py` IN THE FOLDER (2026-07-30): a tool that never
    logs cannot appear in the log by construction, so asking whether it is watched has no answer
    that would change anything -- `upgrade.py` runs, reaches a verdict, and never logs. Naming it
    on every single run would put a permanent line above the one line that means something, which
    is the fastest way to get this report skimmed instead of read.

    Measured on this machine 2026-07-30, when this function was written: five of the shipped
    tools logged -- build_index, check_links, check_duplicates, write_command, check_freshness --
    and those five were exactly the five in jobs.json. So the honest population is "can it log",
    and the check that follows is "has anyone said which list it belongs to".

    HALF OF IT IS NOW READ, NOT GUESSED (2026-07-31). It used to take every stem in the folder
    whose file text mentioned the logging call. That was a guess with two known faults, and the
    merge into one file turned both fatal: `vault_paths.py` showed up because it DEFINED the
    call and needed a `not_invoked` entry as a patch, a tool that forgot to log was invisible by
    construction -- and with every guard in `vaultkit.py`, the guess now yields exactly one stem,
    `vaultkit`, which is no job's name at all. Every job would read as unclassified forever.

    So the kit's own jobs come from COMMANDS at the end of this file, which states them instead
    of inferring them. The folder scan stays for the user's OWN tools: a script they wrote that
    logs is still a job that can go stale, and nothing here knows about it in advance. This file
    is skipped by name in that scan, because the register already answered for it.

    Suites are excluded structurally, not by taste: `test_X.py` is not a job, and one that
    exercised the logging call would otherwise ask to be classified as a scheduled job.
    """
    names = {spec["job"] for spec in COMMANDS.values() if spec["job"]}
    folder = tool_folder(vault_root)
    if not folder.is_dir():
        return names, 0
    unreadable = 0
    for path in sorted(folder.glob("*.py")):
        if path.name.startswith("test_") or path.name == Path(__file__).name:
            continue
        try:
            text = path.read_text(encoding="utf-8-sig", errors="replace")
        except OSError:
            # Counted and printed, never a silent continue: a skip that does not count itself
            # still prints a total, over fewer files than it names.
            unreadable += 1
            continue
        if "log_run(" in text:
            names.add(path.stem)
    return names, unreadable


def job_lists(vault_root):
    """(watched, on_demand, not_invoked) — read once, so they can never disagree about the fallback.

    No config file is normal -- a project-only run has none, and both defaults stand. A config
    that exists and cannot be read is not normal, and falling back to the default over it
    checks a job list the user never chose while printing nothing about it. utf-8-sig is how
    that used to happen: Notepad writes a BOM, json.loads raises, the except swallowed it.

    A config that exists and has no `on_demand` key gets an EMPTY on-demand list, not the
    default above. That is the same rule one line further: substituting a classification the
    user never made is the silent fallback this docstring is about. Empty is honest, and the
    unclassified line then names the tools instead of guessing at them.

    Either shape is accepted for `on_demand` and for `not_invoked`: the mapping that ships
    (name -> reason) or a bare list, which a user mirroring `jobs` will write. A list simply
    carries no reasons; refusing it would hard-fail an honest config over cosmetics.
    """
    config = tool_folder(vault_root) / "jobs.json"
    if not config.exists():
        return list(DEFAULT_JOBS), dict(DEFAULT_ON_DEMAND), dict(DEFAULT_NOT_INVOKED)
    try:
        data = json.loads(config.read_text(encoding="utf-8-sig"))
        watched = list(data["jobs"])
        return watched, _mapping(data, "on_demand"), _mapping(data, "not_invoked")
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print(f"{config}: unreadable ({exc}) — falling back to {DEFAULT_JOBS}", file=sys.stderr)
        return list(DEFAULT_JOBS), dict(DEFAULT_ON_DEMAND), dict(DEFAULT_NOT_INVOKED)


def _mapping(data, key):
    """One optional name->reason list out of a config that exists. Missing means EMPTY.

    Never the built-in default: a config the user wrote and a classification they never made must
    not be mixed, or the unclassified line reports against a list nobody chose. Same rule as the
    docstring above, applied to both optional keys instead of one.
    """
    raw = data.get(key) or {}
    return dict(raw) if isinstance(raw, dict) else {name: "" for name in raw}


def parse_log(log_path):
    """(newest healthy per job, every job name seen, lines, malformed).

    `seen` covers failed runs too: a tool that only ever fails is still either classified or
    not, and leaving it out of that question would hide the tool that needs the decision most.
    """
    healthy = {}
    seen = set()
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
            seen.add(job)
            if when.tzinfo is None:
                when = when.replace(tzinfo=timezone.utc)
            if status not in HEALTHY:
                continue
            if job not in healthy or when > healthy[job]:
                healthy[job] = when
    return healthy, seen, lines, malformed


def freshness_main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--vault", required=True, help="vault root")
    parser.add_argument("--log", help="run log path (defaults to the vault's own)")
    parser.add_argument("--max-age-hours", type=float, default=DEFAULT_MAX_AGE_HOURS)
    parser.add_argument("--jobs", nargs="*", help="override the expected job list")
    args = parser.parse_args(argv)

    vault_root = Path(args.vault).resolve()
    log_path = Path(args.log).resolve() if args.log else vault_root / RUN_LOG_RELPATH
    configured, on_demand, not_invoked = job_lists(vault_root)
    jobs = args.jobs if args.jobs else configured

    # Before any measurement, because the answer to "which list wins" is none of them. Letting one
    # win would be an invisible decision: the other entry would sit there doing nothing, and no
    # run could show which of the statements applies.
    #
    # The CONFIGURED list, not the effective one: the defect is in the file, so `--jobs` must not
    # be able to dodge it -- and `--jobs check_duplicates` is a deliberate one-off watch of an
    # on-demand tool, which is not a contradiction and must not be treated as one.
    #
    # Three lists since 2026-07-30, so every pair is checked rather than the one that used to
    # exist. `not_invoked` contradicts either of the others just as loudly: a tool cannot both be
    # called by no chain and be the thing a chain is watched for.
    clash = sorted({name for a, b in ((configured, on_demand), (configured, not_invoked),
                                      (set(on_demand), set(not_invoked)))
                    for name in set(a) & set(b)})
    if clash:
        print(f"{', '.join(clash)}: classified twice. Watched means it may be late, on demand "
              f"means it cannot be, not invoked means no chain calls it — a name belongs to "
              f"exactly one. Take it out of the others in {tool_folder(vault_root) / 'jobs.json'}.",
              file=sys.stderr)
        log_run(vault_root, "check_freshness", "did-not-run",
                f"{len(clash)} jobs in more than one list")
        return EXIT_USAGE

    if not jobs:
        did_not_run("no expected jobs configured")
        log_run(vault_root, "check_freshness", "did-not-run", "no expected jobs configured")
        return EXIT_DEFECT

    if not log_path.exists() or log_path.stat().st_size == 0:
        did_not_run(f"no run log at {log_path}")
        for job in jobs:
            print(f"{job}: {DID_NOT_RUN} — no log", file=sys.stderr)
        print(f"0/{len(jobs)} jobs have a healthy run", file=sys.stderr)
        log_run(vault_root, "check_freshness", "did-not-run", f"no run log at {log_path}")
        return EXIT_DEFECT

    healthy, seen, lines, malformed = parse_log(log_path)
    now = datetime.now(timezone.utc)
    fresh = []
    problems = []

    for job in jobs:
        when = healthy.get(job)
        if when is None:
            problems.append(f"{job}: {DID_NOT_RUN} — no healthy line in {lines} log lines")
            continue
        age_h = (now - when).total_seconds() / 3600.0
        if age_h > args.max_age_hours:
            problems.append(f"{job}: last healthy run {age_h:.1f}h ago, threshold {args.max_age_hours}h")
        else:
            fresh.append((job, age_h))

    # In no list. The only real signal at this point: somebody built a tool and nobody decided
    # whether it is watched. It does NOT change the exit code -- an unclassified tool has not
    # failed, and a chain that goes red the first time a user adds a tool of their own is one
    # they will stop running.
    # `configured` is subtracted as well as `jobs`, so a `--jobs` override does not turn the rest
    # of the user's own watch list into news.
    #
    # THE POPULATION IS THE FOLDER AS WELL AS THE LOG (2026-07-30, #24). It used to be `seen`
    # alone, and that made the check confirm its own silence: a tool no chain calls never writes
    # a line, and without a line it could not turn up as unclassified. Measured that day against
    # a fresh vault -- `0 unclassified` while count_tokens sat in the folder in neither list, the
    # one tool the report existed to name. The self-confirming shape is the point: the tools that
    # fall out of the chain are exactly the ones a log-derived population cannot see.
    on_disk, unreadable = loggable_tools(vault_root)
    unclassified = sorted((seen | on_disk) - set(jobs) - set(configured)
                          - set(on_demand) - set(not_invoked))

    print(
        f"{len(fresh)}/{len(jobs)} jobs fresh · {len(on_demand)} on demand · "
        f"{len(not_invoked)} not invoked · {len(unclassified)} unclassified · "
        f"{lines} log lines · {malformed} malformed · threshold {args.max_age_hours}h"
    )
    for job, age_h in fresh:
        print(f"  {job}: {age_h:.1f}h ago")
    if unclassified:
        print(f"  in none of the three lists: {', '.join(unclassified)}")
    if unreadable:
        print(f"  {unreadable} file(s) in {tool_folder(vault_root)} could not be read, so they "
              f"are outside every count above", file=sys.stderr)

    status = "defects" if (problems or malformed) else "ok"
    log_run(vault_root, "check_freshness", status,
            f"{len(fresh)}/{len(jobs)} fresh · {len(unclassified)} unclassified")

    if problems or malformed:
        for problem in problems:
            print(problem, file=sys.stderr)
        if malformed:
            print(f"{malformed} malformed log lines", file=sys.stderr)
        return EXIT_DEFECT
    return EXIT_OK

# --------------------------------- vaultkit.py tokens   (was count_tokens.py)
"""Report the size of what was read, for cost.

Never invents a precision: every number is labelled `exact` or `estimated`. Without a real
tokenizer installed the token count is a chars/4 heuristic and says so on every line.
"""

CHARS_PER_TOKEN = 4.0


def tokenizer():
    """Return (name, callable) if a real tokenizer is importable, else (None, None)."""
    try:
        import tiktoken  # type: ignore

        enc = tiktoken.get_encoding("cl100k_base")
        return "tiktoken/cl100k_base", lambda s: len(enc.encode(s))
    except Exception:
        return None, None


def tokens_main(argv: list[str] | None = None) -> int:
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
            return EXIT_USAGE

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
        did_not_run("0 files matched")
        return EXIT_DEFECT

    source = name if name else f"chars/{CHARS_PER_TOKEN:g} heuristic"
    print(f"{tokens} tokens ({precision}, {source}) · {chars} chars · {len(files) - skipped}/{len(files)} files")
    if skipped:
        print(f"{skipped} files skipped — denominator incomplete", file=sys.stderr)
        return EXIT_DEFECT
    return EXIT_OK


def main(argv: list[str] | None = None) -> int:
    """Hand the remaining arguments to the subcommand's own parser, untouched.

    NO SHARED ARGUMENT PARSING, ON PURPOSE. `--vault` means one project directory after `index`
    and the vault root after `links`; `--root` exists only for `index`. That collision is the
    trap the `/vaultkit` command was written for, and folding the guards into one file did not
    remove it -- it only put it inside one file. A parser here that tried to unify the two would
    either pick a winner or invent a third spelling. Each subcommand keeps its own parser and its
    own `--help`, so what a user types is what the section above documents.
    """
    argv = list(sys.argv[1:] if argv is None else argv)
    if not argv or argv[0] in ("-h", "--help"):
        parser = argparse.ArgumentParser(prog="vaultkit.py", description=__doc__,
                                         formatter_class=argparse.RawDescriptionHelpFormatter)
        parser.add_argument("subcommand", choices=sorted(COMMANDS),
                            help="the guard to run; each has its own --help")
        parser.parse_args(argv)
        return EXIT_USAGE

    name, rest = argv[0], argv[1:]
    if name not in COMMANDS:
        print(f"vaultkit.py: no subcommand {name!r}. Known: {', '.join(sorted(COMMANDS))}",
              file=sys.stderr)
        return EXIT_USAGE
    return COMMANDS[name]["run"](rest)


# --------------------------------------------------------------------------- the register
#
# AT THE END OF THE FILE, AND THAT IS LOAD-BEARING THREE TIMES OVER.
#
# 1. It is where `freshness` takes its own population from. That population used to be a GUESS:
#    the folder was globbed for `*.py` and a stem taken when the text mentioned the logging call,
#    so `vault_paths.py` appeared because it DEFINED that call and needed a `not_invoked` entry
#    as a patch -- and a tool that forgot to log was invisible by construction. With one file
#    the guess has no meaning left at all: every job would come out as `vaultkit`. `job` below is
#    the answer instead, and `None` says "reaches no verdict, never logs" out loud.
# 2. It is what build_kit.py holds every logging literal to. The rule used to be "the label
#    equals the filename", and after the merge there is one filename for six jobs.
# 3. It is what `upgrade.py --prove` asks for to decide this file arrived whole -- and that
#    check lives THERE, in another block, because nothing here can do it. Measured on this
#    machine 2026-07-31, cutting this file twice, once just above this register and once
#    mid-file after a complete function: `compileall` exit 0, `import vaultkit` exit 0, and
#    `vaultkit.py index` exit 0 having done nothing at all. Both cuts take the entry point below
#    with them, so the script runs to the end of what arrived and reports success. Anything put
#    at the end to catch that goes with the same cut. One long block makes truncation quieter,
#    not louder, and the only reader that can tell is a separate file.
#
# The folder scan in `freshness` stays, for the user's OWN tools: this register describes what
# the kit brought, not what they wrote.

COMMANDS: dict[str, Command] = {
    "index": {"run": index_main, "job": "build_index"},
    "links": {"run": links_main, "job": "check_links"},
    "duplicates": {"run": duplicates_main, "job": "check_duplicates"},
    "freshness": {"run": freshness_main, "job": "check_freshness"},
    "command": {"run": command_main, "job": "write_command"},
    # No job: it reports a size and reaches no verdict, so nothing can be late and no chain has
    # anything to act on. That is also why no command line has to name it.
    "tokens": {"run": tokens_main, "job": None},
}


if __name__ == "__main__":
    raise SystemExit(main())
```

#### Drivers

### `upgrade.py`

```python
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

import sys

# THE SAME CHECK vaultkit.py DOES, AND THE SECOND COPY IS THE POINT (2026-07-31). This file has
# to run when the other one is destroyed -- that is why it stays a separate block at all -- so it
# cannot ask vaultkit.py what the floor is. Same rule as the stdout/stderr fix, same reason.
#
# The floor is 3.10, from `Path.write_text(newline=…)`, used five times below. On an older Python
# every one of those raises TypeError at the moment the update WRITES, i.e. after the kit file
# has been read and classified, with a message naming nothing that points here.
if sys.version_info < (3, 10):
    have = ".".join(str(part) for part in sys.version_info[:3])
    print(f"upgrade.py needs Python 3.10 or newer; this is {have}. Nothing was read or written.",
          file=sys.stderr)
    # The literal, not EXIT_USAGE: this runs before the constants below are defined, and a
    # NameError here would replace the one message that explains what is wrong.
    raise SystemExit(2)

import argparse
import json
import re
import subprocess
from pathlib import Path

TOOLS = Path(__file__).resolve().parent

# Spelled again rather than imported from vaultkit.py, deliberately. The one thing this file
# takes from that one is the register, and only inside --prove, inside a try: everything else
# here has to work on a folder where vaultkit.py is truncated, missing or unparseable. An import
# at the top would make the repair tool depend on the thing being repaired.
#
# Same three meanings, and src/contract.md SECTION 6 states them once for both files:
#   0  clean · 1  it did the work but it does not check out · 2  wrong argument, or the
#   environment refused a file operation -- nothing was written on the strength of a guess.
EXIT_OK = 0
EXIT_DEFECT = 1
EXIT_USAGE = 2

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


def read_kit(path) -> tuple[dict[str, str], str]:
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
        raise SystemExit(EXIT_USAGE)
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


def write_stamp(version: str, files: list[str] | None = None) -> Path | None:
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


def stamp(kit_path) -> int:
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
        return EXIT_USAGE
    found = VERSION_RE.search(text)
    if not found:
        print(f"{kit_path}: no `<!-- kit-version: … -->` line — nothing to stamp. An unstamped "
              f"file cannot say which kit this folder came from, and a guessed value is worse "
              f"than none.", file=sys.stderr)
        return EXIT_DEFECT
    delivered = sorted(name for name, _ in BLOCK_RE.findall(text))
    target = write_stamp(found.group(1), delivered or None)
    if target is None:
        return EXIT_USAGE
    print(f"wrote {target.name}: {found.group(1)}")
    if delivered:
        print(f"wrote {MANIFEST_NAME}: {len(delivered)} files this kit delivers")
    return EXIT_OK


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

      - Set the encoding back to `utf-8` (dropping errors= with it): test_upgrade 33/35. BOTH
        cases go red, because `utf-8` without a replacement handler raises on the bad byte too.
      - Keep `utf-8-sig` and drop only `errors="replace"`: test_upgrade 34/35, and only
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


def prove() -> bool:
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

    # THE CHECK THAT COMPILING CANNOT DO, AND IT LIVES HERE FOR A REASON (2026-07-31). vaultkit.py
    # is one long block now, and a truncated block is the failure a single-file delivery makes
    # more likely, not less. Measured on this machine, cutting that file in two places -- once
    # just before its register, once mid-file after a complete function:
    #
    #     compileall exit 0 · import exit 0 · `vaultkit.py index` exit 0, and NOTHING HAPPENS
    #
    # Both cuts take the trailing `if __name__ == "__main__":` with them, so the script runs to
    # the end of what arrived and exits successfully having done no work. That is the quietest
    # failure this kit can have, and no check inside that file can catch it: whatever you put at
    # the end goes with the cut.
    #
    # So it is checked from HERE, out of a different block, by asking the file for the register
    # it is supposed to end with.
    sys.path.insert(0, str(TOOLS))
    try:
        import vaultkit
        register = vaultkit.COMMANDS
        missing = [sub for sub, spec in register.items() if not callable(spec.get("run"))]
        if not register or missing:
            raise ValueError(f"register empty or unroutable: {missing or 'no subcommands'}")
        text = (TOOLS / "vaultkit.py").read_text(encoding="utf-8-sig")
        if 'if __name__ == "__main__":' not in text.split("COMMANDS = {")[-1]:
            raise ValueError("the file does not end with its entry point")
        print(f"  ok   vaultkit.py is whole: {len(register)} subcommands and an entry point")
    except Exception as exc:
        # Deliberately broad: an incomplete file fails in whatever way it was cut -- ImportError,
        # AttributeError, SyntaxError, NameError. What matters is that the run says so.
        print(f"  FAIL vaultkit.py: {type(exc).__name__}: {exc}\n"
              f"       This is what a block that arrived truncated looks like. Compiling it "
              f"proves nothing -- a cut file compiles and then does nothing at exit 0.")
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


def main(argv: list[str] | None = None) -> int:
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
        return EXIT_OK if prove() else EXIT_DEFECT
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
                    return EXIT_USAGE
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
            return EXIT_OK
        print("nothing to do.")
        return EXIT_OK
    if not args.apply:
        what = "write and remove these files" if removed else "write these files"
        print(f"\nnothing written, nothing removed. Re-run with --apply to {what}.")
        return EXIT_OK

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
        return EXIT_USAGE

    mismatched = [name for name in changed + added if not reads_back(name, blocks[name])]
    if mismatched:
        print(f"\n{len(mismatched)} file(s) do not read back as the kit wrote them: "
              f"{', '.join(mismatched)}\n"
              f"Nothing was removed and nothing was stamped, so this folder still has every "
              f"file it started with. Re-run --apply once the cause is fixed.", file=sys.stderr)
        return EXIT_USAGE

    kept = [name for name in removed if not remove_file(name)]
    if kept:
        # Same reasoning as a refused write: the manifest must not claim a file is gone while it
        # is still there, or nothing will ever try again.
        print(f"\n{len(kept)} file(s) could not be removed: {', '.join(kept)}\n"
              f"{MANIFEST_NAME} was NOT updated, so the next --apply tries them again.",
              file=sys.stderr)
        return EXIT_USAGE

    if write_stamp(new_version, sorted(blocks)) is None:
        print("the scripts are current, the stamp is not -- re-run --apply once it can be written.",
              file=sys.stderr)
        return EXIT_USAGE
    written = len(changed) + len(added)
    print(f"\nwrote {written} files, removed {len(removed)}. Proving them:")
    checked = prove_from_disk() if SELF in changed + added else prove()
    if not checked:
        print("the updated folder does not pass its own checks -- restore it from git.",
              file=sys.stderr)
        return EXIT_DEFECT
    print(f"updated to {new_version} · every script compiles and jobs.json parses.")
    return EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
```

---

*Generated by `tools/build_kit.py`. Edit the sources, never this file.*
*Source and newest published copy: https://github.com/nibor1896/claude-obsidian-vault-kit*
*Compare the `kit-version` at the top against the published file to see whether this copy is current.*
