"""Synthetic fixtures verify analysis math; these are not measurement results."""
import csv
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

spec = importlib.util.spec_from_file_location("pipeline_summary", Path(__file__).resolve().parents[2] / "analysis/pipeline_summary.py")
summary = importlib.util.module_from_spec(spec)
spec.loader.exec_module(summary)


def write_csv(path, header, data):
    with path.open("w", newline="") as stream:
        writer = csv.writer(stream)
        writer.writerow(header.split(","))
        writer.writerows(data)


class SummaryTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.run = Path(self.tmp.name)
        write_csv(self.run / "bridge.csv", "seq,frame_id,t_input_ns,t_done_ns,t_send_ns",
                  [(1, 0, 1000, 2000, 3001), (3, 2, 5000, 8000, 10000)])
        write_csv(self.run / "rx.csv", "type,seq,frame_id,t_input_ns,t_send_ns,t_rx_ns,age_at_send_us,crc_ok",
                  [("HEARTBEAT", 0, "", "", 1000, 1100, "", 1),
                   ("INFERENCE", 1, 0, 1000, 4000, 4001, 3, 1),
                   ("CRC_ERROR", "", "", "", "", 5000, "", 0)])
        write_csv(self.run / "source.csv", "frame_id,t_input_ns,status",
                  [(0, 1000, "sent"), (1, 2000, "sent"), (2, 5000, "sent"), (3, 6000, "dropped")])
        write_csv(self.run / "infer.csv", "frame_id,t_input_ns,t_done_ns,work_us,status",
                  [(0, 1000, 2000, 1, "sent"), (1, 2000, 3000, 1, "sent"), (2, 5000, 8000, 3, "sent")])
        (self.run / "bridge.stderr.log").write_text(json.dumps({"overwritten": 1, "dropped": 0, "discarded_on_stop": 0}))

    def test_stages_exact_join_and_losses(self):
        report = summary.summarize(self.run)
        metrics = report["latency_us"]
        self.assertEqual(metrics["input_to_done_us"], {"n": 3, "p50": 1., "p95": 3., "p99": 3., "max": 3.})
        self.assertEqual(metrics["done_to_send_us"]["p50"], 1.001)
        self.assertEqual(metrics["send_to_rx_us"]["max"], 1.)
        self.assertEqual(metrics["aoi_at_reception_us"]["max"], 3.001)
        self.assertEqual(report["counts"]["end_to_end_missing"], 3)
        self.assertEqual(report["counts"]["bridge_to_rx_missing"], 1)
        self.assertEqual(report["counts"]["bridge_overwritten"], 1)
        self.assertEqual(report["counts"]["rx_crc_errors"], 1)
        self.assertEqual(report["counts"]["source_ipc_dropped"], 1)

    def test_real_uart_without_rx(self):
        (self.run / "rx.csv").unlink()
        (self.run / "config.json").write_text('{"serial":"/dev/ttyAMA0"}')
        write_csv(self.run / "echo.csv", "accepted", [(1,), (0,)])
        write_csv(self.run / "mcu_status.csv", "state", [(3,)])
        report = summary.summarize(self.run)
        self.assertEqual(report["counts"]["echo_accepted"], 1)
        self.assertEqual(report["counts"]["mcu_status"], 1)
        self.assertNotIn("send_to_rx_us", report["latency_us"])
        self.assertIn("UNVERIFIED ON HARDWARE", report["evidence"])

    def test_empty_percentiles(self):
        self.assertIsNone(summary.distribution([])["p99"])

    def test_duplicate_ids_rejected(self):
        with self.assertRaises(ValueError):
            summary.indexed([{"frame_id": "0"}, {"frame_id": "0"}], "fixture")

    def test_bad_clock_rejected(self):
        write_csv(self.run / "bridge.csv", "seq,frame_id,t_input_ns,t_done_ns,t_send_ns", [(1, 0, 2000, 1000, 3000)])
        with self.assertRaisesRegex(ValueError, "clock regression"):
            summary.summarize(self.run)

    def test_throttled_excluded_and_unknown_label(self):
        self.assertTrue(summary.validity(self.run).startswith("UNKNOWN"))
        (self.run / "meta_after.json").write_text('{"throttled":"0x50000"}')
        self.assertTrue(summary.summarize(self.run)["excluded"])
        for name in ("meta_before.json", "meta_after.json"):
            (self.run / name).write_text('{"throttled":"0x0"}')
        self.assertEqual(summary.validity(self.run), "OK")


if __name__ == "__main__":
    unittest.main()
