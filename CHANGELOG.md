# Changelog

The delivered file carries its own version on line 1 — `<!-- kit-version: … -->`, a SHA-256 over the
built body. It changes whenever the sources change, so it is a fingerprint, not a sequence: it tells
you *whether* your copy differs from the published one, never which is newer. This file is where the
order lives.

Compare the stamp in your `00_Global/06_tools/kit-version.txt` against line 1 of the published file,
then run `python upgrade.py <newer kit file>` to see what would change, and `--apply` to write it.

---

## `9cad3ee80c8e` — 2026-08-01

**Four places where the text was wrong about the machine it runs on.** No new capability: a rule that
left a Linux session with no legal answer, a filesystem boundary the contract did not know exists, an
update message that tells a user to destroy a healthy folder, and a delivered command the setup
announces without saying when it works.

### What a user gets

- **The vault-location rule has one statement, and it no longer rules out Linux.** SECTION 1.4 said
  the home directory disqualifies "a subfolder of it too" and recommended `~/Documents/<VaultName>`
  in the same sentence. On Windows a session rarely starts in the home directory and the
  contradiction never fires; on Linux it is the ordinary case. Measured: a cold run started in
  `/home/<user>` excluded the entire home tree — correctly, by the letter of that sentence — and had
  nothing left but the Windows mount. The home directory now disqualifies itself and nothing below
  it. SECTION 7 no longer carries a second copy of the rule that could drift from the first; it
  carries the cost and points at 1.4.
- **The setup asks where Obsidian runs — when, and only when, it has measured a boundary.** A setup
  in WSL built a vault at `/home/<user>/<VaultName>`. The Windows Obsidian reached it over
  `\\wsl.localhost\…` and refused to load it:
  `Error: EISDIR: illegal operation on a directory, watch '\\wsl.localhost\Ubuntu\home\<user>\…\'`.
  The app's file watcher does not work across that protocol. Whether a guest exists is measurable
  (`/proc/version`); which side the user's client runs on is not measurable from inside the guest —
  so it is a question, asked one round before the path it decides, and it does not exist on a machine
  with no boundary.
- **The update page says what a failed first update means, where the failure is read.** The advice
  *restore it from git* now carries its own exception in the same paragraph instead of thirty-three
  lines later, and the exception states the measured cause. A `/vaultkit` from before the rewrite
  gets its own section: no update rewrites that file, and the chain it holds still runs suites that
  are no longer part of the delivery.
- **The setup says when `/vaultkit` starts working, and what a second vault gets.** Slash commands
  are read at session start, so the file the setup just wrote is not in the session that wrote it —
  type it straight away and the answer is `No matching commands` on a vault where nothing is wrong.
  Hit on two cold runs, both times read as a failed setup. And there is one commands folder per
  machine: a second vault finds the first one's file, leaves it alone — which is what protects a
  `/vaultkit` you wrote yourself — and ends up without a command while the old one keeps working.
  Measured across three consecutive setups, each blocked by its predecessor. Both facts are now
  announced where the path is reported, in `README.md`, and in the how-it-works page.

### Fixed

- **The update page named the wrong cause, and promised a cleanup that cannot happen.** It said the
  old checks went looking for files the new kit had deleted. Measured on 2026-08-01 against an
  installation from 2026-07-27: without a manifest nothing was deleted, the old suites were present
  and ran, and the one that failed was the suite covering `upgrade.py` — it asserts the wording the
  previous release printed and got the new one. The page also said the update after the blind cycle
  *can remove normally*; it cannot, and now says so, with the count.
- **The `<workdir>` in the contract meant two things.** SECTION 1.2 spelled it "one level below where
  you were started" while 1.4 may settle somewhere else entirely. It is now defined as the parent 1.4
  settled on, which is what every other path in the document already assumed.
- **The contract described one of its own outcomes from twelve hours earlier.** SECTION 8 lists three
  outcomes of writing the command and called the second one *"prints nothing and exits 0"*. That had
  stopped being true that same morning, when the fix for #27 taught the branch to name both vaults.
  It is the outcome three cold runs went on to hit. Found by reading the text against the code it
  describes — nothing else could have found it, since no run reads either.

