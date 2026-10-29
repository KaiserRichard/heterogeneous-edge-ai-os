"""Fixed MobileNetV2 workload. Third-party imports occur only when needed."""
from pathlib import Path

DEFAULT_MODEL = 'mobilenetv2-12.onnx'
INPUT_SHAPE = (1, 3, 224, 224)


def load_image(np, seed, path=None):
    if path is None:
        return np.random.default_rng(seed).integers(0, 256, (256, 256, 3), dtype=np.uint8)
    path = Path(path)
    if path.suffix.lower() == '.npy':
        image = np.load(path, allow_pickle=False)
    else:
        # P6 RGB PPM: parse header tokens/comments without an image library.
        with path.open('rb') as stream:
            def token():
                value = bytearray()
                while True:
                    byte = stream.read(1)
                    if not byte:
                        raise ValueError('truncated PPM header')
                    if byte == b'#' and not value:
                        stream.readline()
                    elif byte.isspace():
                        if value:
                            # Treat CRLF as a single header separator.
                            if byte == b'\r' and stream.peek(1)[:1] == b'\n':
                                stream.read(1)
                            return bytes(value)
                    else:
                        value.extend(byte)
            if token() != b'P6':
                raise ValueError('image must be .npy or binary RGB PPM (P6)')
            width, height, maximum = int(token()), int(token()), int(token())
            if (width, height, maximum) != (256, 256, 255):
                raise ValueError('PPM must be 256x256 with maxval 255')
            payload = stream.read()
        if len(payload) != 256 * 256 * 3:
            raise ValueError('incorrect PPM pixel byte count')
        image = np.frombuffer(payload, dtype=np.uint8).reshape(256, 256, 3)
    if image.shape != (256, 256, 3) or image.dtype != np.uint8:
        raise ValueError('image must be 256x256x3 RGB uint8')
    return image


def preprocess(np, image):
    # Nearest-neighbor resize; identical indices for the original 256x256 input.
    rows = np.arange(224, dtype=np.int64) * image.shape[0] // 224
    cols = np.arange(224, dtype=np.int64) * image.shape[1] // 224
    rgb = image[rows[:, None], cols[None, :], :].astype(np.float32)
    rgb /= np.float32(255)
    rgb -= np.array([0.485, 0.456, 0.406], dtype=np.float32)
    rgb /= np.array([0.229, 0.224, 0.225], dtype=np.float32)
    return np.ascontiguousarray(rgb.transpose(2, 0, 1)[None, ...])


class ShmImage:
    """Lazy native seqlock reader. Open after the first camera notification.

    ctypes releases the GIL during the bounded atomic copy. No view into shared
    memory escapes the native sequence check; preprocessing uses a private copy.
    """
    def __init__(self, name):
        import ctypes
        import re
        import sys
        if not re.fullmatch(r'/?[A-Za-z0-9_-]{1,100}', name):
            raise ValueError('invalid shared-memory name')
        self.name = name
        suffix = 'dylib' if sys.platform == 'darwin' else 'so'
        path = Path(__file__).resolve().parents[1] / 'camera/build' / f'libhea_camera.{suffix}'
        self.lib = ctypes.CDLL(str(path))
        self.lib.hea_camera_open.argtypes = [ctypes.c_char_p, ctypes.POINTER(ctypes.c_uint32),
                                           ctypes.POINTER(ctypes.c_uint32)]
        self.lib.hea_camera_open.restype = ctypes.c_void_p
        self.lib.hea_camera_read.argtypes = [ctypes.c_void_p, ctypes.c_uint32,
                                           ctypes.POINTER(ctypes.c_uint8), ctypes.c_size_t]
        self.lib.hea_camera_read.restype = ctypes.c_int
        self.lib.hea_camera_close.argtypes = [ctypes.c_void_p]
        self.lib.hea_camera_close.restype = None
        self.lib.hea_camera_error.restype = ctypes.c_char_p
        self.handle = None

    def read(self, np, frame_id):
        import ctypes
        if self.handle is None:
            width, height = ctypes.c_uint32(), ctypes.c_uint32()
            self.handle = self.lib.hea_camera_open(self.name.encode(), ctypes.byref(width),
                                                 ctypes.byref(height))
            if not self.handle:
                raise RuntimeError(self.lib.hea_camera_error().decode())
            self.width, self.height = width.value, height.value
            self.buffer = (ctypes.c_uint8 * (self.width * self.height * 3))()
        result = self.lib.hea_camera_read(self.handle, frame_id, self.buffer, len(self.buffer))
        if result < 0:
            raise RuntimeError(self.lib.hea_camera_error().decode())
        if result:
            return None, {1: 'overwritten', 2: 'torn'}[result]
        # bytes owns the verified copy, including across subsequent read calls.
        return np.frombuffer(bytes(self.buffer), dtype=np.uint8).reshape(
            self.height, self.width, 3), None

    def close(self):
        if self.handle is not None:
            self.lib.hea_camera_close(self.handle)
            self.handle = None


class Model:
    def __init__(self, ort, path, threads):
        options = ort.SessionOptions()
        options.intra_op_num_threads = threads
        options.inter_op_num_threads = 1
        options.execution_mode = ort.ExecutionMode.ORT_SEQUENTIAL
        # Disable implicit worker affinity; --cpu applies before workers are created.
        self.session = ort.InferenceSession(str(path), sess_options=options,
                                            providers=['CPUExecutionProvider'])
        inputs = self.session.get_inputs()
        if len(inputs) != 1 or inputs[0].type != 'tensor(float)':
            raise ValueError('model must have one float32 input')
        shape = inputs[0].shape
        if len(shape) != len(INPUT_SHAPE) or any(
                isinstance(actual, int) and actual != expected
                for actual, expected in zip(shape, INPUT_SHAPE)):
            raise ValueError('model input must accept fixed 1x3x224x224 tensor')
        if self.session.get_providers() != ['CPUExecutionProvider']:
            raise RuntimeError('CPUExecutionProvider must be the only active provider')
        self.input_name = inputs[0].name
        self.output_name = self.session.get_outputs()[0].name

    def run(self, tensor):
        return self.session.run([self.output_name], {self.input_name: tensor})[0]


def classify(np, output):
    # Zoo model emits logits: stable softmax produces the reported confidence.
    scores = np.asarray(output, dtype=np.float64).reshape(-1)
    if scores.size != 1000 or not np.isfinite(scores).all():
        raise ValueError('expected 1000 finite ImageNet logits')
    class_id = int(np.argmax(scores))
    weights = np.exp(scores - scores.max())
    return class_id, float(weights[class_id] / weights.sum())


def add_runtime_args(parser):
    parser.add_argument('--model', default=DEFAULT_MODEL)
    parser.add_argument('--threads', type=int, choices=range(1, 5), default=1)
    parser.add_argument('--cpu', help='Linux CPU IDs, e.g. 0,1')
    parser.add_argument('--seed', type=int, default=12345)
    parser.add_argument('--image', help='256x256 RGB uint8 .npy or P6 PPM image')
