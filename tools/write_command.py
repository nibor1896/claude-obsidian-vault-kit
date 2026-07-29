"""Write a `/vaultkit` slash command for Claude Code, with this vault's real paths already in it.

The verification chain in SECTION 8 is five commands with three traps in them, and every one of
the three was hit on a real run:

  1. `--vault` means two different things. `check_links.py` wants the vault ROOT,
     `build_index.py` wants ONE PROJECT, `check_duplicates.py` takes either. Typing the same
     path after every `--vault` is wrong in two places out of three.
  2. The tool folder is `<VaultRoot>/00_Global/06_tools/`, not `06_tools/`. A relative prefix is
     an invitation to run it from a directory where it does not resolve.
  3. `--root`, not `--vault`, for the sweep. Rerunning only `--vault` after adding a note leaves
     the root index on yesterday's count -- green, silent, and wrong. Measured on a cold run:
     one added note left the root index reading 5 entries against a vault holding 6.

A command file removes all three by spelling out the answers once, per vault, with the paths
filled in. It is a convenience for Claude Code and nothing depends on it: the workflow page in
`05_workflows` carries the same chain in prose for anyone working in a browser.

    python write_command.py --vault <VaultRoot> --target vault --shell powershell
    python write_command.py --vault <VaultRoot> --target home  --shell posix

CREATED WHEN MISSING, NEVER OVERWRITTEN, same as the note templates. A command file is there to
be edited -- the user adds their own steps -- and a tool that rewrites it every run eats that
edit without saying so. The second run therefore prints nothing at all: there is no news, and
`runs.log` carries the run either way, so silence here never means "did not run".

Undo recipe for that guard, measured on this machine 2026-07-29: copy tools/ somewhere, delete
the `if target.exists():` block in main(), and run the three drivers there --
test_write_command 8/10, acceptance 11/12, verify_setup 13/14.
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
        "## 1 · Index each project",
        "",
        "`--vault` here means ONE PROJECT DIRECTORY, not the vault root. One line per project:",
        "",
    ]
    for project in projects:
        lines.append(f"- `python {tool('build_index.py')} --vault {show(project, shell)}`")
    lines += [
        "",
        "## 2 · Index the vault root",
        "",
        "`--root`, not `--vault`. This is the one invocation that walks every project *and* "
        "writes the root hub. Running only step 1 after adding a note leaves the root index "
        "holding yesterday's entry count, with no message and a green exit — measured on a cold "
        "run: one added note left it reading `5 entries` against a vault holding 6.",
        "",
        f"- `python {tool('build_index.py')} --root {root}`",
        "",
        "## 3 · Check the links",
        "",
        "`--vault` here means THE VAULT ROOT — the same flag, the other meaning. The project "
        "hubs link back to the root index, so anything narrower reports a broken link that is "
        "not broken:",
        "",
        f"- `python {tool('check_links.py')} --vault {root}`",
        "",
        "## 4 · Check for duplicates",
        "",
        "`--vault` here takes either the root or a single project:",
        "",
        f"- `python {tool('check_duplicates.py')} --vault {root}`",
        "",
        "## 5 · Run the suites",
        "",
        f"- `python {tool('run_suites.py')}`",
        "",
        "## 6 · Prove the second run changes nothing",
        "",
        "Repeat step 2, then the working tree must be clean. A generator that drifts on every "
        "run is indistinguishable from a clean one after a single pass, and it turns every later "
        "`git status` into noise nobody reads.",
        "",
        f"- `python {tool('build_index.py')} --root {root}`",
        f"- `git -C {root} status --porcelain`  — must print nothing",
        "",
        "## Report",
        "",
        "One line per step, each with its denominator. `Open:` lists what you did **not** "
        "measure, not only what is unfinished.",
        "",
    ]
    return "\n".join(lines)


def target_path(vault_root, target):
    if target == "home":
        return Path.home() / ".claude" / "commands" / f"{COMMAND_NAME}.md"
    return Path(vault_root).resolve() / ".claude" / "commands" / f"{COMMAND_NAME}.md"


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--vault", required=True, help="vault root")
    parser.add_argument("--target", choices=("vault", "home"), default="vault",
                        help="vault: <VaultRoot>/.claude/commands · home: ~/.claude/commands")
    parser.add_argument("--shell", choices=("powershell", "posix"), default="powershell",
                        help="the syntax the paths are written in")
    args = parser.parse_args(argv)

    vault_root = Path(args.vault).resolve()
    if not vault_root.is_dir():
        print(f"not a directory: {vault_root}", file=sys.stderr)
        return 2

    target = target_path(vault_root, args.target)
    projects = project_dirs(vault_root)
    if not projects:
        # Not a silent skip: a vault with no projects means the wrong path was given, and a
        # command file listing no projects would be a working file that does nothing.
        print(f"no projects under {vault_root} — nothing to write a command for", file=sys.stderr)
        return 1

    if target.exists():
        log_run(vault_root, "write_command", "ok", f"{target} already there · nothing written")
        return 0

    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(command_text(vault_root, projects, args.shell),
                      encoding="utf-8", newline="\n")
    print(f"wrote {target} — /{COMMAND_NAME} covers {len(projects)} projects; "
          f"edit it freely, no run overwrites it")
    log_run(vault_root, "write_command", "ok", f"{target} written · {len(projects)} projects")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
