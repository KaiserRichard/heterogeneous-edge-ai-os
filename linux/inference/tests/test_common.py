"""Host tests: only standard library, no ONNX Runtime or numpy required."""
import csv
import math
import struct
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from bench_common import (RESULT_RECORD, SOURCE_RECORD, clock, pack_result,
                          parse_cpu, percentile, pin_cpu, sha256, summarize,
                          unpack_source, unpack_result, write_csv)


class PercentileTests(unittest.TestCase):
    def test_interpolation_and_unsorted_input(self):
        values = [40, 10, 30, 20]
        self.assertEqual(percentile(values, 50), 25)
        self.assertAlmostEqual(percentile(values, 95), 38.5)
        self.assertAlmostEqual(percentile(values, 99), 39.7)
        self.assertEqual(values, [40, 10, 30, 20])

    def test_endpoints_single_and_duplicates(self):
        self.assertEqual(percentile([9, 1], 0), 1)
        self.assertEqual(percentile([9, 1], 100), 9)
        self.assertEqual(percentile([7], 99), 7)
        self.assertEqual(percentile([7, 7, 7], 95), 7)

    def test_invalid(self):
        with self.assertRaises(ValueError):
            percentile([], 50)
        for percent in (-1, 101, math.nan, math.inf):
            with self.subTest(percent=percent), self.assertRaises(ValueError):
                percentile([1], percent)

    def test_summary(self):
        result = summarize([10, 20, 30])
        self.assertEqual(result['count'], 3)
        self.assertEqual(result['mean_ns'], 20)
        self.assertEqual(result['max_ns'], 30)
        self.assertAlmostEqual(result['p95_ns'], 29)


class CsvTests(unittest.TestCase):
    def test_all_samples_preserved(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'samples.csv'
            write_csv(path, [(0, 12, 345), (1, 67, 890)])
            with path.open(newline='') as stream:
                self.assertEqual(list(csv.reader(stream)), [
                    ['run_idx', 'pre_ns', 'infer_ns'], ['0', '12', '345'], ['1', '67', '890']])

    def test_empty_has_header(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'samples.csv'
            write_csv(path, [])
            self.assertEqual(path.read_text().splitlines(), ['run_idx,pre_ns,infer_ns'])

    def test_hash_known_vector(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'data'
            path.write_bytes(b'abc')
            self.assertEqual(sha256(path), 'ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad')


class RecordTests(unittest.TestCase):
    def test_source_golden_bytes(self):
        data = bytes.fromhex('040302011817161514131211')
        self.assertEqual(SOURCE_RECORD.size, 12)
        self.assertEqual(unpack_source(data), (0x01020304, 0x1112131415161718))
        self.assertEqual(SOURCE_RECORD.pack(*unpack_source(data)), data)

    def test_result_golden_bytes(self):
        data = pack_result(1, 2, 3, 255, 50)
        self.assertEqual(RESULT_RECORD.size, 22)
        self.assertEqual(data.hex(), '0100000002000000000000000300000000000000ff32')
        self.assertEqual(unpack_result(data), (1, 2, 3, 255, 50))

    def test_boundaries(self):
        frame, stamp = (1 << 32) - 1, (1 << 64) - 1
        self.assertEqual(unpack_source(SOURCE_RECORD.pack(frame, stamp)), (frame, stamp))
        self.assertEqual(unpack_result(pack_result(frame, stamp, stamp, 255, 100)),
                         (frame, stamp, stamp, 255, 100))
        for args in ((1 << 32, 0, 0, 0, 0), (0, 0, 0, 256, 0)):
            with self.assertRaises(struct.error):
                pack_result(*args)

    def test_bad_sizes_and_values(self):
        for length in (0, 11, 13, 100):
            with self.assertRaises(ValueError):
                unpack_source(bytes(length))
        for length in (0, 21, 23, 100):
            with self.assertRaises(ValueError):
                unpack_result(bytes(length))
        for confidence in (-1, 101, 0.5, math.nan, math.inf):
            with self.assertRaises(ValueError):
                pack_result(0, 0, 0, 0, confidence)
        for data in (RESULT_RECORD.pack(0, 2, 1, 0, 0),
                     RESULT_RECORD.pack(0, 0, 0, 0, 101)):
            with self.assertRaises(ValueError):
                unpack_result(data)
        with self.assertRaises(ValueError):
            pack_result(0, 2, 1, 0, 0)


class PlatformTests(unittest.TestCase):
    def test_cpu_list(self):
        self.assertEqual(parse_cpu('0,2,2'), {0, 2})
        for value in ('', '-1', '0,a', '0,'):
            with self.subTest(value=value), self.assertRaises(ValueError):
                parse_cpu(value)

    def test_nonlinux_affinity_fails_explicitly(self):
        with patch('bench_common.sys.platform', 'darwin'), self.assertRaises(RuntimeError):
            pin_cpu({0})

    def test_clock_increases(self):
        now, name = clock()
        self.assertIn(name, ('CLOCK_MONOTONIC_RAW', 'perf_counter_ns'))
        start = now()
        self.assertGreaterEqual(now(), start)

    @unittest.skipUnless(sys.platform.startswith('linux'), 'Linux affinity only')
    def test_linux_affinity_roundtrip(self):
        import os
        original = os.sched_getaffinity(0)
        try:
            self.assertEqual(pin_cpu({min(original)}), [min(original)])
        finally:
            os.sched_setaffinity(0, original)


if __name__ == '__main__':
    unittest.main()
