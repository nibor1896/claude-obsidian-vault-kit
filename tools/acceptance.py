"""Acceptance test: prove each guard reacts as specified to one input, on this machine.

Each fixture is built in its own throwaway vault under the system temp directory. Most hand a
guard bad input and require it to go red; the rest hand the tools input or behaviour the
structure explicitly allows and require them to stay green. Both halves are needed: a suite that
only ever sees bad input is exactly as blind as one that only ever sees good input. The counts
are derived from FIXTURES below, never written into a sentence here -- one of them changed sides
once, and a sentence would have gone on being wrong.

The verdict comes from process exit codes and from files on disk -- never from parsing console
text alone, which wraps at the terminal width and differs per shell. Where a printed line *is*
the specified behaviour it is read as well, never instead: fixtures 9 and 11 require a run to
name what it touched, and several red fixtures require a particular phrase or require silence.
SECTION 9 of the contract lists the three kinds.

    python acceptance.py            one pass
    python acceptance.py --repeat 10

Exit 0 only when every fixture behaved as specified in every pass.
"""

import argparse
import shutil
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from _testkit import make_vault, run_tool, write_note
from vault_paths import category_index_name

for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass

PROJECT = "ProjektEins"


def index_text(project, folder="00_Notes"):
    path = project / folder / category_index_name(PROJECT, folder)
    return path.read_text(encoding="utf-8") if path.exists() else ""


