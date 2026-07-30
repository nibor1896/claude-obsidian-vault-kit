"""Report the age of the last HEALTHY run of each expected job.

Without this, a scheduler that quietly stopped firing looks identical to one that is fine.
"no log" is reported as "did not run" — never as "fine".

Log format, one line per run, appended by every tool (see vault_paths.log_run):

    2026-07-27T09:15:00+00:00\tbuild_index\tok\t0 defects

LOGGING AND BEING WATCHED ARE TWO DIFFERENT THINGS, AND jobs.json CARRIES THE LISTS. Every tool
writes a line; only a tool that runs on a schedule can be *late*. Put the on-demand ones under an
age limit and the report is red every single day, which is the fastest way to get the whole check
switched off. So `jobs` is what must be fresh, `on_demand` is what logs and is never late,
`not_invoked` is what no chain calls at all, and a name in none of them is reported as
unclassified rather than assumed into one of them.

THE UNCLASSIFIED LIST IS READ FROM THE FOLDER, NOT ONLY FROM THE LOG. A tool that no chain calls
never writes a line, and a population derived from the log alone therefore cannot see the one
thing this report is for -- the check confirms its own silence. Measured 2026-07-30: `0
unclassified` over a folder holding a tool in neither list.

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

# The third classification: no chain calls it, and the value says why. Same rule as above -- the
# reason is the entry, because JSON has no comments.
DEFAULT_NOT_INVOKED = {
    "vault_paths": "a module, not a command -- it has no main(), the other tools import it",
    "_testkit": "a module, imported by the suites only",
    "count_tokens": "answers a question on request and reaches no verdict: it reports a size, so "
                    "it has no pass, no fail and nothing a chain could act on",
}


def tool_folder(vault_root):
    """The one folder both the config and the population come out of.

    Derived from RUN_LOG_RELPATH rather than spelled again: a population read from one folder and
    a classification read from another would disagree without either being wrong.
    """
    return Path(vault_root).resolve() / RUN_LOG_RELPATH.parent


def loggable_tools(vault_root):
    """(names of tools on disk that can ever appear in the log, files that could not be read).

    WHY THE POPULATION IS NOT SIMPLY EVERY `.py` IN THE FOLDER (2026-07-30): a tool that never
    calls log_run() cannot appear in the log by construction, so asking whether it is watched has
    no answer that would change anything -- `run_suites.py`, `acceptance.py`, `verify_setup.py`
    and `upgrade.py` all run, all reach a verdict, and none of them log. Naming those four on
    every single run would put four permanent lines above the one line that means something,
    which is the fastest way to get this report skimmed instead of read.

    Measured on this machine 2026-07-30, before this function existed: five of the shipped tools
    call log_run() -- build_index, check_links, check_duplicates, write_command, check_freshness
    -- and those five are exactly the five in jobs.json. So the honest population is "can it log",
    and the check that follows is "has anyone said which list it belongs to".

    Suites are excluded structurally, not by taste: `test_X.py` is not a job, it is what
    run_suites.py collects, and a suite that exercises log_run() would otherwise ask to be
    classified as a scheduled job.

    Reading is by text, so a file that only mentions log_run() in a comment asks for a decision it
    does not need. That is the cheap direction to be wrong in -- the expensive one, a tool that
    logs and is never asked about, is the defect this whole function exists for.
    """
    folder = tool_folder(vault_root)
    if not folder.is_dir():
        return set(), 0
    names, unreadable = set(), 0
    for path in sorted(folder.glob("*.py")):
        if path.name.startswith("test_"):
            continue
        try:
            text = path.read_text(encoding="utf-8-sig", errors="replace")
        except OSError:
            # Counted and printed, never a silent continue: a skip that does not count itself
            # still prints a total, over fewer files than it names.
            unreadable += 1
            continue
        if "log_run(" in text:
            names.add(path.stem)
    return names, unreadable


def job_lists(vault_root):
    """(watched, on_demand, not_invoked) — read once, so they can never disagree about the fallback.

    No config file is normal -- a project-only run has none, and both defaults stand. A config
    that exists and cannot be read is not normal, and falling back to the default over it
    checks a job list the user never chose while printing nothing about it. utf-8-sig is how
    that used to happen: Notepad writes a BOM, json.loads raises, the except swallowed it.

    A config that exists and has no `on_demand` key gets an EMPTY on-demand list, not the
    default above. That is the same rule one line further: substituting a classification the
    user never made is the silent fallback this docstring is about. Empty is honest, and the
    unclassified line then names the tools instead of guessing at them.

    Either shape is accepted for `on_demand` and for `not_invoked`: the mapping that ships
    (name -> reason) or a bare list, which a user mirroring `jobs` will write. A list simply
    carries no reasons; refusing it would hard-fail an honest config over cosmetics.
    """
    config = tool_folder(vault_root) / "jobs.json"
    if not config.exists():
        return list(DEFAULT_JOBS), dict(DEFAULT_ON_DEMAND), dict(DEFAULT_NOT_INVOKED)
    try:
        data = json.loads(config.read_text(encoding="utf-8-sig"))
        watched = list(data["jobs"])
        return watched, _mapping(data, "on_demand"), _mapping(data, "not_invoked")
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print(f"{config}: unreadable ({exc}) — falling back to {DEFAULT_JOBS}", file=sys.stderr)
        return list(DEFAULT_JOBS), dict(DEFAULT_ON_DEMAND), dict(DEFAULT_NOT_INVOKED)


def _mapping(data, key):
    """One optional name->reason list out of a config that exists. Missing means EMPTY.

    Never the built-in default: a config the user wrote and a classification they never made must
    not be mixed, or the unclassified line reports against a list nobody chose. Same rule as the
    docstring above, applied to both optional keys instead of one.
    """
    raw = data.get(key) or {}
    return dict(raw) if isinstance(raw, dict) else {name: "" for name in raw}


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
    configured, on_demand, not_invoked = job_lists(vault_root)
    jobs = args.jobs if args.jobs else configured

    # Before any measurement, because the answer to "which list wins" is none of them. Letting one
    # win would be an invisible decision: the other entry would sit there doing nothing, and no
    # run could show which of the statements applies.
    #
    # The CONFIGURED list, not the effective one: the defect is in the file, so `--jobs` must not
    # be able to dodge it -- and `--jobs check_duplicates` is a deliberate one-off watch of an
    # on-demand tool, which is not a contradiction and must not be treated as one.
    #
    # Three lists since 2026-07-30, so every pair is checked rather than the one that used to
    # exist. `not_invoked` contradicts either of the others just as loudly: a tool cannot both be
    # called by no chain and be the thing a chain is watched for.
    clash = sorted({name for a, b in ((configured, on_demand), (configured, not_invoked),
                                      (set(on_demand), set(not_invoked)))
                    for name in set(a) & set(b)})
    if clash:
        print(f"{', '.join(clash)}: classified twice. Watched means it may be late, on demand "
              f"means it cannot be, not invoked means no chain calls it — a name belongs to "
              f"exactly one. Take it out of the others in {tool_folder(vault_root) / 'jobs.json'}.",
              file=sys.stderr)
        log_run(vault_root, "check_freshness", "did-not-run",
                f"{len(clash)} jobs in more than one list")
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

    # In no list. The only real signal at this point: somebody built a tool and nobody decided
    # whether it is watched. It does NOT change the exit code -- an unclassified tool has not
    # failed, and a chain that goes red the first time a user adds a tool of their own is one
    # they will stop running.
    # `configured` is subtracted as well as `jobs`, so a `--jobs` override does not turn the rest
    # of the user's own watch list into news.
    #
    # THE POPULATION IS THE FOLDER AS WELL AS THE LOG (2026-07-30, #24). It used to be `seen`
    # alone, and that made the check confirm its own silence: a tool no chain calls never writes
    # a line, and without a line it could not turn up as unclassified. Measured that day against
    # a fresh vault -- `0 unclassified` while count_tokens sat in the folder in neither list, the
    # one tool the report existed to name. The self-confirming shape is the point: the tools that
    # fall out of the chain are exactly the ones a log-derived population cannot see.
    on_disk, unreadable = loggable_tools(vault_root)
    unclassified = sorted((seen | on_disk) - set(jobs) - set(configured)
                          - set(on_demand) - set(not_invoked))

    print(
        f"{len(fresh)}/{len(jobs)} jobs fresh · {len(on_demand)} on demand · "
        f"{len(not_invoked)} not invoked · {len(unclassified)} unclassified · "
        f"{lines} log lines · {malformed} malformed · threshold {args.max_age_hours}h"
    )
    for job, age_h in fresh:
        print(f"  {job}: {age_h:.1f}h ago")
    if unclassified:
        print(f"  in none of the three lists: {', '.join(unclassified)}")
    if unreadable:
        print(f"  {unreadable} file(s) in {tool_folder(vault_root)} could not be read, so they "
              f"are outside every count above", file=sys.stderr)

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
