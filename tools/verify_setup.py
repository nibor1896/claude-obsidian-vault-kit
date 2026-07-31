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

# Imported, never respelled: a second copy verifies a tree the tools no longer build.
from vault_paths import CATEGORY_FOLDERS, TEMPLATES_DIR, template_name  # noqa: E402

PROJECTS = ["ProjektEins", "ProjektZwei"]

# The stamp on the throwaway kit file this run "installs" from. Step 13 requires the folder to
# come out carrying exactly this, so the value has to be named once and read, never written twice.
SETUP_KIT_VERSION = "abcabcabcabc"

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


def run(cmd, cwd, expect_zero=True, label="", home=None):
    env = dict(os.environ)
    env.pop("PYTHONIOENCODING", None)
    env.pop("PYTHONUTF8", None)
    if home is not None:
        # Redirects Path.home() inside the subprocess. The only way to exercise a tool that
        # writes into the user's own config folder without writing into it. Both names are set
        # because Python reads USERPROFILE on Windows and HOME elsewhere.
        env["USERPROFILE"] = str(home)
        env["HOME"] = str(home)
        env.pop("HOMEDRIVE", None)
        env.pop("HOMEPATH", None)
    result = subprocess.run([str(c) for c in cmd], cwd=str(cwd), env=env, capture_output=True)
    out = result.stdout.decode("utf-8", errors="replace")
    err = result.stderr.decode("utf-8", errors="replace")
    if expect_zero and result.returncode != 0:
        raise Failed(f"{label or cmd[1]} exited {result.returncode}\n{out}\n{err}")
    if not expect_zero and result.returncode == 0:
        raise Failed(f"{label or cmd[1]} exited 0 but had to fail\n{out}\n{err}")
    return result.returncode, out, err


def tool(vault, script, *args, expect_zero=True, home=None):
    return run([sys.executable, str(vault / "00_Global" / "06_tools" / script), *args],
               cwd=vault, expect_zero=expect_zero, label=script, home=home)


def write_note(path, title, summary, body):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(f'---\ntitle: "{title}"\nsummary: "{summary}"\ncreated: "2026-07-27"\n---\n\n{body}\n',
                    encoding="utf-8", newline="\n")


def delivered_scripts():
    """The files a real install ends up with -- not whatever happens to sit next to this one.

    WHY THIS IS NOT A GLOB (2026-07-29): it was one, `TOOLS.glob("*.py")`, and in the repository
    that folder holds tools the user never receives. The verified tree was therefore richer than
    the delivered one, which is precisely why none of the thirteen steps could see a script
    leaking into or out of the delivery. build_kit.py owns that list; here it is asked.

    In an installed vault build_kit.py is absent -- it is not shipped either -- and there the
    folder *is* the answer, so the fallback is the folder. Two branches, one meaning.
    """
    try:
        import build_kit
    except ImportError:
        return sorted(p.name for p in TOOLS.glob("*.py")) + ["jobs.json"]
    return build_kit.delivered_files()


