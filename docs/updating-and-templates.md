# The header is there before you type, and the folder knows which kit wrote it

Two things the kit does that are easy to miss, because both of them are quiet when they work: it
writes a note template per project so the frontmatter is filled in before you start, and it records
which version of the kit installed your tool folder so an update can tell you what would change.

This page is for you, the person with the vault. The contract inside
`claude-obsidian-vault-kit.md` is written for the agent doing the setup; this is the same ground in
the order a human needs it.

---

## Part 1 — The note template per project

### What gets created

Every `--root` run of the index generator writes one template per project:

```
<VaultRoot>/_templates/TEMPLATE - <Project>.md
```

They are named like the indexes (`INDEX - <Name>.md`) so they sort together in the file tree.
Each one carries **the four fields every note actually has when it is created**:

```
---
title: "{{title}}"
summary:
project: "ProjectName"
created: {{date}}
---
```

`{{title}}` and `{{date}}` are filled in by Obsidian when you insert the template — the title comes
from the filename, which is the convention this vault runs on. `project:` is written into each
template by name, so it can never be guessed wrong; that mismatch is a defect the guards report,
and this is what stops it happening in the first place.

### Why the other five contract fields are not in it

The frontmatter contract defines nine fields. `updated`, `issues`, `generator`, `retired` and
`stale` are **situational** — they get set when something has happened, not when a note is started,
and a template full of empty keys teaches you to leave them empty.

One of them is more than tidiness. **`generator:` must never sit in a template waiting to be
filled.** A note carrying that field is declaring itself derived output, and a rebuild is then
entitled to overwrite or delete it. A blank `generator:` in every new note is a trap with your own
writing in it.

Nothing is hidden by leaving them out: Obsidian's *Add property* offers every field already used
anywhere in the vault, so they are one click away in any note that needs them.

### The one setting you have to make yourself

**Obsidian does not find the templates until you point it at the folder.** Once:

> Settings → Core plugins → Templates → *Template folder location* = `_templates`

After that, `Ctrl+P → Insert template` in a new note offers one entry per project.

The kit does **not** write this setting for you, and the reason is not that it cannot. Obsidian
1.12.7 does read an externally written `.obsidian/templates.json` — measured three times, including
a control probe: delete the file with Obsidian closed and the setting comes back empty on the next
start; write it from outside and the setting is live on the start after that.

It is left to you because **`.obsidian/` is your application state**, not the vault's content. This
kit writes notes, indexes and its own tool folder. Reaching into the directory that holds your
themes, your hotkeys and your plugin config to flip a switch you can flip yourself is a different
kind of act, and one you would have no reason to expect.

### What happens if you edit a template

**Nothing overwrites it.** The template is there to be changed — add a field your project needs,
drop one you never fill in. A rerun of the generator leaves an existing template exactly as it is
and only writes the ones that are missing. That is covered by its suite and by the end-to-end setup
run, in both directions: a hand edit survives, and a project added later still gets its template on
the next `--root` run.

### Why `_templates` is not a project

It sits at the vault root, where every other directory *is* a project. It is the one exception, and
the generator skips it explicitly. Without that it would grow six category folders of its own, and
the templates themselves would be reported as defects for having no `summary:` — they are headers
with the values left blank, which is the whole point of them.

### One thing to expect from the duplicate check

The templates are nearly identical to each other by design. They live outside the scanned tree, so
the duplicate check does not see them — but if you ever move them, or copy one into a project
folder as a starting point, expect a flagged pair. That is the check working, not a false alarm.

---

## Part 2 — Updating the tools from a newer kit

### The version stamp and the file list

Your tool folder holds `kit-version.txt`, twelve hex characters naming the kit file the folder came
from, and `kit-manifest.txt`, one line per file that kit delivered. Both are written at install time
by:

```
python <VaultRoot>/00_Global/06_tools/upgrade.py --stamp <path to the kit file>
```

The version is read out of the kit file's own first line, never typed by hand. A kit file with no
version line is **refused** rather than recorded as `unversioned` — that string would then be
compared against every future kit and never match, which is a wrong answer wearing a right answer's
clothes.

