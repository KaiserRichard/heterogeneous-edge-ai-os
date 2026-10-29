import csv
import json
import os
from pathlib import Path
import socket
import struct
import subprocess
import sys
import tempfile
import unittest
import uuid

CAMERA = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(CAMERA))
from analyze_t1 import COLUMNS, summarize


def ring_path(name):
    return Path('/tmp/hea-cam-' + name) if sys.platform == 'darwin' else Path('/dev/shm') / name


class CameraTests(unittest.TestCase):
    def test_fake_csv_datagrams_timestamps_and_drops(self):
        name = 'cam-test-' + uuid.uuid4().hex[:12]
        self.addCleanup(lambda: ring_path(name).unlink(missing_ok=True))
        with tempfile.TemporaryDirectory() as directory:
            # Dedicated socketpair passes a real connected Unix endpoint into hea_cam.
            tx, rx = socket.socketpair(socket.AF_UNIX, socket.SOCK_DGRAM)
            with tx, rx:
                path = Path(directory) / 'frames.csv'
                run = subprocess.run([str(CAMERA / 'build/hea_cam'), '--backend', 'fake',
                    '--output-fd', str(tx.fileno()), '--csv', str(path), '--shm', name,
                    '--width', '8', '--height', '4', '--fps', '20', '--count', '6',
                    '--fake-offset-ns', '2000000', '--fake-drop-every', '2'],
                    pass_fds=(tx.fileno(),), capture_output=True, text=True, timeout=10)
                self.assertEqual(run.returncode, 0, run.stderr)
                with path.open() as stream:
                    rows = list(csv.DictReader(stream))
                self.assertEqual(list(rows[0]), COLUMNS)
                self.assertEqual([r['status'] for r in rows], ['sent', 'injected_drop'] * 3)
                rx.settimeout(1)
                for row in rows:
                    self.assertEqual(int(row['t_recv_mono_ns']) - int(row['t_sensor_ns']), 2000000)
                    self.assertEqual(row['t_input_ns'], row['t_sensor_ns'])
                    if row['status'] == 'sent':
                        self.assertEqual(rx.recv(100), struct.pack('<IQ', int(row['frame_id']), int(row['t_sensor_ns'])))
                metadata = json.loads(Path(str(path) + '.meta.json').read_text())
                self.assertEqual(metadata['slots'], 4)
                self.assertGreater(metadata['clock_monotonic_ns'], 0)
                self.assertIn('clock_boottime_ns', metadata)
                counts = json.loads(run.stderr.splitlines()[-1])
                self.assertEqual((counts['generated'], counts['sent'], counts['dropped']), (6, 3, 3))
                output = Path(directory) / 'summary.json'
                analysis = subprocess.run([sys.executable, str(CAMERA / 'analyze_t1.py'), str(path),
                                           '--fps', '20', '--output', str(output)], capture_output=True, text=True)
                self.assertEqual(analysis.returncode, 0, analysis.stderr)
                report = json.loads(output.read_text())
                self.assertEqual(report['capture_drops'], 3)
                self.assertEqual(report['sequence_gaps'], 2)
                self.assertEqual(report['recv_sensor_offset_ns']['p99'], 2000000)

    def test_invalid_options_and_backend_fail(self):
        for args in (['--width', '0'], ['--slots', '0'], ['--fps', 'nan'],
                     ['--shm', '../bad'], ['--backend', 'bad'],
                     ['--fps', '30', '--period-ms', '100']):
            run = subprocess.run([str(CAMERA / 'build/hea_cam'), '--output', '/unused', *args],
                                 capture_output=True, text=True, timeout=5)
            self.assertNotEqual(run.returncode, 0, args)

    def test_analysis_exact_metrics_and_invalid_clock(self):
        def row(seq, sensor, offset=10):
            return dict(frame_id=seq, seq=seq, t_sensor_ns=sensor,
                        t_recv_mono_ns=sensor + offset, t_input_ns=sensor, status='sent')
        result = summarize([row(0, 100), row(1, 100000100, 20), row(3, 300000100, 40)], 10)
        self.assertEqual(result['interval_mean_ns'], 150000000)
        self.assertEqual(result['jitter_p99_ns'], 99000000)
        self.assertEqual(result['sequence_gaps'], 1)
        self.assertEqual(result['capture_drops'], 1)
        self.assertEqual(result['recv_sensor_offset_ns'], dict(p50=20, p99=39.6, max=40, min=10))
        result = summarize([row(0, 100, -1)], 10)
        self.assertFalse(result['timing_checks']['offset_positive_and_bounded'])
        with self.assertRaises(ValueError):
            summarize([row(0, 100), row(1, 99)], 10)
        with self.assertRaises(ValueError):
            summarize([], 10)


if __name__ == '__main__':
    unittest.main()
