"""Real fake-camera process -> Unix datagrams -> native ring reader -> inference.

ORT is replaced by a deterministic model; numpy preprocessing is real. Socketpair
endpoints exercise the IPC on hosts that prohibit binding filesystem sockets.
"""
import contextlib
import csv
import io
import json
import mmap
import os
from pathlib import Path
import socket
import struct
import subprocess
import sys
import tempfile
import time
from types import SimpleNamespace
import unittest
from unittest.mock import patch
import uuid

INFERENCE = Path(__file__).resolve().parents[1]
CAMERA = INFERENCE.parent / 'camera'
sys.path.insert(0, str(INFERENCE))
import infer_server
from bench_common import RESULT_RECORD, SOURCE_RECORD
from model_runtime import ShmImage, preprocess
try:
    import numpy as np
except ImportError:
    np = None


def ring_path(name):
    return Path('/tmp/hea-cam-' + name) if sys.platform == 'darwin' else Path('/dev/shm') / name


class Endpoint:
    def __init__(self, sock):
        self.sock = sock
    def __enter__(self):
        return self
    def __exit__(self, *args):
        pass
    def bind(self, path):
        pass  # Already connected real Unix socketpair, no filesystem bind needed.
    def recv(self, *args):
        return self.sock.recv(*args)
    def sendto(self, payload, flags, path):
        return self.sock.send(payload, flags)


@unittest.skipIf(np is None, 'numpy unavailable')
class CameraInferenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        build = subprocess.run(['make', '-C', str(CAMERA), 'all'], capture_output=True, text=True)
        if build.returncode:
            raise RuntimeError(build.stdout + build.stderr)

    def test_fake_camera_to_inference_overwrites_and_rgb(self):
        name = 'infer-test-' + uuid.uuid4().hex[:12]
        self.addCleanup(lambda: ring_path(name).unlink(missing_ok=True))
        source_tx, source_rx = socket.socketpair(socket.AF_UNIX, socket.SOCK_DGRAM)
        bridge_tx, bridge_rx = socket.socketpair(socket.AF_UNIX, socket.SOCK_DGRAM)
        with source_tx, source_rx, bridge_tx, bridge_rx, tempfile.TemporaryDirectory() as directory:
            source_rx.settimeout(2)
            bridge_rx.settimeout(2)
            csv_path = Path(directory) / 'camera.csv'
            result = subprocess.run([str(CAMERA / 'build/hea_cam'), '--output-fd', str(source_tx.fileno()),
                '--shm', name, '--width', '16', '--height', '8', '--slots', '2', '--fps', '20',
                '--count', '5', '--csv', str(csv_path)], pass_fds=(source_tx.fileno(),),
                capture_output=True, text=True, timeout=10)
            self.assertEqual(result.returncode, 0, result.stderr)
            with csv_path.open() as stream:
                source_rows = list(csv.DictReader(stream))
            self.assertEqual([int(r['frame_id']) for r in source_rows], list(range(5)))
            calls = []
            def run(tensor):
                calls.append(tensor.copy())
                logits = np.zeros(1000)
                logits[7] = 100
                return logits
            reader = ShmImage(name)
            self.addCleanup(reader.close)
            output = io.StringIO()
            with patch.object(infer_server.socket, 'socket', side_effect=[Endpoint(source_rx), Endpoint(bridge_tx)]), \
                    patch.object(Path, 'unlink'), contextlib.redirect_stderr(io.StringIO()) as stderr:
                count = infer_server.serve(SimpleNamespace(run=run), np, None, 's', 'b',
                    lambda: time.clock_gettime_ns(time.CLOCK_MONOTONIC), 5,
                    csv.writer(output), image_source=reader)
            self.assertEqual(count, 2)
            rows = list(csv.reader(io.StringIO(output.getvalue())))
            self.assertEqual([r[-1] for r in rows], ['overwritten'] * 3 + ['sent'] * 2)
            self.assertTrue(all(row[2] == '' for row in rows[:3]))
            self.assertEqual(json.loads(stderr.getvalue()), dict(processed=2, skipped=0, overwritten=3, torn=0))
            for index, frame_id in enumerate((3, 4)):
                record = RESULT_RECORD.unpack(bridge_rx.recv(100))
                self.assertEqual(record[:2], (frame_id, int(source_rows[frame_id]['t_input_ns'])))
                self.assertEqual(record[3:], (7, 100))
                self.assertGreaterEqual(record[2], record[1])
                image = np.empty((8, 16, 3), dtype=np.uint8)
                image[:, :, 0] = np.arange(16) + frame_id
                image[:, :, 1] = np.arange(8)[:, None] + frame_id
                image[:, :, 2] = frame_id
                np.testing.assert_array_equal(calls[index], preprocess(np, image))
            # Force an in-progress write in one slot; no preprocessing/inference/result.
            with ring_path(name).open('r+b') as stream, mmap.mmap(stream.fileno(), 0) as mapping:
                stride = struct.unpack_from('<I', mapping, 24)[0]
                slot = 64 + (4 % 2) * stride
                seq = struct.unpack_from('<Q', mapping, slot)[0]
                struct.pack_into('<Q', mapping, slot, seq + 1)
                source_tx.send(SOURCE_RECORD.pack(4, int(source_rows[4]['t_sensor_ns'])))
                output = io.StringIO()
                with patch.object(infer_server.socket, 'socket', side_effect=[Endpoint(source_rx), Endpoint(bridge_tx)]), \
                        patch.object(Path, 'unlink'), contextlib.redirect_stderr(io.StringIO()) as stderr:
                    self.assertEqual(infer_server.serve(SimpleNamespace(run=run), np, None, 's', 'b',
                        lambda: time.clock_gettime_ns(time.CLOCK_MONOTONIC), 1,
                        csv.writer(output), image_source=reader), 0)
                self.assertEqual(list(csv.reader(io.StringIO(output.getvalue())))[0][-2:], ['', 'torn'])
                self.assertEqual(json.loads(stderr.getvalue())['torn'], 1)
                self.assertEqual(len(calls), 2)

    def test_fixed_preprocessing_bit_identical(self):
        image = np.random.default_rng(12345).integers(0, 256, (256, 256, 3), dtype=np.uint8)
        indices = np.arange(224, dtype=np.int64) * 256 // 224
        old = image[indices[:, None], indices[None, :], :].astype(np.float32)
        old /= np.float32(255)
        old -= np.array([.485, .456, .406], dtype=np.float32)
        old /= np.array([.229, .224, .225], dtype=np.float32)
        old = np.ascontiguousarray(old.transpose(2, 0, 1)[None, ...])
        self.assertEqual(old.tobytes(), preprocess(np, image).tobytes())

    def test_latest_reader_returns_newest_consistent_slot_and_repeated_status(self):
        name = 'latest-test-' + uuid.uuid4().hex[:12]
        self.addCleanup(lambda: ring_path(name).unlink(missing_ok=True))
        source_tx, source_rx = socket.socketpair(socket.AF_UNIX, socket.SOCK_DGRAM)
        with source_tx, source_rx:
            result = subprocess.run([str(CAMERA / 'build/hea_cam'), '--shm', name,
                '--width', '16', '--height', '8', '--slots', '4', '--fps', '1000',
                '--count', '7', '--output-fd', str(source_tx.fileno())],
                pass_fds=(source_tx.fileno(),),
                capture_output=True, text=True, timeout=10)
        self.assertEqual(result.returncode, 0, result.stderr)
        reader = ShmImage(name)
        try:
            image, sequence, freshness = reader.read_latest(np)
            self.assertEqual((sequence, freshness), (6, 'new'))
            self.assertEqual(tuple(image[0, 0]), (6, 6, 6))
            repeated, repeated_seq, repeated_status = reader.read_latest(np)
            self.assertEqual((repeated_seq, repeated_status), (6, 'repeated'))
            np.testing.assert_array_equal(image, repeated)
        finally:
            reader.close()