## `c350ee4831db` — 2026-08-01

**Three places that stayed silent, and a text that did not add up.** No new capability — four
defects that a cold run had exposed and one number that described the old release.

### What a user gets

- **The setup now names the folder to open in Obsidian.** It says `<workdir>/<VaultName>`, not
  `<workdir>`, at the point the tree is first opened — and again where the template setting is
  explained, because `_templates` only resolves from the vault root and is therefore the cheapest
  test of whether the right folder is open. Opening the wrong one raises no error; it shifts every
  path in the contract by one level.
- **`/vaultkit` says which vault it serves.** A command file already carrying the marker is still
  left untouched and the exit code is still 0 — setting up a second vault is not an error. What
  changed is the silence: it now prints the vault the file points at and the vault the run is for.
  Measured on a cold run before the fix: exit 0, no output, and the setup reported `/vaultkit` as
  ready while it kept synchronising a different vault.
- **The GitHub handle is asked one round before the values built from it.** The contract used to
  demand it in the same call as `user.name` and `user.email`, which a dialog cannot do — every
  question in a round is rendered before any of them is answered, so option 1 could never carry the
  handle. Measured after the fix, on a cold run: three rounds of four questions, the handle in
  round one, `<handle>` as a clickable option 1 on both identity questions.

### Fixed

- **A build-time guard read half of what it checked.** `check_generated_command()` rendered the
  `/vaultkit` chain once, against a path with no `.git`, so the branch that only exists in a vault
  *with* a repository was never text anybody checked. That is exactly where a `must print nothing`
  defect had lived for a full release, found by a cold run while seven guards stayed green. It now
  renders both branches and names the branch a finding came from.
- **The contract counted its own questions wrong.** Section 1.4 said "five questions" while holding
  seven, then four bullets holding six. The count is gone: what stands there is the rule — one call,
  and a second round rather than prose when the dialog will not take them all.
- **`ten passes each` described a release that no longer exists.** The acceptance figure now says
  `one pass each`, measured on 2026-08-01 under PowerShell 5.1 and Git Bash: 12/12 both times, with
  11/11 suites and 15/15 setup steps beside it.

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
  and removes nothing; the run after that can act. **What it cannot do is clean the folder** — the
  manifest that blind run writes names only what the new kit delivered, so scripts from before it are
  named by nothing and are never removed by any later update either. Measured 2026-08-01 on a folder
  installed 2026-07-27: twenty `.py` files present, three of them the current kit's. Removal takes
  back what *this* kit once delivered; it is not a cleanup mechanism.

### Fixed

- **A failing index run left no trace.** `write_if_changed()` wrote outside the `try` that guarded
  the read next to it, so a read-only `INDEX` file — normal enough on OneDrive — took the run down
  *before* it reached `log_run()`. The result was half a rebuilt tree and **not one line in the run
  log**: the silence said "never ran" while the tree said otherwise. Measured: 46 of 63 index files
  written, no log line; now 62 of 63, the file named on stderr, and the log line present.
- **`upgrade.py` crashed on a mistyped path.** `FileNotFoundError` with a full traceback on the very
  first step of the update path. Now exit 2 and a sentence.
- **`upgrade.py` overwrote itself mid-run.** The running process kept the old code, so its own
  post-update check ran out of the previous release and told the user to "restore it from git" — on a
  healthy folder. The checks now run in a fresh process, and `--prove` became a command of its own.
  **Corrected 2026-08-01, measured:** the sentence here used to say the old check *looked for files
  the new kit had just correctly deleted*. It did not. Without a manifest nothing was deleted at all;
  the old suites were still on disk and ran. What failed was the suite covering `upgrade.py`, which
  asserts the sentence the previous version printed and got the new, more precise one. And **this fix
  cannot reach the run that installs it** — every folder older than this release carries the old
  `upgrade.py`, so it is that copy doing the checking. The update page carries the full case under
  *If your first update ends by telling you to restore from git*.
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
