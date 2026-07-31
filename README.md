# Claude × Obsidian — Vault Kit

[![license MIT](https://img.shields.io/badge/license-MIT-3b82f6?style=flat&labelColor=24292f)](LICENSE)
[![python ≥3.10](https://img.shields.io/badge/python-%E2%89%A53.10-3b82f6?style=flat&labelColor=24292f&logo=python&logoColor=white)](docs/how-it-works.md#requirements)
[![dependencies zero](https://img.shields.io/badge/dependencies-zero-22c55e?style=flat&labelColor=24292f)](docs/how-it-works.md#requirements)
[![docs live](https://img.shields.io/badge/docs-live-22c55e?style=flat&labelColor=24292f&logo=github&logoColor=white)](https://nibor1896.github.io/claude-obsidian-vault-kit/)

A setup contract for Claude that builds you a project-knowledge vault in Obsidian: predictable
structure, a **generated** index, and guards that go red instead of quietly passing.

## Setup

1. Download [`claude-obsidian-vault-kit.md`](claude-obsidian-vault-kit.md) — one file, nothing else.
2. Drop it into a Claude conversation.
3. Say **"set this up for me"**.

Claude interviews you first — do you already use Obsidian, do you want a throwaway test vault to
rearrange before it becomes real, which projects, which backup, which shell — and only then writes
anything to disk. The vault you end up with is **empty**: the tree, the tools, and four pages
describing them. No example notes, no demo content, nothing invented.

The tools are shipped, not generated: the file carries every script verbatim, and the setup writes
them to disk instead of composing its own. Measured on Windows 11, Python 3.13, under PowerShell 5.1
**and** Git Bash — **9/9 suites green, 12/12 acceptance checks correct and 14/14 end-to-end setup
steps, ten consecutive runs under each shell.** [Reproduce it yourself](docs/how-it-works.md#reproduce-the-numbers)
before you trust it.

## How the index works

Every note carries a short frontmatter header — title, summary, project, topic, created. The
generator reads **only that header**. There is no code path in it that opens a note body, which is
what structurally prevents prose from leaking into the index.

It writes three levels, each one line per thing below it:

```
<VaultRoot>/INDEX - <Vault>.md                one line per project
<Project>/INDEX - <Project>.md                one line per category
<Project>/<Folder>/INDEX - <Category>.md      the notes themselves
```

You never edit an index — you edit the note and re-run the generator. A note whose header is missing
or broken is **not** quietly skipped: the run names the file, says what is wrong, and exits non-zero.
A folder you created by hand becomes a category of its own, and that is printed too, because a run
that changes the tree silently is the failure the whole thing exists to prevent.

## Keeping it in sync

The setup writes a `/vaultkit` slash command into `~/.claude/commands/`, with your vault's real
paths already filled in. Run it in any Claude conversation:

```
/vaultkit
```

It rebuilds the index and runs every guard in the order that leaves nothing stale — so a note you
added, renamed or broke shows up as a changed index line or as a red run, not as silence.

## More

- **[How it works](docs/how-it-works.md)** — what you end up with, the rules that carry it, requirements, and the numbers
- **[Updating and templates](docs/updating-and-templates.md)** — the two quiet parts: note templates and the version stamp
- **[Website](https://nibor1896.github.io/claude-obsidian-vault-kit/)**

## License

MIT — see [LICENSE](LICENSE).

Obsidian and Claude are trademarks of their respective owners. This kit is an independent, unofficial
template and implies no endorsement by either.

---

Free and MIT — no account, no sign-up, nothing to buy. If it saved you an afternoon, you can throw
a coffee at it: [ko-fi.com/nibor1896](https://ko-fi.com/nibor1896).
