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
6. **The scripts are inside this file. Write them out; do not rewrite them.** SECTION 10 carries
   every tool, every suite and the three runners verbatim — measured on Windows 11 with Python 3.13
   under PowerShell 5.1 and Git Bash: **8/8 suites green, 11/11 acceptance checks and 11/11
   end-to-end setup steps, in ten consecutive runs under each shell.** Write each block to disk
   byte for byte. Retyping them from the contracts in SECTION 5 and SECTION 6 throws that
   measurement away and reintroduces the defects those sections describe — every one was found the
   expensive way. Change a shipped script only when the user's structure genuinely needs it, and
   then rerun the suites and `acceptance.py` before reporting anything.
   **Tell the user how to update later.** The header of this file carries a line like
   `<!-- kit-version: … -->` (twelve hex characters). It is a hash of the contract and every shipped script, so
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
- The four starting pages named in SECTION 8 — and **no other notes**. Nothing invented.
- Backup and git set up per SECTION 7.
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
- **Is there a cross-project or "global" bucket** for things that belong to no single project
  (tooling, personal working rules, cross-cutting decisions)? Most people want one.

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
  the first option so it is one click.

### 1.5 Environment

- **OS and shell**, exactly. Every command you emit later depends on this.
- **Python 3.10+ available?** Check with `python --version` / `python3 --version`. The guard scripts
  are Python. If Python is absent, offer the install and wait.

**The vault this setup hands over is empty.** It is structure, tools and the four starting pages from
SECTION 8 — no imported notes, no migrated memory, no example content. If the user has knowledge
elsewhere they want in here, that is their own step afterwards, against the frontmatter contract in
SECTION 4. Do not offer to do it as part of the setup: an import that runs before the structure has
verified clean makes a failure of the structure indistinguishable from a failure of the import.

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

Every project gets the *same* folders, so a path is predictable without looking. You create them
once during setup; after that the index generator creates any that are missing, including in a
project folder the user makes themselves later (SECTION 5).

```
<VaultRoot>/
├── INDEX - <VaultName>.md           generated — one line per project
├── 00_Global/                       optional: things belonging to no single project
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
- **Tools live in exactly one place.** Put the scripts under one project's `06_tools/` (or under
  `00_Global/06_tools/`) and have every other project supply only its own small config file. Two
  copies of a script means one of them is silently out of date.
- **Optional extras**, add only if the user has the need: `07_reports/` (one report per
  investigation) is the common one. Any folder the user adds by hand becomes a category of its own
  on the next index run (SECTION 5) — they do not have to ask permission for a folder.
- If the user changed folder names in a test vault, **their names win** — carry them consistently
  into every project and into every script's config.
- **A directory at the vault root is a project, and the generator will treat it as one.** It gets
  the category folders and a hub index on the next run. Say this before the user parks an
  `attachments/` or a `_scratch/` next to their projects: it is not wrong, but they will get six
  folders inside it and the run will tell them it made them.

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

> Generated by `06_tools/build_index.py` from note frontmatter.
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
`node_modules` and anything starting with a dot are never adopted. One `node_modules` at project
level would otherwise become a permanent category with an index file inside it.

A folder that cannot be created — permissions, a file of that name in the way — **is** a defect,
with the OS error attached. That is the one case here where the run goes red.

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

### `check_freshness.py` in particular

Any job on a schedule (task scheduler, cron, launchd) writes a line to an append-only log on **every
run, including the healthy ones**. `check_freshness.py` reads that log and reports the age of the
last healthy run per job, against a threshold the user sets. Without this, a scheduler that quietly
stopped firing looks identical to one that is fine.

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
- **Stuck on something?** Search `00_Notes/` first. A past procedure that already fits beats a new
  one you invent now.

---

## SECTION 9 — Acceptance test: prove the guards react as specified

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
`11/11 checks behaved as specified`. Anything less is a defect in a script, not in the expectation.
`--repeat 10` runs ten full passes; use it after any change to a guard.

The table below is what the driver checks, and it is the specification a changed script must still
meet. **Nine fixtures require red, two require green** — fixture 0 is the healthy control and
fixture 9 is input the structure explicitly allows. A suite that only ever sees bad input is exactly
as blind as one that only ever sees good input. The driver counts the two kinds from the fixture
list rather than printing a fixed sentence, so a fixture that changes sides changes the summary with
it.

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

The driver leaves nothing behind — every fixture vault lives under the system temp directory and is
deleted in a `finally` block. After the run, `git status --porcelain` in the real vault must still be
empty; if it is not, something wrote outside the throwaway tree and that is the finding.

**Run the suites under every shell the user has**, not just the one you happen to be in. On Windows
that means PowerShell *and* Git Bash. This is where the encoding defect in SECTION 6 shows up, and it
is invisible from inside a single shell.

Report it like this, one line per check, and **name any check you did not run**:

```
Acceptance: 11/11 checks behaved as specified (9 red on bad input, 2 green on allowed input)
            (or) 9/11 — #5 non-ASCII filename NOT caught, #9 not run
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