def build_vault(root):
    """Step 1-3: the folder tree, the shipped tools, the starting pages."""
    for project in ["00_Global"] + PROJECTS:
        for folder in CATEGORY_FOLDERS:
            (root / project / folder).mkdir(parents=True, exist_ok=True)
    dst = root / "00_Global" / "06_tools"
    for name in delivered_scripts():
        shutil.copy2(TOOLS / name, dst / name)
    # The stamp SECTION 8 writes during setup -- by running the shipped tool, exactly as the
    # contract now tells the agent to. This function used to write the file itself, which made
    # step 13 read back a value this file had just typed and call that a pass. The kit file is a
    # stand-in with a made-up stamp; what is under test is that `--stamp` puts that stamp on
    # disk and that upgrade.py reads it back.
    kit = root.parent / "the-kit-the-user-dropped-in.md"
    kit.write_text(f"<!-- kit-version: {SETUP_KIT_VERSION} -->\n\n# Kit\n",
                   encoding="utf-8", newline="\n")
    run([sys.executable, str(dst / "upgrade.py"), "--stamp", str(kit)],
        cwd=root, label="upgrade.py --stamp")
    for project, folder, name, title, summary, body in NOTES:
        write_note(root / project / folder / name, title, summary, body)
    (root / ".gitignore").write_text(
        ".obsidian/plugins/\n.obsidian/workspace.json\n.obsidian/graph.json\n"
        ".claude/*\n!.claude/commands/\n"
        "**/runs.log\n**/__pycache__/\n*.pyc\n",
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
    # No count in the string: acceptance.py exits non-zero unless every fixture behaved, and a
    # literal here goes stale the moment a fixture is added.
    if "checks behaved as specified" not in out:
        raise Failed(f"acceptance did not report its verdict: {out!r}")


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


@step("11 a project and a folder added by hand are scaffolded, adopted and stable")
def _s11(root):
    """What the user does the week after setup, which no earlier step covers.

    They make a folder in Obsidian's file pane. Both requirements of the promise are here:
    an empty project folder gets its categories, and a folder they invent gets an index
    instead of a complaint -- and the tree is still clean on the run after that.
    """
    (root / "ProjektDrei").mkdir()
    (root / "ProjektDrei" / "Rechnungen").mkdir(parents=True)
    write_note(root / "ProjektDrei" / "Rechnungen" / "eine-rechnung.md",
               "Eine Rechnung", "Was darauf stand.", "Betrag, Datum und wofuer sie ausgestellt war.")
    _, out, _ = tool(root, "build_index.py", "--root", ".")

    missing = [f for f in CATEGORY_FOLDERS if not (root / "ProjektDrei" / f).is_dir()]
    if missing:
        raise Failed(f"category folders not created in a hand-made project: {missing}")
    if "created" not in out or "adopted" not in out:
        raise Failed(f"the run changed the tree without saying so:\n{out}")
    adopted_index = root / "ProjektDrei" / "Rechnungen" / "INDEX - ProjektDrei Rechnungen.md"
    if "eine-rechnung" not in adopted_index.read_text(encoding="utf-8"):
        raise Failed("the hand-made folder has an index but the note is not in it")

    git_commit_all(root, "chore: a project added by hand")
    tool(root, "build_index.py", "--root", ".")
    _, status, _ = run(["git", "status", "--porcelain"], cwd=root, label="git status")
    if status.strip():
        raise Failed(f"tree not clean after scaffolding and a rerun:\n{status}")


@step("12 a note template per project, and a hand-edited one survives a rerun")
def _s12(root):
    """The two promises write_templates makes, neither of which any earlier step looks at.

    WHY THIS EXISTS (2026-07-29): steps 1-11 only ever inspect index files. A delivery that
    silently stopped writing templates altogether still reported every step green -- the gap was
    found by reading the tool, not by a red test. (That sentence quoted `11/11` until step 14
    landed and made it read as a current claim about a run with fourteen steps. History gets
    described, not counted.) The second half matters more than the first: every run prints
    "edit it freely, no run overwrites it", and until now nothing held the tool to it.
    """
    folder = root / TEMPLATES_DIR
    expected = ["00_Global"] + PROJECTS + ["ProjektDrei"]  # ProjektDrei is added by hand in step 11
    missing = [p for p in expected if not (folder / template_name(p)).is_file()]
    if missing:
        raise Failed(f"no note template written for: {missing}")

    # A template that comes back unchanged proves nothing unless it went in changed.
    victim = folder / template_name(PROJECTS[0])
    edited = victim.read_text(encoding="utf-8") + "\nfield the user added by hand\n"
    victim.write_text(edited, encoding="utf-8", newline="\n")
    tool(root, "build_index.py", "--root", ".")
    if victim.read_text(encoding="utf-8") != edited:
        raise Failed(f"a rerun overwrote a hand-edited template: {victim.name}")


@step("13 the tool folder knows which kit version installed it")
def _s13(root):
    """The one value the whole update path compares against, and nothing used to write it.

    WHY THIS EXISTS (2026-07-29): kit-version.txt was only ever written by upgrade.py's --apply
    branch, which means from the *second* version onwards. A freshly installed folder answered
    `installed: unknown`, and steps 1-12 stayed green through it -- not one of them looks at the
    update path.

    WHY IT STOPPED TESTING ITSELF (same day): the first version of this step passed because
    build_vault() had typed the value it then read back. SECTION 8 now runs
    `upgrade.py --stamp <kitfile>`, build_vault() does the same, and the value under test comes
    out of a file the tool parsed -- step 12's shape, not step 13's old one.

    Undo recipe, to watch it go red: copy tools/ somewhere, delete the two `if args.stamp:` lines
    from upgrade.py's main(), and run both drivers there. Measured on this machine 2026-07-29 --
    verify_setup 13/14, failing in step 1 with `upgrade.py --stamp exited 2`, and test_upgrade
    7/9. Both, which is the point of covering it in two places: the driver proves the setup does
    it, the suite proves the tool can.

    That 13/14 was 12/13 for one commit, because it was measured before step 14 existed and then
    typed rather than re-run. Nothing catches that: check_prose_claims() reads the contract, the
    SECTION 10 header and README.md, and never the docstrings of the scripts it embeds. A number
    in here is only as good as the last time somebody actually ran the recipe above.
    """
    tools = root / "00_Global" / "06_tools"
    stamp = tools / "kit-version.txt"
    if not stamp.is_file():
        raise Failed("no kit-version.txt beside the tools -- upgrade.py cannot say what is installed")
    installed = stamp.read_text(encoding="utf-8-sig").strip()
    if installed != SETUP_KIT_VERSION:
        raise Failed(f"the stamp beside the tools reads {installed!r}, not the "
                     f"{SETUP_KIT_VERSION!r} the kit file it was installed from carried")

    # A kit file carrying one block byte-identical to what is installed: upgrade.py then has
    # nothing to write, so the whole answer is what it says. It lives outside the vault, which is
    # where a downloaded kit file actually sits.
    jobs = (tools / "jobs.json").read_text(encoding="utf-8").rstrip()
    kit = root.parent / "newer-kit.md"
    kit.write_text(f"<!-- kit-version: ffffffffffff -->\n\n### `jobs.json`\n\n```json\n{jobs}\n```\n",
                   encoding="utf-8", newline="\n")
    _, out, _ = run([sys.executable, str(tools / "upgrade.py"), str(kit)], cwd=root,
                    label="upgrade.py")
    if f"installed: {installed}" not in out or "unknown" in out:
        raise Failed(f"upgrade.py did not read the installed stamp back:\n{out}")

    # SHARPENED 2026-07-30, NOT EXTENDED (#23). This fixture was already the exact case -- a
    # newer kit whose one block is identical to what is on disk -- and it only ever read the
    # first printed line. Everything after it went unexamined, which is where the defect lived:
    # upgrade.py returned on `nothing to do` before it ever compared ffffffffffff against the
    # stamp, so a release that changed no script left the folder on the previous version and
    # said nothing. A new step would have moved 14/14 in three sources for no new fixture.
    #
    # Undo recipe, measured on this machine 2026-07-30: replace the stamp comparison in
    # upgrade.py's main() with `if False:`, which is what the early return amounted to.
    # verify_setup 13/14 here, and test_upgrade 12/15.
    if "ffffffffffff" not in out:
        raise Failed(f"upgrade.py did not say the kit carries a version the folder does not:\n{out}")
    if stamp.read_text(encoding="utf-8-sig").strip() != installed:
        raise Failed("upgrade.py rewrote kit-version.txt without --apply")


@step("14 a /vaultkit command is written once, carries this vault's own paths, and is left alone")
def _s14(root):
    """The convenience the setup offers, held to the same three things as step 12.

    The command exists because `--vault` means a PROJECT after build_index.py and the ROOT after
    check_links.py, and a chain typed from memory gets that wrong. So the file existing proves
    nothing on its own -- what is checked is that the two invocations differ, that the second run
    leaves a hand edit alone, and that the vault gains nothing from the run.

    It goes to `~/.claude/commands/`, the only destination there is, with Path.home() redirected
    into this throwaway tree. An in-vault copy was offered once and removed: it loads only in a
    session started at the vault root, which is not how a sync command gets used.

    Undo recipes, measured on this machine 2026-07-30 against a copy of tools/:

      - Make the `if target.exists():` block in write_command.py's main() unreachable: the hand
        edit is eaten and the second run reports work. verify_setup 13/14, acceptance 11/12,
        test_write_command 8/12.
      - Remove `.claude` from SKIP_DIRS in vault_paths.py: the link checker counts a `.claude/`
        file in the vault as a note. verify_setup 13/14, test_write_command 11/12 -- and
        acceptance stays 12/12, because fixture 11 checks the file and the message, not the
        denominators. That gap is the reason this step carries the denominator half at all.
    """
    home = root.parent / "FakeHome"
    home.mkdir(parents=True, exist_ok=True)
    target = home / ".claude" / "commands" / "vaultkit.md"
    _, links_before, _ = tool(root, "check_links.py", "--vault", ".")

    _, out, _ = tool(root, "write_command.py", "--vault", str(root),
                     "--shell", "posix", home=home)
    if not target.is_file():
        raise Failed(f"no /vaultkit command at {target}\n{out}")
    if target.name not in out:
        raise Failed(f"a file was written outside the vault tree without being named:\n{out}")
    if (root / ".claude" / "commands").exists():
        raise Failed("a command was written into the vault, where it would not load")

    text = target.read_text(encoding="utf-8")
    root_arg = f'--root "{root.as_posix()}"'
    if root_arg not in text:
        raise Failed(f"the command never sweeps the whole vault with --root:\n{text[:400]}")
    for project in ["00_Global"] + PROJECTS:
        if f'--vault "{(root / project).as_posix()}"' not in text:
            raise Failed(f"no index line for {project} in the command")
    if f'--vault "{root.as_posix()}"' not in text:
        raise Failed("nothing in the command hands the vault root to the link checker")

    edited = text + "\n## 7 · A step the user added\n"
    target.write_text(edited, encoding="utf-8", newline="\n")
    _, second, _ = tool(root, "write_command.py", "--vault", str(root),
                        "--shell", "posix", home=home)
    if second.strip():
        raise Failed(f"the second run reported work it did not do:\n{second}")
    if target.read_text(encoding="utf-8") != edited:
        raise Failed("a rerun overwrote a hand-edited command file")

    # A `.claude/` folder in the vault is ordinary -- the user may keep settings beside their
    # notes -- and the guards must not count what is in it. Written by hand here, because the
    # command itself no longer lands in the vault at all.
    (root / ".claude").mkdir(exist_ok=True)
    (root / ".claude" / "settings.json").write_text("{}\n", encoding="utf-8", newline="\n")
    _, links_after, _ = tool(root, "check_links.py", "--vault", ".")
    if links_before != links_after:
        raise Failed(f"a file under .claude/ entered the note denominators:\n"
                     f"  before: {links_before.strip()}\n  after:  {links_after.strip()}")

    # The .gitignore promise, asked of git rather than read off the file: the agent's own state
    # stays out of the vault's history.
    code, _, _ = run(["git", "check-ignore", "-q", ".claude/settings.json"],
                     cwd=root, label="git check-ignore settings")
    if code != 0:
        raise Failed("the agent's own settings are versioned -- .claude/ must stay ignored")


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
