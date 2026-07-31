# Changelog

The delivered file carries its own version on line 1 — `<!-- kit-version: … -->`, a SHA-256 over the
built body. It changes whenever the sources change, so it is a fingerprint, not a sequence: it tells
you *whether* your copy differs from the published one, never which is newer. This file is where the
order lives.

Compare the stamp in your `00_Global/06_tools/kit-version.txt` against line 1 of the published file,
then run `python upgrade.py <newer kit file>` to see what would change, and `--apply` to write it.

---

## `488e08d22ef7` — 2026-07-31

**The delivery went from 22 files to 3.** The kit file lost a third of its size, and the daily sync
lost the step that made up most of its runtime. Nothing was deleted: the suites and the verification
drivers moved into this repository, where a release is verified once, instead of into every user's
vault, where they answered the same question every day.

### What a user gets

| | before | now |
|---|---|---|
| Files written into `00_Global/06_tools/` | 22 | **3** — `vaultkit.py`, `upgrade.py`, `jobs.json` |
| Delivered file | 5916 lines · 285 KB | **3897 lines · 208 KB** |
| Steps in the `/vaultkit` chain | 7 | **6** |
| `/vaultkit` runtime | 13 min 38 s · 12.0k tokens | **1 min 44 s · 2.3k tokens** |

The runtime figures are two cold runs against different vaults, not a controlled benchmark — but the
cause is not in doubt: `run_suites.py` started 112 unit tests as separate processes on every sync,
over code that had not changed since setup.

### Breaking

- **The seven tools are now subcommands of one script.** `build_index.py`, `check_links.py`,
  `check_duplicates.py`, `check_freshness.py`, `count_tokens.py`, `write_command.py` and
  `vault_paths.py` became `vaultkit.py index|links|duplicates|freshness|tokens|command`. Each one is
  still called on its own, returns its own exit code and writes its own line to `runs.log` — the job
  names in the log did not change, so an existing log stays readable and `jobs.json` stays valid.
- **`run_suites.py`, `acceptance.py`, `verify_setup.py`, `_testkit.py` and the nine suites are no
  longer delivered.** They live here and run before a release.
- **The generated index header now reads `06_tools/vaultkit.py index`.** The first run after an
  update rewrites every `INDEX - *.md` once for that line alone. Harmless, but it looks like drift if
  nobody says so.
- **`upgrade.py` can now remove files.** Update from an older kit and the 19 files that left the
  delivery are deleted — but only those, and only when `kit-manifest.txt` names them. A folder
  installed by an older kit has no manifest yet, so its **first** update reports what it would remove
  and removes nothing; the run after that can act.

### Fixed

- **A failing index run left no trace.** `write_if_changed()` wrote outside the `try` that guarded
  the read next to it, so a read-only `INDEX` file — normal enough on OneDrive — took the run down
  *before* it reached `log_run()`. The result was half a rebuilt tree and **not one line in the run
  log**: the silence said "never ran" while the tree said otherwise. Measured: 46 of 63 index files
  written, no log line; now 62 of 63, the file named on stderr, and the log line present.
- **`upgrade.py` crashed on a mistyped path.** `FileNotFoundError` with a full traceback on the very
  first step of the update path. Now exit 2 and a sentence.
- **`upgrade.py` overwrote itself mid-run.** The running process kept the old code, so its own
  post-update check looked for files the new kit had just correctly deleted, and told the user to
  "restore it from git" — on a healthy folder. The checks now run in a fresh process, and `--prove`
  became a command of its own.
- **The generated `/vaultkit` file said `must print nothing`** for the second-run check. The contract
  is more precise: `?? .obsidian/` and notes you wrote yourself may appear; drift is an `INDEX` file
  changing *without* a new note. Following the command file literally reported a defect that was not
  one.
- **`freshness` counted a JSON comment as a job.** `not_invoked` in `jobs.json` held one key,
  `_comment`, and every fresh vault reported `1 not invoked` over a job that does not exist.
- **The setup read the GitHub handle off this file's own footer.** A cold run offered
  `<kit author>@users.noreply.github.com` as the recommended default — into a stranger's commits,
  permanently. The handle is now a question of its own, asked before the two values built from it,
  and it has exactly one source: the answer.
- **A vault could be built inside a configuration directory.** The rule "the vault sits inside the
  folder you were given" had no exception for `.claude`, `.config`, `.cursor` or the home directory.
  Starting a session in one now produces a proposal *outside* it, with the reason said out loud.
- **The setup asked which shell to use** after measuring and naming it. The answer only decides
  whether paths in the generated command file are spelled with backslashes or forward slashes, and
  Python takes either.
- **The deliverables demanded a test that is not shipped.** SECTION 0 required "the acceptance test
  from SECTION 9, passed, on this machine" while SECTION 9 says the user does not run it. A setup
  could never formally finish.

### Added

- **`kit-manifest.txt`** beside `kit-version.txt`, listing what the kit installed. It is what makes
  removal possible without guessing, and it is written last — after the files, so an interrupted
  update is always resumable.
- **An entrance to the update path.** `freshness` — step 1 of the daily chain — now prints the
  installed version and where to compare it, but only once the installation is older than 60 days.
  It makes no network request; there is no way for it to know that a newer version exists, only that
  yours has been sitting there a while. The 60 days are a choice, not a measurement.
- **Seven build-time guards** in `build_kit.py`, all running before the file is written: the folder
  against the delivery lists in both directions, every delivered tool having a suite, `jobs.json`
  against its copy in code, every `log_run` label against its subcommand, every runnable script
  carrying the stdout/stderr fix, `docs/*.md` against what is actually delivered, and the generated
  `/vaultkit` text against the same. Two defects in this release were found by them.
- **A Python version check** at the top of both shipped scripts. The floor is 3.10, and it came from
  a single keyword argument — below it, everything used to start and fail at the first write with a
  `TypeError` that looks like anything but a version problem.
- **Named exit codes and one "did not run" format.** `0` clean, `1` defect or did-not-run, `2` bad
  argument or contradicting sources. The one deliberate exception is documented: `duplicates` returns
  `0` when there are fewer than two comparable notes, because the first run of a new vault must not
  be red.

### Verification

Measured on Windows 11, Python 3.13.3, under PowerShell 5.1 and Git Bash: 11/11 suites, 12/12
acceptance checks, 15/15 end-to-end setup steps, `build_kit.py --check` and `--verify` both clean.

Two cold runs against this release, both from an empty folder with the delivered file as the only
input — 14 min 23 s / 18.0k tokens and 19 min 2 s / 22.0k tokens. The full entries, including what
each run does **not** show, are in
[#14](https://github.com/nibor1896/claude-obsidian-vault-kit/issues/14).

### Known and unmeasured

- macOS and Linux have never been run.
- The duplicate threshold `0.75` is uncalibrated ([#20](https://github.com/nibor1896/claude-obsidian-vault-kit/issues/20)).
- `vaultkit.py command` leaves an existing command file alone when it was written by this kit — even
  when it points at a *different* vault. The path is in the marker and is not compared, so the run
  says nothing at all.
- Both cold runs above were made by the author, with global instructions and hooks active. A
  stranger's session sees less.

---

## `4974313a90c5` — 2026-07-30

The last release before the refactor: 22 files in the delivery, suites and verification drivers
shipped into every vault, `run_suites.py` as step 6 of the daily chain. Its cold runs are runs 1–4 in
[#14](https://github.com/nibor1896/claude-obsidian-vault-kit/issues/14).
