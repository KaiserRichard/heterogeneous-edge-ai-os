"""Synthetic data only; these tests run on macOS and Linux."""
import csv
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from analysis import cyclictest_summary as summary


ROOT = Path(__file__).resolve().parents[2]
FIXTURE = Path(__file__).parent / "fixtures" / "cyclictest_hist.txt"
HISTOGRAM = FIXTURE.read_text(encoding="utf-8")


class SummaryTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(dir=Path(__file__).parent)
        self.addCleanup(self.temporary.cleanup)
        self.campaign = Path(self.temporary.name)

    def run_directory(self, name="idle_r1", histogram=HISTOGRAM):
        directory = self.campaign / name
        directory.mkdir()
        metadata = dict(kernel="synthetic_kernel", governor="performance",
                        temp_millic=40000, throttled="0x0")
        for filename in ("meta_before.json", "meta_after.json"):
            (directory / filename).write_text(json.dumps(metadata), encoding="utf-8")
        (directory / "thermal.csv").write_text(
            "timestamp,temp_millic,cpu0_khz,throttled\n1,42000,2400000,0x0\n",
            encoding="utf-8")
        (directory / "cyclictest_hist.txt").write_text(histogram, encoding="utf-8")
        return directory

    def parse_text(self, text):
        path = self.campaign / "hist.txt"
        path.write_text(text, encoding="utf-8")
        return summary.parse_histogram(path)

    def test_histogram_statistics_and_nearest_rank(self):
        result = summary.parse_histogram(FIXTURE)
        self.assertEqual(result["samples"], 1000)
        self.assertEqual(result["overflows"], 0)
        self.assertEqual(result["min_us"], 1)
        self.assertAlmostEqual(result["avg_us"], 1.561)
        self.assertEqual(result["avg_source"], "histogram")
        self.assertEqual([result[key] for key in ("p50_us", "p95_us", "p99_us", "p99_9_us", "max_us")],
                         [1, 2, 3, 4, 5])

    def test_overflow_count_max_and_unknown_tail(self):
        text = HISTOGRAM.replace("# Histogram Overflows: 00000", "# Histogram Overflows: 00020")
        text = text.replace("# Max Latencies: 00005", "# Max Latencies: 00100")
        text = text.replace("# Avg Latencies: 00001", "# Avg Latencies: 00002")
        result = self.parse_text(text)
        self.assertEqual(result["samples"], 1020)
        self.assertEqual(result["max_us"], 100)
        self.assertEqual(result["p50_us"], 2)
        self.assertIsNone(result["p99_us"])
        self.assertIsNone(result["p99_9_us"])
        self.assertEqual(result["avg_us"], 2)
        self.assertEqual(result["avg_source"], "cyclictest_footer_truncated")

    def test_overflow_only_and_rank_n_is_max(self):
        result = self.parse_text("# Histogram\n000000 000000\n# Total: 0\n"
                                 "# Min Latencies: 10\n# Avg Latencies: 15\n"
                                 "# Max Latencies: 20\n# Histogram Overflows: 2\n")
        self.assertEqual(result["samples"], 2)
        self.assertIsNone(result["p50_us"])
        self.assertEqual(result["p99_us"], 20)

    def test_reject_incomplete_inconsistent_or_multithread_histograms(self):
        for text in ("", HISTOGRAM.split("# Total:")[0],
                     HISTOGRAM.replace("000001000", "000000999"),
                     HISTOGRAM.replace("000001 000500", "000001 000500 000100"),
                     HISTOGRAM.replace("000001 000500", "000001 -1"),
                     HISTOGRAM.replace("000001 000500", "000001 000500\n000001 1"),
                     HISTOGRAM.replace("# Max Latencies: 00005", "# Max Latencies: 00004"),
                     HISTOGRAM.replace("# Histogram Overflows: 00000", "# Histogram Overflows: 00001")):
            with self.subTest(text=text), self.assertRaises(ValueError):
                self.parse_text(text)

    def test_throttle_in_each_health_source_invalidates(self):
        for index, filename in enumerate(("meta_before.json", "meta_after.json", "thermal.csv"), 1):
            directory = self.run_directory(f"idle_r{index}")
            path = directory / filename
            path.write_text(path.read_text(encoding="utf-8").replace("0x0", "0x1"), encoding="utf-8")
            with self.subTest(filename=filename):
                row = summary.summarize_run(directory)
                self.assertEqual(row["status"], "INVALID")
                self.assertIn(filename, row["reason"])
                self.assertIn("0x1", row["throttled"])

    def test_sticky_bits_only_invalidate_when_new_during_run(self):
        directory = self.run_directory("idle_r1")
        for name in ("meta_before.json", "meta_after.json", "thermal.csv"):
            path = directory / name
            path.write_text(path.read_text(encoding="utf-8").replace("0x0", "0x50000"), encoding="utf-8")
        self.assertEqual(summary.summarize_run(directory)["status"], "VALID")
        before = directory / "meta_before.json"
        before.write_text(before.read_text(encoding="utf-8").replace("0x50000", "0x0"), encoding="utf-8")
        row = summary.summarize_run(directory)
        self.assertEqual(row["status"], "INVALID")
        self.assertIn("new sticky", row["reason"])

    def test_headerless_legacy_thermal_and_numeric_zero(self):
        directory = self.run_directory()
        (directory / "thermal.csv").write_text("1,45000,2400000,0x00000000\n2,44000,2400000,0\n", encoding="utf-8")
        row = summary.summarize_run(directory)
        self.assertEqual(row["status"], "VALID")
        self.assertEqual(row["max_temp_c"], 45)
        self.assertEqual(row["throttled"], "0x0")

    def test_missing_or_bad_health_data_invalid(self):
        for index, text in enumerate(("", "1,42000,2400000,unavailable\n", "1,nan,2400000,0x0\n", "bad,row\n"), 1):
            directory = self.run_directory(f"idle_r{index}")
            (directory / "thermal.csv").write_text(text, encoding="utf-8")
            self.assertEqual(summary.summarize_run(directory)["status"], "INVALID")
        directory = self.run_directory("idle_r5")
        (directory / "meta_after.json").unlink()
        self.assertEqual(summary.summarize_run(directory)["status"], "INVALID")

    def test_failed_commands_invalid(self):
        for index, filename in enumerate(("exit_code", "stress_exit_code"), 1):
            directory = self.run_directory(f"idle_r{index}")
            (directory / filename).write_text("1\n", encoding="utf-8")
            self.assertEqual(summary.summarize_run(directory)["status"], "INVALID")

    def test_kernel_change_invalid(self):
        directory = self.run_directory()
        path = directory / "meta_after.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        data["kernel"] = "changed_kernel"
        path.write_text(json.dumps(data), encoding="utf-8")
        self.assertEqual(summary.summarize_run(directory)["status"], "INVALID")

    def test_profile_is_part_of_condition(self):
        directory = self.run_directory()
        for name in ("meta_before.json", "meta_after.json"):
            path = directory / name
            data = json.loads(path.read_text(encoding="utf-8"))
            data["profile"] = "P1"
            path.write_text(json.dumps(data), encoding="utf-8")
        self.assertEqual(summary.summarize_run(directory)["condition"], "P1_idle")

    def test_aggregate_median_max_and_invalid_exclusion(self):
        rows = [summary.summarize_run(self.run_directory(f"idle_r{r}")) for r in range(1, 5)]
        for row, p99, maximum in zip(rows, [3, 5, 7, 999], [5, 8, 10, 999]):
            row.update(p99_us=p99, max_us=maximum)
        rows[-1]["status"] = "INVALID"
        result = summary.aggregate_runs(rows)[0]
        self.assertEqual((result["runs"], result["invalid_runs"], result["p99_us"], result["max_us"]),
                         (3, 1, 5, 10))
        rows[0]["p99_us"] = None
        self.assertIsNone(summary.aggregate_runs(rows)[0]["p99_us"])

    def test_all_invalid_condition_still_reported(self):
        directory = self.run_directory()
        (directory / "thermal.csv").write_text("1,42000,2400000,0x1\n", encoding="utf-8")
        result = summary.aggregate_runs([summary.summarize_run(directory)])[0]
        self.assertEqual(result["runs"], 0)
        self.assertEqual(result["invalid_runs"], 1)
        self.assertIsNone(result["max_us"])

    def test_cli_csv_table_and_raw_preservation(self):
        directory = self.run_directory("idle_test_r1")
        result = subprocess.run([sys.executable, str(ROOT / "analysis" / "cyclictest_summary.py"), str(self.campaign)],
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        with (self.campaign / "summary.csv").open(newline="", encoding="utf-8") as handle:
            rows = list(csv.DictReader(handle))
        self.assertEqual(rows[0]["p99_us"], "3")
        with (self.campaign / "summary_by_condition.csv").open(newline="", encoding="utf-8") as handle:
            self.assertEqual(list(csv.DictReader(handle))[0]["runs"], "1")
        table = (self.campaign / "summary_table.tex").read_text(encoding="utf-8")
        self.assertIn(r"\toprule", table)
        self.assertIn(r"idle\_test", table)
        self.assertIn(r"synthetic\_kernel", table)
        self.assertEqual((directory / "cyclictest_hist.txt").read_text(encoding="utf-8"), HISTOGRAM)

    def test_cli_no_runs_fails(self):
        result = subprocess.run([sys.executable, str(ROOT / "analysis" / "cyclictest_summary.py"), str(self.campaign)],
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 2)
        self.assertFalse((self.campaign / "summary.csv").exists())

    def test_latex_escape(self):
        self.assertEqual(summary.latex_escape("a_b&c%#"), r"a\_b\&c\%\#")


if __name__ == "__main__":
    unittest.main()
