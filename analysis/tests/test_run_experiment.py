"""Run the wrapper's exact inner shell with synthetic metadata, no tmux or Pi."""
import os
from pathlib import Path
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]

class WrapperTests(unittest.TestCase):
    def test_command_failure_with_healthy_power_marks_failed(self):
        source = (ROOT / 'scripts/pi/run_experiment.sh').read_text()
        block = source[source.index('inner=$(cat <<INNER'):source.index('# tmux keeps')]
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / 'scripts/pi').mkdir(parents=True)
            meta = root / 'scripts/pi/collect_metadata.sh'
            meta.write_text('#!/bin/bash\necho \'{"throttled":"0x0"}\'\n')
            meta.chmod(0o755)
            jq = root / 'jq'
            jq.write_text('#!/bin/bash\necho 0x0\n')
            jq.chmod(0o755)
            for rc in (0, 7):
                run = root / str(rc); run.mkdir()
                harness = 'repo=$1; run=$2; shift 2\n' + block + '\nbash -c "$inner"\n'
                result = subprocess.run(['bash', '-c', harness, 'test', str(root), str(run),
                                         'bash', '-c', f'exit {rc}'],
                                        env=dict(os.environ, PATH=str(root)+os.pathsep+os.environ['PATH'], HEA_PUSH='0'),
                                        capture_output=True, text=True)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual((run / 'exit_code').read_text().strip(), str(rc))
                self.assertEqual((run / 'DONE').exists(), rc == 0)
                self.assertEqual((run / 'FAILED').exists(), rc != 0)
                self.assertEqual((run / 'validity').read_text().strip(), 'OK' if rc == 0 else 'INVALID command exit=7')
