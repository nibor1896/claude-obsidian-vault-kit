"""End-to-end verification of a complete setup, from empty folder to committed vault.

acceptance.py proves each guard reacts correctly to one bad input. This proves the whole
sequence a setup actually performs still works when the steps run in order on one tree:
folders, tools, notes, git, indexes, every check, the suites, the acceptance run, and a
second index run that must leave the tree byte-identical and `git status` empty.

    python verify_setup.py
    python verify_setup.py --repeat 10

Everything happens in a throwaway tree under the system temp directory. Exit 0 only when
every step passed in every pass.
"""

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
sys.path.insert(0, str(TOOLS))

for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass

CATEGORY_FOLDERS = ["00_Notes", "01_Issues", "02_docs", "03_technical_docs",
                    "04_feedback", "05_workflows", "06_tools"]
PROJECTS = ["ProjektEins", "ProjektZwei"]

NOTES = [
    ("00_Global", "03_technical_docs", "the-rules-this-vault-runs-on.md", "The rules this vault runs on",
     "Twelve rules and the frontmatter contract.",
     "Every note carries frontmatter. The index is generated and never hand written."),
    ("00_Global", "03_technical_docs", "tooling-00_Global.md", "Tooling",
     "What each guard refuses to do.",
     "A check that cannot tell working from broken is not evidence, so each one prints a denominator."),
    ("ProjektEins", "00_Notes", "knowledge-transfer-ProjektEins.md", "Knowledge transfer ProjektEins",
     "How to pick this project up.",
     "Where the code lives, which decisions are settled, and what the next session should read first."),
    ("ProjektZwei", "00_Notes", "knowledge-transfer-ProjektZwei.md", "Knowledge transfer ProjektZwei",
     "How to pick that project up.",
     "Open questions, the last measurement, and the reason the current approach was chosen."),
]


class Failed(Exception):
    pass


def run(cmd, cwd, expect_zero=True, label=""):
    env = dict(os.environ)
    env.pop("PYTHONIOENCODING", None)
    env.pop("PYTHONUTF8", None)
    result = subprocess.run([str(c) for c in cmd], cwd=str(cwd), env=env, capture_output=True)
    out = result.stdout.decode("utf-8", errors="replace")
    err = result.stderr.decode("utf-8", errors="replace")
    if expect_zero and result.returncode != 0:
        raise Failed(f"{label or cmd[1]} exited {result.returncode}\n{out}\n{err}")
    if not expect_zero and result.returncode == 0:
        raise Failed(f"{label or cmd[1]} exited 0 but had to fail\n{out}\n{err}")
    return result.returncode, out, err


def tool(vault, script, *args, expect_zero=True):
    return run([sys.executable, str(vault / "00_Global" / "06_tools" / script), *args],
               cwd=vault, expect_zero=expect_zero, label=script)


def write_note(path, title, summary, body):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(f'---\ntitle: "{title}"\nsummary: "{summary}"\ncreated: "2026-07-27"\n---\n\n{body}\n',
                    encoding="utf-8", newline="\n")


def build_vault(root):
    """Step 1-3: the folder tree, the shipped tools, the starting pages."""
    for project in ["00_Global"] + PROJECTS:
        for folder in CATEGORY_FOLDERS:
            (root / project / folder).mkdir(parents=True, exist_ok=True)
    dst = root / "00_Global" / "06_tools"
    for src in list(TOOLS.glob("*.py")) + [TOOLS / "jobs.json"]:
        shutil.copy2(src, dst / src.name)
    for project, folder, name, title, summary, body in NOTES:
        write_note(root / project / folder / name, title, summary, body)
    (root / ".gitignore").write_text(
        ".obsidian/plugins/\n.obsidian/workspace.json\n.obsidian/graph.json\n"
        "**/runs.log\n**/__pycache__/\n*.pyc\n_acceptance/\n",
        encoding="utf-8", newline="\n")


def git_setup(root):
    run(["git", "init", "-q"], cwd=root, label="git init")
    run(["git", "config", "user.name", "vaultkit-verify"], cwd=root, label="git config name")
    run(["git", "config", "user.email", "verify@localhost"], cwd=root, label="git config email")


def git_commit_all(root, message):
    run(["git", "add", "-A"], cwd=root, label="git add")
    run(["git", "commit", "-q", "-m", message], cwd=root, label="git commit")


def index_all(root):
    for project in ["00_Global"] + PROJECTS:
        tool(root, "build_index.py", "--vault", str(root / project))
    tool(root, "build_index.py", "--root", ".")


