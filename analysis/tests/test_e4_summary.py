"""Synthetic E4 fixtures only: these values are not hardware measurements."""
import csv
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch, Mock

REPO = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location("e4", REPO / "analysis/e4_summary.py")
e4 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(e4)
runner_spec = importlib.util.spec_from_file_location("campaign", REPO / "tools/experiments/e4_campaign.py")
campaign = importlib.util.module_from_spec(runner_spec)
runner_spec.loader.exec_module(campaign)


def write_csv(path, columns, data):
    with path.open("w", newline="") as stream:
        writer = csv.writer(stream)
        writer.writerow(columns)
        writer.writerows(data)


class E4Tests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.run = self.root / "F3-r01"
        self.run.mkdir()
        (self.run / "pipeline").mkdir()
        (self.run / "recovery").mkdir()
        self.meta = dict(fault="F3", rep=1, status="COMPLETE", steady_start_pi_ns=101_000_000_000,
                         onset_pi_ns=121_000_000_000, fault_end_pi_ns=122_000_000_000,
                         observation_end_pi_ns=131_000_000_000, recovery_start_pi_ns=131_100_000_000,
                         recovery_observation_end_pi_ns=134_000_000_000)
        self.save_meta()
        self.power()
        self.echo("pipeline", [(100_500_000_000, -99_000_000, 10), (120_500_000_000, -99_000_000, 10)])
        self.echo("recovery", [(132_500_000_000, -131_000_000, 10)])
        self.event_rows = [
            [1, 100_000_000_000, 1_000_000, "INIT", "FRESH", "READY", 999_000, 999_000, 0, ""],
            [2, 121_250_000_000, 22_200_000, "FRESH", "HOLD", "RESULT_SILENCE", 22_190_000, 22_000_000, 0, ""],
            [3, 121_550_000_000, 22_500_000, "HOLD", "FAILSAFE", "RESULT_TIMEOUT", 22_490_000, 22_000_000, 0, ""]]
        self.events()
        write_csv(self.run / "recovery/state_events.csv", e4.EVENT_COLUMNS,
                  [[4, 132_100_000_000, 1_000_000, 0, 1, 1, 990_000, 990_000, 0, ""]])

    def save_meta(self):
        (self.run / "run.json").write_text(json.dumps(self.meta))

    def events(self):
        write_csv(self.run / "pipeline/state_events.csv", e4.EVENT_COLUMNS, self.event_rows)

    def echo(self, segment, rows):
        write_csv(self.run / segment / "echo.csv",
                  ["accepted", "t4_pi_ns", "reference_pi_us", "mapping_offset_us", "mapping_drift", "rms_residual_us", "sample_count"],
                  [[1, t, 100_000_000, offset, 0, rms, 2] for t, offset, rms in rows])

    def power(self, baseline="0x0", last=None):
        data = [[t, baseline, 45000] for t in range(100_000_000_000, 134_000_000_001, 500_000_000)]
        if last is not None:
            data[-1][1] = last
        write_csv(self.run / "power.csv", ["t_pi_ns", "throttled", "temp_millic"], data)

    def test_latency_uses_mcu_mapping_not_delayed_receive_time(self):
        report = e4.summarize_run(self.run)
        self.assertEqual(report["validity"], "VALID", report)
        self.assertEqual(report["detection_us"], 200000)
        self.assertEqual(report["detection_mcu_us"], 200000)
        self.assertEqual(report["failsafe_us"], 500000)
        self.assertEqual(report["failsafe_mcu_us"], 500000)
        self.assertEqual(report["recovery_us"], 10000000)
        self.assertEqual(report["false_transitions"], 0)

    def test_explicit_mapped_timestamp(self):
        self.event_rows[1][-1] = 121_201_000_000
        self.events()
        self.assertEqual(e4.summarize_run(self.run)["detection_us"], 201000)

    def test_f1_replay_ignores_decoder_clock_and_uses_last_heartbeat(self):
        self.meta.update(fault="F1", fault_end_pi_ns=131_100_000_000)
        self.save_meta()
        capture = self.run / "capture"
        capture.mkdir()
        self.event_rows[1][6] = 22_000_000
        self.event_rows[1][-1] = 999_000_000_000  # bogus replay epoch
        write_csv(capture / "state_events.csv", e4.EVENT_COLUMNS, self.event_rows[1:])
        self.event_rows = self.event_rows[:1]
        self.events()
        report = e4.summarize_run(self.run)
        self.assertEqual(report["validity"], "VALID", report)
        self.assertEqual(report["detection_us"], 200000)
        self.assertEqual(report["detection_mcu_us"], 200000)
        self.assertEqual(report["recovery_us"], 900000)

    def test_live_and_new_sticky_bits_invalid_old_sticky_allowed(self):
        self.power("0x50000")
        self.assertEqual(e4.summarize_run(self.run)["validity"], "VALID")
        self.power("0x50000", "0x50001")
        self.assertIn("live throttle bits", e4.summarize_run(self.run)["reasons"])
        self.power("0x10000", "0x50000")
        self.assertIn("new sticky", e4.summarize_run(self.run)["reasons"])

    def test_rms_bound_and_lost_events(self):
        self.echo("pipeline", [(100_500_000_000, -99_000_000, 201)])
        self.assertIn("residual RMS", e4.summarize_run(self.run)["reasons"])
        self.assertEqual(e4.summarize_run(self.run, 250, 30)["validity"], "VALID")
        self.event_rows[-1][-2] = 1
        self.events()
        self.assertIn("lost_count", e4.summarize_run(self.run, 250, 30)["reasons"])

    def test_missing_fit_and_monitor_are_invalid(self):
        (self.run / "pipeline/echo.csv").unlink()
        self.assertEqual(e4.summarize_run(self.run)["validity"], "INVALID")
        (self.run / "power.csv").unlink()
        self.assertEqual(e4.summarize_run(self.run)["validity"], "INVALID")

    def test_false_transitions_and_short_windows_invalid(self):
        self.echo("pipeline", [(100_500_000_000, -99_000_000, 10), (109_500_000_000, -99_000_000, 10), (120_500_000_000, -99_000_000, 10)])
        self.event_rows.insert(1, [8, 110_000_000_000, 11_000_000, 1, 2, 2, 10_900_000, 10_800_000, 0, ""])
        self.events()
        report = e4.summarize_run(self.run)
        self.assertEqual(report["false_transitions"], 1)
        self.assertIn("continuously FRESH", report["reasons"])
        self.meta["onset_pi_ns"] -= 1
        self.save_meta()
        self.assertIn("shorter than 20", e4.summarize_run(self.run)["reasons"])

    def test_censored_results_are_blank_and_excluded_from_percentiles(self):
        self.event_rows = self.event_rows[:1]
        self.events()
        report = e4.summarize_run(self.run)
        self.assertEqual(report["validity"], "VALID", report)
        self.assertIsNone(report["detection_us"])
        self.assertIsNone(report["recovery_us"])
        table = e4.fault_table([report], {}, "fixture")
        row = next(r for r in table if r["fault"] == "F3" and r["metric"] == "detection_us")
        self.assertEqual(row["n_valid"], 1)
        self.assertEqual(row["n_samples"], 0)
        self.assertIsNone(row["p50_us"])

    def test_recovery_within_observation(self):
        self.event_rows.append([4, 122_300_000_000, 23_200_000, 3, 1, 1, 23_190_000, 23_190_000, 0, ""])
        self.events()
        self.assertEqual(e4.summarize_run(self.run)["recovery_us"], 200000)

    def test_clock_drift_inverse(self):
        fit = (0, 100_000_000, -99_000_000, .0001, 5)
        self.assertAlmostEqual(e4.map_mcu(1_000_000 + 10_001_000, fit), 110_000_000_000)

    def test_malformed_schema_and_nonfinite_data_invalid(self):
        write_csv(self.run / "pipeline/state_events.csv", ["state"], [[1]])
        self.assertIn("missing columns", e4.summarize_run(self.run)["reasons"])
        self.events()
        self.echo("pipeline", [(100_500_000_000, -99_000_000, "nan")])
        self.assertIn("non-finite", e4.summarize_run(self.run)["reasons"])

    def test_unknown_thresholds_and_literal_header_config(self):
        include = self.root / "include"
        include.mkdir()
        (include / "config.h").write_text("#define SUPERVISOR_HEARTBEAT_TIMEOUT_US 100000u\n#define RESULT_HOLD_US (200 * 1000)\n")
        values, _ = e4.thresholds(include=include)
        self.assertEqual(values["heartbeat_timeout_us"], 100000)
        self.assertIsNone(values["result_hold_us"])
        config = self.root / "thresholds.json"
        config.write_text('{"result_hold_us":200000,"result_failsafe_us":500000}')
        values, source = e4.thresholds(config)
        table = e4.fault_table([e4.summarize_run(self.run)], values, source)
        row = next(r for r in table if r["fault"] == "F3" and r["metric"] == "detection_mcu_us")
        self.assertEqual(row["p50_minus_threshold_us"], 0)
        self.assertEqual(e4.distribution([1, 2, 3, 4, 5]), (3, 5, 5))

    def test_cli_outputs_and_not_done(self):
        skipped = self.root / "F5-r01"
        skipped.mkdir()
        (skipped / "run.json").write_text(json.dumps(dict(fault="F5", rep=1, status="NOT_DONE", reason="no control")))
        result = subprocess.run([sys.executable, str(REPO / "analysis/e4_summary.py"), str(self.root)], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        rows = e4.read_csv(self.root / "e4_runs.csv")
        self.assertEqual([r["validity"] for r in rows], ["VALID", "NOT_DONE"])
        self.assertEqual(rows[1]["evidence"], "NOT DONE")
        self.assertIn("MEASURED", (self.root / "e4_faults.tex").read_text())
        self.assertEqual(len(e4.read_csv(self.root / "e4_faults.csv")), 25)

    def test_monitor_gap_invalid(self):
        records = e4.read_csv(self.run / "power.csv")
        records.pop(1)
        write_csv(self.run / "power.csv", list(records[0]), [list(r.values()) for r in records])
        self.assertIn("monitor gap", e4.summarize_run(self.run)["reasons"])

    def test_estimate_does_not_access_hardware_or_create_directory(self):
        target = self.root / "untouched"
        result = subprocess.run([sys.executable, str(REPO / "tools/experiments/e4_campaign.py"), str(target), "5", "--estimate-only"], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("13.3 min", result.stdout)
        self.assertIn("42.5 min", result.stdout)
        self.assertFalse(target.exists())

    def test_event_discontinuity_invalid(self):
        self.event_rows[-1][3] = "FRESH"
        self.events()
        self.assertIn("discontinuity", e4.summarize_run(self.run)["reasons"])

    def test_cli_reuses_campaign_bound_and_threshold_snapshot(self):
        self.echo("pipeline", [(100_500_000_000, -99_000_000, 201), (120_500_000_000, -99_000_000, 201)])
        (self.root / "campaign.json").write_text('{"rms_bound_us":250}')
        (self.root / "supervisor_thresholds.json").write_text('{"result_hold_us":200000}')
        result = subprocess.run([sys.executable, str(REPO / "analysis/e4_summary.py"), str(self.root)], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(e4.read_csv(self.root / "e4_runs.csv")[0]["validity"], "VALID")
        rows = e4.read_csv(self.root / "e4_faults.csv")
        row = next(r for r in rows if r["fault"] == "F3" and r["metric"] == "detection_mcu_us")
        self.assertEqual(row["threshold_us"], "200000.0")

    def test_signal_onset_order_and_resume_on_interrupt(self):
        calls = []
        clock_values = iter([123, 456])
        def clock():
            calls.append("clock")
            return next(clock_values)
        with patch.object(campaign, "raw", side_effect=clock), patch.object(campaign.os, "kill", side_effect=lambda pid, sig: calls.append(sig)), patch.object(campaign.time, "sleep", side_effect=KeyboardInterrupt):
            meta = {}
            with self.assertRaises(KeyboardInterrupt):
                campaign.signal_fault(1234, "F3", meta)
        self.assertEqual(calls, ["clock", campaign.signal.SIGSTOP, "clock", campaign.signal.SIGCONT])
        self.assertEqual(meta, dict(onset_pi_ns=123, fault_end_pi_ns=456))

    def test_kill_signal_has_no_sudo_or_hardware(self):
        with patch.object(campaign, "raw", return_value=123), patch.object(campaign.os, "kill") as kill, patch.object(campaign.time, "sleep") as sleep:
            meta = {}
            campaign.signal_fault(1234, "F1", meta)
            kill.assert_called_once_with(1234, campaign.signal.SIGKILL)
            sleep.assert_not_called()
            self.assertNotIn("fault_end_pi_ns", meta)

    def test_f5_suppression_ack_and_resume_on_interrupt(self):
        pipe = Mock()
        pipe.toggle_inference.side_effect = [150, 450]
        with patch.object(campaign, "raw", side_effect=[100, 400]), patch.object(
                campaign.time, "sleep", side_effect=KeyboardInterrupt):
            meta = {}
            with self.assertRaises(KeyboardInterrupt):
                campaign.stale_fault(pipe, meta)
        self.assertEqual([call.args for call in pipe.toggle_inference.call_args_list], [(True,), (False,)])
        self.assertEqual(meta, dict(suppress_request_pi_ns=100, onset_pi_ns=150,
                                    resume_request_pi_ns=400, fault_end_pi_ns=450))

    def test_f2_hold_does_not_compare_with_heartbeat_threshold(self):
        self.meta["fault"] = "F2"
        self.save_meta()
        self.event_rows[1][5] = "9"
        self.event_rows[1][6] = 22_101_404
        self.event_rows[2][5] = "3"
        self.event_rows[2][6] = 22_399_404
        self.events()
        report = e4.summarize_run(self.run)
        self.assertEqual(report["detection_reference"], "last_inf_mcu_us")
        self.assertEqual(report["failsafe_reference"], "last_hb_mcu_us")
        self.assertEqual(report["failsafe_mcu_us"], 100596)
        table = e4.fault_table([report], {"heartbeat_timeout_us": 100000}, "fixture")
        hold = next(r for r in table if r["fault"] == "F2" and r["metric"] == "detection_mcu_us")
        self.assertIn("age_at_send_us", hold["threshold"])
        self.assertIsNone(hold["p50_minus_threshold_us"])
        fail = next(r for r in table if r["fault"] == "F2" and r["metric"] == "failsafe_mcu_us")
        self.assertEqual(fail["p50_minus_threshold_us"], 596)

    def test_cleanup_resumes_stopped_children_and_escalates_owned_pid(self):
        pipe = campaign.Pipeline(self.root, None, self.root, -1)
        stopped = Mock()
        stopped.poll.return_value = None
        stopped.wait.side_effect = [subprocess.TimeoutExpired("fake", 2), 0]
        exited = Mock()
        exited.poll.return_value = 0
        pipe.processes = {"hea_bridge": stopped, "hea_infer_stub": exited}
        pipe.close()
        stopped.send_signal.assert_called_once_with(campaign.signal.SIGCONT)
        stopped.terminate.assert_called_once()
        stopped.kill.assert_called_once()
        self.assertEqual(stopped.wait.call_count, 2)
        exited.terminate.assert_not_called()

    def test_monitor_cleanup_before_start_is_safe(self):
        campaign.Monitor(self.root).close()

    def test_stale_live_explicit_and_replay_mappings_unavailable(self):
        self.echo('pipeline', [(100_500_000_000, -99_000_000, 10)])
        self.event_rows[1][-1] = 121_200_000_000
        self.events()
        fits = e4.clock_fits(self.run / 'pipeline')
        for replay in (False, True):
            rows = e4.events(self.run / 'pipeline', fits, replay=replay)
            self.assertIsNone(rows[1]['pi_ns'])
            self.assertIsNone(rows[2]['pi_ns'])
            self.assertIsNotNone(e4.events(self.run / 'pipeline', fits, replay=replay,
                                          max_calibration_age_s=30)[1]['pi_ns'])
        report = e4.summarize_run(self.run)
        self.assertEqual(report['validity'], 'INVALID')
        self.assertIsNone(report['detection_us'])
        self.assertIn('stale calibration', report['reasons'])

    def test_replay_and_startup_extrapolation_age_boundary(self):
        self.event_rows = [[1, 999_000_000_000, 1_000_000, 'INIT', 'FRESH', 1, 0, 0, 0, '']]
        self.events()
        fit = (105_000_000_000, 100_000_000, -99_000_000, 0, 1)
        self.assertIsNotNone(e4.events(self.run / 'pipeline', [fit], replay=True)[0]['pi_ns'])
        self.assertIsNone(e4.events(self.run / 'pipeline', [(fit[0]+1, *fit[1:])], replay=True)[0]['pi_ns'])


if __name__ == "__main__":
    unittest.main()