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
Each one carries **every field the frontmatter contract knows**, with the rest left empty:

```
---
title: "{{title}}"
summary:
project: "ProjectName"
created: {{date}}
updated:
issues:
generator:
retired:
stale:
---
```

`{{title}}` and `{{date}}` are filled in by Obsidian when you insert the template — the title comes
from the filename, which is the convention this vault runs on. `project:` is written into each
template by name, so it can never be guessed wrong; that mismatch is a defect the guards report,
and this is what stops it happening in the first place.

### The one setting you have to make yourself

**Obsidian does not find the templates until you point it at the folder.** Once:

> Settings → Core plugins → Templates → *Template folder location* = `_templates`

After that, `Ctrl+P → Insert template` in a new note offers one entry per project.

The kit does **not** write this setting for you, and that is deliberate. The key inside
`.obsidian/templates.json` has not been verified from the outside on a clean install, and a wrong
key does nothing *quietly* — which is the exact failure class the guards exist to catch. A setting
you made once and can see is better than one a tool wrote and neither of you can confirm.

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

### The version stamp

Your tool folder holds `kit-version.txt`, twelve hex characters naming the kit file the folder came
from. It is written at install time by:

```
python <VaultRoot>/00_Global/06_tools/upgrade.py --stamp <path to the kit file>
```

The value is read out of the kit file's own first line, never typed by hand. A kit file with no
version line is **refused** rather than recorded as `unversioned` — that string would then be
compared against every future kit and never match, which is a wrong answer wearing a right answer's
clothes.

### Seeing what a newer kit would change

Download a newer `claude-obsidian-vault-kit.md` and point the updater at it:

```
python <VaultRoot>/00_Global/06_tools/upgrade.py <path to the newer kit file>
```

It prints the version you have against the version in the file, then lists every script that would
be overwritten and every one that would be added. **Nothing is written without `--apply`.** Local
edits to the tools are overwritten by an update, which is why they are listed first, by name: that
makes it a decision rather than a surprise.

```
python <VaultRoot>/00_Global/06_tools/upgrade.py <newer kit file> --apply
```

`--apply` writes the files, updates the stamp, and then **reruns the suites and the acceptance
driver**. If either goes red it says so and fails: a tool folder that was updated but never
re-proven is the state this kit exists to prevent. Restore from git if that happens — which is one
of the reasons the vault is a git repository.

### Two things it now tells you that it used to swallow

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

---

## Where the authority actually lives

Everything on this page is behaviour with a test behind it, and the tests ship in your tool folder
along with the tools. If this page and a run ever disagree, the run is right and this page is
stale — check the docstring of the relevant test, which carries the recipe for making that
behaviour go red on purpose.
