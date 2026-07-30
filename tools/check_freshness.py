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
