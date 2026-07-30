"""Suite for check_freshness.py."""

import shutil
import sys
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from _testkit import make_vault, run_tool


def stamp(hours_ago):
    return (datetime.now(timezone.utc) - timedelta(hours=hours_ago)).strftime("%Y-%m-%dT%H:%M:%S+00:00")


class CheckFreshnessTest(unittest.TestCase):
    def setUp(self):
        self.vault = make_vault(("ProjektEins",))
        self.log = self.vault / "00_Global" / "06_tools" / "runs.log"

    def tearDown(self):
        shutil.rmtree(self.vault.parent, ignore_errors=True)

    def write_log(self, *lines):
        self.log.parent.mkdir(parents=True, exist_ok=True)
        self.log.write_text("\n".join(lines) + ("\n" if lines else ""), encoding="utf-8", newline="\n")

    # ------------------------------------------------------------------ control

    def test_healthy_control(self):
        self.write_log(f"{stamp(1)}\tbuild_index\tok\t0 defects")
        code, out, err = run_tool("check_freshness.py", "--vault", self.vault, "--jobs", "build_index")
        self.assertEqual(code, 0, err)
        self.assertIn("1/1 jobs fresh", out)

    # ------------------------------------------------------------ failure modes

    def test_missing_log_is_did_not_run_not_fine(self):
        code, out, err = run_tool("check_freshness.py", "--vault", self.vault, "--jobs", "build_index")
        self.assertEqual(code, 1)
        self.assertIn("did not run", err)
        self.assertNotIn("fresh", out)

    def test_blank_log_is_did_not_run(self):
        self.write_log()
        code, _, err = run_tool("check_freshness.py", "--vault", self.vault, "--jobs", "build_index")
        self.assertEqual(code, 1)
        self.assertIn("did not run", err)

    def test_stale_healthy_run_is_red(self):
        self.write_log(f"{stamp(72)}\tbuild_index\tok\t0 defects")
        code, out, err = run_tool("check_freshness.py", "--vault", self.vault,
                                  "--jobs", "build_index", "--max-age-hours", "24")
        self.assertEqual(code, 1)
        self.assertIn("0/1 jobs fresh", out)
        self.assertIn("72", err)

    def test_only_failed_runs_count_as_did_not_run(self):
        self.write_log(f"{stamp(1)}\tbuild_index\tdefects\t3 defects")
        code, _, err = run_tool("check_freshness.py", "--vault", self.vault, "--jobs", "build_index")
        self.assertEqual(code, 1)
        self.assertIn("did not run", err)
        self.assertIn("no healthy line", err)

    def test_malformed_lines_are_counted_not_swallowed(self):
        self.write_log(f"{stamp(1)}\tbuild_index\tok\t0 defects", "kaputte zeile ohne tabs")
        code, out, err = run_tool("check_freshness.py", "--vault", self.vault, "--jobs", "build_index")
        self.assertEqual(code, 1)
        self.assertIn("1 malformed", out)
        self.assertIn("malformed", err)

    def test_jobs_config_written_with_a_bom_is_still_read(self):
        """#12. Recipe without the fix: put encoding="utf-8" back in job_lists.

        json.loads then raises on the BOM, the except returned the default job list, and the
        check measured a set of jobs the user never configured -- without a word. Measured
        that way on this machine: a jobs.json naming only build_index produced a run that
        also demanded check_links.
        """
        config = self.vault / "00_Global" / "06_tools" / "jobs.json"
        config.parent.mkdir(parents=True, exist_ok=True)
        config.write_text('{"jobs": ["build_index"]}', encoding="utf-8-sig", newline="\n")
        self.write_log(f"{stamp(1)}\tbuild_index\tok\t0 defects")
        code, out, err = run_tool("check_freshness.py", "--vault", self.vault)
        self.assertEqual(code, 0, out + err)
        self.assertIn("1/1 jobs fresh", out)

    def test_an_unreadable_jobs_config_says_so_instead_of_defaulting_quietly(self):
        config = self.vault / "00_Global" / "06_tools" / "jobs.json"
        config.parent.mkdir(parents=True, exist_ok=True)
        config.write_text("{ das ist kein json", encoding="utf-8", newline="\n")
        self.write_log(f"{stamp(1)}\tbuild_index\tok\t0 defects")
        code, out, err = run_tool("check_freshness.py", "--vault", self.vault)
        self.assertIn("jobs.json", err)
        self.assertIn("unreadable", err)

    def test_non_ascii_job_name_survives_the_subprocess_round_trip(self):
        self.write_log(f"{stamp(1)}\tbuild_index\tok\t0 defects")
        code, _, err = run_tool("check_freshness.py", "--vault", self.vault, "--jobs", "Zählung")
        self.assertEqual(code, 1)
        self.assertIn("Zählung", err)

    # ------------------------------------------------- the second list (#3)

    def write_config(self, text):
        config = self.vault / "00_Global" / "06_tools" / "jobs.json"
        config.parent.mkdir(parents=True, exist_ok=True)
        config.write_text(text, encoding="utf-8", newline="\n")
        return config

    def test_an_on_demand_tool_stays_out_of_the_unclassified_line(self):
        """The reason the second list exists at all.

        Every tool logs, so without it the "nobody watches this" line names every tool in the
        vault on every run -- noise, and a report nobody reads is one that gets dropped from the
        chain. Classified means silent here, and only here.

        Recipe without the fix, measured on this machine 2026-07-30: drop the `- set(on_demand)`
        term from `unclassified` in check_freshness.py. test_check_freshness 13/15 -- this case
        and the bare-list one, which asserts the same count from the other shape. The healthy
        control stays green, which is why the control alone could never have caught it.
        """
        self.write_config('{"jobs": ["build_index"], '
                          '"on_demand": {"mein_werkzeug": "laeuft von Hand"}}')
        self.write_log(f"{stamp(1)}\tbuild_index\tok\t0 defects",
                       f"{stamp(5)}\tmein_werkzeug\tok\tetwas getan")
        code, out, err = run_tool("check_freshness.py", "--vault", self.vault)
        self.assertEqual(code, 0, out + err)
        self.assertIn("1/1 jobs fresh", out)
        self.assertIn("1 on demand", out)
        self.assertIn("0 unclassified", out)
        self.assertNotIn("mein_werkzeug", out)

    def test_an_unclassified_tool_is_named_and_does_not_change_the_exit_code(self):
        """The only real signal here: somebody built a tool and nobody decided about it.

        It must be loud enough to see and cheap enough to ignore. Red would be neither -- the
        first tool a user writes for themselves would make the chain red every run, and a check
        that is always red gets switched off rather than answered.

        Recipe without the fix, measured on this machine 2026-07-30: return 1 when `unclassified`
        is non-empty. test_check_freshness 13/15 -- this case and the missing-key one, both on
        the exit code alone and with their output unchanged, which is the distinction they are
        here to hold.
        """
        self.write_log(f"{stamp(1)}\tbuild_index\tok\t0 defects",
                       f"{stamp(2)}\tmein_werkzeug\tok\tetwas getan")
        code, out, err = run_tool("check_freshness.py", "--vault", self.vault,
                                  "--jobs", "build_index")
        self.assertEqual(code, 0, out + err)
        self.assertIn("1 unclassified", out)
        self.assertIn("mein_werkzeug", out)

    def write_tool(self, name, body="from vault_paths import log_run\nlog_run(v, 'x', 'ok')\n"):
        """A script in the vault's own tool folder. Never executed -- only read."""
        target = self.log.parent / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(body, encoding="utf-8", newline="\n")
        return target

    # ------------------------------------------- the population, not only the log (#24)

    def test_a_tool_that_never_ran_is_still_reported_as_unclassified(self):
        """#24, and the check used to confirm its own silence over exactly this case.

        `unclassified` was derived from the log alone. A tool no chain calls never writes a line,
        so it could not appear in `seen`, so it could not be reported -- and the tools that fall
        out of a chain are precisely the ones that never log. Measured 2026-07-30 against a real
        vault: `0 unclassified` while count_tokens.py sat in the folder in neither list.

        Exit stays 0. That is decided, not incidental: an unclassified tool has not failed, and a
        chain that goes red the first time a user adds a tool of their own gets switched off.

        Recipe without the fix, measured on this machine 2026-07-30: drop `| on_disk` from the
        `unclassified` line in main(). This case goes red on the count alone -- the tool is on
        disk, in no list, and the report says `0 unclassified` with exit 0 either way, which is
        why nothing noticed.
        """
        self.write_log(f"{stamp(1)}\tbuild_index\tok\t0 defects")
        self.write_tool("mein_werkzeug.py")
        code, out, err = run_tool("check_freshness.py", "--vault", self.vault,
                                  "--jobs", "build_index")
        self.assertEqual(code, 0, out + err)
        self.assertIn("1 unclassified", out)
        self.assertIn("mein_werkzeug", out)

    def test_a_tool_that_cannot_log_is_not_asked_to_be_classified(self):
        """The population's edge, and the healthy control for the case above.

        Without it, the fix above would name every `.py` in the folder -- run_suites, acceptance,
        verify_setup and upgrade all run, all reach a verdict and none of them log, so all four
        would sit in the report permanently. Four standing lines above the one line that means
        something is how a report stops being read.

        Asking whether a tool that cannot log is watched has no answer that changes anything: it
        can never be late, because it can never be in the log at all.
        """
        self.write_log(f"{stamp(1)}\tbuild_index\tok\t0 defects")
        self.write_tool("stilles_werkzeug.py", "print('reaches a verdict, writes no line')\n")
        code, out, err = run_tool("check_freshness.py", "--vault", self.vault,
                                  "--jobs", "build_index")
        self.assertEqual(code, 0, out + err)
        self.assertIn("0 unclassified", out)
        self.assertNotIn("stilles_werkzeug", out)

    def test_a_suite_in_the_tool_folder_is_not_a_job(self):
        """`test_X.py` is what run_suites.py collects, not something a scheduler runs.

        Excluded structurally rather than by taste: a suite that exercises log_run() would
        otherwise ask to be classified as a scheduled job, and the user's only way out would be
        to declare every suite in their config.
        """
        self.write_log(f"{stamp(1)}\tbuild_index\tok\t0 defects")
        self.write_tool("test_mein_werkzeug.py")
        code, out, err = run_tool("check_freshness.py", "--vault", self.vault,
                                  "--jobs", "build_index")
        self.assertEqual(code, 0, out + err)
        self.assertIn("0 unclassified", out)
        self.assertNotIn("test_mein_werkzeug", out)

    def test_the_third_list_takes_a_tool_out_of_the_unclassified_line(self):
        """`not_invoked` is the decision, and this is what making it is worth.

        The same key build_kit.py's chain check reads: one structure, so "deliberately outside
        the chain" is stated once and cannot be answered two different ways by two tools.
        """
        self.write_config('{"jobs": ["build_index"], '
                          '"not_invoked": {"mein_werkzeug": "ein Modul, kein Kommando"}}')
        self.write_log(f"{stamp(1)}\tbuild_index\tok\t0 defects")
        self.write_tool("mein_werkzeug.py")
        code, out, err = run_tool("check_freshness.py", "--vault", self.vault)
        self.assertEqual(code, 0, out + err)
        self.assertIn("1 not invoked", out)
        self.assertIn("0 unclassified", out)

    def test_a_job_watched_and_declared_uncalled_stops_the_run(self):
        """The pair check extended to three lists, on the pair that did not exist before.

        A tool cannot both be called by no chain and be the thing a chain is watched for. Same
        reasoning as the watched/on-demand clash: picking a winner leaves the other entry sitting
        in the file doing nothing, and no run can then show which statement applies.

        Recipe without the fix, measured on this machine 2026-07-30: reduce the `clash` set back
        to `set(configured) & set(on_demand)`. This case goes red -- the run reports the job as
        watched and never mentions that its own config also calls it uninvoked.
        """
        self.write_config('{"jobs": ["build_index", "mein_werkzeug"], '
                          '"not_invoked": {"mein_werkzeug": "kein Kommando"}}')
        self.write_log(f"{stamp(1)}\tbuild_index\tok\t0 defects")
        code, out, err = run_tool("check_freshness.py", "--vault", self.vault)
        self.assertEqual(code, 2, out + err)
        self.assertIn("mein_werkzeug", err)
        self.assertIn("jobs.json", err)
        self.assertNotIn("jobs fresh", out, "it measured anyway over a config it called broken")

    def test_a_job_in_both_lists_stops_the_run_instead_of_picking_one(self):
        """Exit 2, and deliberately not "watched wins".

        Picking a winner leaves the losing entry sitting in the file doing nothing, and no run
        can then show which of the two statements applies. Stopping is the only outcome that
        makes the contradiction visible where it lives, which is the config file.

        Recipe without the fix, measured on this machine 2026-07-30: delete the `both` block from
        main(). test_check_freshness 14/15 -- this case and nothing else. The tool then reports
        the job as watched and never says that its own config says otherwise.
        """
        self.write_config('{"jobs": ["build_index", "mein_werkzeug"], '
                          '"on_demand": {"mein_werkzeug": "laeuft von Hand"}}')
        self.write_log(f"{stamp(1)}\tbuild_index\tok\t0 defects")
        code, out, err = run_tool("check_freshness.py", "--vault", self.vault)
        self.assertEqual(code, 2, out + err)
        self.assertIn("mein_werkzeug", err)
        self.assertIn("jobs.json", err)
        self.assertNotIn("jobs fresh", out, "it measured anyway over a config it called broken")

    def test_a_config_without_the_second_key_does_not_borrow_the_built_in_one(self):
        """A present config that gets silently completed measures a list the user never chose.

        That is the same defect as the BOM case two tests up, one level quieter: the file is
        readable, so nothing warns, and the tool would classify three tools on the strength of a
        default the user cannot see. Empty is the honest reading, and the unclassified line then
        names them so the decision is theirs.

        Recipe without the fix, measured on this machine 2026-07-30: make the missing key fall
        back to DEFAULT_ON_DEMAND in job_lists(). test_check_freshness 14/15 -- this case and
        nothing else. check_duplicates disappears from the output and the count reads
        `3 on demand` against a config that says nothing about any of them.
        """
        self.write_config('{"jobs": ["build_index"]}')
        self.write_log(f"{stamp(1)}\tbuild_index\tok\t0 defects",
                       f"{stamp(3)}\tcheck_duplicates\tok\t0 flagged")
        code, out, err = run_tool("check_freshness.py", "--vault", self.vault)
        self.assertEqual(code, 0, out + err)
        self.assertIn("0 on demand", out)
        self.assertIn("check_duplicates", out)

    def test_the_second_list_may_also_be_written_as_a_bare_list(self):
        """A user mirroring the shape of `jobs` writes a list. It carries no reasons, and that
        is the only thing it loses -- refusing it would hard-fail an honest config over
        cosmetics.

        Recipe without the fix, measured on this machine 2026-07-30: drop the
        `isinstance(raw, dict)` branch from job_lists(). test_check_freshness 14/15 -- this case
        and nothing else. `dict(["mein_werkzeug"])` raises ValueError, which the config reader
        already catches, so the whole file is declared unreadable and BOTH lists fall back to
        the built-in ones: the run then demands check_links, which the log never mentions, and
        exits 1 over a config that was merely written in the other shape.
        """
        self.write_config('{"jobs": ["build_index"], "on_demand": ["mein_werkzeug"]}')
        self.write_log(f"{stamp(1)}\tbuild_index\tok\t0 defects",
                       f"{stamp(2)}\tmein_werkzeug\tok\tetwas getan")
        code, out, err = run_tool("check_freshness.py", "--vault", self.vault)
        self.assertEqual(code, 0, out + err)
        self.assertIn("1 on demand", out)
        self.assertIn("0 unclassified", out)

    def test_the_check_logs_its_own_run_like_every_other_tool(self):
        """Otherwise "the freshness check runs in the chain" is a claim about a command file.

        Delete the step from `/vaultkit` and a log with no check_freshness line in it looks
        exactly like a check that ran and found nothing. The line is what tells those two apart,
        and it is why check_freshness stands in the on-demand list rather than nowhere.

        Recipe without the fix, measured on this machine 2026-07-30: remove the log_run call from
        the success path in main(). test_check_freshness 14/15 -- this case and nothing else,
        because no other case reads the log back after the run.
        """
        self.write_log(f"{stamp(1)}\tbuild_index\tok\t0 defects")
        code, out, err = run_tool("check_freshness.py", "--vault", self.vault,
                                  "--jobs", "build_index")
        self.assertEqual(code, 0, out + err)
        written = self.log.read_text(encoding="utf-8").splitlines()
        mine = [line for line in written if "\tcheck_freshness\t" in line]
        self.assertEqual(len(mine), 1, f"no line of its own in {written}")
        self.assertIn("\tok\t", mine[0])
        # It reads before it writes, so its own line must not be in the denominator it reports.
        self.assertIn("1 log lines", out)


if __name__ == "__main__":
    unittest.main(verbosity=1)
