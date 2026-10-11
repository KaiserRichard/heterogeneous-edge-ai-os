"""Session configuration checks with a fake ORT API (standard library only)."""
import sys
import unittest
from pathlib import Path
from types import SimpleNamespace

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from model_runtime import Model


class SessionTests(unittest.TestCase):
    def fake_ort(self, shape=(1, 3, 224, 224), providers=None):
        captured = {}

        def session(path, sess_options, providers):
            captured.update(path=path, options=sess_options, providers=providers)
            return SimpleNamespace(
                get_inputs=lambda: [SimpleNamespace(name='image', shape=shape, type='tensor(float)')],
                get_outputs=lambda: [SimpleNamespace(name='logits')],
                get_providers=lambda: captured['active'],
                run=lambda outputs, feed: captured.update(outputs=outputs, feed=feed) or ['output'])

        captured['active'] = providers if providers is not None else ['CPUExecutionProvider']
        ort = SimpleNamespace(SessionOptions=SimpleNamespace,
                              ExecutionMode=SimpleNamespace(ORT_SEQUENTIAL='sequential'),
                              InferenceSession=session)
        return ort, captured

    def test_thread_options_provider_and_tensor_feed(self):
        ort, captured = self.fake_ort()
        model = Model(ort, 'fixture.onnx', 4)
        options = captured['options']
        self.assertEqual(options.intra_op_num_threads, 4)
        self.assertEqual(options.inter_op_num_threads, 1)
        self.assertEqual(options.execution_mode, 'sequential')
        self.assertEqual(captured['providers'], ['CPUExecutionProvider'])
        self.assertEqual(model.run('tensor'), 'output')
        self.assertEqual(captured['outputs'], ['logits'])
        self.assertEqual(captured['feed'], {'image': 'tensor'})

    def test_dynamic_dimensions_accept_fixed_tensor(self):
        ort, _ = self.fake_ort(shape=('batch', 3, 224, 224))
        Model(ort, 'fixture.onnx', 1)

    def test_wrong_shape_rejected(self):
        ort, _ = self.fake_ort(shape=(1, 3, 256, 256))
        with self.assertRaises(ValueError):
            Model(ort, 'fixture.onnx', 1)

    def test_extra_provider_rejected(self):
        ort, _ = self.fake_ort(providers=['OtherProvider', 'CPUExecutionProvider'])
        with self.assertRaises(RuntimeError):
            Model(ort, 'fixture.onnx', 1)


if __name__ == '__main__':
    unittest.main()
