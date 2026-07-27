"""Acceptance test: prove every guard goes red on bad input, on this machine.

Nine fixtures, each built in a throwaway vault under the system temp directory. The verdict
comes from process exit codes and from files on disk -- never from parsing console text, which
wraps at the terminal width and differs per shell.

    python acceptance.py            one pass
    python acceptance.py --repeat 10

Exit 0 only when all nine passed in every pass.
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


def fixture_9_unknown_folder(vault, project):
    (project / "99_extra").mkdir(exist_ok=True)
    write_note(project / "99_extra" / "verlorene-notiz.md", title="Verloren")
    code, _, err = run_tool("build_index.py", "--vault", project)
    return code != 0 and "99_extra" in err


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


FIXTURES = [
    ("0 healthy control: clean vault is green and stable", control_clean_vault_is_green),
    ("1 note without title", fixture_1_missing_title),
    ("2 markdown debris in summary", fixture_2_summary_debris),
    ("3 dead wikilink", fixture_3_dead_wikilink),
    ("4 forbidden character in filename", fixture_4_forbidden_filename),
    ("5 non-ASCII filename stays in the denominator", fixture_5_non_ascii_filename),
    ("6 second index run changes nothing", fixture_6_second_run_is_a_noop),
    ("7 suite runner on an empty directory", fixture_7_empty_suite_dir),
    ("8 freshness check without a run log", fixture_8_freshness_without_log),
    ("9 folder that is not a configured category", fixture_9_unknown_folder),
]


def one_pass(verbose=True):
    """Every fixture gets its own vault, so one fixture cannot poison the next."""
    results = []
    for label, fn in FIXTURES:
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
              f"9 guards red on bad input, 1 healthy control green (pass {run})")

    if failures:
        print(f"\n{len(failures)} failing fixture runs:", file=sys.stderr)
        for run, label in failures:
            print(f"  pass {run}: {label}", file=sys.stderr)
        return 1
    print(f"\n{args.repeat} pass(es), {len(FIXTURES)}/{len(FIXTURES)} every time.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
