"""Discover and run every test_*.py next to the tools.

Reports n/m. Zero suites collected is NOT green — a tool without a suite is invisible to
the runner, which is worse than red.
"""

import sys

for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass

import argparse
import os
import subprocess
from pathlib import Path


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tools", default=str(Path(__file__).resolve().parent), help="directory to scan")
    args = parser.parse_args(argv)

    tools = Path(args.tools).resolve()
    if not tools.is_dir():
        print(f"not a directory: {tools}", file=sys.stderr)
        return 2

    suites = sorted(tools.glob("test_*.py"))
    if not suites:
        print(f"0 suites collected in {tools} — not green, nothing ran", file=sys.stderr)
        return 1

    env = dict(os.environ)
    env["PYTHONPATH"] = str(tools) + os.pathsep + env.get("PYTHONPATH", "")
    env["PYTHONIOENCODING"] = "utf-8"

    passed = []
    failed = []
    for suite in suites:
        result = subprocess.run(
            [sys.executable, str(suite)],
            cwd=str(tools),
            env=env,
            capture_output=True,
        )
        out = (result.stdout + result.stderr).decode("utf-8", errors="replace")
        if result.returncode == 0:
            passed.append(suite.name)
        else:
            failed.append((suite.name, out.strip()))

    print(f"{len(passed)}/{len(suites)} suites green")
    for name in passed:
        print(f"  ok   {name}")
    for name, out in failed:
        print(f"  FAIL {name}", file=sys.stderr)
        for line in out.splitlines()[-15:]:
            print(f"       {line}", file=sys.stderr)

    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