class CameraCliTests(unittest.TestCase):
    def test_fixed_default_and_explicit_csv_identical(self):
        from unittest.mock import MagicMock
        outputs = []
        for extra in ([], ['--image-source', 'fixed']):
            receiver, sender = MagicMock(), MagicMock()
            receiver.__enter__.return_value = receiver
            sender.__enter__.return_value = sender
            receiver.recv.return_value = SOURCE_RECORD.pack(3, 100)
            with tempfile.TemporaryDirectory() as directory:
                path = Path(directory) / 'infer.csv'
                with patch.dict(sys.modules, {'numpy': SimpleNamespace(), 'onnxruntime': SimpleNamespace()}), \
                        patch.object(infer_server, 'Model', return_value=SimpleNamespace(run=lambda x: None)), \
                        patch.object(infer_server, 'load_image', return_value='image'), \
                        patch.object(infer_server, 'preprocess', return_value='tensor'), \
                        patch.object(infer_server, 'classify', return_value=(1, .5)), \
                        patch.object(infer_server, 'clock', return_value=(lambda: 200, 'fixed-test')), \
                        patch.object(infer_server.socket, 'socket', side_effect=[receiver, sender]), \
                        patch.object(infer_server, 'ShmImage') as shm, patch.object(Path, 'unlink'), \
                        patch.object(infer_server.signal, 'signal'), contextlib.redirect_stderr(io.StringIO()):
                    infer_server.main(['--socket', 's', '--output', 'b', '--max-frames', '1',
                                       '--csv', str(path), *extra])
                    shm.assert_not_called()
                outputs.append(path.read_bytes())
        self.assertEqual(outputs, [b'frame_id,t_input_ns,t_done_ns,status\r\n3,100,200,sent\r\n'] * 2)

    def test_shm_cli_selects_bridge_clock_and_closes_reader(self):
        with patch.dict(sys.modules, {'numpy': SimpleNamespace(), 'onnxruntime': SimpleNamespace()}), \
                patch.object(infer_server, 'Model'), patch.object(infer_server, 'load_image') as fixed, \
                patch.object(infer_server, 'ShmImage') as shm, patch.object(infer_server, 'serve') as serve, \
                patch.object(infer_server, 'clock', return_value=(lambda: 123, 'bridge-clock')) as selected_clock, \
                patch.object(infer_server.signal, 'signal'), contextlib.redirect_stderr(io.StringIO()):
            infer_server.main(['--socket', 's', '--output', 'b', '--image-source', 'shm:test'])
        fixed.assert_not_called()
        shm.assert_called_once_with('test')
        self.assertEqual(serve.call_args.args[5](), 123)
        self.assertEqual(selected_clock.call_count, 2)
        self.assertIs(serve.call_args.kwargs['image_source'], shm.return_value)
        shm.return_value.close.assert_called_once()


if __name__ == '__main__':
    unittest.main()
