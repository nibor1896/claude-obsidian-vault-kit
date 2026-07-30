<!-- kit-version: ee38a2f889f9 -->
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
   and waiting for a yes. **One exception, and it is the only one:**
   `~/.claude/commands/vaultkit.md`, written in SECTION 8. That file is part of this setup, not an
   extra — it is how the verification chain gets run from then on, and it works nowhere else. Name
   the path out loud before writing it, then write it. Do **not** turn it into a question: an offer
   with a "no" in it produces a vault whose own maintenance command does not exist. The tool never
   overwrites, so the only thing a yes could protect is a file it already refuses to touch.
6. **The scripts are inside this file. Write them out; do not rewrite them.** SECTION 10 carries
   every tool, every suite and the three runners verbatim — measured on Windows 11 with Python 3.13
   under PowerShell 5.1 and Git Bash: **9/9 suites green, 12/12 acceptance checks and 14/14
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
   acceptance driver afterwards. **Name where a newer file comes from** — the repository is in the
   last lines of this file; a user holding only the `.md` has no other way to find out that a newer
   one exists. Say this once during setup -- a user who does not know an update path exists will not
   go looking for one. The stamp `upgrade.py` compares against is written in SECTION 8.
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

Each of these is a small script with one job, and each ships with a `test_*.py` in the same commit.
Every suite needs at least one **failure-mode fixture** *and* one **healthy control** — a test that
only ever sees good input cannot tell you the check still works.

| Script | Job | Must refuse |
|---|---|---|
| `build_index.py` | the index tree (SECTION 5) | a silent fallback on a degraded entry |
| `check_links.py` | every `[[wikilink]]` resolves to a file | reporting `0 broken` when it scanned 0 files |
| `check_duplicates.py` | notes whose content overlaps | being ignored — every hit gets a decision |
| `check_freshness.py` | age of the last **healthy** run of each scheduled job | treating "no log" as "fine", or a job listed as both watched and on-demand as watched |
| `run_suites.py` | discovers and runs every `test_*.py` | reporting green when it collected zero suites |
| `count_tokens.py` | size of what was read, for cost | inventing a precision — output `exact` or `estimated` |
| `write_command.py` | the `/vaultkit` command, with this vault's real paths in it | overwriting a command the user has edited, or writing one without naming the path |

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

**Logging and being watched are two different lists, and `jobs.json` carries both.** Every tool
writes a line; only a tool that runs on a schedule can be *late*. Put the on-demand ones under an
age limit and the report is red every single day — which is the fastest way to get the whole check
switched off, and a check nobody runs is worth less than none. So `jobs` is what must be fresh,
`on_demand` is what logs and is never late, and each on-demand entry carries its reason as its
value, because JSON has no comments and an exception without a reason is indistinguishable from an
oversight.

Three consequences, and each one is a behaviour, not a preference:

- **A name in both lists stops the tool with exit 2.** Not "watched wins": that would be an
  invisible decision, with the on-demand entry sitting there doing nothing and no run able to show
  which of the two statements applies.
- **A name in neither is reported, and does not change the exit code.** That line is the only real
  signal in this area — somebody built a tool and nobody decided whether it is watched. Turning it
  red would make the chain permanently red for every user who adds a tool of their own.
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

# The agent's own folder, if one turns up here: sessions, settings and caches are its state, not
# project knowledge. Nothing this setup writes lives here -- the /vaultkit command goes to the
# user's own ~/.claude/commands/ -- so the whole folder is ignored, with no exception to maintain.
.claude/

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

### Stamp the tool folder with the version that wrote it

Before the verification run, run this once — it is a command, not a file you write:

```
python <VaultRoot>/00_Global/06_tools/upgrade.py --stamp <path to this kit file>
```

It writes

```
<VaultRoot>/00_Global/06_tools/kit-version.txt
```

whose whole content is the twelve hex characters from the `<!-- kit-version: … -->` comment on
line 1 of this file, plus a newline. UTF-8, no BOM, nothing else in the file — no date, no label,
no sentence around it; `upgrade.py` reads the file and strips it, and anything else in there
becomes part of the version. `--stamp` writes that one file and touches nothing else; it needs no
`--apply`.

**Do not type those twelve characters yourself**, even though you can see them. They already exist
verbatim in a file on disk, which makes copying them mechanical work — operating rule 7. If the kit
file carries no stamp line, `--stamp` refuses instead of recording `unversioned`: that string would
be compared against every future kit and never match.

This is the value the entire update path compares against. `upgrade.py` prints
`installed: <version> · kit file: <version>`, and until this file exists it prints
`installed: unknown` — so a user cannot tell an outdated tool folder from a current one, which is
the one question the update path exists to answer. Nothing else writes it at setup time:
`upgrade.py` writes it again when it applies an update, i.e. from the *second* version onwards.

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
python <VaultRoot>/00_Global/06_tools/write_command.py --vault <VaultRoot> \
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
hits them: `--vault` means one project after `build_index.py` and the vault root after
`check_links.py`; the tool folder is a full path, not `06_tools/`; and the sweep is `--root`.
**This is a Claude Code convenience, not a deliverable.** The workflow page in `05_workflows`
carries the same chain in prose, so a user working in a browser loses nothing.

### Verification run — all of it, no exceptions

```bash
python 06_tools/check_freshness.py --vault <VaultRoot>   # FIRST, and not as a formality
python 06_tools/build_index.py --vault <Project>     # once per project
python 06_tools/build_index.py --root  <VaultRoot>
python 06_tools/check_links.py --vault <VaultRoot>
python 06_tools/check_duplicates.py --vault <VaultRoot>
python 06_tools/run_suites.py
```

**The freshness check goes first because every line below it writes to the run log.** Measured
after them, it sees the side effect of this very chain and reports the jobs as fresh — including a
scheduled one that stopped firing a week ago. There is no reading of the order that puts it
anywhere else.

**Red there is a report, not a stop.** It judges the past; the rest of the chain produces the
present. Run every remaining step regardless, carry its numbers into the report below, and do not
fold its verdict into a line that claims the vault is in order — the two answer different questions.

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
Freshness: <n>/<m> jobs fresh · <k> on demand · <u> unclassified
Tests:     <n>/<m> suites green
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
  **Do not write `.obsidian/templates.json` for them — and not because it would fail.** It works:
  measured on 2026-07-29 against Obsidian **1.12.7**, a `templates.json` that Obsidian did not
  write itself is read at startup. The file was `{"folder": "_templates"}` — 23 bytes, UTF-8
  **without a BOM**, written while Obsidian was closed — and the setting was live on the next
  start; observed twice. Three things were not tested: the same file *with* a BOM, writing it
  while Obsidian is running, and any other Obsidian version.
  The rule stands on the other reason: `.obsidian/` is the user's application state, and this kit
  does not write into it. Name the setting and let them make it. If they would rather have the
  file than click through Settings, that is theirs to write, with Obsidian closed — one line,
  no BOM: `{"folder": "_templates"}`.
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
user's notes, and it takes its verdict from process exit codes and files on disk. Console text
wraps at the terminal width and differs per shell, so **it never stands alone as evidence** — a
fixture that only greps stdout passes a tool which prints the right sentence and does the wrong
thing. **Where the message itself is the specified behaviour, the message is what gets checked** —
in addition to the exit code, never instead of it. Three kinds of row below are that case, and the
third is easy to forget:

- the ones that require the run to **name the file**,
- the ones that require it to **show a denominator**,
- and the ones that require a **particular phrase** — *"did not run"*, *"0 suites collected"*,
  *"adopted"* — **including the requirement to stay silent**, which is a claim about output that
  nothing but the output can settle.

"It is reported" is the requirement, and a guard that goes red without saying which file has not
met it. The shipped driver reads output only where a row below asks it to; fixture 9 carries the
reasoning in its docstring. Expect
`12/12 checks behaved as specified`. Anything less is a defect in a script, not in the expectation.
`--repeat 10` runs ten full passes; use it after any change to a guard.

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
| 11 | run `write_command.py` twice against a vault, hand-editing the command in between, then once more against a file of the same name it did not write | the file appears, spells `--root` and `--vault` as the two different things they are, the run **names it on stdout**; the second run writes nothing and **says nothing**; the foreign file is **named on stderr with a non-zero exit** and is not touched | a tool that writes into a config folder without naming it — the destination can be outside the vault, which is the one place operating rule 5 forbids anything quiet — or, worse, one that returns 0 over a command it never wrote, so the setup reports `/vaultkit` ready while someone else's file holds the name |

The driver leaves nothing behind — every fixture vault lives under the system temp directory and is
deleted in a `finally` block. After the run, `git status --porcelain` in the real vault must still be
empty; if it is not, something wrote outside the throwaway tree and that is the finding.

**Run the suites under every shell the user has**, not just the one you happen to be in. On Windows
that means PowerShell *and* Git Bash. This is where the encoding defect in SECTION 6 shows up, and it
is invisible from inside a single shell.

Report it like this, one line per check, and **name any check you did not run**:

```
Acceptance: 12/12 checks behaved as specified (<n> red on bad input, <n> green on allowed input)
            (or) 10/12 — #5 non-ASCII filename NOT caught, #9 not run
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

## SECTION 10 — The scripts, verbatim

Everything below is the finished implementation. **Write each block to disk exactly as it stands —
byte for byte, same filename — into the vault's tool folder** (`<VaultRoot>/00_Global/06_tools/`,
created in SECTION 3). Do not retype them from the contracts above, do not "improve" them while
copying, and do not skip the suites: they are the only reason the numbers in SECTION 0 mean
anything.

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

# Imported, never respelled. A second copy of this list makes the fixtures agree with a tree
# the tools no longer build, and every suite stays green while doing it.
sys.path.insert(0, str(TOOLS))
from vault_paths import CATEGORY_FOLDERS  # noqa: E402


def make_vault(projects=("ProjektEins",)):
    """A throwaway vault with the real folder tree. Caller deletes the returned tempdir."""
    tmp = Path(tempfile.mkdtemp(prefix="vaultkit_")) / "Vault"
    for project in projects:
        for folder in CATEGORY_FOLDERS:
            (tmp / project / folder).mkdir(parents=True, exist_ok=True)
    (tmp / "00_Global" / "06_tools").mkdir(parents=True, exist_ok=True)
    return tmp


def write_note(path, title="Ein Titel", summary="Eine Zusammenfassung.", bom=False, **extra):
    """Write a note with frontmatter. Pass title=None or summary=None to omit the key.

    bom=True writes UTF-8 *with* a byte-order mark -- what Notepad and PowerShell 5.1's
    `Set-Content -Encoding utf8` produce, and what a user creating a note outside Obsidian
    on Windows gets by default.
    """
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
    path.write_text("\n".join(lines), encoding="utf-8-sig" if bom else "utf-8", newline="\n")
    return path


def run_tool(script, *args, strip_io_encoding=True, home=None):
    """Run a tool as a real subprocess. Returns (returncode, stdout, stderr) as UTF-8 text.

    PYTHONIOENCODING is removed on purpose: the tools must force UTF-8 themselves, or the
    same suite goes green under PowerShell and red under Git Bash on one machine.

    `home` redirects what `Path.home()` resolves to inside the subprocess, which is the only way
    to test a tool that writes into the user's own config folder without writing into it. Both
    variables are set because Python reads USERPROFILE on Windows and HOME elsewhere; setting one
    on the wrong platform is a no-op that silently leaves the real folder in play.
    """
    env = dict(os.environ)
    env["PYTHONPATH"] = str(TOOLS) + os.pathsep + env.get("PYTHONPATH", "")
    if strip_io_encoding:
        env.pop("PYTHONIOENCODING", None)
        env.pop("PYTHONUTF8", None)
    if home is not None:
        env["USERPROFILE"] = str(home)
        env["HOME"] = str(home)
        env.pop("HOMEDRIVE", None)
        env.pop("HOMEPATH", None)
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
  "_comment": "Two lists, and a name belongs to exactly one of them. \"jobs\" must show a healthy run inside the threshold -- these are the ones a dead scheduler would silently take with it. \"on_demand\" logs like everything else but is never late, because it runs when someone asks. A name in both stops the tool with exit 2. A name in neither is reported, never guessed at. Verify with: python check_freshness.py --vault <VaultRoot>",
  "jobs": ["build_index", "check_links"],
  "on_demand": {
    "check_duplicates": "runs in the verification chain and by hand, never on a schedule",
    "write_command": "runs once during setup, and again only if the command file is gone",
    "check_freshness": "this tool itself -- logged, never watched: an age limit on the watcher is a regress"
  }
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

It also owns the shape of a project: a project folder that is missing category folders gets
them, and a folder the user made by hand becomes a category of its own. Both are printed --
they change the tree, and a run that changes the tree silently is the failure this whole
file exists to prevent. Neither is a defect.

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
    TEMPLATES_DIR,
    category_index_name,
    category_label,
    has_forbidden_chars,
    is_index_file,
    log_run,
    project_dirs,
    project_index_name,
    root_index_name,
    template_name,
    template_text,
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
    every index. Adoption keeps those notes indexed; main() prints the folder either way.
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

    Returns (entries, categories, created, adopted) -- the last two are folder names, and main()
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
        write_if_changed(folder / category_index_name(project_name, folder_name), "\n".join(lines))
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
    write_if_changed(project_dir / project_index_name(project_dir), "\n".join(lines))
    return total_entries, len(category_rows), created, adopted


def write_templates(vault_root, projects):
    """One note template per project under <VaultRoot>/_templates/. Returns what it created.

    CREATED WHEN MISSING, NEVER OVERWRITTEN. A template exists to be edited -- a user adds the
    fields their vault actually uses -- and a tool that rewrites it on every run eats that edit
    without saying so. The doctrine rule that generated files are not hand-edited covers the
    index tree; _templates is deliberately not part of it, which is why it is written once and
    then left alone.
    """
    folder = Path(vault_root).resolve() / TEMPLATES_DIR
    written = []
    for project in projects:
        target = folder / template_name(project.name)
        if target.exists():
            continue
        folder.mkdir(parents=True, exist_ok=True)
        target.write_text(template_text(project.name), encoding="utf-8", newline="\n")
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
    write_if_changed(vault_root / root_index_name(vault_root), "\n".join(lines))
    templates = write_templates(vault_root, projects)
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
        projects, entries, categories, created, adopted, templates = build_root(vault_root, defects)
        names = check_unique_basenames(vault_root, defects)
        print(f"{entries} entries in {categories} categories · {projects} projects · {names} distinct filenames")
    else:
        project_dir = Path(args.vault).resolve()
        if not project_dir.is_dir():
            print(f"not a directory: {project_dir}", file=sys.stderr)
            return 2
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
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

### `write_command.py`

```python
"""Write a `/vaultkit` slash command for Claude Code, with this vault's real paths already in it.

The verification chain in SECTION 8 is six commands with three traps in them, and every one of
the three was hit on a real run:

  1. `--vault` means two different things. `check_links.py` wants the vault ROOT,
     `build_index.py` wants ONE PROJECT, `check_duplicates.py` takes either. Typing the same
     path after every `--vault` is wrong in two places out of three.
  2. The tool folder is `<VaultRoot>/00_Global/06_tools/`, not `06_tools/`. A relative prefix is
     an invitation to run it from a directory where it does not resolve.
  3. `--root`, not `--vault`, for the sweep. Rerunning only `--vault` after adding a note leaves
     the root index on yesterday's count -- green, silent, and wrong. Measured on a cold run:
     one added note left the root index reading 5 entries against a vault holding 6.

There is a fourth thing the file gets right and a typed chain cannot: ORDER. `check_freshness.py`
stands first, because every other step appends an `ok` line and a freshness check measured after
them reports the side effect of its own chain as health.

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
added: copy tools/ somewhere, make the `if target.exists():` block in main() unreachable, and run
the three drivers there -- test_write_command 8/12, acceptance 11/12, verify_setup 13/14.
"""

import argparse
import sys
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
sys.path.insert(0, str(TOOLS))

for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass

from vault_paths import log_run, project_dirs  # noqa: E402

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

    def tool(name):
        return show(tools / name, shell)

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
        "**Before you start:** `build_index.py` writes. Say so, and check `git status` first, so "
        "its output is not mistaken for someone else's uncommitted work.",
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
        f"- `python {tool('check_freshness.py')} --vault {root}`",
        "",
        "## 2 · Index each project",
        "",
        "`--vault` here means ONE PROJECT DIRECTORY, not the vault root. One line per project:",
        "",
    ]
    for project in projects:
        lines.append(f"- `python {tool('build_index.py')} --vault {show(project, shell)}`")
    lines += [
        "",
        "## 3 · Index the vault root",
        "",
        "`--root`, not `--vault`. This is the one invocation that walks every project *and* "
        "writes the root hub. Running only step 1 after adding a note leaves the root index "
        "holding yesterday's entry count, with no message and a green exit — measured on a cold "
        "run: one added note left it reading `5 entries` against a vault holding 6.",
        "",
        f"- `python {tool('build_index.py')} --root {root}`",
        "",
        "## 4 · Check the links",
        "",
        "`--vault` here means THE VAULT ROOT — the same flag, the other meaning. The project "
        "hubs link back to the root index, so anything narrower reports a broken link that is "
        "not broken:",
        "",
        f"- `python {tool('check_links.py')} --vault {root}`",
        "",
        "## 5 · Check for duplicates",
        "",
        "`--vault` here takes either the root or a single project:",
        "",
        f"- `python {tool('check_duplicates.py')} --vault {root}`",
        "",
        "## 6 · Run the suites",
        "",
        f"- `python {tool('run_suites.py')}`",
        "",
        "## 7 · Prove the second run changes nothing",
        "",
        "A generator that drifts on every run is indistinguishable from a clean one after a "
        "single pass, and it turns every later `git status` into noise nobody reads.",
        "",
        f"- `python {tool('build_index.py')} --root {root}`",
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


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--vault", required=True, help="vault root")
    parser.add_argument("--shell", choices=("powershell", "posix"), default="powershell",
                        help="the syntax the paths are written in")
    args = parser.parse_args(argv)

    vault_root = Path(args.vault).resolve()
    if not vault_root.is_dir():
        print(f"not a directory: {vault_root}", file=sys.stderr)
        return 2

    target = target_path()
    projects = project_dirs(vault_root)
    if not projects:
        # Not a silent skip: a vault with no projects means the wrong path was given, and a
        # command file listing no projects would be a working file that does nothing.
        print(f"no projects under {vault_root} — nothing to write a command for", file=sys.stderr)
        return 1

    if target.exists():
        if written_by_us(target):
            # Ours from a previous run, possibly hand-edited since. Nothing to say.
            log_run(vault_root, "write_command", "ok", f"{target} already ours · nothing written")
            return 0
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
        return 1

    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(command_text(vault_root, projects, args.shell),
                      encoding="utf-8", newline="\n")
    print(f"wrote {target} — /{COMMAND_NAME} covers {len(projects)} projects; "
          f"edit it freely, no run overwrites it")
    log_run(vault_root, "write_command", "ok", f"{target} written · {len(projects)} projects")
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
        print(f"did not run: 0 of {len(files)} markdown files scanned", file=sys.stderr)
        log_run(vault_root, "check_links", "did-not-run", "0 files scanned")
        return 1

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

LOGGING AND BEING WATCHED ARE TWO DIFFERENT THINGS, AND jobs.json CARRIES BOTH LISTS. Every tool
writes a line; only a tool that runs on a schedule can be *late*. Put the on-demand ones under an
age limit and the report is red every single day, which is the fastest way to get the whole check
switched off. So `jobs` is what must be fresh, `on_demand` is what logs and is never late, and a
name in neither is reported as unclassified rather than assumed into one of them.

This tool logs itself and stands in `on_demand`. Without its own line, "the freshness check runs in
the chain" is a claim about a command file: delete the step and it looks exactly like a check that
runs and finds nothing. Watching itself would be the regress -- logging is not watching, and that
separation is the whole point.

RUN IT FIRST, BEFORE ANYTHING ELSE IN THE CHAIN. Every other tool appends an `ok` line, so a run
measured afterwards sees the side effect of the chain it is part of and reports fresh over a job
that died a week ago.
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

from vault_paths import RUN_LOG_RELPATH, log_run

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
    "check_freshness": "this tool itself -- logged, never watched: an age limit on the watcher "
                       "is a regress",
}


