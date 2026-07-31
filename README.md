<p align="center">
  <img src="docs/media/neural_hero-animated-960x480.gif" width="960"
       alt="Claude × Obsidian Vault Kit — neural strands drifting behind the title, sweeping between the Claude and Obsidian brand colours">
</p>

# Claude × Obsidian — Vault Kit

[![Claude — setup contract](https://img.shields.io/badge/Claude-setup_contract-C4522C?style=flat&labelColor=24292f&logo=claude&logoColor=white)](https://claude.ai)
[![Obsidian — vault](https://img.shields.io/badge/Obsidian-vault-7C3AED?style=flat&labelColor=24292f&logo=obsidian&logoColor=white)](https://obsidian.md)
[![license MIT](https://img.shields.io/badge/license-MIT-1E6FF5?style=flat&labelColor=24292f)](LICENSE)
[![python ≥3.10](https://img.shields.io/badge/python-%E2%89%A53.10-1E6FF5?style=flat&labelColor=24292f&logo=python&logoColor=white)](docs/how-it-works.md#requirements)
[![dependencies zero](https://img.shields.io/badge/dependencies-zero-178841?style=flat&labelColor=24292f)](docs/how-it-works.md#requirements)
[![docs live](https://img.shields.io/badge/docs-live-178841?style=flat&labelColor=24292f&logo=github&logoColor=white)](docs/how-it-works.md)

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
them to disk instead of composing its own. Those exact bytes were verified in this repository before
the file was published — on Windows 11, Python 3.13, under PowerShell 5.1 **and** Git Bash: **10/10
suites green, 12/12 acceptance checks correct and 14/14 end-to-end setup steps, ten consecutive runs
under each shell.** The suites stay here rather than going into your vault; your vault runs the
guards over your notes, not unit tests over code that has not
changed. [Reproduce it yourself](docs/how-it-works.md#reproduce-the-numbers) before you trust it.

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

## Changing the kit

`claude-obsidian-vault-kit.md` is **generated** from `src/contract.md` and `tools/*` — edit those,
never the result. Then, before every commit:

```
python tools/build_kit.py --check
```

It is the only check that sits above the delivery, and nothing triggers it automatically: there is
no CI here, so it runs when a person runs it. It compares the delivered file against its sources and
refuses a build whose lists, prose, guards or config have drifted apart — a file in `tools/` that no
delivery list mentions, a tool shipped without its suite, `jobs.json` disagreeing with its copy in
code, a run-log label that no longer matches its filename, a runnable script missing the
stdout/stderr fix, a command line naming a tool nobody gets, or a count in the text the code does
not count.

## License

MIT — see [LICENSE](LICENSE).

Obsidian and Claude are trademarks of their respective owners. This kit is an independent, unofficial
template and implies no endorsement by either.

---

Free and MIT — no account, no sign-up, nothing to buy. If it saved you an afternoon, you can throw
a coffee at it: [ko-fi.com/nibor1896](https://ko-fi.com/nibor1896).
