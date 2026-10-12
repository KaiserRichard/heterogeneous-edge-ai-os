"""Compare Python serialization with the production C packers; no ORT needed."""
import os
from pathlib import Path
import shlex
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from bench_common import SOURCE_RECORD, pack_result, unpack_source, unpack_result


class CrossLanguageTests(unittest.TestCase):
    def test_production_c_vectors(self):
        linux = Path(__file__).resolve().parents[2]
        with tempfile.TemporaryDirectory() as directory:
            helper = Path(directory) / 'ipc_vectors'
            subprocess.run(shlex.split(os.environ.get('CC', 'cc')) + [
                '-std=c99', '-Wall', '-Wextra', '-Werror', '-I', str(linux / 'include'),
                str(linux / 'tests/ipc_vectors.c'), str(linux / 'src/hea_ipc.c'),
                '-o', str(helper)], check=True, capture_output=True)
            data = subprocess.check_output([str(helper)])
        self.assertEqual(len(data), 34)
        frame, start, done = 0x01020304, 0x1112131415161718, 0x2122232425262728
        self.assertEqual(SOURCE_RECORD.pack(frame, start), data[:12])
        self.assertEqual(unpack_source(data[:12]), (frame, start))
        self.assertEqual(pack_result(frame, start, done, 231, 50), data[12:])
        self.assertEqual(unpack_result(data[12:]), (frame, start, done, 231, 50))


if __name__ == '__main__':
    unittest.main()
