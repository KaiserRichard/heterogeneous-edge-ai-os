"""Behavioral integration tests using fake inference, never performance evidence."""
import contextlib
import errno
import io
import json
import socket
import sys
import tempfile
import threading
import time
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import infer_bench
import infer_server
from bench_common import RESULT_RECORD, SOURCE_RECORD


class BenchmarkTests(unittest.TestCase):
    def test_cold_warmup_and_measured_partition(self):
        calls = []
        preparations = []

        class FakeModel:
            def __init__(self, ort, path, threads):
                self.session = SimpleNamespace(get_providers=lambda: ['CPUExecutionProvider'])
                calls.append(('create', threads))

            def run(self, tensor):
                calls.append(('run', tensor))

        def prepare(np, image):
            preparations.append(image)
            return 'tensor'

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            model = root / 'fixture.onnx'
            model.write_bytes(b'fake model; not a measurement')
            ticks = iter(range(0, 10000, 10))
            with patch.dict(sys.modules, {
                    'numpy': SimpleNamespace(__version__='fake-numpy'),
                    'onnxruntime': SimpleNamespace(__version__='fake-ort')}), \
                    patch.object(infer_bench, 'Model', FakeModel), \
                    patch.object(infer_bench, 'load_image', return_value='image'), \
                    patch.object(infer_bench, 'preprocess', side_effect=prepare), \
                    patch.object(infer_bench, 'clock', return_value=(lambda: next(ticks), 'synthetic')), \
                    patch.object(infer_bench, 'pin_cpu', return_value=[0]), \
                    contextlib.redirect_stdout(io.StringIO()):
                infer_bench.main(['--model', str(model), '--threads', '3', '--warmup', '2',
                                  '--runs', '3', '--output', str(root / 'run')])
            self.assertEqual(calls[0], ('create', 3))
            self.assertEqual(len(calls) - 1, 1 + 2 + 3)
            self.assertEqual(len(preparations), 1 + 2 + 3)
            report = json.loads((root / 'run/summary.json').read_text())
            self.assertEqual(report['summary']['inference']['count'], 3)
            self.assertEqual(report['summary']['cold_start']['count'], 1)
            self.assertEqual(report['config']['ort_version'], 'fake-ort')
            self.assertEqual((root / 'run/samples.csv').read_text().splitlines(),
                             ['run_idx,pre_ns,infer_ns', '0,10,10', '1,10,10', '2,10,10'])


@unittest.skipUnless(hasattr(socket, 'AF_UNIX'), 'Unix sockets unavailable')
class ServerTests(unittest.TestCase):
    def bind_or_skip(self, sock, path):
        try:
            sock.bind(str(path))
        except OSError as exc:
            if exc.errno in (errno.EPERM, errno.EACCES):
                self.skipTest(f'Unix socket bind denied by environment: {exc}')
            raise

    def test_datagrams_preserve_timestamps_drop_bad_sizes_and_cleanup(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / 's'
            bridge = Path(directory) / 'b'
            errors = []
            calls = []
            model = SimpleNamespace(run=lambda tensor: calls.append(tensor) or 'output')

            def worker():
                try:
                    infer_server.serve(model, None, 'image', source, bridge, lambda: 200, 1)
                except BaseException as exc:
                    errors.append(exc)

            with socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM) as receiver, \
                    socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM) as sender, \
                    patch.object(infer_server, 'preprocess', return_value='tensor'), \
                    patch.object(infer_server, 'classify', return_value=(999, 0.5)), \
                    contextlib.redirect_stderr(io.StringIO()) as stderr:
                self.bind_or_skip(receiver, bridge)
                receiver.settimeout(2)
                thread = threading.Thread(target=worker, daemon=True)
                thread.start()
                deadline = time.monotonic() + 2
                while not source.exists() and thread.is_alive() and time.monotonic() < deadline:
                    time.sleep(0.005)
                self.assertTrue(source.exists(), errors)
                sender.sendto(b'x' * 15, str(source))
                sender.sendto(b'x' * 100, str(source))
                sender.sendto(SOURCE_RECORD.pack(42, 100), str(source))
                record = receiver.recv(100)
                thread.join(2)
                self.assertFalse(thread.is_alive())
                self.assertEqual(errors, [])
                self.assertEqual(RESULT_RECORD.unpack(record), (42, 100, 200, 231, 50))
                self.assertEqual(calls, ['tensor'])
                self.assertEqual(stderr.getvalue().count('dropping malformed'), 2)
                self.assertFalse(source.exists())

    def test_existing_endpoint_is_preserved(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 's'
            with socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM) as owner:
                self.bind_or_skip(owner, path)
                with self.assertRaises(OSError):
                    infer_server.serve(None, None, None, path, path, lambda: 0, 1)
                self.assertTrue(path.exists())