def note(path, title, summary, created, body):
    """A note with its own body. The shared helper writes one body for every note, which is
    itself a duplicate pair once two of them exist."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        f'---\ntitle: "{title}"\nsummary: "{summary}"\ncreated: "{created}"\n---\n\n{body}\n',
        encoding="utf-8", newline="\n")
    return path


def build_both(vault, project):
    """Category and project indexes, then the root hub.

    Both invocations are needed before the link checker means anything: the project hub
    back-links to the root index, and --vault alone never writes it. Skipping --root leaves
    exactly one broken link, which makes an unrelated fixture pass for the wrong reason.
    """
    run_tool("build_index.py", "--vault", project)
    run_tool("build_index.py", "--root", vault)


def fixture_1_missing_title(vault, project):
    write_note(project / "00_Notes" / "ohne-titel.md", title=None)
    code, _, err = run_tool("build_index.py", "--vault", project)
    return code != 0 and "ohne-titel.md" in err


def fixture_2_summary_debris(vault, project):
    write_note(project / "00_Notes" / "debris.md", summary="> Ein Zitatrest")
    code, _, err = run_tool("build_index.py", "--vault", project)
    return code != 0 and "debris.md" in err and "— > Ein Zitatrest" not in index_text(project)


def fixture_3_dead_wikilink(vault, project):
    write_note(project / "00_Notes" / "toter-link.md")
    (project / "00_Notes" / "toter-link.md").write_text(
        '---\ntitle: "Toter Link"\nsummary: "Zeigt ins Leere."\n---\n\n'
        "[[gibt-es-nicht-im-vault]]\n", encoding="utf-8", newline="\n")
    build_both(vault, project)
    code, out, err = run_tool("check_links.py", "--vault", vault)
    scanned = any(ch.isdigit() for ch in out)
    return code != 0 and scanned and "toter-link.md" in (out + err)


def fixture_4_forbidden_filename(vault, project):
    write_note(project / "00_Notes" / "kaputt#name.md", title="Kaputter Name")
    code, _, err = run_tool("build_index.py", "--vault", project)
    text = index_text(project)
    return code != 0 and "kaputt#name.md" in err and "[Kaputter Name](" in text


def fixture_5_non_ascii_filename(vault, project):
    write_note(project / "00_Notes" / "Übergröße-Ärger.md", title="Umlaut-Notiz")
    code, out, err = run_tool("build_index.py", "--vault", project)
    if code != 0:
        return False
    if "Übergröße-Ärger" not in index_text(project):
        return False
    run_tool("build_index.py", "--root", vault)
    code2, out2, err2 = run_tool("check_links.py", "--vault", vault)
    return code2 == 0 and "0 files scanned" not in out2 and "Übergröße-Ärger" not in err2


def fixture_6_second_run_is_a_noop(vault, project):
    write_note(project / "00_Notes" / "stabil.md")
    run_tool("build_index.py", "--vault", project)
    before = {p.name: p.read_bytes() for p in project.rglob("INDEX - *.md")}
    run_tool("build_index.py", "--vault", project)
    after = {p.name: p.read_bytes() for p in project.rglob("INDEX - *.md")}
    return bool(before) and before == after


def fixture_7_empty_suite_dir(vault, project):
    empty = Path(tempfile.mkdtemp(prefix="vaultkit_empty_"))
    try:
        code, out, err = run_tool("run_suites.py", "--tools", empty)
        return code != 0 and "0 suites" in (out + err)
    finally:
        shutil.rmtree(empty, ignore_errors=True)


def fixture_8_freshness_without_log(vault, project):
    blank = vault / "leeres-protokoll.log"
    blank.write_text("", encoding="utf-8")
    code, out, err = run_tool("check_freshness.py", "--vault", vault, "--log", blank)
    return code != 0 and "did not run" in (out + err)


def fixture_9_hand_made_folder_is_adopted(vault, project):
    """The second green-expected check, and the reason it is not a red one.

    A folder the user makes by hand is allowed by the structure, so the run must not go red
    over it -- but it must not swallow it either. What is checked here is all three parts:
    the folder survives, its note reaches an index, and the run names it on stdout. Drop the
    third and this passes over exactly the silent behaviour it exists to forbid.
    """
    (project / "99_extra").mkdir(exist_ok=True)
    write_note(project / "99_extra" / "verlorene-notiz.md", title="Verloren")
    code, out, _ = run_tool("build_index.py", "--vault", project)
    if code != 0 or not (project / "99_extra").is_dir():
        return False
    if "99_extra" not in out or "adopted" not in out:
        return False
    return "verlorene-notiz" in index_text(project, "99_extra")


def fixture_11_command_is_written_named_and_left_alone(vault, project):
    """The third green-expected check, and all three parts of it are load-bearing.

    Fixture 9 established the shape: an effect on disk, an effect in the content, and the line
    that says so. Here the same three are the whole specification of write_command.py -- the
    file appears, it distinguishes `--root` from `--vault` (the trap the command exists for),
    and the run names what it wrote. Drop the third and a tool that writes into
    `~/.claude/commands/` without a word passes this. That path is outside the vault, which is
    the one place operating rule 5 says nothing may happen quietly.
    """
    code, out, _ = run_tool("write_command.py", "--vault", vault, "--target", "vault",
                            "--shell", "posix")
    target = vault / ".claude" / "commands" / "vaultkit.md"
    if code != 0 or not target.is_file():
        return False
    if target.name not in out:
        return False
    text = target.read_text(encoding="utf-8")
    if f'--root "{vault.as_posix()}"' not in text:
        return False
    if f'--vault "{project.as_posix()}"' not in text:
        return False
    # Second run: nothing said, nothing written, the hand edit still there.
    edited = text + "\nA line the user added.\n"
    target.write_text(edited, encoding="utf-8", newline="\n")
    _, second, _ = run_tool("write_command.py", "--vault", vault, "--target", "vault",
                            "--shell", "posix")
    if second.strip() or target.read_text(encoding="utf-8") != edited:
        return False

    # A file of the same name this kit did NOT write: refused, named, non-zero -- never a quiet
    # zero, which would let a setup report /vaultkit ready while a stranger holds the name.
    foreign = "---\ndescription: A command the user already had\n---\n\nMine.\n"
    target.write_text(foreign, encoding="utf-8", newline="\n")
    code, out, err = run_tool("write_command.py", "--vault", vault, "--target", "vault",
                              "--shell", "posix")
    return (code != 0 and target.name in (out + err)
            and target.read_text(encoding="utf-8") == foreign)


def fixture_10_project_disagrees_with_folder(vault, project):
    """The field that looked like it worked: nothing reads it, so only a guard can say so.

    Both directions in one fixture, because the asymmetry is the whole defect -- a note whose
    `project:` matches its folder behaved identically to one that contradicted it, which is
    exactly why the contradiction went unnoticed. Red on disagreement is only half the check;
    a guard that also fires on agreement would make the field unusable instead of advisory.
    """
    write_note(project / "00_Notes" / "falsches-projekt.md", title="Falsch einsortiert",
               project="Homelab")
    code, _, err = run_tool("build_index.py", "--vault", project)
    if code == 0 or "falsches-projekt.md" not in err or "Homelab" not in err:
        return False
    (project / "00_Notes" / "falsches-projekt.md").unlink()
    write_note(project / "00_Notes" / "richtiges-projekt.md", title="Richtig einsortiert",
               project=PROJECT)
    write_note(project / "00_Notes" / "ohne-projekt.md", title="Feld weggelassen")
    code, _, err = run_tool("build_index.py", "--vault", project)
    return code == 0 and "project" not in err


def control_clean_vault_is_green(vault, project):
    """The healthy control: a suite that only ever sees bad input is as blind as one that
    only ever sees good input. Every tool must exit 0 on a clean tree, and say so with a
    denominator."""
    # Distinct bodies on purpose: two notes sharing the shared-fixture body are a genuine
    # duplicate pair, and check_duplicates is right to flag them.
    note(project / "00_Notes" / "eine-erkenntnis.md", "Eine Erkenntnis", "Genau ein Satz.",
         "2026-07-01", "Was an diesem Tag gemessen wurde und warum es zaehlt.")
    note(project / "03_technical_docs" / "ein-subsystem.md", "Ein Subsystem", "Handbuchseite.",
         "2026-07-02", "Wie das Teilsystem aufgebaut ist, Schnittstellen und Grenzen.")
    build_both(vault, project)

    for script in ("check_links.py", "check_duplicates.py"):
        code, out, err = run_tool(script, "--vault", vault)
        if code != 0 or not any(ch.isdigit() for ch in out + err):
            return False

    log = vault / "runs.log"
    log.write_text("", encoding="utf-8")
    code, out, err = run_tool("check_freshness.py", "--vault", vault, "--log", log)
    if code == 0:  # an empty log is not a healthy run, and must not read as one
        return False

    before = {p.name: p.read_bytes() for p in vault.rglob("INDEX - *.md")}
    build_both(vault, project)
    after = {p.name: p.read_bytes() for p in vault.rglob("INDEX - *.md")}
    return bool(before) and before == after


# The third column is what the fixture expects of the tool: "red" means the guard must refuse
# the input, "green" means the tool must accept it and keep working. Counted from here rather
# than written into the summary line -- the sentence "9 guards red, 1 control green" was true
# until a fixture changed sides, and nothing would have caught that.
FIXTURES = [
    ("0 healthy control: clean vault is green and stable", control_clean_vault_is_green, "green"),
    ("1 note without title", fixture_1_missing_title, "red"),
    ("2 markdown debris in summary", fixture_2_summary_debris, "red"),
    ("3 dead wikilink", fixture_3_dead_wikilink, "red"),
    ("4 forbidden character in filename", fixture_4_forbidden_filename, "red"),
    ("5 non-ASCII filename stays in the denominator", fixture_5_non_ascii_filename, "red"),
    ("6 second index run changes nothing", fixture_6_second_run_is_a_noop, "red"),
    ("7 suite runner on an empty directory", fixture_7_empty_suite_dir, "red"),
    ("8 freshness check without a run log", fixture_8_freshness_without_log, "red"),
    ("9 hand-made folder is adopted, indexed and named", fixture_9_hand_made_folder_is_adopted, "green"),
    ("10 project: disagreeing with its folder", fixture_10_project_disagrees_with_folder, "red"),
    ("11 /vaultkit command written, named and never overwritten",
     fixture_11_command_is_written_named_and_left_alone, "green"),
]

RED = sum(1 for _, _, kind in FIXTURES if kind == "red")
GREEN = len(FIXTURES) - RED


def one_pass(verbose=True):
    """Every fixture gets its own vault, so one fixture cannot poison the next."""
    results = []
    for label, fn, _kind in FIXTURES:
        vault = make_vault((PROJECT,))
        try:
            try:
                ok = bool(fn(vault, vault / PROJECT))
            except Exception as exc:  # a crashing fixture is a failing fixture
                ok = False
                label = f"{label} [raised {type(exc).__name__}: {exc}]"
        finally:
            shutil.rmtree(vault.parent, ignore_errors=True)
        results.append((label, ok))
        if verbose:
            print(f"  {'ok  ' if ok else 'FAIL'} {label}")
    return results


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repeat", type=int, default=1, help="number of full passes")
    args = parser.parse_args(argv)

    failures = []
    for run in range(1, args.repeat + 1):
        if args.repeat > 1:
            print(f"--- pass {run}/{args.repeat} ---")
        for label, ok in one_pass():
            if not ok:
                failures.append((run, label))
        passed = len(FIXTURES) - sum(1 for r, _ in failures if r == run)
        print(f"{passed}/{len(FIXTURES)} checks behaved as specified — "
              f"{RED} guards red on bad input, {GREEN} green on input the structure allows "
              f"(pass {run})")

    if failures:
        print(f"\n{len(failures)} failing fixture runs:", file=sys.stderr)
        for run, label in failures:
            print(f"  pass {run}: {label}", file=sys.stderr)
        return 1
    print(f"\n{args.repeat} pass(es), {len(FIXTURES)}/{len(FIXTURES)} every time.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