def job_lists(vault_root):
    """(watched, on_demand) — read once, so the two can never disagree about the fallback.

    No config file is normal -- a project-only run has none, and both defaults stand. A config
    that exists and cannot be read is not normal, and falling back to the default over it
    checks a job list the user never chose while printing nothing about it. utf-8-sig is how
    that used to happen: Notepad writes a BOM, json.loads raises, the except swallowed it.

    A config that exists and has no `on_demand` key gets an EMPTY on-demand list, not the
    default above. That is the same rule one line further: substituting a classification the
    user never made is the silent fallback this docstring is about. Empty is honest, and the
    unclassified line then names the tools instead of guessing at them.

    Either shape is accepted for `on_demand`: the mapping that ships (name -> reason) or a bare
    list, which a user mirroring `jobs` will write. A list simply carries no reasons; refusing
    it would hard-fail an honest config over cosmetics.
    """
    config = Path(vault_root).resolve() / "00_Global" / "06_tools" / "jobs.json"
    if not config.exists():
        return list(DEFAULT_JOBS), dict(DEFAULT_ON_DEMAND)
    try:
        data = json.loads(config.read_text(encoding="utf-8-sig"))
        watched = list(data["jobs"])
        raw = data.get("on_demand") or {}
        on_demand = dict(raw) if isinstance(raw, dict) else {name: "" for name in raw}
        return watched, on_demand
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print(f"{config}: unreadable ({exc}) — falling back to {DEFAULT_JOBS}", file=sys.stderr)
        return list(DEFAULT_JOBS), dict(DEFAULT_ON_DEMAND)


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


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--vault", required=True, help="vault root")
    parser.add_argument("--log", help="run log path (defaults to the vault's own)")
    parser.add_argument("--max-age-hours", type=float, default=DEFAULT_MAX_AGE_HOURS)
    parser.add_argument("--jobs", nargs="*", help="override the expected job list")
    args = parser.parse_args(argv)

    vault_root = Path(args.vault).resolve()
    log_path = Path(args.log).resolve() if args.log else vault_root / RUN_LOG_RELPATH
    configured, on_demand = job_lists(vault_root)
    jobs = args.jobs if args.jobs else configured

    # Before any measurement, because the answer to "which list wins" is neither of them. Letting
    # the watched list win would be an invisible decision: the on-demand entry would sit there
    # doing nothing, and no run could show which of the two statements applies.
    #
    # The CONFIGURED list, not the effective one: the defect is in the file, so `--jobs` must not
    # be able to dodge it -- and `--jobs check_duplicates` is a deliberate one-off watch of an
    # on-demand tool, which is not a contradiction and must not be treated as one.
    both = sorted(set(configured) & set(on_demand))
    if both:
        print(f"{', '.join(both)}: in the watched list AND in the on-demand list. A job is one or "
              f"the other — watched means it may be late, on demand means it cannot be. Take it "
              f"out of one of them in {vault_root / '00_Global' / '06_tools' / 'jobs.json'}.",
              file=sys.stderr)
        log_run(vault_root, "check_freshness", "did-not-run", f"{len(both)} jobs in both lists")
        return 2

    if not jobs:
        print("did not run: no expected jobs configured", file=sys.stderr)
        log_run(vault_root, "check_freshness", "did-not-run", "no expected jobs configured")
        return 1

    if not log_path.exists() or log_path.stat().st_size == 0:
        print(f"did not run: no run log at {log_path}", file=sys.stderr)
        for job in jobs:
            print(f"{job}: did not run — no log", file=sys.stderr)
        print(f"0/{len(jobs)} jobs have a healthy run", file=sys.stderr)
        log_run(vault_root, "check_freshness", "did-not-run", f"no run log at {log_path}")
        return 1

    healthy, seen, lines, malformed = parse_log(log_path)
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

    # In neither list. The only real signal at this point: somebody built a tool and nobody
    # decided whether it is watched. It does NOT change the exit code -- an unclassified tool has
    # not failed, and a chain that goes red the first time a user adds a tool of their own is one
    # they will stop running.
    # `configured` is subtracted as well as `jobs`, so a `--jobs` override does not turn the rest
    # of the user's own watch list into news.
    unclassified = sorted(seen - set(jobs) - set(configured) - set(on_demand))

    print(
        f"{len(fresh)}/{len(jobs)} jobs fresh · {len(on_demand)} on demand · "
        f"{len(unclassified)} unclassified · {lines} log lines · "
        f"{malformed} malformed · threshold {args.max_age_hours}h"
    )
    for job, age_h in fresh:
        print(f"  {job}: {age_h:.1f}h ago")
    if unclassified:
        print(f"  neither watched nor listed as on demand: {', '.join(unclassified)}")

    status = "defects" if (problems or malformed) else "ok"
    log_run(vault_root, "check_freshness", status,
            f"{len(fresh)}/{len(jobs)} fresh · {len(unclassified)} unclassified")

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
            # utf-8-sig so a byte-order mark is not counted as a character of content.
            text = path.read_text(encoding="utf-8-sig", errors="replace")
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
"""Acceptance test: prove each guard reacts as specified to one input, on this machine.

Each fixture is built in its own throwaway vault under the system temp directory. Most hand a
guard bad input and require it to go red; the rest hand the tools input or behaviour the
structure explicitly allows and require them to stay green. Both halves are needed: a suite that
only ever sees bad input is exactly as blind as one that only ever sees good input. The counts
are derived from FIXTURES below, never written into a sentence here -- one of them changed sides
once, and a sentence would have gone on being wrong.

The verdict comes from process exit codes and from files on disk -- never from parsing console
text alone, which wraps at the terminal width and differs per shell. Where a printed line *is*
the specified behaviour it is read as well, never instead: fixtures 9 and 11 require a run to
name what it touched, and several red fixtures require a particular phrase or require silence.
SECTION 9 of the contract lists the three kinds.

    python acceptance.py            one pass
    python acceptance.py --repeat 10

Exit 0 only when every fixture behaved as specified in every pass.
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


def fixture_9_hand_made_folder_is_adopted(vault, project):
    """The second green-expected check, and the reason it is not a red one.

    A folder the user makes by hand is allowed by the structure, so the run must not go red
    over it -- but it must not swallow it either. What is checked here is all three parts:
    the folder survives, its note reaches an index, and the run names it on stdout. Drop the
    third and this passes over exactly the silent behaviour it exists to forbid.
    """
    (project / "99_extra").mkdir(exist_ok=True)
    write_note(project / "99_extra" / "verlorene-notiz.md", title="Verloren")
    code, out, _ = run_tool("build_index.py", "--vault", project)
    if code != 0 or not (project / "99_extra").is_dir():
        return False
    if "99_extra" not in out or "adopted" not in out:
        return False
    return "verlorene-notiz" in index_text(project, "99_extra")


def fixture_11_command_is_written_named_and_left_alone(vault, project):
    """The third green-expected check, and all three parts of it are load-bearing.

    Fixture 9 established the shape: an effect on disk, an effect in the content, and the line
    that says so. Here the same three are the whole specification of write_command.py -- the
    file appears, it distinguishes `--root` from `--vault` (the trap the command exists for),
    and the run names what it wrote. Drop the third and a tool that writes into
    `~/.claude/commands/` without a word passes this. That path is outside the vault, which is
    the one place operating rule 5 says nothing may happen quietly.

    `~/.claude/commands/` is also the only destination the tool has, so this fixture redirects
    `Path.home()` into the throwaway tree instead of checking a lesser path that ships to nobody.
    Without the redirect this would edit the config of whoever runs the acceptance driver.
    """
    home = vault.parent / "FakeHome"
    home.mkdir(parents=True, exist_ok=True)
    code, out, _ = run_tool("write_command.py", "--vault", vault,
                            "--shell", "posix", home=home)
    target = home / ".claude" / "commands" / "vaultkit.md"
    if code != 0 or not target.is_file():
        return False
    if target.name not in out:
        return False
    text = target.read_text(encoding="utf-8")
    if f'--root "{vault.as_posix()}"' not in text:
        return False
    if f'--vault "{project.as_posix()}"' not in text:
        return False
    # Second run: nothing said, nothing written, the hand edit still there.
    edited = text + "\nA line the user added.\n"
    target.write_text(edited, encoding="utf-8", newline="\n")
    _, second, _ = run_tool("write_command.py", "--vault", vault,
                            "--shell", "posix", home=home)
    if second.strip() or target.read_text(encoding="utf-8") != edited:
        return False

    # A file of the same name this kit did NOT write: refused, named, non-zero -- never a quiet
    # zero, which would let a setup report /vaultkit ready while a stranger holds the name.
    foreign = "---\ndescription: A command the user already had\n---\n\nMine.\n"
    target.write_text(foreign, encoding="utf-8", newline="\n")
    code, out, err = run_tool("write_command.py", "--vault", vault,
                              "--shell", "posix", home=home)
    return (code != 0 and target.name in (out + err)
            and target.read_text(encoding="utf-8") == foreign)


def fixture_10_project_disagrees_with_folder(vault, project):
    """The field that looked like it worked: nothing reads it, so only a guard can say so.

    Both directions in one fixture, because the asymmetry is the whole defect -- a note whose
    `project:` matches its folder behaved identically to one that contradicted it, which is
    exactly why the contradiction went unnoticed. Red on disagreement is only half the check;
    a guard that also fires on agreement would make the field unusable instead of advisory.
    """
    write_note(project / "00_Notes" / "falsches-projekt.md", title="Falsch einsortiert",
               project="Homelab")
    code, _, err = run_tool("build_index.py", "--vault", project)
    if code == 0 or "falsches-projekt.md" not in err or "Homelab" not in err:
        return False
    (project / "00_Notes" / "falsches-projekt.md").unlink()
    write_note(project / "00_Notes" / "richtiges-projekt.md", title="Richtig einsortiert",
               project=PROJECT)
    write_note(project / "00_Notes" / "ohne-projekt.md", title="Feld weggelassen")
    code, _, err = run_tool("build_index.py", "--vault", project)
    return code == 0 and "project" not in err


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


# The third column is what the fixture expects of the tool: "red" means the guard must refuse
# the input, "green" means the tool must accept it and keep working. Counted from here rather
# than written into the summary line -- the sentence "9 guards red, 1 control green" was true
# until a fixture changed sides, and nothing would have caught that.
FIXTURES = [
    ("0 healthy control: clean vault is green and stable", control_clean_vault_is_green, "green"),
    ("1 note without title", fixture_1_missing_title, "red"),
    ("2 markdown debris in summary", fixture_2_summary_debris, "red"),
    ("3 dead wikilink", fixture_3_dead_wikilink, "red"),
    ("4 forbidden character in filename", fixture_4_forbidden_filename, "red"),
    ("5 non-ASCII filename stays in the denominator", fixture_5_non_ascii_filename, "red"),
    ("6 second index run changes nothing", fixture_6_second_run_is_a_noop, "red"),
    ("7 suite runner on an empty directory", fixture_7_empty_suite_dir, "red"),
    ("8 freshness check without a run log", fixture_8_freshness_without_log, "red"),
    ("9 hand-made folder is adopted, indexed and named", fixture_9_hand_made_folder_is_adopted, "green"),
    ("10 project: disagreeing with its folder", fixture_10_project_disagrees_with_folder, "red"),
    ("11 /vaultkit command written, named and never overwritten",
     fixture_11_command_is_written_named_and_left_alone, "green"),
]

RED = sum(1 for _, _, kind in FIXTURES if kind == "red")
GREEN = len(FIXTURES) - RED


def one_pass(verbose=True):
    """Every fixture gets its own vault, so one fixture cannot poison the next."""
    results = []
    for label, fn, _kind in FIXTURES:
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
              f"{RED} guards red on bad input, {GREEN} green on input the structure allows "
              f"(pass {run})")

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

# Imported, never respelled: a second copy verifies a tree the tools no longer build.
from vault_paths import CATEGORY_FOLDERS, TEMPLATES_DIR, template_name  # noqa: E402

PROJECTS = ["ProjektEins", "ProjektZwei"]

# The stamp on the throwaway kit file this run "installs" from. Step 13 requires the folder to
# come out carrying exactly this, so the value has to be named once and read, never written twice.
SETUP_KIT_VERSION = "abcabcabcabc"

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


def run(cmd, cwd, expect_zero=True, label="", home=None):
    env = dict(os.environ)
    env.pop("PYTHONIOENCODING", None)
    env.pop("PYTHONUTF8", None)
    if home is not None:
        # Redirects Path.home() inside the subprocess. The only way to exercise a tool that
        # writes into the user's own config folder without writing into it. Both names are set
        # because Python reads USERPROFILE on Windows and HOME elsewhere.
        env["USERPROFILE"] = str(home)
        env["HOME"] = str(home)
        env.pop("HOMEDRIVE", None)
        env.pop("HOMEPATH", None)
    result = subprocess.run([str(c) for c in cmd], cwd=str(cwd), env=env, capture_output=True)
    out = result.stdout.decode("utf-8", errors="replace")
    err = result.stderr.decode("utf-8", errors="replace")
    if expect_zero and result.returncode != 0:
        raise Failed(f"{label or cmd[1]} exited {result.returncode}\n{out}\n{err}")
    if not expect_zero and result.returncode == 0:
        raise Failed(f"{label or cmd[1]} exited 0 but had to fail\n{out}\n{err}")
    return result.returncode, out, err


def tool(vault, script, *args, expect_zero=True, home=None):
    return run([sys.executable, str(vault / "00_Global" / "06_tools" / script), *args],
               cwd=vault, expect_zero=expect_zero, label=script, home=home)


def write_note(path, title, summary, body):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(f'---\ntitle: "{title}"\nsummary: "{summary}"\ncreated: "2026-07-27"\n---\n\n{body}\n',
                    encoding="utf-8", newline="\n")


def delivered_scripts():
    """The files a real install ends up with -- not whatever happens to sit next to this one.

    WHY THIS IS NOT A GLOB (2026-07-29): it was one, `TOOLS.glob("*.py")`, and in the repository
    that folder holds tools the user never receives. The verified tree was therefore richer than
    the delivered one, which is precisely why none of the thirteen steps could see a script
    leaking into or out of the delivery. build_kit.py owns that list; here it is asked.

    In an installed vault build_kit.py is absent -- it is not shipped either -- and there the
    folder *is* the answer, so the fallback is the folder. Two branches, one meaning.
    """
    try:
        import build_kit
    except ImportError:
        return sorted(p.name for p in TOOLS.glob("*.py")) + ["jobs.json"]
    return build_kit.delivered_files()


def build_vault(root):
    """Step 1-3: the folder tree, the shipped tools, the starting pages."""
    for project in ["00_Global"] + PROJECTS:
        for folder in CATEGORY_FOLDERS:
            (root / project / folder).mkdir(parents=True, exist_ok=True)
    dst = root / "00_Global" / "06_tools"
    for name in delivered_scripts():
        shutil.copy2(TOOLS / name, dst / name)
    # The stamp SECTION 8 writes during setup -- by running the shipped tool, exactly as the
    # contract now tells the agent to. This function used to write the file itself, which made
    # step 13 read back a value this file had just typed and call that a pass. The kit file is a
    # stand-in with a made-up stamp; what is under test is that `--stamp` puts that stamp on
    # disk and that upgrade.py reads it back.
    kit = root.parent / "the-kit-the-user-dropped-in.md"
    kit.write_text(f"<!-- kit-version: {SETUP_KIT_VERSION} -->\n\n# Kit\n",
                   encoding="utf-8", newline="\n")
    run([sys.executable, str(dst / "upgrade.py"), "--stamp", str(kit)],
        cwd=root, label="upgrade.py --stamp")
    for project, folder, name, title, summary, body in NOTES:
        write_note(root / project / folder / name, title, summary, body)
    (root / ".gitignore").write_text(
        ".obsidian/plugins/\n.obsidian/workspace.json\n.obsidian/graph.json\n"
        ".claude/*\n!.claude/commands/\n"
        "**/runs.log\n**/__pycache__/\n*.pyc\n",
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
    # No count in the string: acceptance.py exits non-zero unless every fixture behaved, and a
    # literal here goes stale the moment a fixture is added.
    if "checks behaved as specified" not in out:
        raise Failed(f"acceptance did not report its verdict: {out!r}")


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


@step("11 a project and a folder added by hand are scaffolded, adopted and stable")
def _s11(root):
    """What the user does the week after setup, which no earlier step covers.

    They make a folder in Obsidian's file pane. Both requirements of the promise are here:
    an empty project folder gets its categories, and a folder they invent gets an index
    instead of a complaint -- and the tree is still clean on the run after that.
    """
    (root / "ProjektDrei").mkdir()
    (root / "ProjektDrei" / "Rechnungen").mkdir(parents=True)
    write_note(root / "ProjektDrei" / "Rechnungen" / "eine-rechnung.md",
               "Eine Rechnung", "Was darauf stand.", "Betrag, Datum und wofuer sie ausgestellt war.")
    _, out, _ = tool(root, "build_index.py", "--root", ".")

    missing = [f for f in CATEGORY_FOLDERS if not (root / "ProjektDrei" / f).is_dir()]
    if missing:
        raise Failed(f"category folders not created in a hand-made project: {missing}")
    if "created" not in out or "adopted" not in out:
        raise Failed(f"the run changed the tree without saying so:\n{out}")
    adopted_index = root / "ProjektDrei" / "Rechnungen" / "INDEX - ProjektDrei Rechnungen.md"
    if "eine-rechnung" not in adopted_index.read_text(encoding="utf-8"):
        raise Failed("the hand-made folder has an index but the note is not in it")

    git_commit_all(root, "chore: a project added by hand")
    tool(root, "build_index.py", "--root", ".")
    _, status, _ = run(["git", "status", "--porcelain"], cwd=root, label="git status")
    if status.strip():
        raise Failed(f"tree not clean after scaffolding and a rerun:\n{status}")


@step("12 a note template per project, and a hand-edited one survives a rerun")
def _s12(root):
    """The two promises write_templates makes, neither of which any earlier step looks at.

    WHY THIS EXISTS (2026-07-29): steps 1-11 only ever inspect index files. A delivery that
    silently stopped writing templates altogether still reported every step green -- the gap was
    found by reading the tool, not by a red test. (That sentence quoted `11/11` until step 14
    landed and made it read as a current claim about a run with fourteen steps. History gets
    described, not counted.) The second half matters more than the first: every run prints
    "edit it freely, no run overwrites it", and until now nothing held the tool to it.
    """
    folder = root / TEMPLATES_DIR
    expected = ["00_Global"] + PROJECTS + ["ProjektDrei"]  # ProjektDrei is added by hand in step 11
    missing = [p for p in expected if not (folder / template_name(p)).is_file()]
    if missing:
        raise Failed(f"no note template written for: {missing}")

    # A template that comes back unchanged proves nothing unless it went in changed.
    victim = folder / template_name(PROJECTS[0])
    edited = victim.read_text(encoding="utf-8") + "\nfield the user added by hand\n"
    victim.write_text(edited, encoding="utf-8", newline="\n")
    tool(root, "build_index.py", "--root", ".")
    if victim.read_text(encoding="utf-8") != edited:
        raise Failed(f"a rerun overwrote a hand-edited template: {victim.name}")


@step("13 the tool folder knows which kit version installed it")
def _s13(root):
    """The one value the whole update path compares against, and nothing used to write it.

    WHY THIS EXISTS (2026-07-29): kit-version.txt was only ever written by upgrade.py's --apply
    branch, which means from the *second* version onwards. A freshly installed folder answered
    `installed: unknown`, and steps 1-12 stayed green through it -- not one of them looks at the
    update path.

    WHY IT STOPPED TESTING ITSELF (same day): the first version of this step passed because
    build_vault() had typed the value it then read back. SECTION 8 now runs
    `upgrade.py --stamp <kitfile>`, build_vault() does the same, and the value under test comes
    out of a file the tool parsed -- step 12's shape, not step 13's old one.

    Undo recipe, to watch it go red: copy tools/ somewhere, delete the two `if args.stamp:` lines
    from upgrade.py's main(), and run both drivers there. Measured on this machine 2026-07-29 --
    verify_setup 13/14, failing in step 1 with `upgrade.py --stamp exited 2`, and test_upgrade
    7/9. Both, which is the point of covering it in two places: the driver proves the setup does
    it, the suite proves the tool can.

    That 13/14 was 12/13 for one commit, because it was measured before step 14 existed and then
    typed rather than re-run. Nothing catches that: check_prose_claims() reads the contract, the
    SECTION 10 header and README.md, and never the docstrings of the scripts it embeds. A number
    in here is only as good as the last time somebody actually ran the recipe above.
    """
    tools = root / "00_Global" / "06_tools"
    stamp = tools / "kit-version.txt"
    if not stamp.is_file():
        raise Failed("no kit-version.txt beside the tools -- upgrade.py cannot say what is installed")
    installed = stamp.read_text(encoding="utf-8-sig").strip()
    if installed != SETUP_KIT_VERSION:
        raise Failed(f"the stamp beside the tools reads {installed!r}, not the "
                     f"{SETUP_KIT_VERSION!r} the kit file it was installed from carried")

    # A kit file carrying one block byte-identical to what is installed: upgrade.py then has
    # nothing to write, and the only thing under test is the line it prints first. It lives
    # outside the vault, which is where a downloaded kit file actually sits.
    jobs = (tools / "jobs.json").read_text(encoding="utf-8").rstrip()
    kit = root.parent / "newer-kit.md"
    kit.write_text(f"<!-- kit-version: ffffffffffff -->\n\n### `jobs.json`\n\n```json\n{jobs}\n```\n",
                   encoding="utf-8", newline="\n")
    _, out, _ = run([sys.executable, str(tools / "upgrade.py"), str(kit)], cwd=root,
                    label="upgrade.py")
    if f"installed: {installed}" not in out or "unknown" in out:
        raise Failed(f"upgrade.py did not read the installed stamp back:\n{out}")


@step("14 a /vaultkit command is written once, carries this vault's own paths, and is left alone")
def _s14(root):
    """The convenience the setup offers, held to the same three things as step 12.

    The command exists because `--vault` means a PROJECT after build_index.py and the ROOT after
    check_links.py, and a chain typed from memory gets that wrong. So the file existing proves
    nothing on its own -- what is checked is that the two invocations differ, that the second run
    leaves a hand edit alone, and that the vault gains nothing from the run.

    It goes to `~/.claude/commands/`, the only destination there is, with Path.home() redirected
    into this throwaway tree. An in-vault copy was offered once and removed: it loads only in a
    session started at the vault root, which is not how a sync command gets used.

    Undo recipes, measured on this machine 2026-07-30 against a copy of tools/:

      - Make the `if target.exists():` block in write_command.py's main() unreachable: the hand
        edit is eaten and the second run reports work. verify_setup 13/14, acceptance 11/12,
        test_write_command 8/12.
      - Remove `.claude` from SKIP_DIRS in vault_paths.py: the link checker counts a `.claude/`
        file in the vault as a note. verify_setup 13/14, test_write_command 11/12 -- and
        acceptance stays 12/12, because fixture 11 checks the file and the message, not the
        denominators. That gap is the reason this step carries the denominator half at all.
    """
    home = root.parent / "FakeHome"
    home.mkdir(parents=True, exist_ok=True)
    target = home / ".claude" / "commands" / "vaultkit.md"
    _, links_before, _ = tool(root, "check_links.py", "--vault", ".")

    _, out, _ = tool(root, "write_command.py", "--vault", str(root),
                     "--shell", "posix", home=home)
    if not target.is_file():
        raise Failed(f"no /vaultkit command at {target}\n{out}")
    if target.name not in out:
        raise Failed(f"a file was written outside the vault tree without being named:\n{out}")
    if (root / ".claude" / "commands").exists():
        raise Failed("a command was written into the vault, where it would not load")

    text = target.read_text(encoding="utf-8")
    root_arg = f'--root "{root.as_posix()}"'
    if root_arg not in text:
        raise Failed(f"the command never sweeps the whole vault with --root:\n{text[:400]}")
    for project in ["00_Global"] + PROJECTS:
        if f'--vault "{(root / project).as_posix()}"' not in text:
            raise Failed(f"no index line for {project} in the command")
    if f'--vault "{root.as_posix()}"' not in text:
        raise Failed("nothing in the command hands the vault root to the link checker")

    edited = text + "\n## 7 · A step the user added\n"
    target.write_text(edited, encoding="utf-8", newline="\n")
    _, second, _ = tool(root, "write_command.py", "--vault", str(root),
                        "--shell", "posix", home=home)
    if second.strip():
        raise Failed(f"the second run reported work it did not do:\n{second}")
    if target.read_text(encoding="utf-8") != edited:
        raise Failed("a rerun overwrote a hand-edited command file")

    # A `.claude/` folder in the vault is ordinary -- the user may keep settings beside their
    # notes -- and the guards must not count what is in it. Written by hand here, because the
    # command itself no longer lands in the vault at all.
    (root / ".claude").mkdir(exist_ok=True)
    (root / ".claude" / "settings.json").write_text("{}\n", encoding="utf-8", newline="\n")
    _, links_after, _ = tool(root, "check_links.py", "--vault", ".")
    if links_before != links_after:
        raise Failed(f"a file under .claude/ entered the note denominators:\n"
                     f"  before: {links_before.strip()}\n  after:  {links_after.strip()}")

    # The .gitignore promise, asked of git rather than read off the file: the agent's own state
    # stays out of the vault's history.
    code, _, _ = run(["git", "check-ignore", "-q", ".claude/settings.json"],
                     cwd=root, label="git check-ignore settings")
    if code != 0:
        raise Failed("the agent's own settings are versioned -- .claude/ must stay ignored")


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
from vault_paths import (
    CATEGORY_FOLDERS,
    RUN_LOG_RELPATH,
    TEMPLATES_DIR,
    category_index_name,
    project_index_name,
    root_index_name,
    template_name,
)


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
        self.assertIn("1 entries in 6 categories", out)
        text = self.index_text()
        self.assertIn("[[ProjektEins/00_Notes/eine-erkenntnis|Eine Erkenntnis]]", text)
        self.assertIn("Genau ein Satz.", text)

    def test_empty_category_still_gets_an_index(self):
        code, _, err = run_tool("build_index.py", "--vault", self.project)
        self.assertEqual(code, 0, err)
        for folder in ("00_Notes", "02_docs", "06_tools"):
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

    def test_note_written_with_a_bom_keeps_its_frontmatter(self):
        """#12. Recipe for the failure without the fix: change the encoding in read_frontmatter
        back from utf-8-sig to utf-8 and rerun this file. Measured that way on this machine --
        exit 1 with three defects on mit-bom.md (no frontmatter block, missing title, missing
        summary) and the entry titled after its filename instead of its title.

        "﻿".isspace() is False, so a byte-order mark survives strip() and the opening
        '---' never matches. Windows editors write one by default.
        """
        write_note(self.project / "00_Notes" / "mit-bom.md", title="Mit BOM",
                   summary="Aus Notepad gespeichert.", bom=True)
        code, out, err = run_tool("build_index.py", "--vault", self.project)
        self.assertEqual(code, 0, err)
        self.assertIn("1 entries", out)
        text = self.index_text()
        self.assertIn("[[ProjektEins/00_Notes/mit-bom|Mit BOM]]", text)
        self.assertIn("Aus Notepad gespeichert.", text)

    def test_a_bom_does_not_hide_a_real_defect(self):
        """The other half: the fix must not turn the guard off for BOM'd files."""
        write_note(self.project / "00_Notes" / "bom-ohne-titel.md", title=None, bom=True)
        code, _, err = run_tool("build_index.py", "--vault", self.project)
        self.assertEqual(code, 1)
        self.assertIn("bom-ohne-titel.md", err)
        self.assertIn("title", err)

    # ------------------------------------------------------------ project: is advisory (#15)

    def test_project_disagreeing_with_the_folder_is_a_defect(self):
        """#15. Recipe for the failure without the fix: delete the `declared = ...` assignment
        AND the `if declared and ...` block under it from collect_entries in build_index.py --
        cutting only the assignment leaves an orphaned defects.add() and measures something
        else. Re-measured that way on this machine 2026-07-29 -- 29 of 30 tests pass and this
        one fails with `AssertionError: 0 != 1`: the run exits 0, says nothing, and indexes the
        note under ProjektEins while its frontmatter goes on claiming Homelab. acceptance.py
        drops to 11/12 in the same state. The asymmetry is what made it hard to see: agreement
        behaved exactly the same, so the field looked like it worked.
        """
        write_note(self.project / "00_Notes" / "falsches-projekt.md",
                   title="Gehoert woandershin", project="Homelab")
        code, _, err = run_tool("build_index.py", "--vault", self.project)
        self.assertEqual(code, 1)
        self.assertIn("falsches-projekt.md", err)
        self.assertIn("Homelab", err)
        self.assertIn("ProjektEins", err)

    def test_project_matching_the_folder_is_silent(self):
        """A guard that fires on the agreeing case would make the field unusable."""
        write_note(self.project / "00_Notes" / "richtiges-projekt.md",
                   title="Gehoert hierher", project="ProjektEins")
        code, out, err = run_tool("build_index.py", "--vault", self.project)
        self.assertEqual(code, 0, err)
        self.assertNotIn("project", err)
        self.assertIn("1 entries", out)

    def test_a_missing_project_field_is_not_a_defect(self):
        """This is the promise the contract makes by writing `# optional` next to the field.

        Without this case, tightening the guard into a required field would go unnoticed --
        and 135 of the 339 notes in the vault this kit came from carry no `project:` at all.
        """
        write_note(self.project / "00_Notes" / "ohne-projekt.md", title="Kein Projektfeld")
        code, out, err = run_tool("build_index.py", "--vault", self.project)
        self.assertEqual(code, 0, err)
        self.assertNotIn("project", err)
        self.assertIn("1 entries", out)

    def test_a_quoted_project_value_compares_cleanly(self):
        """`project: "ProjektEins"` and `project: ProjektEins` are the same claim.

        _clean_scalar strips the quotes before anything compares them; without that, every
        quoted value in the vault -- which is how the contract writes them -- would be a defect.
        """
        path = self.project / "00_Notes" / "zitiert.md"
        path.write_text('---\ntitle: "Zitiert"\nsummary: "Wert in Anfuehrungszeichen."\n'
                        'project: "ProjektEins"\n---\n\nRumpf.\n', encoding="utf-8", newline="\n")
        code, out, err = run_tool("build_index.py", "--vault", self.project)
        self.assertEqual(code, 0, err)
        self.assertIn("1 entries", out)

    # ------------------------------------------------------- scaffolding and adoption (#6)

    def test_empty_project_folder_gets_its_categories(self):
        """Requirement 1 of #6: a project folder a user creates is empty and must not stay so."""
        fresh = self.vault / "ProjektNeu"
        fresh.mkdir()
        code, out, err = run_tool("build_index.py", "--vault", fresh)
        self.assertEqual(code, 0, err)
        for folder in CATEGORY_FOLDERS:
            self.assertTrue((fresh / folder).is_dir(), f"{folder} not created")
            self.assertTrue((fresh / folder / category_index_name("ProjektNeu", folder)).exists())
        self.assertIn("created", out)
        self.assertIn("ProjektNeu/00_Notes", out)

    def test_hand_made_folder_is_adopted_and_indexed(self):
        """Requirement 2 of #6: it stays where it is and gets an index of its own."""
        (self.project / "Rechnungen").mkdir()
        write_note(self.project / "Rechnungen" / "eine-rechnung.md", title="Eine Rechnung")
        code, out, err = run_tool("build_index.py", "--vault", self.project)
        self.assertEqual(code, 0, err)
        self.assertTrue((self.project / "Rechnungen").is_dir(), "the folder was moved or removed")
        text = self.index_text("Rechnungen")
        self.assertIn("[[ProjektEins/Rechnungen/eine-rechnung|Eine Rechnung]]", text)
        self.assertIn("1 entries in 7 categories", out)

    def test_adoption_is_announced_and_logged(self):
        """Adopting silently is the old defect wearing a green exit code.

        A renamed 06_tools once dropped a real run from 21 categories to 20 with no message.
        Adoption keeps the notes indexed; the printed line is what makes a typo'd folder name
        visible at all.
        """
        (self.project / "06_werkzeuge").mkdir()
        write_note(self.project / "06_werkzeuge" / "verlorene-notiz.md", title="Verloren")
        code, out, err = run_tool("build_index.py", "--vault", self.project)
        self.assertEqual(code, 0, err)
        self.assertIn("adopted", out)
        self.assertIn("ProjektEins/06_werkzeuge", out)
        log = (self.vault / RUN_LOG_RELPATH).read_text(encoding="utf-8")
        self.assertIn("1 adopted", log)

    def test_skip_dirs_are_never_adopted(self):
        """__pycache__ under 06_tools is normal. As a category it would be indexed forever."""
        (self.project / "__pycache__").mkdir()
        (self.project / ".obsidian").mkdir()
        code, out, err = run_tool("build_index.py", "--vault", self.project)
        self.assertEqual(code, 0, err)
        self.assertNotIn("__pycache__", out)
        self.assertNotIn(".obsidian", out)
        self.assertFalse((self.project / "__pycache__" / "INDEX - ProjektEins __pycache__.md").exists())

    def test_second_run_after_adoption_creates_nothing_new(self):
        (self.project / "Rechnungen").mkdir()
        run_tool("build_index.py", "--vault", self.project)
        before = {p: p.read_bytes() for p in self.project.rglob("INDEX - *.md")}
        code, out, err = run_tool("build_index.py", "--vault", self.project)
        after = {p: p.read_bytes() for p in self.project.rglob("INDEX - *.md")}
        self.assertEqual(code, 0, err)
        self.assertEqual(before, after)
        self.assertNotIn("created", out)   # nothing was missing the second time
        self.assertIn("adopted", out)      # but the folder is still worth naming

    # ------------------------------------------------------ note templates (#16)

    def test_a_template_is_written_for_every_project(self):
        """The other half of #15: the guard catches a wrong `project:`, the template prevents one.

        Nothing in Obsidian can fill this in by itself -- core Templates knows {{title}},
        {{date}} and {{time}}, and no folder variable at all. So the project name has to be in
        the file, and that means one file per project.
        """
        code, out, err = run_tool("build_index.py", "--root", self.vault)
        self.assertEqual(code, 0, err)
        template = self.vault / TEMPLATES_DIR / template_name("ProjektEins")
        self.assertTrue(template.exists(), f"{template} missing")
        text = template.read_text(encoding="utf-8")
        self.assertIn('project: "ProjektEins"', text)
        self.assertIn("{{title}}", text)
        self.assertIn("{{date}}", text)
        for field in ("title:", "summary:", "project:", "created:"):
            self.assertIn(field, text)
        # The other direction is the real test: a template shipping `generator:` invites someone
        # to fill it, and a note carrying that marker is declared derived and may be overwritten
        # or deleted by a rebuild. Without this line the field set grows back the next time
        # someone tidies up.
        #
        # Recipe, so the number below stays reproducible: copy tools/ somewhere, add the five
        # lines back to template_text() in vault_paths.py, run `python -m unittest
        # test_build_index` there. Measured on this machine 2026-07-29 -- 29/30, failing here
        # and nowhere else.
        for field in ("updated:", "issues:", "generator:", "retired:", "stale:"):
            self.assertNotIn(field, text)
        self.assertIn("template", out)
        self.assertIn(template.name, out)

    def test_a_hand_edited_template_survives_the_next_run(self):
        """A template is there to be edited. A tool that resets it every run eats the edit."""
        run_tool("build_index.py", "--root", self.vault)
        template = self.vault / TEMPLATES_DIR / template_name("ProjektEins")
        mine = template.read_text(encoding="utf-8").replace(
            "created: {{date}}\n", "created: {{date}}\nowner:\n")
        template.write_text(mine, encoding="utf-8", newline="\n")
        code, out, err = run_tool("build_index.py", "--root", self.vault)
        self.assertEqual(code, 0, err)
        self.assertEqual(template.read_text(encoding="utf-8"), mine)
        self.assertNotIn("template", out)   # nothing was missing the second time

    def test_templates_are_neither_a_project_nor_a_category(self):
        """_templates sits at the vault root, and a directory at the vault root is a project.

        Recipe for the failure without the exemption: drop TEMPLATES_DIR from SKIP_DIRS in
        vault_paths.py and rerun. Re-measured on this machine 2026-07-29 -- 28/30 here, 11/12 in
        acceptance.py and 13/14 in verify_setup.py. The run then reports six `created
        _templates/<category>` lines and writes a `TEMPLATE - _templates.md` for the folder it
        just mistook for a project.
        """
        run_tool("build_index.py", "--root", self.vault)
        code, out, err = run_tool("build_index.py", "--root", self.vault)
        self.assertEqual(code, 0, err)
        folder = self.vault / TEMPLATES_DIR
        self.assertTrue(folder.is_dir())
        # One per project and nothing else -- no category folders, no index of its own.
        self.assertEqual(sorted(p.name for p in folder.iterdir()),
                         [template_name("00_Global"), template_name("ProjektEins")])
        root_index = (self.vault / root_index_name(self.vault)).read_text(encoding="utf-8")
        self.assertNotIn(TEMPLATES_DIR, root_index)
        self.assertIn("2 projects", out)

    def test_a_note_made_from_the_template_passes_every_guard(self):
        """The template is only worth having if what it produces is accepted.

        Obsidian substitutes {{title}} and {{date}}; everything else goes in as it stands, so
        this fills those two the way Obsidian would.

        Since the template shrank to four fields, the assertions below check the inverse case: a
        note carrying no `generator:`, `retired:` or `stale:` at all must get no marker either.
        Same promise as before, made over the absent key instead of the empty one -- and this is
        the only place that notices if a reader ever tests presence instead of value.
        """
        run_tool("build_index.py", "--root", self.vault)
        text = (self.vault / TEMPLATES_DIR / template_name("ProjektEins")).read_text(
            encoding="utf-8")
        text = text.replace("{{title}}", "Eine Erkenntnis").replace("{{date}}", "2026-07-29")
        text = text.replace("summary:\n", 'summary: "Genau ein Satz."\n')
        note = self.project / "00_Notes" / "eine-erkenntnis.md"
        note.write_text(text + "\nRumpf.\n", encoding="utf-8", newline="\n")
        code, out, err = run_tool("build_index.py", "--vault", self.project)
        self.assertEqual(code, 0, err)
        text = self.index_text()
        self.assertIn("[[ProjektEins/00_Notes/eine-erkenntnis|Eine Erkenntnis]]", text)
        self.assertNotIn("generated", text)   # an absent generator: marks nothing
        self.assertNotIn("[retired", text)
        self.assertNotIn("[stale", text)

    def test_a_new_project_gets_its_template_on_the_next_root_run(self):
        """Projects arrive later. A template set that only matches the first run is a trap."""
        run_tool("build_index.py", "--root", self.vault)
        (self.vault / "ProjektSpaeter").mkdir()
        code, out, err = run_tool("build_index.py", "--root", self.vault)
        self.assertEqual(code, 0, err)
        later = self.vault / TEMPLATES_DIR / template_name("ProjektSpaeter")
        self.assertTrue(later.exists(), f"{later} missing")
        self.assertIn('project: "ProjektSpaeter"', later.read_text(encoding="utf-8"))
        self.assertIn(later.name, out)
        self.assertNotIn(template_name("ProjektEins"), out)   # the existing one is not touched

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