class ServerMockTests(unittest.TestCase):
    def test_record_flow_without_socket_permission(self):
        from unittest.mock import MagicMock
        receiver, sender = MagicMock(), MagicMock()
        receiver.__enter__.return_value = receiver
        sender.__enter__.return_value = sender
        receiver.recv.side_effect = [b'x' * 17, SOURCE_RECORD.pack(99, 100)]
        model = SimpleNamespace(run=lambda tensor: 'logits')
        with patch.object(infer_server.socket, 'socket', side_effect=[receiver, sender]), \
                patch.object(infer_server, 'preprocess', return_value='tensor'), \
                patch.object(infer_server, 'classify', return_value=(999, 0.255)), \
                patch.object(Path, 'unlink') as unlink, \
                contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(infer_server.serve(model, None, None, 'source', 'bridge', lambda: 200, 1), 1)
        data, flags, target = sender.sendto.call_args.args
        self.assertEqual(flags, socket.MSG_DONTWAIT)
        self.assertEqual(RESULT_RECORD.unpack(data), (99, 100, 200, 231, 26))
        self.assertEqual(target, 'bridge')
        unlink.assert_called_once()

    def test_completion_csv_includes_nonblocking_ipc_drop(self):
        import csv
        from unittest.mock import MagicMock
        receiver, sender = MagicMock(), MagicMock()
        receiver.__enter__.return_value = receiver
        sender.__enter__.return_value = sender
        receiver.recv.return_value = SOURCE_RECORD.pack(99, 100)
        sender.sendto.side_effect = BlockingIOError(errno.EAGAIN, 'full queue')
        model = SimpleNamespace(run=lambda tensor: 'logits')
        output = io.StringIO()
        with patch.object(infer_server.socket, 'socket', side_effect=[receiver, sender]), \
                patch.object(infer_server, 'preprocess', return_value='tensor'), \
                patch.object(infer_server, 'classify', return_value=(1, 0.5)), \
                patch.object(Path, 'unlink'):
            self.assertEqual(infer_server.serve(model, None, None, 's', 'b', lambda: 200,
                                               1, csv.writer(output)), 1)
        self.assertEqual(list(csv.reader(io.StringIO(output.getvalue()))),
                         [['99', '100', '200', 'dropped']])

    def test_c_pipeline_options(self):
        with patch.dict(sys.modules, {'numpy': SimpleNamespace(),
                                     'onnxruntime': SimpleNamespace()}), \
                patch.object(infer_server, 'pin_cpu') as affinity, \
                patch.object(infer_server, 'Model') as model, \
                patch.object(infer_server, 'load_image'), \
                patch.object(infer_server, 'clock', return_value=(lambda: 1, 'synthetic')), \
                patch.object(infer_server, 'serve') as serve, \
                patch.object(infer_server.signal, 'signal'), \
                contextlib.redirect_stderr(io.StringIO()):
            infer_server.main(['--socket', 'source', '--output', 'bridge',
                               '--model', 'fixture.onnx', '--threads', '2', '--cpu', '1'])
        affinity.assert_called_once_with({1})
        self.assertEqual(model.call_args.args[1:], ('fixture.onnx', 2))
        self.assertEqual(serve.call_args.args[3:5], ('source', 'bridge'))

    def test_cleanup_on_send_failure(self):
        from unittest.mock import MagicMock
        receiver, sender = MagicMock(), MagicMock()
        receiver.__enter__.return_value = receiver
        sender.__enter__.return_value = sender
        receiver.recv.return_value = SOURCE_RECORD.pack(99, 100)
        sender.sendto.side_effect = FileNotFoundError('bridge absent')
        model = SimpleNamespace(run=lambda tensor: 'logits')
        with patch.object(infer_server.socket, 'socket', side_effect=[receiver, sender]), \
                patch.object(infer_server, 'preprocess', return_value='tensor'), \
                patch.object(infer_server, 'classify', return_value=(12, 0.25)), \
                patch.object(Path, 'unlink') as unlink:
            with self.assertRaises(FileNotFoundError):
                infer_server.serve(model, None, None, 'source', 'bridge', lambda: 200, 1)
        unlink.assert_called_once()


if __name__ == '__main__':
    unittest.main()
