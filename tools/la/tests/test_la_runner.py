"""Preflight contract using fake tools; never connects to hardware."""
import os
from pathlib import Path
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[3]


class RunnerTests(unittest.TestCase):
    def test_dry_run_only_probes_and_prints_gpio_commands(self):
        with tempfile.TemporaryDirectory() as temp:
            p = Path(temp)
            log = p / 'calls'
            script = '''#!/usr/bin/env python3
import os, sys
from pathlib import Path
name = Path(sys.argv[0]).name
with open(os.environ['LA_TEST_LOG'], 'a') as stream:
    stream.write(name + ' ' + ' '.join(sys.argv[1:]) + '\\n')
if name == 'sigrok-cli':
    print('fx2lafw: synthetic device')
if name == 'ssh':
    source = sys.stdin.read()
    compile(source, '<dry-run ssh Python>', 'exec')
    assert 'GPIO27' in source and 'gpioset' in source
    assert "subprocess.run(['gpioset', '--version']" in source
    assert 'print(shlex.join' in source
    print('Would run: gpioset --mode=time --sec=1 /dev/gpiochip4 27=1')
'''
            for name in ('sigrok-cli', 'ssh', 'st-flash'):
                path = p / name
                path.write_text(script)
                path.chmod(0o755)
            out = p / 'must-not-exist'
            env = dict(os.environ, PATH=str(p)+os.pathsep+os.environ['PATH'],
                       SIGROK_CLI=str(p/'sigrok-cli'), LA_TEST_LOG=str(log))
            result = subprocess.run(['bash', str(ROOT/'tools/la/la_e4.sh'), '--dry-run', str(out)],
                                    env=env, capture_output=True, text=True, timeout=10)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertFalse(out.exists())
            calls = log.read_text().splitlines()
            self.assertEqual(len(calls), 3)
            self.assertIn('sigrok-cli --scan', calls)
            self.assertIn('st-flash read /dev/null 0x08000000 4', calls)
            self.assertIn('Would run: gpioset', result.stdout)
            self.assertFalse(any('reset' in call or '--output-file' in call for call in calls))


if __name__ == '__main__':
    unittest.main()