The manifest is the shorter story and it does one job: it says which files in that folder are the
kit's. Everything else in there — a tool you wrote, `runs.log`, a `jobs.json` you extended — is
yours, and an update never touches it. Two files rather than one, because `kit-version.txt` has to
stay a single line: every copy of `upgrade.py` already installed anywhere reads that whole file and
compares it against twelve characters, so growing it would break the update path in exactly the
folders an update is for.

### How you find out that any of this exists

Nothing here phones home, so nothing can tell you a newer kit was published. What the vault does
instead is remind you to look, once the reminder is worth reading. After about two months, the
freshness check — step 1 of your daily chain — ends its counts with two extra lines:

```
kit-version a1b2c3d4e5f6 · installed 73 days ago
compare it against the kit-version on line 1 at github.com/nibor1896/claude-obsidian-vault-kit
```

Those twelve characters are a made-up example, deliberately: a real stamp printed on this page
would go stale on the next build and read as though your copy were the outdated one. Yours comes
out of your own folder.

That is the whole mechanism. It states what is on your disk and where to look; you open the
published file, glance at line 1, and either the twelve characters match or they do not.

**It is silent for the first sixty days**, on purpose: a line printed on every single run is read
for about a week and skimmed forever afterwards, which is worse than no line at all. It is also
silent if your tool folder has no `kit-version.txt`, or if that file holds something other than a
version — a folder put together by hand gets no invented answer, and a stamp that looks wrong is
what `upgrade.py` is for. And it never changes the check's exit code: an old installation is not a
defect, it is an installation.

### Seeing what a newer kit would change

Download a newer `claude-obsidian-vault-kit.md` and point the updater at it:

```
python <VaultRoot>/00_Global/06_tools/upgrade.py <path to the newer kit file>
```

It prints the version you have against the version in the file, then lists every script that would
be overwritten, every one that would be added, and every one that would be **removed**. **Nothing is
written and nothing is deleted without `--apply`.** Local edits to the tools are overwritten by an
update, which is why they are listed first, by name: that makes it a decision rather than a
surprise.

Removal exists because a kit that stops shipping a script would otherwise leave it in your folder
forever — and an orphaned `test_something.py` is not inert. The suite runner collects `test_*.py`
by name, so it picks the orphan up, the import fails, and your vault reports red permanently over a
tool that is no longer there. Only files named in `kit-manifest.txt` are ever removed, and
`upgrade.py` never removes itself.

```
python <VaultRoot>/00_Global/06_tools/upgrade.py <newer kit file> --apply
```

`--apply` works in a fixed order, and the order is the reason a failed update is always
recoverable: it writes each file through a temporary name and one atomic replace, reads every
written file back and compares it against the block it came from, **stops there if anything
disagrees — before deleting anything**, then removes, then records the manifest, and writes the
stamp **last**. The stamp is what a later run reads to decide it has nothing to do, so a run that
died anywhere before it leaves a folder whose next `--apply` recomputes the same plan and finishes
it. Nothing you can interrupt leaves a state the next run cannot get out of.

Then it **compiles every script it just wrote and parses `jobs.json`**. If either fails it says so
and exits non-zero: a tool folder that was updated but never re-checked is the state this kit exists
to prevent. Restore from git if that happens — which is one of the reasons the vault is a git
repository.

It used to run the suites here instead, and it cannot: they are not in your folder. They live in the
kit's repository and ran there, over the exact bytes the new kit file carries, before it was
published. **Name what that costs:** after an update your folder can no longer demonstrate that its
guards go red on bad input. That claim rests on the release plus the byte-for-byte comparison the
updater does — it reads every file back before it removes anything — not on something you can re-run
here.

You can check the folder at any time without an update:

```
python <VaultRoot>/00_Global/06_tools/upgrade.py --prove
```

