"""Report the age of the last HEALTHY run of each expected job.

Without this, a scheduler that quietly stopped firing looks identical to one that is fine.
"no log" is reported as "did not run" — never as "fine".

Log format, one line per run, appended by every tool (see vault_paths.log_run):

    2026-07-27T09:15:00+00:00\tbuild_index\tok\t0 defects
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

from vault_paths import RUN_LOG_RELPATH

DEFAULT_MAX_AGE_HOURS = 24.0
HEALTHY = {"ok"}


DEFAULT_JOBS = ["build_index", "check_links"]


def expected_jobs(vault_root):
    """Jobs that must have a healthy run. Configured per vault, defaulted here.

    No config file is normal -- a project-only run has none, and the default stands. A config
    that exists and cannot be read is not normal, and falling back to the default over it
    checks a job list the user never chose while printing nothing about it. utf-8-sig is how
    that used to happen: Notepad writes a BOM, json.loads raises, the except swallowed it.
    """
    config = Path(vault_root).resolve() / "00_Global" / "06_tools" / "jobs.json"
    if not config.exists():
        return DEFAULT_JOBS
    try:
        data = json.loads(config.read_text(encoding="utf-8-sig"))
        return list(data["jobs"])
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print(f"{config}: unreadable ({exc}) — falling back to {DEFAULT_JOBS}", file=sys.stderr)
        return DEFAULT_JOBS


def parse_log(log_path):
    """job -> newest healthy datetime. Malformed lines are counted, not swallowed."""
    healthy = {}
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
            if when.tzinfo is None:
                when = when.replace(tzinfo=timezone.utc)
            if status not in HEALTHY:
                continue
            if job not in healthy or when > healthy[job]:
                healthy[job] = when
    return healthy, lines, malformed


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--vault", required=True, help="vault root")
    parser.add_argument("--log", help="run log path (defaults to the vault's own)")
    parser.add_argument("--max-age-hours", type=float, default=DEFAULT_MAX_AGE_HOURS)
    parser.add_argument("--jobs", nargs="*", help="override the expected job list")
    args = parser.parse_args(argv)

    vault_root = Path(args.vault).resolve()
    log_path = Path(args.log).resolve() if args.log else vault_root / RUN_LOG_RELPATH
    jobs = args.jobs if args.jobs else expected_jobs(vault_root)

    if not jobs:
        print("did not run: no expected jobs configured", file=sys.stderr)
        return 1

    if not log_path.exists() or log_path.stat().st_size == 0:
        print(f"did not run: no run log at {log_path}", file=sys.stderr)
        for job in jobs:
            print(f"{job}: did not run — no log", file=sys.stderr)
        print(f"0/{len(jobs)} jobs have a healthy run", file=sys.stderr)
        return 1

    healthy, lines, malformed = parse_log(log_path)
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

    print(
        f"{len(fresh)}/{len(jobs)} jobs fresh · {lines} log lines · "
        f"{malformed} malformed · threshold {args.max_age_hours}h"
    )
    for job, age_h in fresh:
        print(f"  {job}: {age_h:.1f}h ago")

    if problems or malformed:
        for problem in problems:
            print(problem, file=sys.stderr)
        if malformed:
            print(f"{malformed} malformed log lines", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