def snapshot(root):
    return {str(p.relative_to(root)): p.read_bytes() for p in sorted(root.rglob("INDEX - *.md"))}


STEPS = []


def step(name):
    def wrap(fn):
        STEPS.append((name, fn))
        return fn
    return wrap


@step("1 tree, tools and starting pages exist")
def _s1(root):
    build_vault(root)
    missing = [p for p in (root / "00_Global" / "06_tools" / "build_index.py",
                           root / "ProjektEins" / "00_Notes",
                           root / ".gitignore") if not p.exists()]
    if missing:
        raise Failed(f"missing after build: {missing}")


@step("2 git initialised and the untouched state committed")
def _s2(root):
    git_setup(root)
    git_commit_all(root, "chore: vault skeleton before any generated file")


@step("3 index generator writes all three levels")
def _s3(root):
    index_all(root)
    for project in ["00_Global"] + PROJECTS:
        hub = list((root / project).glob("INDEX - *.md"))
        if not hub:
            raise Failed(f"no project hub in {project}")
    if not list(root.glob("INDEX - *.md")):
        raise Failed("no root index")


@step("4 link checker green with a denominator")
def _s4(root):
    _, out, err = tool(root, "check_links.py", "--vault", ".")
    if "wikilinks resolve" not in out or not any(c.isdigit() for c in out):
        raise Failed(f"no denominator: {out!r} {err!r}")


@step("5 duplicate check green with a denominator")
def _s5(root):
    _, out, _ = tool(root, "check_duplicates.py", "--vault", ".")
    if "compared" not in out:
        raise Failed(f"no denominator: {out!r}")


@step("6 freshness sees the healthy runs the tools just logged")
def _s6(root):
    _, out, err = tool(root, "check_freshness.py", "--vault", ".")
    if "jobs fresh" not in (out + err):
        raise Failed(f"freshness did not report per-job freshness: {out!r} {err!r}")


@step("7 suites green")
def _s7(root):
    _, out, _ = tool(root, "run_suites.py")
    if "suites green" not in out:
        raise Failed(f"unexpected suite output: {out!r}")


@step("8 acceptance run correct")
def _s8(root):
    _, out, _ = tool(root, "acceptance.py")
    if "10/10" not in out:
        raise Failed(f"acceptance not 10/10: {out!r}")


@step("9 second index run is byte-identical")
def _s9(root):
    before = snapshot(root)
    index_all(root)
    after = snapshot(root)
    if not before:
        raise Failed("no index files to compare")
    changed = [k for k in before if before[k] != after.get(k)]
    if changed or set(before) != set(after):
        raise Failed(f"index churn: {changed or set(after) ^ set(before)}")


@step("10 working tree clean after committing the generated files")
def _s10(root):
    git_commit_all(root, "chore: generated indexes")
    index_all(root)
    _, out, _ = run(["git", "status", "--porcelain"], cwd=root, label="git status")
    if out.strip():
        raise Failed(f"tree not clean after a rerun:\n{out}")


def one_pass(verbose=True):
    root = Path(tempfile.mkdtemp(prefix="vaultkit_flow_")) / "Vault"
    root.mkdir(parents=True)
    failures = []
    try:
        for name, fn in STEPS:
            try:
                fn(root)
                ok, detail = True, ""
            except Failed as exc:
                ok, detail = False, str(exc)
            except Exception as exc:
                ok, detail = False, f"{type(exc).__name__}: {exc}"
            if verbose:
                print(f"  {'ok  ' if ok else 'FAIL'} {name}")
            if not ok:
                failures.append((name, detail))
                break  # later steps depend on this one; a cascade hides the cause
    finally:
        shutil.rmtree(root.parent, ignore_errors=True)
    return failures


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repeat", type=int, default=1)
    args = parser.parse_args(argv)

    all_failures = []
    for run_no in range(1, args.repeat + 1):
        if args.repeat > 1:
            print(f"--- pass {run_no}/{args.repeat} ---")
        failures = one_pass()
        print(f"{len(STEPS) - len(failures)}/{len(STEPS)} steps passed (pass {run_no})")
        all_failures += [(run_no, n, d) for n, d in failures]

    if all_failures:
        print(f"\n{len(all_failures)} failing steps:", file=sys.stderr)
        for run_no, name, detail in all_failures:
            print(f"  pass {run_no}: {name}\n    {detail}", file=sys.stderr)
        return 1
    print(f"\n{args.repeat} pass(es), {len(STEPS)}/{len(STEPS)} steps every time.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