def note_with_body(path, body, title="Ein Titel", bom=False):
    write_note(path, title=title, bom=bom)
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

    def test_a_bom_does_not_hide_a_duplicate(self):
        """#12. Recipe without the fix: put encoding="utf-8" back in body_shingles.

        A BOM makes startswith("---") false, so the frontmatter is compared as body text and
        its words dilute the overlap. Two byte-identical bodies then score below 1.0 instead
        of at it.

        The threshold is raised to 0.9 on purpose. At the default 0.75 this exact pair still
        scores just above the line and the test passes without the fix -- measured that way
        on this machine, which is the only reason the number is here.
        """
        note_with_body(self.notes / "eins.md", SAME_BODY, title="Eins")
        note_with_body(self.notes / "kopie.md", SAME_BODY, title="Kopie", bom=True)
        code, out, err = run_tool("check_duplicates.py", "--vault", self.vault,
                                  "--threshold", "0.9")
        self.assertEqual(code, 1, out)
        self.assertIn("1 pairs flagged of 1 compared", out)
        self.assertIn("kopie.md", err)

    def test_non_ascii_filename_survives_the_subprocess_round_trip(self):
        note_with_body(self.notes / "Übergröße.md", SAME_BODY, title="Eins")
        note_with_body(self.notes / "Ärgernis.md", SAME_BODY, title="Zwei")
        code, _, err = run_tool("check_duplicates.py", "--vault", self.vault)
        self.assertEqual(code, 1)
        self.assertIn("Übergröße.md", err + "")
        self.assertIn("Ärgernis.md", err)

    def test_a_root_run_leaves_exactly_one_run_log(self):
        """The run log belongs at the vault root, and a root run puts it nowhere else.

        `log_run` builds its path relative to the directory it was handed
        (`vault_paths.RUN_LOG_RELPATH`). SECTION 8 prescribed `--vault <Project>` until
        2026-07-30, so the chain wrote `<Project>/00_Global/06_tools/runs.log` — a folder the
        generator adopts as a category on its next pass. Measured on cold run 2: 21 categories
        became 24, exit 0, three `adopted` lines as the only signal. Nothing went red, because
        no run reads the contract's prose.

        Undo recipe: put `--vault <Project>` back on `src/contract.md:896`, then run this tool
        against `<vault>/ProjektEins` instead of the root. A second `00_Global` appears under the
        project and this check goes red. Without that line the number is not reproducible.
        """
        note_with_body(self.notes / "eins.md", SAME_BODY, title="Eins")
        note_with_body(self.notes / "zwei.md", OTHER_BODY, title="Zwei")
        code, _, err = run_tool("check_duplicates.py", "--vault", self.vault)
        self.assertEqual(code, 0, err)

        logs = sorted(p.relative_to(self.vault).as_posix() for p in self.vault.rglob("runs.log"))
        self.assertEqual(logs, ["00_Global/06_tools/runs.log"], f"run logs found: {logs}")
        globals_ = sorted(p.relative_to(self.vault).as_posix()
                          for p in self.vault.rglob("00_Global") if p.is_dir())
        self.assertEqual(globals_, ["00_Global"], f"00_Global folders found: {globals_}")


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

    def test_jobs_config_written_with_a_bom_is_still_read(self):
        """#12. Recipe without the fix: put encoding="utf-8" back in job_lists.

        json.loads then raises on the BOM, the except returned the default job list, and the
        check measured a set of jobs the user never configured -- without a word. Measured
        that way on this machine: a jobs.json naming only build_index produced a run that
        also demanded check_links.
        """
        config = self.vault / "00_Global" / "06_tools" / "jobs.json"
        config.parent.mkdir(parents=True, exist_ok=True)
        config.write_text('{"jobs": ["build_index"]}', encoding="utf-8-sig", newline="\n")
        self.write_log(f"{stamp(1)}\tbuild_index\tok\t0 defects")
        code, out, err = run_tool("check_freshness.py", "--vault", self.vault)
        self.assertEqual(code, 0, out + err)
        self.assertIn("1/1 jobs fresh", out)

    def test_an_unreadable_jobs_config_says_so_instead_of_defaulting_quietly(self):
        config = self.vault / "00_Global" / "06_tools" / "jobs.json"
        config.parent.mkdir(parents=True, exist_ok=True)
        config.write_text("{ das ist kein json", encoding="utf-8", newline="\n")
        self.write_log(f"{stamp(1)}\tbuild_index\tok\t0 defects")
        code, out, err = run_tool("check_freshness.py", "--vault", self.vault)
        self.assertIn("jobs.json", err)
        self.assertIn("unreadable", err)

    def test_non_ascii_job_name_survives_the_subprocess_round_trip(self):
        self.write_log(f"{stamp(1)}\tbuild_index\tok\t0 defects")
        code, _, err = run_tool("check_freshness.py", "--vault", self.vault, "--jobs", "Zählung")
        self.assertEqual(code, 1)
        self.assertIn("Zählung", err)

    # ------------------------------------------------- the second list (#3)

    def write_config(self, text):
        config = self.vault / "00_Global" / "06_tools" / "jobs.json"
        config.parent.mkdir(parents=True, exist_ok=True)
        config.write_text(text, encoding="utf-8", newline="\n")
        return config

    def test_an_on_demand_tool_stays_out_of_the_unclassified_line(self):
        """The reason the second list exists at all.

        Every tool logs, so without it the "nobody watches this" line names every tool in the
        vault on every run -- noise, and a report nobody reads is one that gets dropped from the
        chain. Classified means silent here, and only here.

        Recipe without the fix, measured on this machine 2026-07-30: drop the `- set(on_demand)`
        term from `unclassified` in check_freshness.py. test_check_freshness 13/15 -- this case
        and the bare-list one, which asserts the same count from the other shape. The healthy
        control stays green, which is why the control alone could never have caught it.
        """
        self.write_config('{"jobs": ["build_index"], '
                          '"on_demand": {"mein_werkzeug": "laeuft von Hand"}}')
        self.write_log(f"{stamp(1)}\tbuild_index\tok\t0 defects",
                       f"{stamp(5)}\tmein_werkzeug\tok\tetwas getan")
        code, out, err = run_tool("check_freshness.py", "--vault", self.vault)
        self.assertEqual(code, 0, out + err)
        self.assertIn("1/1 jobs fresh", out)
        self.assertIn("1 on demand", out)
        self.assertIn("0 unclassified", out)
        self.assertNotIn("mein_werkzeug", out)

    def test_an_unclassified_tool_is_named_and_does_not_change_the_exit_code(self):
        """The only real signal here: somebody built a tool and nobody decided about it.

        It must be loud enough to see and cheap enough to ignore. Red would be neither -- the
        first tool a user writes for themselves would make the chain red every run, and a check
        that is always red gets switched off rather than answered.

        Recipe without the fix, measured on this machine 2026-07-30: return 1 when `unclassified`
        is non-empty. test_check_freshness 13/15 -- this case and the missing-key one, both on
        the exit code alone and with their output unchanged, which is the distinction they are
        here to hold.
        """
        self.write_log(f"{stamp(1)}\tbuild_index\tok\t0 defects",
                       f"{stamp(2)}\tmein_werkzeug\tok\tetwas getan")
        code, out, err = run_tool("check_freshness.py", "--vault", self.vault,
                                  "--jobs", "build_index")
        self.assertEqual(code, 0, out + err)
        self.assertIn("1 unclassified", out)
        self.assertIn("mein_werkzeug", out)

    def test_a_job_in_both_lists_stops_the_run_instead_of_picking_one(self):
        """Exit 2, and deliberately not "watched wins".

        Picking a winner leaves the losing entry sitting in the file doing nothing, and no run
        can then show which of the two statements applies. Stopping is the only outcome that
        makes the contradiction visible where it lives, which is the config file.

        Recipe without the fix, measured on this machine 2026-07-30: delete the `both` block from
        main(). test_check_freshness 14/15 -- this case and nothing else. The tool then reports
        the job as watched and never says that its own config says otherwise.
        """
        self.write_config('{"jobs": ["build_index", "mein_werkzeug"], '
                          '"on_demand": {"mein_werkzeug": "laeuft von Hand"}}')
        self.write_log(f"{stamp(1)}\tbuild_index\tok\t0 defects")
        code, out, err = run_tool("check_freshness.py", "--vault", self.vault)
        self.assertEqual(code, 2, out + err)
        self.assertIn("mein_werkzeug", err)
        self.assertIn("jobs.json", err)
        self.assertNotIn("jobs fresh", out, "it measured anyway over a config it called broken")

    def test_a_config_without_the_second_key_does_not_borrow_the_built_in_one(self):
        """A present config that gets silently completed measures a list the user never chose.

        That is the same defect as the BOM case two tests up, one level quieter: the file is
        readable, so nothing warns, and the tool would classify three tools on the strength of a
        default the user cannot see. Empty is the honest reading, and the unclassified line then
        names them so the decision is theirs.

        Recipe without the fix, measured on this machine 2026-07-30: make the missing key fall
        back to DEFAULT_ON_DEMAND in job_lists(). test_check_freshness 14/15 -- this case and
        nothing else. check_duplicates disappears from the output and the count reads
        `3 on demand` against a config that says nothing about any of them.
        """
        self.write_config('{"jobs": ["build_index"]}')
        self.write_log(f"{stamp(1)}\tbuild_index\tok\t0 defects",
                       f"{stamp(3)}\tcheck_duplicates\tok\t0 flagged")
        code, out, err = run_tool("check_freshness.py", "--vault", self.vault)
        self.assertEqual(code, 0, out + err)
        self.assertIn("0 on demand", out)
        self.assertIn("check_duplicates", out)

    def test_the_second_list_may_also_be_written_as_a_bare_list(self):
        """A user mirroring the shape of `jobs` writes a list. It carries no reasons, and that
        is the only thing it loses -- refusing it would hard-fail an honest config over
        cosmetics.

        Recipe without the fix, measured on this machine 2026-07-30: drop the
        `isinstance(raw, dict)` branch from job_lists(). test_check_freshness 14/15 -- this case
        and nothing else. `dict(["mein_werkzeug"])` raises ValueError, which the config reader
        already catches, so the whole file is declared unreadable and BOTH lists fall back to
        the built-in ones: the run then demands check_links, which the log never mentions, and
        exits 1 over a config that was merely written in the other shape.
        """
        self.write_config('{"jobs": ["build_index"], "on_demand": ["mein_werkzeug"]}')
        self.write_log(f"{stamp(1)}\tbuild_index\tok\t0 defects",
                       f"{stamp(2)}\tmein_werkzeug\tok\tetwas getan")
        code, out, err = run_tool("check_freshness.py", "--vault", self.vault)
        self.assertEqual(code, 0, out + err)
        self.assertIn("1 on demand", out)
        self.assertIn("0 unclassified", out)

    def test_the_check_logs_its_own_run_like_every_other_tool(self):
        """Otherwise "the freshness check runs in the chain" is a claim about a command file.

        Delete the step from `/vaultkit` and a log with no check_freshness line in it looks
        exactly like a check that ran and found nothing. The line is what tells those two apart,
        and it is why check_freshness stands in the on-demand list rather than nowhere.

        Recipe without the fix, measured on this machine 2026-07-30: remove the log_run call from
        the success path in main(). test_check_freshness 14/15 -- this case and nothing else,
        because no other case reads the log back after the run.
        """
        self.write_log(f"{stamp(1)}\tbuild_index\tok\t0 defects")
        code, out, err = run_tool("check_freshness.py", "--vault", self.vault,
                                  "--jobs", "build_index")
        self.assertEqual(code, 0, out + err)
        written = self.log.read_text(encoding="utf-8").splitlines()
        mine = [line for line in written if "\tcheck_freshness\t" in line]
        self.assertEqual(len(mine), 1, f"no line of its own in {written}")
        self.assertIn("\tok\t", mine[0])
        # It reads before it writes, so its own line must not be in the denominator it reports.
        self.assertIn("1 log lines", out)


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

    def test_a_bom_does_not_break_fence_detection_on_the_first_line(self):
        """#12, the narrowest of the four. Recipe without the fix: put encoding="utf-8" back
        in the read in main().

        FENCE anchors at ^\\s* and a byte-order mark is not \\s, so a note that OPENS with a
        code fence loses fence detection on line 1: the fence never closes either, and the
        wikilink inside it is reported broken. The note is right and the guard is wrong.
        """
        source = self.notes / "syntax-doku-mit-bom.md"
        source.write_text("```\n[[nur-ein-beispiel]]\n```\n", encoding="utf-8-sig", newline="\n")
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

    def test_stamp_records_the_version_without_writing_anything_else(self):
        """The first install's only writer. Nothing else puts a version beside a fresh folder.

        `--apply` above covers the second kit onwards. Until --stamp existed, the first one was
        covered by nobody: the contract told the agent to type the twelve characters by hand,
        and verify_setup's step 13 read back a value its own fixture had written.
        """
        kit = kit_file(self.tmp / "kit.md", {"build_index.py": "print('new')"},
                       version="0f1e2d3c4b5a")
        code, out, err = run_upgrade(self.tools, "--stamp", kit)
        self.assertEqual(code, 0, err)
        self.assertEqual((self.tools / "kit-version.txt").read_text(encoding="utf-8").strip(),
                         "0f1e2d3c4b5a")
        self.assertEqual((self.tools / "build_index.py").read_text(encoding="utf-8"),
                         "print('old')\n", "--stamp wrote a script file")

    def test_stamp_refuses_a_file_with_no_version_line(self):
        """`unversioned` would be compared against every future kit and never match."""
        kit = self.tmp / "old-kit.md"
        kit.write_text("### `build_index.py`\n\n```python\nprint('new')\n```\n",
                       encoding="utf-8", newline="\n")
        code, out, err = run_upgrade(self.tools, "--stamp", kit)
        self.assertNotEqual(code, 0, "a file with no stamp must not produce one")
        self.assertFalse((self.tools / "kit-version.txt").exists(),
                         "a refused stamp still landed on disk")
        self.assertIn("kit-version", out + err)

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
        self.assertEqual(category_index_name("ProjektEins", "02_docs"), "INDEX - ProjektEins docs.md")
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

