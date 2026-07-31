"""One command for every guard this vault runs: `vaultkit.py <subcommand> …`.

    vaultkit.py index      --root <VaultRoot> | --vault <Project>
    vaultkit.py links      --vault <VaultRoot>
    vaultkit.py duplicates --vault <VaultRoot>
    vaultkit.py freshness  --vault <VaultRoot>
    vaultkit.py tokens     <path> …
    vaultkit.py command    --vault <VaultRoot>

Each subcommand takes exactly the arguments the tool behind it always took, and prints exactly
what it always printed. **The job names in `runs.log` do not move by a single byte** -- every
`log_run()` call passes a string literal, and none of them changed; `jobs.json` stays valid.

WHY ONE FILE (2026-07-31): a user's tool folder held twenty-two files, of which they were told
to run six. Every one of those is a separate block in the kit file a stranger drags into a
Claude conversation, and every block is context that conversation has to carry before it writes
anything. The measured cost of the split was not runtime, it was the cold run.

This is the DISPATCHER STAGE: the bodies still live in their own modules and this file calls
them. That is deliberate -- it lets the contract, the `/vaultkit` command and the setup driver
move to the new spelling while the code stays exactly where it is, so the move and the merge are
two commits and either can be bisected on its own.

`upgrade.py` deliberately stays outside. If its own write breaks off, it is the only tool left
that can repeat the attempt, and folding it in here would make the repair depend on the thing
being repaired.
"""

import argparse
import sys

for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass

# Imported at module level, not inside the dispatch, and that is a decision: `import vaultkit`
# has to pull in everything this file can run, so a broken or missing module is found by an
# import rather than by a user who happens to pick that subcommand. It is also how the merged
# file will behave, so the stage after this one changes nothing about when a defect surfaces.
import build_index  # noqa: E402
import check_duplicates  # noqa: E402
import check_freshness  # noqa: E402
import check_links  # noqa: E402
import count_tokens  # noqa: E402
import write_command  # noqa: E402

MODULES = {
    "build_index": build_index,
    "check_duplicates": check_duplicates,
    "check_freshness": check_freshness,
    "check_links": check_links,
    "count_tokens": count_tokens,
    "write_command": write_command,
}


def main(argv=None):
    """Hand the remaining arguments to the tool's own main(), untouched.

    NO SHARED ARGUMENT PARSING, ON PURPOSE. `--vault` means one project directory after `index`
    and the vault root after `links`; `--root` exists only for `index`. That collision is the
    trap the `/vaultkit` command was written for in the first place, and a parser here that
    tried to unify the two would either pick a winner or invent a third spelling. Each tool
    keeps its own parser and its own `--help`, so what a user types is what the tool documents.
    """
    argv = list(sys.argv[1:] if argv is None else argv)
    if not argv or argv[0] in ("-h", "--help"):
        parser = argparse.ArgumentParser(prog="vaultkit.py", description=__doc__,
                                         formatter_class=argparse.RawDescriptionHelpFormatter)
        parser.add_argument("subcommand", choices=sorted(COMMANDS),
                            help="the guard to run; each has its own --help")
        parser.parse_args(argv)
        return 2

    name, rest = argv[0], argv[1:]
    if name not in COMMANDS:
        print(f"vaultkit.py: no subcommand {name!r}. Known: {', '.join(sorted(COMMANDS))}",
              file=sys.stderr)
        return 2
    return MODULES[COMMANDS[name]["module"]].main(rest)


# --------------------------------------------------------------------------- the register
#
# AT THE END OF THE FILE, AND THAT IS LOAD-BEARING TWICE OVER.
#
# 1. It is what `check_freshness` will read to know which jobs this file can log, once the
#    bodies move in here. Today that population is *guessed*: the folder is globbed for `*.py`
#    and a stem is taken when the text mentions the logging call -- so `vault_paths.py` appeared
#    because it DEFINES that call and needed a `not_invoked` entry as a patch, and a tool that
#    forgets to log is invisible by construction. `job` below is the answer instead of a guess,
#    and `None` says "this one reaches no verdict and never logs" out loud.
#
#    That guess is also why this comment spells the call out in words: written literally, the
#    text scan would pick THIS file up as a job nobody declared and report it as unclassified
#    to every user, over a comment.
# 2. It is an all-or-nothing detector for the delivery. A block that arrived truncated has no
#    register, so the first subcommand fails immediately with a NameError naming COMMANDS.
#    Without it a file cut after a complete function compiles cleanly and simply loses a tool,
#    quietly, which is the failure mode the whole kit is built against.
#
# The folder scan in check_freshness stays for the user's OWN tools -- this register describes
# what the kit brought, not what they wrote.

COMMANDS = {
    "index": {"module": "build_index", "job": "build_index"},
    "links": {"module": "check_links", "job": "check_links"},
    "duplicates": {"module": "check_duplicates", "job": "check_duplicates"},
    "freshness": {"module": "check_freshness", "job": "check_freshness"},
    "command": {"module": "write_command", "job": "write_command"},
    # No job: it reports a size and reaches no verdict, so there is nothing a chain could act
    # on and nothing to be late. Same statement jobs.json makes under `not_invoked`.
    "tokens": {"module": "count_tokens", "job": None},
}


if __name__ == "__main__":
    raise SystemExit(main())
