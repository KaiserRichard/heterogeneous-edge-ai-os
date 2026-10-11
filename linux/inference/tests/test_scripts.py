"""Exercise shell orchestration with fake downloads/benchmarks; no network or timings."""
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1]


@unittest.skipUnless(shutil.which('bash'), 'bash unavailable')
class ScriptTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.bin = self.root / 'bin'
        self.bin.mkdir()
        self.env = dict(os.environ, PATH=str(self.bin) + os.pathsep + os.environ['PATH'],
                        TEST_PYTHON=sys.executable)

    def executable(self, name, body):
        path = self.bin / name
        path.write_text('#!' + sys.executable + '\n' + body)
        path.chmod(0o755)
        return path

    def invoke(self, name, *args):
        return subprocess.run([shutil.which('bash'), str(SCRIPTS / name), *map(str, args)],
                              env=self.env, capture_output=True, text=True, timeout=15)

    def fake_fetch_tools(self, pointer=False):
        self.env['PYTHON'] = str(self.executable('python-fetch', '''
import os, sys
from pathlib import Path
if sys.argv[1:4] == ['-m', 'pip', 'download']:
    args = sys.argv[4:]
    for required in ('manylinux_2_28_aarch64', 'manylinux2014_aarch64', '312', 'cp312', '--only-binary=:all:'):
        assert required in args, required
    dest = Path(args[args.index('--dest') + 1])
    (dest / 'fixture.whl').write_bytes(b'fake wheel, never install')
else:
    os.execv(os.environ['TEST_PYTHON'], [os.environ['TEST_PYTHON'], *sys.argv[1:]])
'''))
        self.executable('curl', '''
import sys
from pathlib import Path
path = Path(sys.argv[sys.argv.index('--output') + 1])
path.write_bytes(''' + ("b'version https://git-lfs.github.com/spec/v1\\n'" if pointer else "b'fake model fixture' + b'X' * 1000000") + ')\n')

    def test_fetch_target_and_manifest(self):
        self.fake_fetch_tools()
        bundle = self.root / 'bundle'
        result = self.invoke('fetch_offline_deps.sh', bundle)
        self.assertEqual(result.returncode, 0, result.stderr)
        manifest = (bundle / 'SHA256SUMS').read_text().splitlines()
        self.assertEqual(len(manifest), 3)
        for line in manifest:
            digest, path = line.split('  ', 1)
            self.assertEqual(hashlib.sha256((bundle / path).read_bytes()).hexdigest(), digest)
        config = json.loads((bundle / 'fetch-config.json').read_text())
        self.assertIn('mobilenetv2-12.onnx', config['model_url'])
        self.assertIn('aarch64', config['target'])

    def test_fetch_rejects_lfs_pointer(self):
        self.fake_fetch_tools(pointer=True)
        bundle = self.root / 'bundle'
        result = self.invoke('fetch_offline_deps.sh', bundle)
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse((bundle / 'SHA256SUMS').exists())

    def fake_sweep_tools(self, throttle):
        self.executable('uname', "print('Linux')\n")
        self.env['PYTHON'] = str(self.executable('python-sweep', '''
import os, sys
from pathlib import Path
if len(sys.argv) > 1 and sys.argv[1].endswith('/infer_bench.py'):
    args = sys.argv[2:]
    out = Path(args[args.index('--output') + 1])
    out.mkdir()
    (out / 'fixture.txt').write_text(args[args.index('--threads') + 1])
else:
    os.execv(os.environ['TEST_PYTHON'], [os.environ['TEST_PYTHON'], *sys.argv[1:]])
'''))
        self.executable('bash', '''
import os, sys
if sys.argv[1].endswith('/collect_metadata.sh'):
    print(''' + repr(json.dumps({'throttled': throttle})) + ''')
else:
    raise SystemExit('unexpected shell invocation')
''')

    def test_sweep_four_directories_and_metadata(self):
        self.fake_sweep_tools('0x0')
        root = self.root / 'sweep'
        result = self.invoke('sweep.sh', root, '--', '--model', 'fixture.onnx')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue((root / 'threads-1/bench/fixture.txt').exists(),
                        (result.stdout, result.stderr, [str(p.relative_to(root)) for p in root.rglob('*')]))
        for threads in range(1, 5):
            run = root / f'threads-{threads}'
            self.assertEqual((run / 'bench/fixture.txt').read_text(), str(threads))
            self.assertTrue((run / 'metadata-before.json').exists())
            self.assertTrue((run / 'metadata-after.json').exists())
            self.assertTrue(json.loads((run / 'validity.json').read_text())['eligible_for_aggregate'])

    def test_sweep_stressor_is_stopped_after_each_run(self):
        self.fake_sweep_tools('0x0')
        self.executable('setsid', "import os, sys\nos.setsid()\nos.execvp(sys.argv[1], sys.argv[1:])\n")
        stress = self.executable('stress-fixture', "import os, time\nprint(os.getpid(), flush=True)\ntime.sleep(30)\n")
        root = self.root / 'sweep'
        result = self.invoke('sweep.sh', root, '--stress', stress, '--')
        self.assertEqual(result.returncode, 0, result.stderr)
        for threads in range(1, 5):
            run = root / f'threads-{threads}'
            pid = int((run / 'stress.log').read_text().strip())
            with self.assertRaises(ProcessLookupError):
                os.kill(pid, 0)
            self.assertTrue(json.loads((run / 'validity.json').read_text())['eligible_for_aggregate'])

    def test_sweep_marks_throttled_runs_ineligible(self):
        self.fake_sweep_tools('0x1')
        root = self.root / 'sweep'
        result = self.invoke('sweep.sh', root)
        self.assertEqual(result.returncode, 0, result.stderr)
        for threads in range(1, 5):
            validity = json.loads((root / f'threads-{threads}/validity.json').read_text())
            self.assertFalse(validity['eligible_for_aggregate'])
            self.assertEqual(len(validity['reasons']), 2)


if __name__ == '__main__':
    unittest.main()