### `test_write_command.py`

```python
"""Suite for write_command.py.

The command file exists to answer three traps in the SECTION 8 chain, so the cases that matter
are not "a file appeared" but "the file answers them". `--vault` means a PROJECT after
build_index.py and the ROOT after check_links.py; getting that backwards is the failure the
command is written to prevent, and a test that only checks the file exists would pass over it.

THE DESTINATION IS THE USER'S OWN `~/.claude/commands/`, AND IT IS THE ONLY ONE. That is also
what makes this suite dangerous to write badly: run it against the real home folder and it edits
the setup of whoever runs it. Every case here redirects `Path.home()` into a throwaway folder via
`run_tool(home=...)`, so the tool takes its real path, writes for real, and touches nothing
outside the tempdir. Checking the path as a value only -- which is what this suite did while an
in-vault option still existed -- left the one destination that ships completely untested.
"""

import shutil
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from _testkit import make_vault, run_tool, write_note  # noqa: E402
from vault_paths import project_dirs  # noqa: E402

import write_command  # noqa: E402

COMMAND_RELPATH = Path(".claude") / "commands" / "vaultkit.md"


class WriteCommandTest(unittest.TestCase):
    def setUp(self):
        self.vault = make_vault(("ProjektEins", "ProjektZwei"))
        # A stand-in for the user's home folder, inside the same tempdir the vault lives in.
        self.home = self.vault.parent / "FakeHome"
        self.home.mkdir(parents=True, exist_ok=True)
        self.target = self.home / COMMAND_RELPATH

    def tearDown(self):
        shutil.rmtree(self.vault.parent, ignore_errors=True)

    def write(self, *extra):
        return run_tool("write_command.py", "--vault", self.vault, *extra, home=self.home)

    # ------------------------------------------------------------------ control

    def test_healthy_control_a_command_is_written_and_named(self):
        code, out, err = self.write()
        self.assertEqual(code, 0, err)
        self.assertTrue(self.target.is_file(), f"no command file: {out} {err}")
        self.assertIn("vaultkit.md", out, "it wrote a file outside the vault without saying so")

    def test_it_writes_into_the_home_folder_and_not_into_the_vault(self):
        """The destination is not a preference. A copy under the vault root would load only in a
        session started at that root, which is why the option was taken out again -- and why the
        vault must come back from this run with nothing added to it."""
        self.write()
        self.assertTrue(self.target.is_file())
        self.assertFalse((self.vault / COMMAND_RELPATH).exists(),
                         "a command was written into the vault, where it would not load")
        self.assertFalse((self.vault / ".claude").exists())

    def test_the_frontmatter_carries_a_description_and_nothing_else(self):
        """All five documented fields are optional. Every one that is set is one more thing to
        keep true, and a command needs exactly one of them to be findable.

        The marker lives on the first line of the BODY for this reason: YAML frontmatter has to
        start at byte zero, and a comment in front of it takes `description:` with it.
        """
        self.write()
        text = self.target.read_text(encoding="utf-8")
        self.assertTrue(text.startswith("---\n"), "something got in front of the frontmatter")
        block = text.split("---")[1]
        keys = [line.split(":")[0] for line in block.strip().splitlines() if ":" in line]
        self.assertEqual(keys, ["description"])
        self.assertNotIn(write_command.MARKER_PREFIX, block, "the marker is inside the frontmatter")

    # -------------------------------------------------------------- the traps

    def test_vault_means_a_project_for_the_generator_and_the_root_for_the_link_checker(self):
        """The trap the command exists for: one flag name, two meanings, three tools.

        check_links.py wants the vault root, build_index.py wants one project directory. A
        command that puts the same path after every `--vault` is wrong in two places out of
        three, and both wrong invocations exit non-zero at the user rather than here.
        """
        self.write("--shell", "powershell")
        root = write_command.show(self.vault, "powershell")
        lines = self.target.read_text(encoding="utf-8").splitlines()

        projects = project_dirs(self.vault)   # counted, never typed -- 00_Global is one of them
        generator = [line for line in lines if "build_index.py" in line and "--vault" in line]
        self.assertEqual(len(generator), len(projects),
                         "one build_index --vault line per project, no more and no fewer")
        for line in generator:
            self.assertNotIn(f"--vault {root}", line,
                             "the generator was handed the vault root, which it refuses")
        for project in projects:
            self.assertTrue(any(write_command.show(project, "powershell") in line
                                for line in generator), f"{project.name} has no index line")

        links = [line for line in lines if "check_links.py" in line]
        self.assertEqual(len(links), 1)
        self.assertIn(f"--vault {root}", links[0],
                      "the link checker was handed something narrower than the vault root")

    def test_the_freshness_check_is_the_first_step_and_the_steps_are_numbered_through(self):
        """Kit #3. Order is the fourth trap, and the only one that cannot be seen in a single line.

        Every other step in this chain appends an `ok` line to the run log. A freshness check
        measured after them reads the side effect of its own chain and reports the jobs as fresh
        -- including a scheduled one that stopped firing a week ago. So its position is the
        behaviour, not its presence, and both halves are checked here: it comes first, and no
        writer runs before it.

        The numbering is held too, because renumbering by hand is how a chain ends up with two
        step 3s and a reader who skips one.

        Recipe without the fix, measured on this machine 2026-07-30: move the check_freshness
        command line in command_text() below the build_index loop, leaving the headings where
        they are. test_write_command 13/14 -- this case and nothing else, which is the point of
        having it: the command still contains every tool, and only the order is wrong.
        """
        self.write("--shell", "powershell")
        lines = self.target.read_text(encoding="utf-8").splitlines()

        headings = [line for line in lines if line.startswith("## ") and " · " in line]
        numbers = [int(line.split()[1]) for line in headings]
        self.assertEqual(numbers, list(range(1, len(numbers) + 1)),
                         f"the steps are not numbered through: {headings}")
        # Runnable lines only. The prose above step 1 names `build_index.py` as a warning that it
        # writes, and matching that would have this test pass on the wrong evidence.
        def first(needle):
            return next(i for i, line in enumerate(lines)
                        if line.startswith("- `python ") and needle in line)

        freshness = first("check_freshness.py")
        self.assertLess(lines.index(headings[0]), freshness)
        self.assertLess(freshness, lines.index(headings[1]),
                        f"the freshness command is not inside step 1: {headings[0]}")
        for writer in ("build_index.py", "check_links.py", "check_duplicates.py", "run_suites.py"):
            self.assertLess(freshness, first(writer),
                            f"{writer} logs before the freshness check reads the log")

    def test_the_sweep_uses_root_and_says_why(self):
        """`--vault` alone leaves the root index on yesterday's count, green and silent."""
        self.write("--shell", "powershell")
        text = self.target.read_text(encoding="utf-8")
        self.assertIn(f"--root {write_command.show(self.vault, 'powershell')}", text)
        self.assertIn("`--root`, not `--vault`", text)

    def test_the_tool_folder_is_written_as_a_full_path(self):
        """`06_tools/` resolves from the vault root and nowhere else."""
        self.write("--shell", "posix")
        text = self.target.read_text(encoding="utf-8")
        tools = (self.vault / "00_Global" / "06_tools").as_posix()
        self.assertIn(tools, text)
        for line in text.splitlines():
            if line.startswith("- `python "):
                self.assertIn(tools, line, f"a bare tool path slipped in: {line}")

    # ------------------------------------------------------------ failure modes

    def test_the_second_run_writes_nothing_and_says_nothing(self):
        """A command file is there to be edited. Silence on the second run is the whole promise:
        it means nothing was missing, and runs.log carries the run either way."""
        self.write()
        before = self.target.read_bytes()
        code, out, err = self.write()
        self.assertEqual(code, 0, err)
        self.assertEqual(out.strip(), "", "the second run reported work it did not do")
        self.assertEqual(self.target.read_bytes(), before)

    def test_a_foreign_command_of_the_same_name_is_named_and_goes_red(self):
        """The other half of "already there", and the half that must not be silent.

        In ~/.claude/commands/ the user may already have a /vaultkit of their own. Nothing is
        overwritten -- but nothing is written either, and a zero exit there would let the setup
        report the command as ready while the stranger keeps the name. Both directions are
        checked here, because the guard is only worth having if it can tell them apart.

        This is the case that could not be tested at all while it only ran against the vault
        copy: the collision it guards against happens in the home folder, by definition.
        """
        self.target.parent.mkdir(parents=True, exist_ok=True)
        self.target.write_text("---\ndescription: My own command\n---\n\nDo my thing.\n",
                               encoding="utf-8", newline="\n")
        mine = self.target.read_bytes()

        code, out, err = self.write()
        self.assertNotEqual(code, 0, "a foreign command was passed over silently")
        self.assertIn(str(self.target), out + err, "the path holding the name was not shown")
        self.assertEqual(self.target.read_bytes(), mine, "a foreign command was overwritten")

    def test_our_own_file_is_recognised_by_its_marker_not_by_its_path(self):
        """A vault that moved is still our file. Re-checking the path inside would call it a
        stranger and turn a working setup red for having been relocated."""
        self.write()
        text = self.target.read_text(encoding="utf-8")
        self.assertIn(write_command.MARKER_PREFIX, text)
        moved = text.replace(self.vault.as_posix(), "/somewhere/else/Vault")
        self.target.write_text(moved, encoding="utf-8", newline="\n")
        code, out, err = self.write()
        self.assertEqual(code, 0, err)
        self.assertEqual(out.strip(), "")
        self.assertEqual(self.target.read_text(encoding="utf-8"), moved)

    def test_a_hand_edited_command_survives_the_next_run(self):
        """One that comes back unchanged proves nothing unless it went in changed."""
        self.write()
        mine = self.target.read_text(encoding="utf-8") + "\n## Mein eigener Schritt\n"
        self.target.write_text(mine, encoding="utf-8", newline="\n")
        code, _, err = self.write()
        self.assertEqual(code, 0, err)
        self.assertEqual(self.target.read_text(encoding="utf-8"), mine)

    def test_a_dot_claude_folder_inside_the_vault_stays_out_of_the_denominators(self):
        """Configuration is not knowledge, and a guard that counts it reports a wrong n/m.

        The command no longer lands in the vault, but a `.claude/` folder there is ordinary --
        the user may keep project settings beside their notes, and the setup itself is often
        started in such a folder. So the guards are held to skipping it, with a file written by
        hand rather than by the tool.

        Measured 2026-07-29 with `.claude` missing from SKIP_DIRS: one such file took
        check_links.py from 26 files scanned to 27, check_duplicates.py from 4 notes to 5 and
        from 6 compared pairs to 10, and the generator from 26 distinct filenames to 27. Nothing
        went red, which is exactly why it needs a test -- the numbers were quietly wrong and no
        run had a reason to mention it.

        Recipe without the fix: take ".claude" out of SKIP_DIRS in vault_paths.py and run this
        suite there; this case fails and no other does.
        """
        write_note(self.vault / "ProjektEins" / "00_Notes" / "eine-erkenntnis.md",
                   title="Eine Erkenntnis")
        run_tool("build_index.py", "--root", self.vault)
        before = [run_tool(script, "--vault", self.vault)[1]
                  for script in ("check_links.py", "check_duplicates.py")]

        intruder = self.vault / COMMAND_RELPATH
        intruder.parent.mkdir(parents=True, exist_ok=True)
        intruder.write_text("---\ndescription: Something the user keeps here\n---\n\nBody.\n",
                            encoding="utf-8", newline="\n")
        after = [run_tool(script, "--vault", self.vault)[1]
                 for script in ("check_links.py", "check_duplicates.py")]
        self.assertEqual(before, after,
                         "a file under .claude/ changed what the guards count as notes")

    def test_a_vault_without_projects_is_refused_not_written_empty(self):
        """A command listing no projects is a working file that does nothing. It means the wrong
        path was given, and that has to be said, not written out."""
        empty = self.vault.parent / "NotAVault"
        empty.mkdir()
        code, out, err = run_tool("write_command.py", "--vault", empty, home=self.home)
        self.assertNotEqual(code, 0, "an empty vault produced a command file")
        self.assertIn("no projects", out + err)
        self.assertFalse(self.target.exists())

    def test_there_is_exactly_one_destination_and_it_is_the_home_folder(self):
        """`target_path()` takes no argument on purpose. A parameter here would be the door back
        to an in-vault copy, and that copy is the thing that got removed -- it loads only in a
        session started at the vault root, which is not how anyone runs a sync command."""
        self.assertEqual(write_command.target_path(),
                         Path.home() / ".claude" / "commands" / "vaultkit.md")


if __name__ == "__main__":
    unittest.main(verbosity=1)
```

---

*Generated by `tools/build_kit.py`. Edit the sources, never this file.*
*Source and newest published copy: https://github.com/nibor1896/claude-obsidian-vault-kit*
*Compare the `kit-version` at the top against the published file to see whether this copy is current.*
