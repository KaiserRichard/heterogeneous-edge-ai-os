"""Optional numerical checks: skipped if numpy is not installed; never needs ORT."""
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from model_runtime import classify, load_image, preprocess

try:
    import numpy as np
except ImportError:
    np = None


@unittest.skipIf(np is None, 'numpy not installed; standard-library tests remain available')
class NumpyTests(unittest.TestCase):
    def test_seeded_input_and_normalization(self):
        image = load_image(np, 12345)
        np.testing.assert_array_equal(image, load_image(np, 12345))
        tensor = preprocess(np, image)
        self.assertEqual(tensor.shape, (1, 3, 224, 224))
        self.assertEqual(tensor.dtype, np.float32)
        self.assertTrue(tensor.flags.c_contiguous)
        for row, col in ((0, 0), (223, 223), (70, 91)):
            rgb = image[row * 256 // 224, col * 256 // 224] / 255
            expected = (rgb - [0.485, 0.456, 0.406]) / [0.229, 0.224, 0.225]
            np.testing.assert_allclose(tensor[0, :, row, col], expected, rtol=1e-5, atol=1e-6)

    def test_ppm_and_npy_equivalence(self):
        image = load_image(np, 12345)
        image[0, 0] = [10, 13, 32]  # Pixel whitespace must not be consumed as header.
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            np.save(root / 'image.npy', image)
            (root / 'image.ppm').write_bytes(b'P6\n# RGB fixture\n256 256\n255\r\n' + image.tobytes())
            for name in ('image.npy', 'image.ppm'):
                np.testing.assert_array_equal(load_image(np, 0, root / name), image)
            (root / 'bad.ppm').write_bytes(b'P6\n256 256\n255\nshort')
            with self.assertRaises(ValueError):
                load_image(np, 0, root / 'bad.ppm')

    def test_softmax_is_stable_and_class_id_zero_based(self):
        logits = np.full((1, 1000), -1000.0)
        logits[0, 999] = 1000
        self.assertEqual(classify(np, logits), (999, 1.0))
        class_id, confidence = classify(np, np.zeros((1, 1000)))
        self.assertEqual(class_id, 0)
        self.assertAlmostEqual(confidence, 0.001)
        for bad in (np.zeros(2), np.full(1000, np.nan)):
            with self.assertRaises(ValueError):
                classify(np, bad)


if __name__ == '__main__':
    unittest.main()