**Your setup ran that line once already**, right after it stamped the folder, and showed you the
output — so the first time you run it yourself you are comparing against something, not meeting it
cold. It compiles every script, parses `jobs.json` and imports the entry point. That last one is the
check compiling cannot do: a script cut short still compiles, still exits 0, and has done nothing.

### One update rewrites every index file, once

The guards are reached as `vaultkit.py <subcommand>` now — one file with a subcommand each,
instead of one file per guard. The header line every generated index carries names the command
that wrote it, so it changed from `06_tools/build_index.py` to `06_tools/vaultkit.py index`.

The first index run after that update therefore rewrites **every** `INDEX - *.md` in your vault:
one line each, nothing else. It is a single commit's worth of churn and it never repeats — the run
after it leaves `git status` empty again, which is the property step 10 of the setup check exists
for. Without this paragraph it reads exactly like the drift the whole kit is built to prevent, so:
it is announced, it is one line per file, and it happens once.

### If your update ended in `FAIL run_suites.py`

`upgrade.py` rewrites itself, and the process doing that keeps the code it started with. So an
update **from a kit older than the one that removed the suites** finishes by running the *old*
checks, which go looking for `run_suites.py` and `acceptance.py` — the two files the new kit just
correctly deleted. The run then prints `restore it from git`, which is exactly the wrong advice on
a folder that is in perfect shape.

This happens once, on that one crossing, and never again: the updater now runs its post-write
checks in a fresh process so the new code does the checking. If you saw it, run the `--prove` line
above — that is the same check, from the code you now have.

### If your folder was installed before manifests existed

It has no `kit-manifest.txt`, so nothing on your machine knows which files that older kit brought.
The updater will not guess — guessing means treating every script in the folder as the kit's, and
that deletes tools you wrote. So the **first** `--apply` on such a folder removes nothing, says so
in as many words, and writes a manifest on its way out. The update after it can remove normally.
Exactly one cycle is blind, and it tells you it is.

### Four things it now tells you that it used to swallow

**A release that changed no script still moves the version.** If a new kit only edits the contract
or the setup instructions, every script on your disk is already current — and the updater used to
stop right there, leaving the stamp on the previous version forever while reporting the folder as
fully up to date. It now names the gap, and `--apply` corrects the stamp even when there is no file
to write. The same line appears if your folder has no stamp at all, which is what a setup that
skipped the `--stamp` step leaves behind.

**A file you opened in Notepad is not a local edit.** Windows editors — Notepad, and PowerShell
5.1's `Set-Content -Encoding utf8` — add an invisible byte-order mark to the front of a file. The
bytes of your code are unchanged, but the comparison used to fail, and the script was listed as
`overwrite` when nothing about it had been edited. Those files now compare as unchanged. And a file
containing genuinely invalid bytes is named in the listing instead of stopping the entire update
with an error that mentions no filename at all.

**A path it cannot read or write is named, not traced.** A mistyped kit file used to come back as a
Python traceback out of the first thing the updater does, which reads as "this tool is broken"
rather than "that path is wrong" — and you are usually already repairing something when you see it.
The same held for a script the updater could not write: the run ended there, and every script behind
it in the list went unwritten with nothing said about those either. Now each refused file is named,
the ones behind it are still written, and **the stamp is deliberately left alone** — a folder that is
part old and part new must not carry a version claiming the update finished. Fix the cause and rerun
`--apply`. These runs exit with code `2`, which means the environment refused a file operation;
code `1` still means what it did, "written, but it does not pass its own checks".

**A file that left the kit is gone from your folder, not left behind.** A script the new kit no
longer carries used to stay on disk with nothing to say it was obsolete. If it was a `test_*.py`,
the suite runner went on collecting it and your vault reported red over a tool that no longer
existed. It is now listed as `remove` and deleted, along with any cached bytecode — but only if
`kit-manifest.txt` says this kit brought it.

---

## Where the authority actually lives

Everything on this page is behaviour with a test behind it, and the tests ship in your tool folder
along with the tools. If this page and a run ever disagree, the run is right and this page is
stale — check the docstring of the relevant test, which carries the recipe for making that
behaviour go red on purpose.
